#requires -Version 7.0
[CmdletBinding()]
param([string]$Root = (Split-Path -Parent $PSScriptRoot), [switch]$RequireProtectedOriginals)
. (Join-Path $PSScriptRoot 'SampleTools.ps1')
$locked=Assert-SampleSourceLock -Root $Root
$lock=$locked.lock
$manifest=Read-SampleJson (Get-SamplePath $Root $lock.acceptance.evidenceManifest)
$schema=Get-SamplePath $Root 'schemas/manifest.schema.json'
Assert-SampleJsonSchema (Get-SamplePath $Root $lock.acceptance.evidenceManifest) $schema
Assert-SampleJsonSchema (Get-SamplePath $Root $manifest.importManifest) $schema
if((Get-FileHash -LiteralPath (Get-SamplePath $Root $manifest.importManifest)).Hash -cne $manifest.importManifestSha256 -or (Get-FileHash -LiteralPath (Get-SamplePath $Root $manifest.linkManifest)).Hash -cne $manifest.linkManifestSha256){throw 'Imported provenance or link-resolution manifest changed.'}
$import=Read-SampleJson (Get-SamplePath $Root $manifest.importManifest)
if($import.sourceSha -cne $lock.evidenceSource.sourceSha -or $manifest.sourceSha -cne $import.sourceSha -or $manifest.fileCount -ne @($manifest.files).Count -or $import.fileCount -ne @($import.files).Count){throw 'Evidence provenance or file count mismatch.'}
$planPath=Get-SamplePath $Root 'releases/v0.4.0/manifests/import-plan.json'
if((Get-FileHash -LiteralPath $planPath).Hash -cne $import.planSha256){throw 'Reviewed import plan changed.'}
$sourceSeen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$archiveSeen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$normalSeen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$gitCount=0;$protectedVerified=0;$protectedAbsent=0;$bytes=0L
foreach($entry in $import.files){
    if(-not $sourceSeen.Add($entry.sourcePath) -or -not $archiveSeen.Add($entry.destinationPath) -or $entry.sourceSha -cne $import.sourceSha){throw 'Duplicate or inconsistent import reference.'}
    $file=Get-SamplePath $Root $entry.destinationPath
    if($entry.storage -ceq 'git'){
        if(-not $entry.destinationPath.StartsWith('archive/imported-from-spherewright/'+$import.sourceSha+'/')){throw 'Raw archive namespace mismatch.'}
        Assert-SampleFile $Root $entry.destinationPath $entry.size $entry.sha256;++$gitCount
    }elseif($entry.storage -ceq 'protected-local'){
        if($entry.sourcePath -cne 'docs/experience-ledger.md' -or -not $entry.destinationPath.StartsWith('.local/protected-import/')){throw 'Unexpected private-original disposition.'}
        if(Test-Path -LiteralPath $file){Assert-SampleFile $Root $entry.destinationPath $entry.size $entry.sha256;++$protectedVerified}else{++$protectedAbsent}
    }else{throw 'Unknown import storage scope.'}
    $bytes += [long]$entry.size
}
if($gitCount -ne $import.gitArchiveCount -or $protectedVerified+$protectedAbsent -ne $import.protectedLocalCount -or $bytes -ne $import.totalSourceBytes){throw 'Archive totals mismatch.'}
if($RequireProtectedOriginals -and $protectedAbsent -gt 0){throw 'Protected originals are unavailable in this environment.'}
foreach($entry in $manifest.files){
    if(-not $normalSeen.Add($entry.path) -or -not $sourceSeen.Contains($entry.sourcePath)){throw 'Duplicate normalized reference or unknown source.'}
    Assert-SampleFile $Root $entry.path $entry.size $entry.sha256
}
if($normalSeen.Count -ne $sourceSeen.Count){throw 'Not every import has a declared normalized derivative.'}
$tracked=@(Get-SampleTrackedPaths $Root)
$actualArchive=@($tracked|Where-Object {$_ -like 'archive/imported-from-spherewright/*'})
if($actualArchive.Count -ne $gitCount -or @($actualArchive|Where-Object {-not $archiveSeen.Contains($_)}).Count -gt 0){throw 'Tracked raw archive is incomplete or contains undeclared files.'}
$findings=[Collections.Generic.List[object]]::new();$relativeLinks=0
foreach($path in $tracked){
    if($path -ceq 'deps/Spherewright'){continue}
    if($path -match '(^|/)(?:\.local|artifacts|bin|obj|TestResults)/|\.(?:dsv(?:\.tmp)?|autosave|dll|exe|pdb|zip|dmp|dump)$|(?:^|/)(?:bridge-[^/]+|[^/]*(?:ticket|credential)[^/]*)\.json$') {throw "Forbidden tracked local/binary payload: $path"}
    $full=Get-SamplePath $Root $path
    if(-not(Test-Path -LiteralPath $full -PathType Leaf)){throw "Tracked sample file missing: $path"}
    if([IO.Path]::GetExtension($full) -notin @('.md','.ps1','.json','.yml','.yaml','.txt','.schema')){continue}
    $text=[IO.File]::ReadAllText($full)
    if([IO.Path]::GetExtension($full) -eq '.json'){$null=$text|ConvertFrom-Json -Depth 100}
    $rules=@{
        absolutePath='(?i)(?:\b[A-Z]:[\\/][^\s`<>"'']+|/(?:home|Users)/[^/\s`<>]+/)'
        credential='\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9_.-]{20,})\b'
        privateField='"(?:steamId|realSaveName|authenticationToken)"\s*:\s*"(?!<|redacted|REDACTED)[^"]+"'
    }
    foreach($rule in $rules.Keys){if($text -match $rules[$rule]){$findings.Add([pscustomobject]@{path=$path;rule=$rule})}}
    if([IO.Path]::GetExtension($full) -ne '.md' -or $path.StartsWith('archive/imported-from-spherewright/')){continue}
    $fence=$false
    foreach($line in ($text -split '\r?\n')){
        if($line -match '^\s*(?:```|~~~)'){$fence=-not $fence;continue};if($fence){continue}
        foreach($m in [regex]::Matches($line,'\]\((?<target>[^)\r\n]+)\)')){
            $target=$m.Groups['target'].Value.Trim().Trim('<','>')
            if($target -match '^(?:[A-Za-z][A-Za-z0-9+.-]*:|#)'){continue}
            $target=($target -split '\s+"',2)[0]
            $target=[Uri]::UnescapeDataString(($target -split '[#?]',2)[0])
            if(-not $target){continue}
            $absolute=[IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $full) $target))
            $relative=[IO.Path]::GetRelativePath($Root,$absolute).Replace('\','/')
            if($relative.StartsWith('../') -or -not(Test-Path -LiteralPath (Get-SamplePath $Root $relative))){throw "Broken or escaping relative Markdown link in $path"}
            ++$relativeLinks
        }
    }
}
if($findings.Count -gt 0){$findings|ConvertTo-Json -Compress|Write-Output;throw 'Potential secret, private field, or absolute path detected; values are withheld.'}
$resolution=Read-SampleJson (Get-SamplePath $Root $manifest.linkManifest)
[ordered]@{passed=$true;gitArchiveFilesVerified=$gitCount;normalizedFilesVerified=$normalSeen.Count;protectedOriginalsVerifiedLocally=$protectedVerified;protectedOriginalsUnavailableHere=$protectedAbsent;protectedOriginalsClaimedVerifiedByCI=$false;originalSourceBytes=$bytes;relativeLinksVerified=$relativeLinks;rawArchiveLinksCheckedInOriginalNamespace=$true;historicalUnresolvedLinks=@($resolution.links|Where-Object result -eq 'pre-existing-unresolved').Count;sourceSha=$lock.spherewright.sourceSha;evidenceSourceSha=$import.sourceSha;acceptanceScope=$locked.acceptance.scope;acceptanceSourceSha=$locked.acceptance.sourceSha;acceptanceAppliesToActiveSource=$locked.acceptance.appliesToActiveSource;gameCalls=0}|ConvertTo-Json

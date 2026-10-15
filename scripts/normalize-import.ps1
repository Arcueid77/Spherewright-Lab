#requires -Version 7.0
[CmdletBinding()]
param([Parameter(Mandatory)][string]$SourceRoot,[ValidatePattern('^[A-F0-9]{64}$')][string]$ExpectedExistingManifestSha256)
. (Join-Path $PSScriptRoot 'SampleTools.ps1')
$root=Get-SampleRoot
$import=Read-SampleJson (Get-SamplePath $root 'releases/v0.4.0/manifests/import-manifest.json')
$manifestPath=Get-SamplePath $root 'releases/v0.4.0/manifests/evidence-manifest.json'
$repair=Test-Path -LiteralPath $manifestPath
$previous=@{};$backupRoot=$null
if($repair){
    if(-not $ExpectedExistingManifestSha256 -or (Get-FileHash -LiteralPath $manifestPath).Hash -cne $ExpectedExistingManifestSha256){throw 'Preserve existing normalization unless the exact reviewed old manifest hash is supplied.'}
    $prior=Read-SampleJson $manifestPath
    foreach($old in $prior.files){Assert-SampleFile $root $old.path $old.size $old.sha256;$previous[$old.path]=$old}
    if((Get-FileHash -LiteralPath (Get-SamplePath $root $prior.linkManifest)).Hash -cne $prior.linkManifestSha256){throw 'Preserve changed prior link-resolution manifest.'}
    $backupRoot=Get-SamplePath $root ('.local/normalization-repairs/'+[guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($backupRoot)|Out-Null
    [IO.File]::Copy($manifestPath,(Join-Path $backupRoot 'evidence-manifest.preimage.json'),$false)
    [IO.File]::Copy((Get-SamplePath $root $prior.linkManifest),(Join-Path $backupRoot 'link-resolution.preimage.json'),$false)
}elseif($ExpectedExistingManifestSha256){throw 'A repair hash requires an existing exact manifest.'}
if((Invoke-SampleGit $SourceRoot @('rev-parse','HEAD')) -cne $import.sourceSha){throw 'Original source snapshot required for link resolution.'}
$map=@{};foreach($e in $import.files){$map[$e.sourcePath]=$e.normalizedPath;Assert-SampleFile $root $e.destinationPath $e.size $e.sha256}
$map['docs/evidence']='releases/v0.4.0/evidence'
$map['docs/save-diaries']='operations/save-diaries'
$linkEvents=[Collections.Generic.List[object]]::new()
$legacyRoot=@('docs/evidence/2026-09-30/AGENTS-history-through-2026-09-30.md','docs/evidence/2026-09-30/current-status-history-through-2026-09-30.md')
function Resolve-ImportedLink {
    param([string]$SourcePath,[string]$DestinationPath,[string]$Target)
    $target=$Target.Trim();$fragment='';$tail=''
    if($target -match '^(<[^>]+>|\S+)(\s+"[^"]*")$'){$tail=$Matches[2];$target=$Matches[1].Trim('<','>')}
    if($target.StartsWith('#') -or $target -match '^(?:https?|mailto|data|codex|app):'){
        if($target -match '^https://github\.com/AvaloNero/Spherewright/(?:blob|tree)/(?:main|master)/(.+)$'){
            $rest=$Matches[1];$target='https://github.com/AvaloNero/Spherewright/blob/'+$import.sourceSha+'/'+$rest
        }
        return $target+$tail
    }
    if($target -match '^([^#?]*)(.*)$'){$fragment=$Matches[2];$target=[Uri]::UnescapeDataString($Matches[1])}
    if(-not $target){return $Target}
    if($target -match '^[A-Za-z]:|^[/\\]'){throw 'An absolute path cannot become an imported Markdown link.'}
    $bases=@(([string](Split-Path -Parent $SourcePath)).Replace('\','/'),'')
    if($legacyRoot -ccontains $SourcePath){$bases=@('')+$bases}
    $resolved=$null
    foreach($base in $bases|Select-Object -Unique){
        $full=[IO.Path]::GetFullPath((Join-Path $SourceRoot (($base+'/'+$target).TrimStart('/'))))
        $relative=[IO.Path]::GetRelativePath($SourceRoot,$full).Replace('\','/')
        if($relative.StartsWith('../')){continue}
        if($map.ContainsKey($relative) -or (Test-Path -LiteralPath $full)){$resolved=$relative;break}
    }
    if($null -eq $resolved){
        $linkEvents.Add([pscustomobject]@{sourcePath=$SourcePath;originalTarget=$Target;result='pre-existing-unresolved';replacement='archive/imported-from-spherewright/'+$import.sourceSha+'/'+$SourcePath})
        $archive='archive/imported-from-spherewright/'+$import.sourceSha+'/'+$SourcePath
        if($SourcePath -ceq 'docs/experience-ledger.md'){$archive='releases/v0.4.0/manifests/import-manifest.json'}
        return [IO.Path]::GetRelativePath((Split-Path -Parent (Get-SamplePath $root $DestinationPath)),(Get-SamplePath $root $archive)).Replace('\','/')+$tail
    }
    if($map.ContainsKey($resolved)){$new=[IO.Path]::GetRelativePath((Split-Path -Parent (Get-SamplePath $root $DestinationPath)),(Get-SamplePath $root $map[$resolved])).Replace('\','/')+$fragment+$tail}
    else{$new='https://github.com/AvaloNero/Spherewright/blob/'+$import.sourceSha+'/'+$resolved+$fragment+$tail}
    $linkEvents.Add([pscustomobject]@{sourcePath=$SourcePath;originalTarget=$Target;resolvedSourcePath=$resolved;result='resolved';replacement=$new})
    return $new
}
$files=@();$redactions=0
foreach($entry in $import.files){
    $raw=Get-SamplePath $root $entry.destinationPath
    $text=[IO.File]::ReadAllText($raw)
    $redacted=$false
    if($entry.storage -ceq 'protected-local'){
        $needle='C:'+[IO.Path]::DirectorySeparatorChar+'Program Files'+[IO.Path]::DirectorySeparatorChar+'dotnet'+[IO.Path]::DirectorySeparatorChar+'dotnet.exe'
        $count=[regex]::Matches($text,[regex]::Escape($needle)).Count
        if($count -ne 1){throw 'The owner-approved single historical path redaction no longer matches.'}
        $text=$text.Replace($needle,'[system PATH dotnet executable]');$redacted=$true;$redactions+=$count
    }
    $fence=$false;$out=[Collections.Generic.List[string]]::new();$plain=[Collections.Generic.List[string]]::new()
    function Flush-Plain {
        if($plain.Count -eq 0){return}
        $chunk=$plain.ToArray() -join "`n"
        $converted=[regex]::Replace($chunk,'\[(?<label>[^\]]+)\]\((?<target>[^)\r\n]+)\)',[Text.RegularExpressions.MatchEvaluator]{param($m)
            $new=Resolve-ImportedLink $entry.sourcePath $entry.normalizedPath $m.Groups['target'].Value
            $label=$m.Groups['label'].Value
            if($linkEvents.Count -gt 0 -and $linkEvents[$linkEvents.Count-1].result -ceq 'pre-existing-unresolved' -and $linkEvents[$linkEvents.Count-1].originalTarget -ceq $m.Groups['target'].Value){$label+=' (historical unresolved target; original context)'}
            '['+$label+']('+$new+')'
        })
        $out.Add($converted);$plain.Clear()
    }
    foreach($line in ($text -split '\r?\n')){
        if($line -match '^\s*(?:```|~~~)'){Flush-Plain;$fence=-not $fence;$out.Add($line);continue}
        if($fence){$out.Add($line);continue}
        $plain.Add($line)
    }
    Flush-Plain
    $header='> Imported historical evidence from `AvaloNero/Spherewright@'+$import.sourceSha+'`, `'+$entry.sourcePath+'`. This migration made no game calls; this is not a fresh runtime observation or new action authorization.'
    if($redacted){$header+=' One standard system path was removed by explicit owner choice; the byte-exact original is protected-local only.'}
    $destination=Get-SamplePath $root $entry.normalizedPath
    $nextText=$header+"`n`n"+($out -join "`n")
    if(Test-Path -LiteralPath $destination){
        if(-not $repair -or -not $previous.ContainsKey($entry.normalizedPath)){throw 'Preserve existing normalized file; explicit review required.'}
        $old=$previous[$entry.normalizedPath];Assert-SampleFile $root $old.path $old.size $old.sha256
        if([IO.File]::ReadAllText($destination) -cne $nextText){
            $preimage=Join-Path $backupRoot $entry.normalizedPath
            [IO.Directory]::CreateDirectory((Split-Path -Parent $preimage))|Out-Null
            [IO.File]::Copy($destination,$preimage,$false)
            [IO.File]::WriteAllText($destination,$nextText,[Text.UTF8Encoding]::new($false))
        }
    }else{
        if($repair){throw 'A prior normalized file unexpectedly disappeared; preserve partial state.'}
        [IO.Directory]::CreateDirectory((Split-Path -Parent $destination))|Out-Null
        [IO.File]::WriteAllText($destination,$nextText,[Text.UTF8Encoding]::new($false))
    }
    $files+=[pscustomobject][ordered]@{sourcePath=$entry.sourcePath;path=$entry.normalizedPath;size=(Get-Item -LiteralPath $destination).Length;sha256=(Get-FileHash -LiteralPath $destination).Hash;redacted=$redacted}
}
if($redactions -ne 1){throw 'Exactly one owner-approved path redaction expected.'}
$linkManifest=Get-SamplePath $root 'releases/v0.4.0/manifests/link-resolution.json'
Write-SampleJson $linkManifest ([ordered]@{schemaVersion=1;sourceSha=$import.sourceSha;historicalNamespace='Raw archives retain original bytes; links are resolved in the original source namespace. Normalized copies use local targets or immutable source URLs. Existing unresolved targets point explicitly to original context, not a claimed missing proof.';links=@($linkEvents.ToArray())})
$manifest=[ordered]@{schemaVersion=1;kind='evidence';sourceRepository=$import.sourceRepository;sourceSha=$import.sourceSha;fileCount=$files.Count;files=$files;importManifest='releases/v0.4.0/manifests/import-manifest.json';importManifestSha256=(Get-FileHash -LiteralPath (Get-SamplePath $root 'releases/v0.4.0/manifests/import-manifest.json')).Hash;linkManifest='releases/v0.4.0/manifests/link-resolution.json';linkManifestSha256=(Get-FileHash -LiteralPath $linkManifest).Hash;redactions=1;protectedOriginalsRequiredForGitVerification=$false}
Write-SampleJson $manifestPath $manifest
@{passed=$true;files=$files.Count;redactions=1;links=$linkEvents.Count;repairExisting=$repair;previousManifestSha256=$ExpectedExistingManifestSha256;preExistingUnresolved=@($linkEvents.ToArray()|Where-Object result -eq 'pre-existing-unresolved').Count;evidenceManifestSha256=(Get-FileHash -LiteralPath $manifestPath).Hash;gameCalls=0}|ConvertTo-Json

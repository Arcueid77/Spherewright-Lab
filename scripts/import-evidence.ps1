#requires -Version 7.0
[CmdletBinding()]
param([Parameter(Mandatory)][string]$SourceRoot, [Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{40}$')][string]$SourceSha)
. (Join-Path $PSScriptRoot 'SampleTools.ps1')
$root = Get-SampleRoot
$planPath = Get-SamplePath $root 'releases/v0.4.0/manifests/import-plan.json'
$plan = Read-SampleJson $planPath
if ($plan.sourceSha -cne $SourceSha -or (Invoke-SampleGit $SourceRoot @('rev-parse','HEAD')) -cne $SourceSha -or (Invoke-SampleGit $SourceRoot @('status','--porcelain=v1','--untracked-files=normal'))) { throw 'Import requires the exact clean source snapshot recorded in the plan.' }
$manifestPath = Get-SamplePath $root 'releases/v0.4.0/manifests/import-manifest.json'
if (Test-Path -LiteralPath $manifestPath) { throw 'Preserve the existing immutable import manifest; verify it instead of reimporting.' }
$tracked = @(Get-SampleTrackedPaths $SourceRoot)
$seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$total = 0L; $gitCount = 0; $protectedCount = 0
foreach ($entry in $plan.files) {
    if (-not $seen.Add($entry.sourcePath) -or $tracked -cnotcontains $entry.sourcePath -or $entry.sourceSha -cne $SourceSha -or $entry.sourceRepository -cne 'AvaloNero/Spherewright') { throw 'Import source is duplicate, untracked, or from another snapshot.' }
    Assert-SampleFile $SourceRoot $entry.sourcePath $entry.size $entry.sha256
    $destination = Get-SamplePath $root $entry.destinationPath
    if ($entry.storage -ceq 'protected-local') {
        if ($entry.sourcePath -cne 'docs/experience-ledger.md' -or -not $entry.destinationPath.StartsWith('.local/protected-import/')) { throw 'Unexpected protected import disposition.' }
        if (-not $IsWindows) { throw 'This one-time protected import requires the owner ACL on Windows.' }
        $protectedRoot = Get-SamplePath $root '.local/protected-import'
        [IO.Directory]::CreateDirectory($protectedRoot) | Out-Null
        $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
        $acl = [Security.AccessControl.DirectorySecurity]::new()
        $acl.SetOwner($sid); $acl.SetAccessRuleProtection($true,$false)
        $rule = [Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow')
        $acl.AddAccessRule($rule)
        Set-Acl -LiteralPath $protectedRoot -AclObject $acl
        Invoke-SampleGit $root @('check-ignore','--', $entry.destinationPath) | Out-Null
        ++$protectedCount
    } elseif ($entry.storage -ceq 'git') {
        if (-not $entry.destinationPath.StartsWith(('archive/imported-from-spherewright/' + $SourceSha + '/'))) { throw 'Raw archive destination must retain the exact source namespace.' }
        ++$gitCount
    } else { throw 'Unknown import storage scope.' }
    [IO.Directory]::CreateDirectory((Split-Path -Parent $destination)) | Out-Null
    if (-not (Test-Path -LiteralPath $destination)) { [IO.File]::Copy((Get-SamplePath $SourceRoot $entry.sourcePath),$destination,$false) }
    Assert-SampleFile $root $entry.destinationPath $entry.size $entry.sha256
    $total += [long]$entry.size
}
if ($protectedCount -ne 1 -or $gitCount + $protectedCount -ne @($plan.files).Count) { throw 'Incomplete archive disposition.' }
$manifest = [ordered]@{schemaVersion=1;kind='import';sourceRepository=$plan.sourceRepository;sourceSha=$SourceSha;planSha256=(Get-FileHash -LiteralPath $planPath).Hash;fileCount=@($plan.files).Count;totalSourceBytes=$total;gitArchiveCount=$gitCount;protectedLocalCount=$protectedCount;files=@($plan.files);protectedScope='Owner-confirmed raw ledger exception: original stays local only; CI verifies its sanitized derivative and never claims to have inspected the absent original.'}
Write-SampleJson $manifestPath $manifest
foreach ($entry in $plan.files) { Assert-SampleFile $root $entry.destinationPath $entry.size $entry.sha256 }
$receipt = [ordered]@{passed=$true;sourceSha=$SourceSha;files=$seen.Count;bytes=$total;gitArchiveFiles=$gitCount;protectedLocalFiles=$protectedCount;allCopiesHashMatched=$true;manifestSha256=(Get-FileHash -LiteralPath $manifestPath).Hash;gameCalls=0;sourceFilesModified=$false}
Write-SampleJson (Get-SamplePath $root '.local/import-verification.json') $receipt
$receipt | ConvertTo-Json

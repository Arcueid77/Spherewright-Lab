#requires -Version 7.0
[CmdletBinding()]
param([Parameter(Mandatory)][string]$FixtureRoot,[switch]$AllowFixtureMutation)
. (Join-Path $PSScriptRoot 'SampleTools.ps1')
if(-not $AllowFixtureMutation){throw 'Use an isolated clean verification checkout and explicitly pass -AllowFixtureMutation.'}
$root=[IO.Path]::GetFullPath($FixtureRoot)
if(Invoke-SampleGit $root @('status','--porcelain=v1','--untracked-files=normal')){throw 'Verifier fixture must start clean.'}
$null=Assert-SampleSourceLock $root
$pwsh=(Get-Command pwsh -ErrorAction Stop).Source
$results=[Collections.Generic.List[string]]::new()
$logs=Get-SamplePath $root ('.local/verifier-tests/'+[guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($logs)|Out-Null
if($IsWindows){
    $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl=[Security.AccessControl.DirectorySecurity]::new();$acl.SetOwner($sid);$acl.SetAccessRuleProtection($true,$false)
    $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))
    Set-Acl -LiteralPath $logs -AclObject $acl
}
function Expect-Rejection {
    param([string]$Name,[string]$Script,[string]$Expected)
    $log=Join-Path $logs ($Name+'.log')
    & $pwsh -NoProfile -File (Get-SamplePath $root ('scripts/'+$Script)) -Root $root *> $log
    if($LASTEXITCODE -eq 0 -or -not([IO.File]::ReadAllText($log).Contains($Expected))){throw "Expected fail-closed rejection was not observed: $Name"}
    $results.Add($Name)
}
$lockPath=Get-SamplePath $root 'source-lock.json'
$releasePath=Get-SamplePath $root 'releases/v0.4.0/source-lock.json'
$lockBytes=[IO.File]::ReadAllBytes($lockPath);$releaseBytes=[IO.File]::ReadAllBytes($releasePath)
$initial=Read-SampleJson $lockPath
try{
    $changed=Read-SampleJson $lockPath;$changed.spherewright.sourceSha='0'*40;Write-SampleJson $lockPath $changed
    Expect-Rejection 'gitlink-sha-mismatch' 'verify-source-lock.ps1' 'Gitlink does not match'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
$fake=Get-SamplePath $root ('artifacts/'+$initial.packages.manual.file)
if(Test-Path -LiteralPath $fake){throw 'Preserve existing frozen input; run negative tests in a clean fixture without packages.'}
try{
    [IO.Directory]::CreateDirectory((Split-Path -Parent $fake))|Out-Null;[IO.File]::WriteAllBytes($fake,[byte[]]@(1,2,3))
    Expect-Rejection 'frozen-package-corruption' 'verify-source-lock.ps1' 'Frozen package size/hash mismatch'
}finally{if(Test-Path -LiteralPath $fake){Remove-Item -LiteralPath $fake}}
$manifestPath=Get-SamplePath $root $initial.acceptance.evidenceManifest
$manifest=Read-SampleJson $manifestPath
$evidencePath=Get-SamplePath $root $manifest.files[0].path
$evidenceBytes=[IO.File]::ReadAllBytes($evidencePath)
try{
    [IO.File]::AppendAllText($evidencePath,"`ncorrupted fixture`n")
    Expect-Rejection 'normalized-evidence-corruption' 'verify-evidence.ps1' 'Manifest size/hash mismatch'
}finally{[IO.File]::WriteAllBytes($evidencePath,$evidenceBytes)}
$readme=Get-SamplePath $root 'README.md';$readmeBytes=[IO.File]::ReadAllBytes($readme)
try{
    $synthetic='ghp_' + ('x'*36)
    [IO.File]::AppendAllText($readme,"`n"+$synthetic+"`n")
    Expect-Rejection 'credential-leak' 'verify-evidence.ps1' 'Potential secret'
}finally{[IO.File]::WriteAllBytes($readme,$readmeBytes)}
try{
    $syntheticPath='C:'+[char]92+'Users'+[char]92+'Fixture'+[char]92+'private.dat'
    [IO.File]::AppendAllText($readme,"`n"+$syntheticPath+"`n")
    Expect-Rejection 'absolute-path-leak' 'verify-evidence.ps1' 'Potential secret'
}finally{[IO.File]::WriteAllBytes($readme,$readmeBytes)}
$manifestBytes=[IO.File]::ReadAllBytes($manifestPath)
try{
    $changed=Read-SampleJson $manifestPath;$changed.files[0].path='../outside';Write-SampleJson $manifestPath $changed
    $changedLock=Read-SampleJson $lockPath;$changedLock.acceptance.evidenceManifestSha256=(Get-FileHash -LiteralPath $manifestPath).Hash
    Write-SampleJson $lockPath $changedLock;Write-SampleJson $releasePath $changedLock
    Expect-Rejection 'manifest-path-traversal' 'verify-evidence.ps1' 'Unsafe relative path'
}finally{
    [IO.File]::WriteAllBytes($manifestPath,$manifestBytes)
    [IO.File]::WriteAllBytes($lockPath,$lockBytes);[IO.File]::WriteAllBytes($releasePath,$releaseBytes)
}
$productReadme=Get-SamplePath $root 'deps/Spherewright/README.md';$productBytes=[IO.File]::ReadAllBytes($productReadme)
try{
    [IO.File]::AppendAllText($productReadme,"`nfixture-only product dirt`n")
    Expect-Rejection 'dirty-product-submodule' 'verify-source-lock.ps1' 'Product submodule must be clean'
}finally{[IO.File]::WriteAllBytes($productReadme,$productBytes)}
if(Invoke-SampleGit $root @('status','--porcelain=v1','--untracked-files=normal')){throw 'Verifier fixture did not return to the original clean state; preserve it for inspection.'}
$null=Assert-SampleSourceLock $root
[ordered]@{passed=$true;negativeCases=$results.Count;cases=@($results.ToArray());fixtureClean=$true;gameCalls=0}|ConvertTo-Json -Depth 5

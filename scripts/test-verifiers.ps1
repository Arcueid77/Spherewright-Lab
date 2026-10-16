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
$positiveCases=[Collections.Generic.List[string]]::new()
function New-HistoricalReferenceFixture {
    $next=Read-SampleJson $lockPath
    $next.scenario='fixture-explicit-historical-reference'
    $next.acceptance|Add-Member -NotePropertyName scope -NotePropertyValue 'historical_reference' -Force
    $next.acceptance|Add-Member -NotePropertyName sourceLock -NotePropertyValue ('releases/v'+$next.spherewright.productVersion+'/source-lock.json') -Force
    $next.acceptance|Add-Member -NotePropertyName sourceLockSha256 -NotePropertyValue (Get-FileHash -LiteralPath $releasePath).Hash -Force
    return $next
}
try{
    $changed=New-HistoricalReferenceFixture;Write-SampleJson $lockPath $changed
    $checked=Assert-SampleSourceLock $root
    if($checked.acceptance.scope -cne 'historical_reference' -or $checked.acceptance.appliesToActiveSource -or
        $checked.acceptance.sourceSha -cne (Read-SampleJson $releasePath).spherewright.sourceSha -or
        (Get-FileHash -LiteralPath $releasePath).Hash -cne $changed.acceptance.sourceLockSha256){throw 'Explicit historical reference must preserve the frozen lock and never inherit its acceptance.'}
    $positiveCases.Add('explicit-historical-reference-is-not-current-acceptance')
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=Read-SampleJson $lockPath;$changed.scenario='fixture-unmarked-drift'
    foreach($field in @('scope','sourceLock','sourceLockSha256')){$changed.acceptance.PSObject.Properties.Remove($field)}
    Write-SampleJson $lockPath $changed
    Expect-Rejection 'unmarked-release-lock-drift' 'verify-source-lock.ps1' 'Root and release source locks differ without an explicit historical reference'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-HistoricalReferenceFixture;$changed.acceptance.PSObject.Properties.Remove('sourceLockSha256');Write-SampleJson $lockPath $changed
    Expect-Rejection 'incomplete-historical-reference' 'verify-source-lock.ps1' 'JSON schema validation failed'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-HistoricalReferenceFixture;$changed.acceptance.sourceLockSha256='0'*64;Write-SampleJson $lockPath $changed
    Expect-Rejection 'wrong-frozen-lock-hash' 'verify-source-lock.ps1' 'Frozen acceptance source-lock hash does not match'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-HistoricalReferenceFixture;$changed.acceptance.sourceLock='source-lock.json';Write-SampleJson $lockPath $changed
    Expect-Rejection 'forged-frozen-lock-path' 'verify-source-lock.ps1' 'Historical acceptance must reference the frozen release source lock'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-HistoricalReferenceFixture;$changed.acceptance.evidenceManifest='releases/v0.4.0/manifests/import-manifest.json'
    $changed.acceptance.evidenceManifestSha256=(Get-FileHash -LiteralPath (Get-SamplePath $root $changed.acceptance.evidenceManifest)).Hash;Write-SampleJson $lockPath $changed
    Expect-Rejection 'forged-historical-manifest' 'verify-source-lock.ps1' 'Historical acceptance manifest or provenance differs'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-HistoricalReferenceFixture;$changed.evidenceSource.sourceSha='1'*40;Write-SampleJson $lockPath $changed
    Expect-Rejection 'forged-historical-provenance' 'verify-source-lock.ps1' 'Historical acceptance manifest or provenance differs'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-HistoricalReferenceFixture
    $frozen=Read-SampleJson $releasePath;$frozen.spherewright.sourceSha='invalid';Write-SampleJson $releasePath $frozen
    $changed.acceptance.sourceLockSha256=(Get-FileHash -LiteralPath $releasePath).Hash;Write-SampleJson $lockPath $changed
    Expect-Rejection 'invalid-frozen-lock-schema' 'verify-source-lock.ps1' 'JSON schema validation failed'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes);[IO.File]::WriteAllBytes($releasePath,$releaseBytes)}
try{
    $changed=New-HistoricalReferenceFixture;Write-SampleJson $releasePath $changed
    $changed.acceptance.sourceLockSha256=(Get-FileHash -LiteralPath $releasePath).Hash;Write-SampleJson $lockPath $changed
    Expect-Rejection 'recursive-historical-reference' 'verify-source-lock.ps1' 'Frozen acceptance source lock must be a legacy release lock'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes);[IO.File]::WriteAllBytes($releasePath,$releaseBytes)}
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
    $changedRelease=Read-SampleJson $releasePath;$changedRelease.acceptance.evidenceManifestSha256=$changedLock.acceptance.evidenceManifestSha256
    Write-SampleJson $releasePath $changedRelease
    if($changedLock.acceptance.PSObject.Properties.Name -ccontains 'scope'){$changedLock.acceptance.sourceLockSha256=(Get-FileHash -LiteralPath $releasePath).Hash}
    Write-SampleJson $lockPath $changedLock
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
[ordered]@{passed=$true;positiveCases=@($positiveCases.ToArray());negativeCases=$results.Count;cases=@($results.ToArray());fixtureClean=$true;gameCalls=0}|ConvertTo-Json -Depth 5

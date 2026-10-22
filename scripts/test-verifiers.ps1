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
function Expect-EntrypointRejection {
    param([string]$Name,[string]$Script,[string[]]$Arguments,[string]$Expected)
    $log=Join-Path $logs ($Name+'.log')
    & $pwsh -NoProfile -File (Get-SamplePath $root ('scripts/'+$Script)) @Arguments *> $log
    if($LASTEXITCODE -eq 0 -or -not([IO.File]::ReadAllText($log).Contains($Expected))){throw "Expected fail-closed entrypoint rejection was not observed: $Name"}
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
    $next.acceptance|Add-Member -NotePropertyName sourceLock -NotePropertyValue ('releases/v'+(Read-SampleJson $releasePath).spherewright.productVersion+'/source-lock.json') -Force
    $next.acceptance|Add-Member -NotePropertyName sourceLockSha256 -NotePropertyValue (Get-FileHash -LiteralPath $releasePath).Hash -Force
    return $next
}
function New-DevelopmentFixture {
    $next=New-HistoricalReferenceFixture
    if($next.PSObject.Properties.Name -cnotcontains 'installed'){
        $installed=[ordered]@{sourceSha=$next.spherewright.sourceSha;productVersion=$next.spherewright.productVersion;releaseTag=$next.spherewright.releaseTag;native=$next.native;packages=$next.packages;evidence='README.md';verification='historical_record';runtimeState='not_observed'}
        $next|Add-Member -NotePropertyName installed -NotePropertyValue ([pscustomobject]$installed)
    }
    $next.schemaVersion=2;$next.status='development';$next.spherewright.releaseTag=$null
    $next.packages=[pscustomobject]@{manual=$null;thunderstore=$null}
    $next|Add-Member -NotePropertyName development -NotePropertyValue ([pscustomobject]@{targetVersion='0.5.0'}) -Force
    return $next
}
function New-ProvisionalFixture {
    $next=New-DevelopmentFixture;$next.status='provisional';$next.development.targetVersion=$next.spherewright.productVersion
    $next.packages=[pscustomobject]@{
        manual=[pscustomobject]@{file=('Spherewright-'+$next.spherewright.productVersion+'-win-x64.zip');sha256=('1'*64);size=3}
        thunderstore=[pscustomobject]@{file=('Spherewright-'+$next.spherewright.productVersion+'-thunderstore.zip');sha256=('2'*64);size=3}
    }
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
    $changed=New-DevelopmentFixture;Write-SampleJson $lockPath $changed
    $checked=Assert-SampleSourceLock $root
    if($checked.packagesNotBuilt -ne 2 -or $checked.packagesNotPresent -ne 0 -or $checked.candidatePackagesReady -or $checked.acceptance.appliesToActiveSource){throw 'Unbuilt development packages must not create candidate or acceptance credit.'}
    $positiveCases.Add('development-with-no-packages-is-not-a-candidate')
    $changed.spherewright.productVersion='0.5.0';Write-SampleJson $lockPath $changed
    Assert-SampleJsonSchema $lockPath (Get-SamplePath $root 'schemas/source-lock.schema.json')
    $history=Assert-SampleAcceptanceReference -Root $root -Lock $changed -LockPath $lockPath
    if($history.appliesToActiveSource -or $history.sourceSha -cne (Read-SampleJson $releasePath).spherewright.sourceSha){throw 'Historical acceptance must remain independent of the active product version.'}
    $positiveCases.Add('cross-version-historical-reference-remains-historical')
    Assert-SampleJsonSchema $releasePath (Get-SamplePath $root 'schemas/source-lock.schema.json')
    $positiveCases.Add('immutable-v1-release-lock-remains-valid')
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-DevelopmentFixture;$changed.packages.manual=(New-ProvisionalFixture).packages.manual;Write-SampleJson $lockPath $changed
    Expect-Rejection 'one-sided-development-package' 'verify-source-lock.ps1' 'JSON schema validation failed'
    Expect-EntrypointRejection 'bootstrap-rejects-invalid-development-lock' 'bootstrap.ps1' @() 'JSON schema validation failed'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-DevelopmentFixture;$changed.status='provisional';Write-SampleJson $lockPath $changed
    Expect-Rejection 'provisional-cannot-claim-null-packages' 'verify-source-lock.ps1' 'JSON schema validation failed'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-DevelopmentFixture;$changed.spherewright.releaseTag='v0.5.0';Write-SampleJson $lockPath $changed
    Expect-Rejection 'development-cannot-claim-release-tag' 'verify-source-lock.ps1' 'JSON schema validation failed'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-DevelopmentFixture;$changed.schemaVersion=1;Write-SampleJson $lockPath $changed
    Expect-Rejection 'legacy-lock-cannot-hide-unbuilt-packages' 'verify-source-lock.ps1' 'JSON schema validation failed'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-DevelopmentFixture
    $taggedHistory=Read-SampleJson $releasePath
    $changed.installed.productVersion=$taggedHistory.spherewright.productVersion
    $changed.installed.releaseTag='v'+$taggedHistory.spherewright.productVersion
    $changed.installed.packages=$taggedHistory.packages
    $changed.installed.sourceSha='1'*40;Write-SampleJson $lockPath $changed
    Expect-Rejection 'installed-tag-source-mismatch' 'verify-source-lock.ps1' 'Installed release tag does not match'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-DevelopmentFixture;$changed.installed.verification='historical_record';$changed.installed.runtimeState='running_verified';Write-SampleJson $lockPath $changed
    Expect-Rejection 'historical-install-is-not-live-verification' 'verify-source-lock.ps1' 'Verified running state requires'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
try{
    $changed=New-DevelopmentFixture
    if($changed.development.targetVersion -ceq $changed.spherewright.productVersion){$changed.development.targetVersion='99.0.0'}
    Write-SampleJson $lockPath $changed
    Expect-EntrypointRejection 'preview-cannot-relabel-old-product-version' 'package-from-submodule.ps1' @() 'has not adopted the development target version'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes)}
$invalidNext=Join-Path $logs 'invalid-next-lock.json'
$changed=New-DevelopmentFixture;$changed.spherewright.sourceSha='1'*40;$changed.packages.manual=(New-ProvisionalFixture).packages.manual;Write-SampleJson $invalidNext $changed
Expect-EntrypointRejection 'update-rejects-null-package-bypass-before-ci' 'update-spherewright.ps1' @('-Sha',('1'*40),'-NewLockPath',$invalidNext) 'JSON schema validation failed'
try{
    $changed=New-ProvisionalFixture;$changed.schemaVersion=1;$changed.scenario='fixture-unmarked-drift'
    foreach($field in @('installed','development')){$changed.PSObject.Properties.Remove($field)}
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
$packageFixture=New-ProvisionalFixture
$fake=Get-SamplePath $root ('artifacts/'+$packageFixture.packages.manual.file)
if(Test-Path -LiteralPath $fake){throw 'Preserve existing frozen input; run negative tests in a clean fixture without packages.'}
try{
    Write-SampleJson $lockPath $packageFixture
    [IO.Directory]::CreateDirectory((Split-Path -Parent $fake))|Out-Null;[IO.File]::WriteAllBytes($fake,[byte[]]@(1,2,3))
    Expect-Rejection 'frozen-package-corruption' 'verify-source-lock.ps1' 'Frozen package size/hash mismatch'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes);if(Test-Path -LiteralPath $fake){Remove-Item -LiteralPath $fake}}
try{
    $changed=New-ProvisionalFixture
    $zip=[IO.Compression.ZipFile]::Open($fake,[IO.Compression.ZipArchiveMode]::Create)
    try{
        $entry=$zip.CreateEntry('Spherewright-'+$changed.spherewright.productVersion+'/manifest.json')
        $writer=[IO.StreamWriter]::new($entry.Open())
        try{$writer.Write((@{sourceCommit=('1'*40);sourceDirty=$false;version=$changed.spherewright.productVersion;productVersion=$changed.spherewright.productVersion;supportedDspVersion=$changed.native.version}|ConvertTo-Json))}finally{$writer.Dispose()}
    }finally{$zip.Dispose()}
    $changed.packages.manual.sha256=(Get-FileHash -LiteralPath $fake).Hash;$changed.packages.manual.size=(Get-Item -LiteralPath $fake).Length;Write-SampleJson $lockPath $changed
    Expect-Rejection 'renamed-package-from-wrong-source' 'verify-source-lock.ps1' 'Package source, version, clean state, or Native cohort differs'
}finally{[IO.File]::WriteAllBytes($lockPath,$lockBytes);if(Test-Path -LiteralPath $fake){Remove-Item -LiteralPath $fake}}
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
$pythonFixture=Get-SamplePath $root 'scenarios/v0.5-voyager/scripts/detached_python_task.py'
$pythonBytes=[IO.File]::ReadAllBytes($pythonFixture)
try{
    $synthetic='ghp_' + ('x'*36)
    [IO.File]::AppendAllText($pythonFixture,"`n# "+$synthetic+"`n")
    Expect-Rejection 'python-credential-leak' 'verify-evidence.ps1' 'Potential secret'
}finally{[IO.File]::WriteAllBytes($pythonFixture,$pythonBytes)}
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

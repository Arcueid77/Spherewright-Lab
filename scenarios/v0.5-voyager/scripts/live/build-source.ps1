[CmdletBinding()]
param([Parameter(Mandatory)][string]$SourceRoot,[Parameter(Mandatory)][string]$SourceSha,
    [Parameter(Mandatory)][string]$DotnetPath,[Parameter(Mandatory)][string]$OutputRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if((& git -C $SourceRoot rev-parse HEAD).Trim() -cne $SourceSha -or (& git -C $SourceRoot status --porcelain)) {throw 'Exact clean source required.'}
if(Test-Path -LiteralPath $OutputRoot){throw 'Preserve previous qualification.'}
$null=New-Item -ItemType Directory -Path $OutputRoot
$rows=[Collections.Generic.List[object]]::new()
function Invoke-Check([string]$Name,[scriptblock]$Command){
    $log=Join-Path $OutputRoot ($Name+'.private.log')
    & $Command *> $log
    if($LASTEXITCODE -ne 0){throw ('Source qualification failed: '+$Name+'; inspect protected log.')}
    $rows.Add(@{name=$Name;exitCode=0;logSha256=(Get-FileHash -LiteralPath $log -Algorithm SHA256).Hash})
}
Push-Location $SourceRoot
try {
    Invoke-Check 'locked-restore' {& $DotnetPath restore Spherewright.sln --locked-mode}
    Invoke-Check 'native-build' {& $DotnetPath build Spherewright.sln -c Release --no-restore --no-incremental -p:DebugType=None -p:DebugSymbols=false "-p:SourceRevisionId=$SourceSha" "-p:InformationalVersion=0.5.0+$SourceSha" -p:IncludeSourceRevisionInInformationalVersion=false}
    Invoke-Check 'core-recovery' {& $DotnetPath test tests/Spherewright.Bridge.Core.Tests -c Release --no-build --filter 'FullyQualifiedName~StoppedSpace|FullyQualifiedName~SpaceReturnAdmission|FullyQualifiedName~CurrentSpaceReturnCloses|FullyQualifiedName~PausedSavedSpace|FullyQualifiedName~LastExit|FullyQualifiedName~SavedWorldOpenGuard|FullyQualifiedName~MechaWarper|FullyQualifiedName~VoyagerStoredWarper|FullyQualifiedName~VoyagerControlReservePolicy|FullyQualifiedName~OwnedWorldAutosaveCoordinatorIntegrationTests|FullyQualifiedName~NativeSailTickEnergy|FullyQualifiedName~NativeLandingTickEnergy|FullyQualifiedName~VoyagerJourneyStoreIntegrationTests|FullyQualifiedName~VoyagerLandingChargePolicyTests|FullyQualifiedName~VoyagerFailedLanding|FullyQualifiedName~VoyagerRemoteResumeCoordinatorIntegrationTests|FullyQualifiedName~GeneratorColdStartFuel|FullyQualifiedName~FuelPower|FullyQualifiedName~StructuredEmptyBeltSource|FullyQualifiedName~StructuredConstructionStoreIntegrationTests|FullyQualifiedName~BeltSourceReusePolicy|FullyQualifiedName~BeltSourceRotation|FullyQualifiedName~SavedFactorySiteTests|FullyQualifiedName~SavedBeltSourceTopologyTests|FullyQualifiedName~SavedPaidSearchCacheRecoveryTests|FullyQualifiedName~NativeSavedConstructionTailPolicyTests|FullyQualifiedName~NativeResumeContact|FullyQualifiedName~NativeResumeInitialization|FullyQualifiedName~LoadedGroundSync' --logger 'trx;LogFileName=core.trx' --results-directory $OutputRoot}
    Invoke-Check 'mcp-contract' {& $DotnetPath test tests/Spherewright.Mcp.Tests -c Release --no-build --filter 'FullyQualifiedName~VoyagerActionToolsTests|FullyQualifiedName~Interplanetary|FullyQualifiedName~OwnedSavedWorld|FullyQualifiedName~ColdGeneratorFuel' --logger 'trx;LogFileName=mcp.trx' --results-directory $OutputRoot}
    Invoke-Check 'source-sdk-metadata' {& pwsh -NoProfile -File scripts/test-source-mcp.ps1 -DotnetPath $DotnetPath}
    Invoke-Check 'documentation' {& pwsh -NoProfile -File scripts/verify-documentation.ps1}
} finally {Pop-Location}
$total=0
foreach($name in @('core','mcp')){
    [xml]$trx=Get-Content -LiteralPath (Join-Path $OutputRoot ($name+'.trx')) -Raw
    $counters=$trx.TestRun.ResultSummary.Counters
    if([int]$counters.failed -ne 0 -or [int]$counters.passed -le 0){throw 'Nonpassing source test result.'}
    $total += [int]$counters.passed
}
if((& git -C $SourceRoot rev-parse HEAD).Trim() -cne $SourceSha -or (& git -C $SourceRoot status --porcelain)){throw 'Source changed during qualification.'}
$proof=@{passed=$true;sourceSha=$SourceSha;totalPassed=$total;scope='exact clean native build and relevant source regressions; full suite remains an exact-SHA CI requirement';rows=@($rows.ToArray());gameCalls=0}
$json=$proof|ConvertTo-Json -Depth 8
foreach($name in @('local-build-validation.private.json','exact-source-validation.private.json')){
    [IO.File]::WriteAllText((Join-Path $OutputRoot $name),$json,[Text.UTF8Encoding]::new($false))
}
@{passed=$true;sourceSha=$SourceSha;nativeBuild=$true;gameCalls=0}|ConvertTo-Json -Compress

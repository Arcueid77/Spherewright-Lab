#requires -Version 7.0
[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$scenario=Get-Content -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'scenario.yaml') -Raw|ConvertFrom-Json
if($scenario.schemaVersion -ne 1 -or $scenario.id -cne 'v0.4-final-owned-peaceful-1x' -or $scenario.gameWritesAuthorizedByThisFile -ne $false -or $scenario.continuousSupply.minimumGameTicks -ne 36000){throw 'Unexpected historical scenario contract.'}
& (Join-Path $root 'scripts/verify-source-lock.ps1')
& (Join-Path $root 'scripts/verify-evidence.ps1')
. (Join-Path $root 'scripts/SampleTools.ps1')
$locked=Assert-SampleSourceLock $root
@{passed=$true;mode='offline-source-and-evidence-only';acceptanceSourceSha=$locked.acceptance.sourceSha;acceptanceAppliesToActiveSource=$locked.acceptance.appliesToActiveSource;gameCalls=0;liveExperimentRepeated=$false}|ConvertTo-Json

#requires -Version 7.0
[CmdletBinding()]
param([string]$Root = (Split-Path -Parent $PSScriptRoot), [string]$PackageDirectory)
. (Join-Path $PSScriptRoot 'SampleTools.ps1')
$result = Assert-SampleSourceLock -Root $Root -PackageDirectory $PackageDirectory
[ordered]@{ passed = $true; sourceSha = $result.lock.spherewright.sourceSha; version = $result.lock.spherewright.productVersion; status = $result.lock.status; releaseTag = $result.lock.spherewright.releaseTag; packagesPresentAndVerified = $result.packagesPresentAndVerified; packagesNotPresent = $result.packagesNotPresent; acceptanceScope = $result.acceptance.scope; acceptanceSourceSha = $result.acceptance.sourceSha; acceptanceAppliesToActiveSource = $result.acceptance.appliesToActiveSource } | ConvertTo-Json

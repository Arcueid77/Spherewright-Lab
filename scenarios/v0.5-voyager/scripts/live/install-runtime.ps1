[CmdletBinding()]
param([Parameter(Mandatory)][string]$TargetsPath,[Parameter(Mandatory)][string]$EvidenceDirectory,
    [ValidatePattern('^\d+\.\d+\.\d+$')][string]$Version='0.5.0',
    [ValidateRange(1,1000)][int]$ExpectedToolCount=74)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$out=[IO.Path]::GetFullPath($EvidenceDirectory)
$targets=Get-Content -LiteralPath $TargetsPath -Raw|ConvertFrom-Json
$cohortPath=$targets.cohortIndexPath
$cohort=Get-Content -LiteralPath $cohortPath -Raw|ConvertFrom-Json
function Require($value,[string]$reason){if(-not $value){throw $reason}}
function Hash([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash}
function NewProof([string]$name,$value){
 $stream=[IO.File]::Open((Join-Path $out $name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$writer=[IO.StreamWriter]::new($stream,[Text.UTF8Encoding]::new($false));try{$writer.Write(($value|ConvertTo-Json -Depth 16));$writer.Flush()}finally{$writer.Dispose()}}finally{$stream.Dispose()}
}
Require ($cohort.sourceSha -ceq $targets.sourceSha -and $targets.sourceSha -ceq $cohort.sourceSha) 'Unqualified source.'
Require ((Hash $cohortPath) -ceq $targets.cohortIndexSha256 -and (Hash $targets.verifierPath) -ceq $targets.verifierSha256) 'Pinned input/verifier changed.'
Require ([IO.Path]::GetFullPath($targets.pluginDestination) -ceq [IO.Path]::GetFullPath((Join-Path $targets.dspRoot 'BepInEx/plugins/Spherewright'))) 'Plugin target differs.'
Require (-not(Test-Path -LiteralPath (Join-Path $out 'install-intent.private.json'))) 'Original transaction intent exists; reconcile without replay.'
Require ((Hash $cohort.officialTransactionScript) -ceq $cohort.officialTransactionSha256 -and (Hash $cohort.officialProbeScript) -ceq $cohort.officialProbeSha256) 'Official helpers changed.'
. $cohort.officialTransactionScript
. $cohort.officialProbeScript
$script:criticalCount=0
function Critical{
 $script:criticalCount++
 & python $targets.verifierPath $TargetsPath *> (Join-Path $out ('critical-'+$script:criticalCount+'.private.log'))
 Require ($LASTEXITCODE -eq 0) 'Current process/progress/protected-record prerequisite failed.'
}
$maps=@{}
foreach($role in @('plugin','mcp')){
 $map=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::OrdinalIgnoreCase)
 foreach($file in @($cohort.files|Where-Object role -CEQ $role)){
  $relative=[string]$file.relativePath
  Require (-not[IO.Path]::IsPathRooted($relative) -and -not$relative.Contains('\') -and -not$relative.Contains(':') -and @($relative.Split('/')|Where-Object{$_ -in @('','.','..')}).Count -eq 0) 'Unsafe relative payload path.'
  Require ((Get-Item -LiteralPath $file.source).Length -eq $file.bytes -and (Hash $file.source) -ceq $file.sha256) 'Source payload changed.'
  $map.Add($relative,[string]$file.sha256)
 }
 $maps[$role]=$map
}
Require ($maps.plugin.Count -eq 5 -and $maps.mcp.Count -eq 224) 'Installed layout changed.'
foreach($target in @($targets.pluginDestination,$targets.mcpDestination)){
 Assert-SpherewrightInstallNonReparseAncestors $target
 foreach($parent in @(Get-SpherewrightInstallExistingAncestorDirectories -Path $target)){Assert-SpherewrightInstallNoPendingArchives -Parent $parent}
}
Assert-SpherewrightInstallNoPendingMarker -MarkerPath (Get-SpherewrightInstallPendingMarkerPath -PluginStageParent (Join-Path $targets.dspRoot 'BepInEx'))
Critical
$operation=[guid]::NewGuid().ToString('N');$stages=@{}
NewProof 'install-intent.private.json' @{sourceSha=$cohort.sourceSha;operationId=$operation;targetsSha256=(Hash $TargetsPath);cohortIndexSha256=(Hash $cohortPath);scriptSha256=(Hash $PSCommandPath);maximumTransactions=1;noReplay=$true;gameCalls=0;loads=0}
foreach($role in @('plugin','mcp')){
 $parent=if($role -ceq 'plugin'){Join-Path $targets.dspRoot 'BepInEx'}else{Split-Path $targets.mcpDestination -Parent}
 $stage=[IO.Path]::GetFullPath((Join-Path $parent ('.spherewright-stage-'+$operation+'-'+$role)))
 Require (-not(Test-Path -LiteralPath $stage) -and [IO.Path]::GetDirectoryName($stage) -ceq [IO.Path]::GetFullPath($parent)) 'Stage escaped its target parent.'
 Assert-SpherewrightInstallNonReparseAncestors $stage
 $stages[$role]=@{root=$stage;payload=(Join-Path $stage 'payload')}
}
Assert-SpherewrightInstallPathBudget -PluginStageParent (Split-Path $stages.plugin.root -Parent) -McpStageParent (Split-Path $stages.mcp.root -Parent) -PluginDestination $targets.pluginDestination -McpDestination $targets.mcpDestination -PluginExpectedFiles $maps.plugin -McpExpectedFiles $maps.mcp
foreach($role in @('plugin','mcp')){
 [IO.Directory]::CreateDirectory($stages[$role].payload)|Out-Null
 foreach($file in @($cohort.files|Where-Object role -CEQ $role)){
  $destination=Join-Path $stages[$role].payload $file.relativePath
  [IO.Directory]::CreateDirectory((Split-Path $destination -Parent))|Out-Null
  Copy-Item -LiteralPath $file.source -Destination $destination
  Require ((Hash $destination) -ceq $file.sha256) 'Staged bytes changed.'
 }
 $null=Assert-SpherewrightInstallSnapshotComplete -Root $stages[$role].payload -ExpectedFiles $maps[$role]
}
$verify={param($liveMcpDirectory)
 $single=Invoke-SpherewrightStagedMcpProbe -ExecutablePath (Join-Path $targets.pluginDestination 'Spherewright.Mcp.exe') -ExpectedVersion $Version -ExpectedPlaybookPath (Join-Path $cohort.manualRoot 'AGENT-PLAYBOOK.md') -IsolationDirectory (Join-Path $out 'installed-singlefile-metadata')
 Require ($single.tools -eq $ExpectedToolCount -and $single.resources -eq 1) 'Standalone MCP metadata differs.'
 NewProof 'installed-singlefile-metadata.private.json' $single
 $manual=Invoke-SpherewrightStagedMcpProbe -ExecutablePath (Join-Path $liveMcpDirectory 'Spherewright.Mcp.exe') -ExpectedVersion $Version -ExpectedPlaybookPath (Join-Path $cohort.manualRoot 'AGENT-PLAYBOOK.md') -IsolationDirectory (Join-Path $out 'installed-directory-metadata')
 Require ($manual.tools -eq $ExpectedToolCount -and $manual.resources -eq 1) 'Directory MCP metadata differs.'
 NewProof 'installed-directory-metadata.private.json' $manual
}
$dispatched=$false;$returned=$false;$failure=$null
try{
 Critical;$dispatched=$true
 $result=Invoke-SpherewrightInstallTransaction -PluginStagePayload $stages.plugin.payload -PluginDestination $targets.pluginDestination -PluginExpectedFiles $maps.plugin -McpStagePayload $stages.mcp.payload -McpDestination $targets.mcpDestination -McpExpectedFiles $maps.mcp -VerifyInstalled $verify
 $returned=$true;NewProof 'transaction.private.json' $result
 Require ($result.installed -and $result.status -ceq 'committed') 'Official transaction did not commit.'
 Critical
 $null=Assert-SpherewrightInstallSnapshotComplete -Root $targets.pluginDestination -ExpectedFiles $maps.plugin -PreservedDirectories @('runtime-handoff')
 $null=Assert-SpherewrightInstallSnapshotComplete -Root $targets.mcpDestination -ExpectedFiles $maps.mcp
}catch{$failure=$_.Exception.ToString()}finally{
 NewProof 'install-result.private.json' @{passed=(-not $failure);sourceSha=$cohort.sourceSha;transactionDispatched=$dispatched;transactionResponseReceived=$returned;transactionOutcomeUnknown=($dispatched -and -not $returned);error=$failure;gameCalls=0;loads=0}
}
if($failure){throw 'The original installation ended; preserve receipts and reconcile, do not retry.'}
@{passed=$true;sourceSha=$cohort.sourceSha;committedTransactions=1;gameCalls=0;loads=0}|ConvertTo-Json -Compress

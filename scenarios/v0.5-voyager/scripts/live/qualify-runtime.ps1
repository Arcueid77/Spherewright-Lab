param([Parameter(Mandatory)][string]$SourceRoot,[Parameter(Mandatory)][string]$SourceSha,[Parameter(Mandatory)][string]$OutputRoot,[Parameter(Mandatory)][string]$SdkHostPath,[ValidatePattern("^[a-z0-9-]+$")][string]$ChecksName="development-checks-qualified")
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$revision=$SourceSha
$repo=$SourceRoot
$runtime=Join-Path $OutputRoot 'runtime-qualified/Spherewright-0.5.0'
$single=Join-Path $OutputRoot 'singlefile-qualified/Spherewright.Mcp.exe'
$checks=Join-Path $OutputRoot $ChecksName
function Require($value,[string]$reason){if(-not$value){throw $reason}}
function Hash([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash}
function Proof([string]$path,$value){
 $stream=[IO.File]::Open($path,[IO.FileMode]::CreateNew)
 try{$writer=[IO.StreamWriter]::new($stream,[Text.UTF8Encoding]::new($false));try{$writer.Write(($value|ConvertTo-Json -Depth 30))}finally{$writer.Dispose()}}finally{$stream.Dispose()}
}
Require (-not(Test-Path -LiteralPath $checks)) 'Preserve previous checks.'
$null=New-Item -ItemType Directory -Path $checks
Require ((& git -C $repo rev-parse HEAD).Trim() -ceq $revision -and -not(& git -C $repo status --porcelain)) 'Exact clean source differs.'
$validation=Get-Content -LiteralPath (Join-Path $OutputRoot 'exact-source-validation.private.json') -Raw|ConvertFrom-Json
Require ($validation.passed -and $validation.sourceSha -ceq $revision -and $validation.totalPassed -gt 0) 'Exact build/regression differs.'
$ciText=& gh run view (Get-Content -LiteralPath (Join-Path $OutputRoot 'exact-ci-run-id.private.txt') -Raw).Trim() --repo Arcueid77/Spherewright --json databaseId,headSha,status,conclusion,event,url,createdAt,updatedAt,jobs
Require ($LASTEXITCODE -eq 0) 'CI query failed.'
$ci=$ciText|ConvertFrom-Json
Proof (Join-Path $checks 'exact-ci.private.json') $ci
Require ($ci.headSha -ceq $revision -and $ci.status -ceq 'completed' -and $ci.conclusion -ceq 'success') 'Exact CI is not successful.'
$manifestPath=Join-Path $runtime 'manifest.json'
$manifest=Get-Content -LiteralPath $manifestPath -Raw|ConvertFrom-Json
Require ($manifest.sourceCommit -ceq $revision -and -not$manifest.sourceDirty -and $manifest.version -ceq '0.5.0' -and @($manifest.files).Count -eq 242) 'Development manifest differs.'
foreach($row in $manifest.files){
 $path=Join-Path $runtime $row.path
 Require ((Get-Item -LiteralPath $path).Length -eq $row.size -and (Hash $path).ToLowerInvariant() -ceq $row.sha256) 'Development file changed.'
}
Require (@(Get-ChildItem -LiteralPath $runtime -Recurse -File).Count -eq 243) 'Unexpected development file.'
$probe=Join-Path $runtime 'Test-SpherewrightStagedMcp.ps1'
$transaction=Join-Path $runtime 'SpherewrightInstallTransaction.ps1'
Require ((Hash $probe) -ceq 'AE864396E01F4023024151BB641D13F3E9450D87A5040FB0B13B874EEDD0DADC') 'Official metadata probe differs.'
Require ((Hash $transaction) -ceq 'D0EEB2D6CA92AAA8F7AA83B64ED142187240CEFA1CABB3EABF21AEF6F28188EA') 'Qualified installer differs.'
. $probe
. (Join-Path $repo 'scripts/SpherewrightPackageSurface.ps1')
$originalRequest=${function:Invoke-SpherewrightStagedMcpMetadataRequest}
function Invoke-SpherewrightStagedMcpMetadataRequest {
 param([Diagnostics.Process]$Process,[object]$Stdout,[object]$Stderr,[Diagnostics.Stopwatch]$Stopwatch,[int]$Id,[string]$Method,[object]$Parameters)
 $response=& $originalRequest @PSBoundParameters
 $script:metadata[$Method]=$response
 return $response
}
$metadataResults=@{}
foreach($role in @('directory','standalone')){
 $executable=if($role -ceq 'directory'){Join-Path $runtime 'mcp/Spherewright.Mcp.exe'}else{$single}
 Require ([Diagnostics.FileVersionInfo]::GetVersionInfo($executable).ProductVersion -ceq ('0.5.0+'+$revision)) 'Executable source differs.'
 $script:metadata=@{}
 $result=Invoke-SpherewrightStagedMcpProbe -ExecutablePath $executable -ExpectedVersion '0.5.0' -ExpectedPlaybookPath (Join-Path $runtime 'AGENT-PLAYBOOK.md') -IsolationDirectory (Join-Path $checks ($role+'-isolation'))
 Require ($result.tools -eq 74 -and $result.resources -eq 1 -and $result.playbookMatches -and $result.exitCode -eq 0) 'Metadata surface differs.'
 Proof (Join-Path $checks ($role+'-metadata.private.json')) $script:metadata
 Assert-SpherewrightPackageSurface -Version '0.5.0' -Tools $script:metadata['tools/list'].tools -Resources $script:metadata['resources/list'].resources -PackagedPlaybook ([IO.File]::ReadAllText((Join-Path $runtime 'AGENT-PLAYBOOK.md'))) -ResourcePlaybook $script:metadata['resources/read'].contents[0].text
 $metadataResults[$role]=$result
}
$managed=@(Get-ChildItem -LiteralPath $runtime -Recurse -File|Where-Object{$_.Name -cmatch '^Spherewright\..*\.dll$'})
Require ($managed.Count -eq 6) 'Managed product module inventory differs.'
foreach($file in $managed){Require ([Diagnostics.FileVersionInfo]::GetVersionInfo($file.FullName).ProductVersion -ceq ('0.5.0+'+$revision)) 'Managed source differs.'}
Assert-SpherewrightNoCodeViewRecord -AssemblyPaths $managed.FullName
function DebugRecords([string]$path){
 $stream=[IO.File]::OpenRead($path);$reader=[Reflection.PortableExecutable.PEReader]::new($stream)
 try{
  Require (-not$reader.HasMetadata) 'Only a native host may use SDK debug-record classification.'
  foreach($entry in $reader.ReadDebugDirectory()){
   if($entry.Type -eq 'CodeView'){$data=$reader.ReadCodeViewDebugDirectoryData($entry);[ordered]@{kind='CodeView';guid=$data.Guid.ToString('D');age=$data.Age;path=$data.Path}}
  }
 }finally{$reader.Dispose();$stream.Dispose()}
}
$sdk=$SdkHostPath
Require ((Hash $sdk) -ceq '4FAF26D6F379712D0D98F5B4F25F1F25D796B28847EE239C823A08817F536117') 'Qualified SDK host differs.'
$actual=@(DebugRecords $single);$expected=@(DebugRecords $sdk)
Require ($actual.Count -eq 1 -and ($actual|ConvertTo-Json -Compress) -ceq ($expected|ConvertTo-Json -Compress)) 'Native host metadata differs from qualified public SDK.'
Proof (Join-Path $checks 'native-host-classification.private.json') @{standaloneSha256=(Hash $single);sdkHostSha256=(Hash $sdk);codeViewExactPublicSdkMatch=$true;managedCodeViewAbsent=$true;debugRecords=$actual}
$files=@()
foreach($role in @('plugin','mcp')){
 $root=if($role -ceq 'plugin'){Join-Path $runtime 'BepInEx/plugins/Spherewright'}else{Join-Path $runtime 'mcp'}
 foreach($file in @(Get-ChildItem -LiteralPath $root -Recurse -File|Sort-Object FullName)){
  $files+=@{role=$role;relativePath=[IO.Path]::GetRelativePath($root,$file.FullName).Replace('\','/');source=$file.FullName;bytes=$file.Length;sha256=(Hash $file.FullName)}
 }
}
$files+=@{role='plugin';relativePath='Spherewright.Mcp.exe';source=$single;bytes=(Get-Item -LiteralPath $single).Length;sha256=(Hash $single)}
Require (@($files|Where-Object role -CEQ 'plugin').Count -eq 5 -and @($files|Where-Object role -CEQ 'mcp').Count -eq 224) 'Installed cohort inventory differs.'
$index=Join-Path $checks 'cohort-index.private.json'
& (Join-Path $PSScriptRoot 'module-stamps.ps1') -PluginDirectory (Join-Path $runtime 'BepInEx/plugins/Spherewright') -NativeAssemblyPath (Join-Path $repo '.local/game-refs/Assembly-CSharp.dll') -SourceSha $revision -NativeAssemblySha256 (Hash (Join-Path $repo '.local/game-refs/Assembly-CSharp.dll')) -OutputPath (Join-Path $checks 'revision-stamps.private.json')
Proof $index @{sourceSha=$revision;kind='development_installation_cohort';manualRoot=$runtime;singleFileMcp=$single;officialTransactionScript=$transaction;officialTransactionSha256=(Hash $transaction);officialProbeScript=$probe;officialProbeSha256=(Hash $probe);files=$files}
Proof (Join-Path $checks 'qualification.private.json') @{passed=$true;sourceSha=$revision;manifestSha256=(Hash $manifestPath);cohortIndexSha256=(Hash $index);pluginFiles=5;mcpFiles=224;metadata=$metadataResults;managedCodeViewAbsent=$true;nativeHostExactSdkMatch=$true;exactCiRun=$ci.databaseId;allTestsPassed=$validation.totalPassed;gameCalls=0;installed=$false;runtimeAcceptance=$false;newDistributionArchives=0}
@{passed=$true;sourceSha=$revision;manifestSha256=(Hash $manifestPath);cohortIndexSha256=(Hash $index);pluginFiles=5;mcpFiles=224;tools=74;resources=1;gameCalls=0;newArchives=0}|ConvertTo-Json -Compress

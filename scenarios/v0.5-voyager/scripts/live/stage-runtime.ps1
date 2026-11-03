[CmdletBinding()]
param([Parameter(Mandatory)][string]$SourceRoot,[Parameter(Mandatory)][string]$SourceSha,[Parameter(Mandatory)][string]$DotnetPath,[Parameter(Mandatory)][string]$OutputRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$revision=$SourceSha
$repoRoot=$SourceRoot
$dotnet=$DotnetPath
if ((& git -C $repoRoot rev-parse HEAD).Trim() -cne $revision -or (& git -C $repoRoot status --porcelain)) {throw 'The qualified clean source changed.'}
$developmentRoot=Join-Path $OutputRoot 'runtime-qualified'
$packageRoot=Join-Path $developmentRoot 'Spherewright-0.5.0'
if(Test-Path -LiteralPath $developmentRoot){throw 'Development runtime staging already exists; preserve it.'}
New-Item -ItemType Directory -Path $packageRoot | Out-Null
$qualified=Get-Content -LiteralPath (Join-Path $OutputRoot 'local-build-validation.private.json') -Raw|ConvertFrom-Json
if(-not$qualified.passed -or $qualified.sourceSha -cne $revision){throw 'Exact source Native build/regression is required.'}
& $dotnet publish (Join-Path $repoRoot 'src/Spherewright.Mcp/Spherewright.Mcp.csproj') -c Release -r win-x64 --self-contained true -p:RestoreLockedMode=true -p:Version=0.5.0 -p:DebugType=None -p:DebugSymbols=false "-p:SourceRevisionId=$revision" "-p:InformationalVersion=0.5.0+$revision" -p:IncludeSourceRevisionInInformationalVersion=false -o (Join-Path $packageRoot 'mcp')
if($LASTEXITCODE){throw 'Coherent self-contained MCP build failed.'}
$pluginDirectory=Join-Path $packageRoot 'BepInEx/plugins/Spherewright'
New-Item -ItemType Directory -Path $pluginDirectory | Out-Null
foreach($name in @('Spherewright.Plugin.dll','Spherewright.Contracts.dll','Spherewright.Bridge.Core.dll','Newtonsoft.Json.dll')){
    Copy-Item -LiteralPath (Join-Path $repoRoot "src/Spherewright.Plugin/bin/Release/net472/$name") -Destination (Join-Path $pluginDirectory $name)
}
foreach($pair in @(@('install-release.ps1','install.ps1'),@('locate-dsp.ps1','locate-dsp.ps1'),@('recover-install.ps1','recover-install.ps1'),@('Test-SpherewrightStagedMcp.ps1','Test-SpherewrightStagedMcp.ps1'),@('SpherewrightInstallTransaction.ps1','SpherewrightInstallTransaction.ps1'),@('SpherewrightInstallRecovery.ps1','SpherewrightInstallRecovery.ps1'))){
    Copy-Item -LiteralPath (Join-Path $repoRoot "scripts/$($pair[0])") -Destination (Join-Path $packageRoot $pair[1])
}
# Reuse the official source's exact guide-link conversion function only; no
# packaging entry point, compression, Thunderstore output or installer is run.
$parseErrors=$null;$parseTokens=$null
$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $repoRoot 'scripts/package-release.ps1'),[ref]$parseTokens,[ref]$parseErrors)
if($parseErrors.Count){throw 'The original guide-link converter did not parse.'}
$definition=$ast.FindAll({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Convert-PackagedGuideLinks'},$true)
if($definition.Count -ne 1){throw 'The exact official converter is ambiguous.'}
$gitCommit=$revision
. ([scriptblock]::Create($definition[0].Extent.Text))
foreach($guide in @(@('docs/release-installation.md','INSTALL.md'),@('docs/installation-recovery.md','RECOVERY.md'),@('docs/release-installation.zh-CN.md','release-installation.zh-CN.md'),@('docs/installation-recovery.zh-CN.md','installation-recovery.zh-CN.md'),@('docs/agent-playbook.zh-CN.md','agent-playbook.zh-CN.md'))){
    $guideText=[IO.File]::ReadAllText((Join-Path $repoRoot $guide[0]))
    [IO.File]::WriteAllText((Join-Path $packageRoot $guide[1]),(Convert-PackagedGuideLinks -Text $guideText -SourcePath $guide[0]),[Text.UTF8Encoding]::new($false))
}
foreach($pair in @(@('docs/agent-playbook.md','AGENT-PLAYBOOK.md'),@('LICENSE','LICENSE'),@('LICENSE.zh-CN.md','LICENSE.zh-CN.md'))){Copy-Item -LiteralPath (Join-Path $repoRoot $pair[0]) -Destination (Join-Path $packageRoot $pair[1])}
$files=@(Get-ChildItem -LiteralPath $packageRoot -File -Recurse | Sort-Object FullName | ForEach-Object {
    [ordered]@{path=[IO.Path]::GetRelativePath($packageRoot,$_.FullName).Replace('\','/');size=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
})
$manifest=[ordered]@{schemaVersion=1;package='Spherewright';version='0.5.0';productVersion='0.5.0';runtime='win-x64';sourceCommit=$revision;sourceDirty=$false;supportedDspVersion='0.10.35.29151';supportedBepInExVersion='5.4.17.0';createdAtUtc=[DateTimeOffset]::UtcNow.ToString('O');files=$files}
[IO.File]::WriteAllText((Join-Path $packageRoot 'manifest.json'),($manifest | ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
[ordered]@{sourceSha=$revision;kind='development_runtime_directory';newDistributionArchives=0;installerInvoked=$false;gameCalls=0;manifestSha256=(Get-FileHash -LiteralPath (Join-Path $packageRoot 'manifest.json')).Hash;files=$files.Count} | ConvertTo-Json -Depth 4

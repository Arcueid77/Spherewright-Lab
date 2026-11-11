param([Parameter(Mandatory)][string]$SourceRoot,[Parameter(Mandatory)][string]$SourceSha,[Parameter(Mandatory)][string]$DotnetPath,[Parameter(Mandatory)][string]$OutputRoot,
    [ValidatePattern('^\d+\.\d+\.\d+$')][string]$Version='0.5.0')
$ErrorActionPreference='Stop'
$repo=$SourceRoot
$dotnet=$DotnetPath
$out=Join-Path $OutputRoot 'singlefile-qualified'
if(Test-Path -LiteralPath $out){throw 'Preserve the previous standalone build.'}
& $dotnet publish (Join-Path $repo 'src/Spherewright.Mcp/Spherewright.Mcp.csproj') -c Release -r win-x64 --self-contained true -p:RestoreLockedMode=true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -p:EnableCompressionInSingleFile=true "-p:Version=$Version" -p:DebugType=None -p:DebugSymbols=false "-p:SourceRevisionId=$SourceSha" "-p:InformationalVersion=$Version+$SourceSha" -p:IncludeSourceRevisionInInformationalVersion=false -o $out
if($LASTEXITCODE){throw 'Same-source standalone MCP build failed.'}

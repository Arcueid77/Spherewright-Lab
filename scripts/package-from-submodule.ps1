#requires -Version 7.0
[CmdletBinding()]
param([string]$DspDir,[string]$DotNetPath)
. (Join-Path $PSScriptRoot 'SampleTools.ps1')
$root=Get-SampleRoot
$checked=Assert-SampleSourceLock $root
$lock=$checked.lock;$product=Get-SamplePath $root 'deps/Spherewright'
if($lock.PSObject.Properties.Name -ccontains 'development' -and $lock.development.targetVersion -cne $lock.spherewright.productVersion){throw 'The locked product has not adopted the development target version; do not relabel an older product as the new candidate.'}
$runId=[guid]::NewGuid().ToString('N')
$relativeOutput='artifacts/previews/'+$lock.spherewright.sourceSha+'/'+$runId
$output=Get-SamplePath $root $relativeOutput
$logRoot=Get-SamplePath $root ('.local/package-runs/'+$runId)
[IO.Directory]::CreateDirectory($output)|Out-Null
[IO.Directory]::CreateDirectory($logRoot)|Out-Null
if($IsWindows){
    $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl=[Security.AccessControl.DirectorySecurity]::new();$acl.SetOwner($sid);$acl.SetAccessRuleProtection($true,$false)
    $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))
    Set-Acl -LiteralPath $logRoot -AclObject $acl
}
$arguments=@{Version=$lock.spherewright.productVersion;OutputDirectory=$output}
if($DspDir){$arguments.DspDir=$DspDir};if($DotNetPath){$arguments.DotNetPath=$DotNetPath}
$log=Join-Path $logRoot 'product-package.log'
# The product entry point itself calls package-thunderstore.ps1. Run that chain once.
& (Join-Path $product 'scripts/package-release.ps1') @arguments *> $log
$raw=[IO.File]::ReadAllText($log);$result=$null
$starts=@([regex]::Matches($raw,'(?m)^\{\r?$'))
for($i=$starts.Count-1;$i -ge 0;$i--){
    try{$parsed=$raw.Substring($starts[$i].Index)|ConvertFrom-Json -Depth 50 -ErrorAction Stop;if($parsed.PSObject.Properties.Name -contains 'sourceCommit' -and $parsed.PSObject.Properties.Name -contains 'thunderstore'){$result=$parsed;break}}catch{}
}
if($null -eq $result -or $result.sourceCommit -cne $lock.spherewright.sourceSha -or $result.sourceDirty -or -not $result.verified){throw 'Product packaging did not return a verified exact-source result; inspect the protected local log.'}
$native=Join-Path $product '.local/game-refs/Assembly-CSharp.dll'
if($null -ne $lock.native.assemblySha256 -and (Get-FileHash -LiteralPath $native).Hash -cne $lock.native.assemblySha256){throw 'Preview Native reference differs from the locked accepted Native.'}
$packages=@()
foreach($name in @(('Spherewright-'+$lock.spherewright.productVersion+'-win-x64.zip'),('Spherewright-'+$lock.spherewright.productVersion+'-thunderstore.zip'))){
    $file=Join-Path $output $name
    $packages+=[pscustomobject]@{file=$name;size=(Get-Item -LiteralPath $file).Length;sha256=(Get-FileHash -LiteralPath $file).Hash}
}
$null=Assert-SampleSourceLock $root
$manifest=[ordered]@{schemaVersion=1;mode='local-preview-only';sourceSha=$result.sourceCommit;sourceDirty=$result.sourceDirty;productVersion=$lock.spherewright.productVersion;entryPoints=@('deps/Spherewright/scripts/package-release.ps1','deps/Spherewright/scripts/package-thunderstore.ps1');entryPointChainRuns=1;outputDirectory=$relativeOutput;packages=$packages;frozenCandidatesReplaced=$false;installed=$false;published=$false;gameCalls=0;uncommittedProductSourceUsed=$false}
Write-SampleJson (Join-Path $output 'run-manifest.json') $manifest
$manifest|ConvertTo-Json -Depth 8

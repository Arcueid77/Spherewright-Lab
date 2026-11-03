param([Parameter(Mandatory)][string]$OutputRoot)
$ErrorActionPreference='Stop'
$x=Get-Content -LiteralPath (Join-Path $OutputRoot 'deployment-inputs.private.json') -Raw|ConvertFrom-Json
$cohort=Get-Content -LiteralPath (Join-Path $OutputRoot 'development-checks-qualified/cohort-index.private.json') -Raw|ConvertFrom-Json
function Stamp([string]$Path,[string]$Relative){
 $stream=[IO.File]::OpenRead($Path);$pe=[Reflection.PortableExecutable.PEReader]::new($stream)
 try{
  $meta=[Reflection.Metadata.PEReaderExtensions]::GetMetadataReader($pe)
  $module=$meta.GetModuleDefinition();$assembly=$meta.GetAssemblyDefinition()
  return @{relativePath=$Relative;assemblyName=$meta.GetString($assembly.Name);moduleVersionId=$meta.GetGuid($module.Mvid).ToString('D');version=[Diagnostics.FileVersionInfo]::GetVersionInfo($Path).ProductVersion;sha256=(Get-FileHash -LiteralPath $Path).Hash}
 }finally{$pe.Dispose();$stream.Dispose()}
}
$rows=@()
foreach($row in @($cohort.files|Where-Object {$_.role -ceq 'plugin' -and $_.relativePath -cmatch '^Spherewright\..*\.dll$'})){
 $stamp=Stamp $row.source ('BepInEx/plugins/Spherewright/'+$row.relativePath)
 if($stamp.version -cne ('0.5.0+'+$x.sourceSha)){throw 'Module source changed.'}
 $rows+=$stamp
}
$native=@($x.nativeReferences|Where-Object {[IO.Path]::GetFileName($_.path) -ceq 'Assembly-CSharp.dll'})[0]
$result=@{passed=$true;sourceSha=$x.sourceSha;modules=$rows;native=(Stamp $native.path 'Assembly-CSharp.dll')}
$path=Join-Path $OutputRoot 'development-checks-qualified/revision-stamps.private.json'
$stream=[IO.File]::Open($path,[IO.FileMode]::CreateNew)
try{$writer=[IO.StreamWriter]::new($stream,[Text.UTF8Encoding]::new($false));try{$writer.Write(($result|ConvertTo-Json -Depth 8))}finally{$writer.Dispose()}}finally{$stream.Dispose()}
@{passed=$true;sourceSha=$x.sourceSha;pluginModules=$rows.Count}|ConvertTo-Json -Compress

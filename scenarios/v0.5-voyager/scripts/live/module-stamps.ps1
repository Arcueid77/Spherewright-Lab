param([Parameter(Mandatory)][string]$PluginDirectory,[Parameter(Mandatory)][string]$NativeAssemblyPath,
 [Parameter(Mandatory)][string]$SourceSha,[Parameter(Mandatory)][string]$NativeAssemblySha256,
 [Parameter(Mandatory)][string]$OutputPath,
 [ValidatePattern('^\d+\.\d+\.\d+$')][string]$Version='0.5.0')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Stamp([string]$Path){
 $stream=[IO.File]::OpenRead($Path)
 $pe=[Reflection.PortableExecutable.PEReader]::new($stream)
 try{
  $metadata=[Reflection.Metadata.PEReaderExtensions]::GetMetadataReader($pe)
  $definition=$metadata.GetModuleDefinition()
  [ordered]@{assemblyName=$metadata.GetString($metadata.GetAssemblyDefinition().Name)
   moduleVersionId=$metadata.GetGuid($definition.Mvid).ToString('D')
   informationalVersion=[Diagnostics.FileVersionInfo]::GetVersionInfo($Path).ProductVersion
   sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash}
 }finally{$pe.Dispose();$stream.Dispose()}
}
$modules=@()
foreach($name in @('Spherewright.Bridge.Core','Spherewright.Contracts','Spherewright.Plugin')){
 $item=Stamp (Join-Path $PluginDirectory ($name+'.dll'))
 if($item.assemblyName -cne $name -or $item.informationalVersion -cne ($Version+'+'+$SourceSha)){throw 'Managed revision differs from the selected cohort.'}
 $modules+=$item
}
$native=Stamp $NativeAssemblyPath
if($native.assemblyName -cne 'Assembly-CSharp' -or $native.sha256 -cne $NativeAssemblySha256){throw 'Native revision differs.'}
$value=[ordered]@{passed=$true;sourceSha=$SourceSha;modules=$modules;native=$native;basis='read_only_PE_metadata_and_exact_file_hash'}
$stream=[IO.File]::Open($OutputPath,[IO.FileMode]::CreateNew)
try{$writer=[IO.StreamWriter]::new($stream,[Text.UTF8Encoding]::new($false));try{$writer.Write(($value|ConvertTo-Json -Depth 8))}finally{$writer.Dispose()}}finally{$stream.Dispose()}
Write-Output 'Current PE module identities captured without loading or executing assemblies.'

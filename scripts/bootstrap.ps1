#requires -Version 7.0
[CmdletBinding()]
param()
. (Join-Path $PSScriptRoot 'SampleTools.ps1')
$root = Get-SampleRoot
$entry = Invoke-SampleGit $root @('ls-files','--stage','--','deps/Spherewright')
if ($entry -cnotmatch '^160000 ([0-9a-f]{40}) 0\s+deps/Spherewright$') { throw 'Missing exact product gitlink.' }
$lock = Read-SampleJson (Get-SamplePath $root 'source-lock.json')
if ($Matches[1] -cne $lock.spherewright.sourceSha) { throw 'Gitlink/lock mismatch before initialization.' }
$product = Get-SamplePath $root 'deps/Spherewright'
if (Test-Path -LiteralPath (Join-Path $product '.git')) {
    if ((Invoke-SampleGit $product @('rev-parse','HEAD')) -cne $lock.spherewright.sourceSha -or (Invoke-SampleGit $product @('status','--porcelain=v1','--untracked-files=normal'))) { throw 'Preserve an unexpected or dirty existing submodule; bootstrap does not overwrite it.' }
}
Invoke-SampleGit $root @('submodule','update','--init','--recursive','--','deps/Spherewright') | Out-Null
foreach ($path in @('.local','artifacts')) { [IO.Directory]::CreateDirectory((Get-SamplePath $root $path)) | Out-Null }
& (Join-Path $PSScriptRoot 'verify-source-lock.ps1') -Root $root

#requires -Version 7.0
[CmdletBinding()]
param([Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{40}$')][string]$Sha, [string]$NewLockPath)
. (Join-Path $PSScriptRoot 'SampleTools.ps1')
$root=Get-SampleRoot
if(Invoke-SampleGit $root @('status','--porcelain=v1','--untracked-files=normal')){throw 'The sample worktree and index must be clean before a product bump.'}
$current=Assert-SampleSourceLock $root
if($current.lock.spherewright.sourceSha -ceq $Sha){@{changed=$false;sourceSha=$Sha;reason='Already locked; no checkout, write, or push.'}|ConvertTo-Json;return}
if(-not $NewLockPath){throw 'A changed product SHA requires -NewLockPath with reviewed package/provenance metadata; old acceptance cannot silently become evidence for new code.'}
Assert-SampleJsonSchema $NewLockPath (Get-SamplePath $root 'schemas/source-lock.schema.json')
$next=Read-SampleJson $NewLockPath
if($next.spherewright.sourceSha -cne $Sha -or $next.spherewright.repository -cne 'Arcueid77/Spherewright' -or $next.spherewright.submodulePath -cne 'deps/Spherewright'){throw 'New lock does not match the requested exact SHA.'}
if((Get-FileHash -LiteralPath (Get-SamplePath $root $next.acceptance.evidenceManifest)).Hash -cne $next.acceptance.evidenceManifestSha256){throw 'Reviewed evidence manifest for new lock is missing or changed.'}
$runsJson=@(& gh run list --repo Arcueid77/Spherewright --commit $Sha --workflow windows-core-ci.yml --limit 20 --json headSha,status,conclusion,databaseId 2>&1)
if($LASTEXITCODE -ne 0){throw 'Cannot verify the exact product CI; preserve the current lock.'}
$runs=($runsJson -join "`n")|ConvertFrom-Json
$green=@($runs|Where-Object {$_.headSha -ceq $Sha -and $_.status -ceq 'completed' -and $_.conclusion -ceq 'success'})
if($green.Count -lt 1){throw 'The requested exact product SHA has no successful completed product CI.'}
$product=Get-SamplePath $root 'deps/Spherewright'
Invoke-SampleGit $product @('fetch','origin',$Sha)|Out-Null
if($null -ne $next.spherewright.releaseTag){Invoke-SampleGit $product @('fetch','origin',('refs/tags/'+$next.spherewright.releaseTag+':refs/tags/'+$next.spherewright.releaseTag))|Out-Null}
Invoke-SampleGit $product @('checkout','--detach',$Sha)|Out-Null
[xml]$props=Get-Content -LiteralPath (Join-Path $product 'Directory.Build.props') -Raw
if([string]$props.Project.PropertyGroup.VersionPrefix -cne $next.spherewright.productVersion){throw 'New checkout version differs from the reviewed lock; preserve and inspect the bounded bump state.'}
$releasePath='releases/v'+$next.spherewright.productVersion+'/source-lock.json'
Write-SampleJson (Get-SamplePath $root 'source-lock.json') $next
Write-SampleJson (Get-SamplePath $root $releasePath) $next
Invoke-SampleGit $root @('add','--','deps/Spherewright','source-lock.json',$releasePath)|Out-Null
$checked=Assert-SampleSourceLock $root
$summary=[ordered]@{changed=$true;oldSourceSha=$current.lock.spherewright.sourceSha;newSourceSha=$Sha;productCiRun=$green[0].databaseId;stagedPaths=@('deps/Spherewright','source-lock.json',$releasePath);committed=$false;pushed=$false;gameCalls=0}
Write-SampleJson (Get-SamplePath $root '.local/product-bump-summary.json') $summary
$summary|ConvertTo-Json -Depth 5

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-SampleRoot { [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)) }
function Get-SamplePath {
    param([string]$Root, [string]$RelativePath)
    if ([string]::IsNullOrWhiteSpace($RelativePath) -or [IO.Path]::IsPathRooted($RelativePath) -or $RelativePath.Contains('\') -or $RelativePath -match '(^|/)\.\.(/|$)|[:\x00-\x1f]') {
        throw 'Unsafe relative path in sample metadata.'
    }
    $base = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $full = [IO.Path]::GetFullPath((Join-Path $base $RelativePath))
    if (-not $full.StartsWith($base + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Path escapes sample root.' }
    $cursor = $full
    while ($cursor.Length -gt $base.Length) {
        if ((Test-Path -LiteralPath $cursor) -and ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Reparse points are not allowed in evidence paths.' }
        $cursor = Split-Path -Parent $cursor
    }
    return $full
}
function Invoke-SampleGit {
    param([string]$Root, [string[]]$Arguments)
    $output = @(& git -C $Root @Arguments 2>&1)
    if ($LASTEXITCODE -ne 0) { throw ('Git operation failed: ' + ($Arguments[0]) + '; inspect local command output without exposing credentials.') }
    return ($output -join "`n").TrimEnd()
}
function Read-SampleJson { param([string]$Path) Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -Depth 80 }
function Write-SampleJson {
    param([string]$Path, $Value)
    [IO.Directory]::CreateDirectory((Split-Path -Parent $Path)) | Out-Null
    [IO.File]::WriteAllText($Path, (($Value | ConvertTo-Json -Depth 80).Replace("`r`n", "`n") + "`n"), [Text.UTF8Encoding]::new($false))
}
function Assert-SampleFile {
    param([string]$Root, [string]$Path, [long]$Size, [string]$Sha256)
    $full = Get-SamplePath $Root $Path
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw "Missing manifest file: $Path" }
    if ((Get-Item -LiteralPath $full).Length -ne $Size -or (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash -cne $Sha256.ToUpperInvariant()) { throw "Manifest size/hash mismatch: $Path" }
}
function Assert-SampleJsonSchema {
    param([string]$Path, [string]$SchemaPath)
    try { $valid = Test-Json -Json (Get-Content -LiteralPath $Path -Raw) -SchemaFile $SchemaPath -ErrorAction Stop }
    catch { throw 'JSON schema validation failed.' }
    if (-not $valid) { throw 'JSON schema validation failed.' }
}
function Get-SampleTrackedPaths {
    param([string]$Root)
    @((Invoke-SampleGit $Root @('-c','core.quotePath=false','ls-files')) -split "`n" | Where-Object { $_ })
}
function Assert-SampleAcceptanceReference {
    param([string]$Root, $Lock, [string]$LockPath)
    $evidencePath = Get-SamplePath $Root $Lock.acceptance.evidenceManifest
    if ((Get-FileHash -LiteralPath $evidencePath).Hash -cne $Lock.acceptance.evidenceManifestSha256) { throw 'Evidence manifest hash does not match source-lock.' }
    if ($Lock.acceptance.PSObject.Properties.Name -cnotcontains 'scope') {
        $releasePath = 'releases/v' + $Lock.spherewright.productVersion + '/source-lock.json'
        $releaseLockPath = Get-SamplePath $Root $releasePath
        if (-not (Test-Path -LiteralPath $releaseLockPath -PathType Leaf) -or (Get-FileHash -LiteralPath $releaseLockPath).Hash -cne (Get-FileHash -LiteralPath $LockPath).Hash) { throw 'Root and release source locks differ without an explicit historical reference.' }
        return [pscustomobject]@{ scope = 'locked_release'; sourceSha = $Lock.spherewright.sourceSha; appliesToActiveSource = $true }
    }
    if ($Lock.acceptance.scope -cne 'historical_reference' -or $Lock.acceptance.sourceLock -cnotmatch '^releases/v[0-9]+\.[0-9]+\.[0-9]+/source-lock\.json$') { throw 'Historical acceptance must reference the frozen release source lock.' }
    $releasePath = $Lock.acceptance.sourceLock
    $releaseLockPath = Get-SamplePath $Root $releasePath
    if ((Get-FileHash -LiteralPath $releaseLockPath).Hash -cne $Lock.acceptance.sourceLockSha256) { throw 'Frozen acceptance source-lock hash does not match the explicit reference.' }
    Assert-SampleJsonSchema $releaseLockPath (Get-SamplePath $Root 'schemas/source-lock.schema.json')
    $frozen = Read-SampleJson $releaseLockPath
    if ($frozen.acceptance.PSObject.Properties.Name -ccontains 'scope') { throw 'Frozen acceptance source lock must be a legacy release lock, not another reference.' }
    if ($releasePath -cne ('releases/v' + $frozen.spherewright.productVersion + '/source-lock.json') -or
        $frozen.acceptance.spec -cne $Lock.acceptance.spec -or
        $frozen.acceptance.evidenceManifest -cne $Lock.acceptance.evidenceManifest -or
        $frozen.acceptance.evidenceManifestSha256 -cne $Lock.acceptance.evidenceManifestSha256 -or
        $frozen.evidenceSource.repository -cne $Lock.evidenceSource.repository -or
        $frozen.evidenceSource.sourceSha -cne $Lock.evidenceSource.sourceSha) { throw 'Historical acceptance manifest or provenance differs from the frozen source lock.' }
    Assert-SampleJsonSchema $evidencePath (Get-SamplePath $Root 'schemas/manifest.schema.json')
    $manifest = Read-SampleJson $evidencePath
    if ($manifest.sourceSha -cne $frozen.evidenceSource.sourceSha) { throw 'Historical evidence manifest does not match frozen provenance.' }
    [pscustomobject]@{ scope = 'historical_reference'; sourceSha = $frozen.spherewright.sourceSha; appliesToActiveSource = $false }
}
function Assert-SamplePackageNames {
    param($Packages, [string]$Version)
    foreach ($kind in @('manual','thunderstore')) {
        $p = $Packages.$kind
        if ($null -eq $p) { continue }
        $suffix = if ($kind -ceq 'manual') { 'win-x64' } else { 'thunderstore' }
        if ($p.file -cne ('Spherewright-' + $Version + '-' + $suffix + '.zip')) { throw 'Package names must match their locked product version and layout.' }
    }
}
function Assert-SamplePackageSource {
    param([string]$Path, [string]$Kind, [string]$Version, [string]$SourceSha, [string]$NativeVersion)
    $zip = [IO.Compression.ZipFile]::OpenRead($Path)
    try {
        $manifestName = if ($Kind -ceq 'manual') { 'Spherewright-' + $Version + '/manifest.json' } else { 'spherewright-manifest.json' }
        $entries = @($zip.Entries | Where-Object FullName -CEQ $manifestName)
        if ($entries.Count -ne 1 -or $entries[0].Length -gt 8388608) { throw 'Package exact-source manifest is missing, duplicate, or oversized.' }
        $reader = [IO.StreamReader]::new($entries[0].Open())
        try { $manifest = $reader.ReadToEnd() | ConvertFrom-Json -Depth 80 } finally { $reader.Dispose() }
        if ($manifest.sourceCommit -cne $SourceSha -or $manifest.sourceDirty -ne $false -or
            $manifest.version -cne $Version -or $manifest.productVersion -cne $Version -or
            $manifest.supportedDspVersion -cne $NativeVersion) { throw 'Package source, version, clean state, or Native cohort differs from the active source lock.' }
    } finally { $zip.Dispose() }
}
function Assert-SampleInstalledRecord {
    param([string]$Root, [string]$Product, $Installed)
    $evidence = Get-SamplePath $Root $Installed.evidence
    if (-not (Test-Path -LiteralPath $evidence -PathType Leaf)) { throw 'Installed-state evidence reference is unavailable.' }
    if ($null -eq $Installed.native.assemblySha256) { throw 'Installed Native record requires its actual assembly hash.' }
    Assert-SamplePackageNames -Packages $Installed.packages -Version $Installed.productVersion
    if ($null -ne $Installed.releaseTag) {
        if ($Installed.releaseTag -cne ('v' + $Installed.productVersion) -or
            (Invoke-SampleGit $Product @('rev-parse',($Installed.releaseTag + '^{commit}'))) -cne $Installed.sourceSha) { throw 'Installed release tag does not match the recorded installed source.' }
    }
    if ($Installed.runtimeState -ceq 'running_verified' -and $Installed.verification -cne 'disk_verified') { throw 'Verified running state requires a disk-verified installation record.' }
}
function Assert-SampleSourceLock {
    param([string]$Root, [string]$PackageDirectory)
    $lockPath = Get-SamplePath $Root 'source-lock.json'
    Assert-SampleJsonSchema $lockPath (Get-SamplePath $Root 'schemas/source-lock.schema.json')
    $lock = Read-SampleJson $lockPath
    if ($lock.spherewright.repository -cnotin @('Arcueid77/Spherewright','AvaloNero/Spherewright') -or $lock.spherewright.submodulePath -cne 'deps/Spherewright') { throw 'Unexpected product repository or submodule path.' }
    $sha = [string]$lock.spherewright.sourceSha
    $entry = Invoke-SampleGit $Root @('ls-files','--stage','--','deps/Spherewright')
    if ($entry -cnotmatch '^160000 ([0-9a-f]{40}) 0\s+deps/Spherewright$' -or $Matches[1] -cne $sha) { throw 'Gitlink does not match the source lock.' }
    $product = Get-SamplePath $Root $lock.spherewright.submodulePath
    if ((Invoke-SampleGit $product @('rev-parse','HEAD')) -cne $sha) { throw 'Submodule HEAD does not match the source lock.' }
    if (Invoke-SampleGit $product @('status','--porcelain=v1','--untracked-files=normal')) { throw 'Product submodule must be clean.' }
    if ((Invoke-SampleGit $Root @('config','--file','.gitmodules','--get','submodule.deps/Spherewright.url')) -cne 'https://github.com/Arcueid77/Spherewright.git') { throw 'Unexpected submodule URL.' }
    $moduleConfig = Get-Content -LiteralPath (Get-SamplePath $Root '.gitmodules') -Raw
    if ($moduleConfig -match '(?m)^\s*branch\s*=') { throw 'Floating submodule branches are forbidden.' }
    if ($null -eq $lock.spherewright.releaseTag) {
        if ($lock.status -cnotin @('development','provisional')) { throw 'An untagged source must remain development or provisional.' }
    } else {
        if ($lock.status -cne 'tagged' -or $lock.spherewright.releaseTag -cnotmatch '^v\d+\.\d+\.\d+$') { throw 'Invalid release tag lock.' }
        if ((Invoke-SampleGit $product @('rev-parse',($lock.spherewright.releaseTag + '^{commit}'))) -cne $sha) { throw 'Release tag does not point to the locked source.' }
    }
    [xml]$props = Get-Content -LiteralPath (Join-Path $product 'Directory.Build.props') -Raw
    $constant = Get-Content -LiteralPath (Join-Path $product 'src/Spherewright.Contracts/Versioning/SpherewrightProduct.cs') -Raw
    if ([string]$props.Project.PropertyGroup.VersionPrefix -cne $lock.spherewright.productVersion -or $constant -cnotmatch ('CurrentVersion\s*=\s*"' + [regex]::Escape($lock.spherewright.productVersion) + '"')) { throw 'Product version does not match the lock.' }
    if ($lock.schemaVersion -eq 2) { Assert-SampleInstalledRecord -Root $Root -Product $product -Installed $lock.installed }
    if ($lock.PSObject.Properties.Name -ccontains 'development' -and $lock.status -cne 'development' -and
        $lock.development.targetVersion -cne $lock.spherewright.productVersion) { throw 'A built candidate must use its development target product version.' }
    $acceptance = Assert-SampleAcceptanceReference -Root $Root -Lock $lock -LockPath $lockPath
    Assert-SamplePackageNames -Packages $lock.packages -Version $lock.spherewright.productVersion
    if (-not $PackageDirectory) { $PackageDirectory = Get-SamplePath $Root 'artifacts' }
    $present = 0; $notBuilt = 0
    foreach ($kind in @('manual','thunderstore')) {
        $p = $lock.packages.$kind
        if ($null -eq $p) { ++$notBuilt; continue }
        if ([IO.Path]::GetFileName($p.file) -cne $p.file) { throw 'Package names must be plain file names.' }
        $file = Join-Path $PackageDirectory $p.file
        if (Test-Path -LiteralPath $file) {
            if (-not (Test-Path -LiteralPath $file -PathType Leaf) -or (Get-Item -LiteralPath $file).Length -ne $p.size -or (Get-FileHash -LiteralPath $file).Hash -cne $p.sha256) { throw "Frozen package size/hash mismatch: $kind" }
            if ($lock.schemaVersion -eq 2) { Assert-SamplePackageSource -Path $file -Kind $kind -Version $lock.spherewright.productVersion -SourceSha $sha -NativeVersion $lock.native.version }
            ++$present
        }
    }
    [pscustomobject]@{ lock = $lock; packagesPresentAndVerified = $present; packagesNotPresent = 2 - $notBuilt - $present; packagesNotBuilt = $notBuilt; candidatePackagesReady = ($notBuilt -eq 0 -and $present -eq 2); acceptance = $acceptance }
}

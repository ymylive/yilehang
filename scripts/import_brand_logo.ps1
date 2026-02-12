param(
  [string]$SourcePath = "C:\Users\Ymy_l\Desktop\6d0a07552c608d4081b82691b7abd9fc.jpg",
  [string]$TargetPath = "E:\project\yinling\yinling\apps\unified-miniapp\src\static\brand-logo.jpg",
  [switch]$CopyOnly
)

if (-not (Test-Path -LiteralPath $SourcePath)) {
  throw "Source file not found: $SourcePath"
}

$targetDir = Split-Path -Path $TargetPath -Parent
if (-not (Test-Path -LiteralPath $targetDir)) {
  New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

if ($CopyOnly) {
  Copy-Item -LiteralPath $SourcePath -Destination $TargetPath -Force
} else {
  Move-Item -LiteralPath $SourcePath -Destination $TargetPath -Force
}

if (-not (Test-Path -LiteralPath $TargetPath)) {
  throw "Target file was not created: $TargetPath"
}

$targetInfo = Get-Item -LiteralPath $TargetPath
Write-Output ("OK: {0} ({1} bytes)" -f $targetInfo.FullName, $targetInfo.Length)

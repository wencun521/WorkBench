# 一键打包部署压缩包（替代手动维护 deploy/backend 快照）
# 用法：仓库根目录执行  powershell -ExecutionPolicy Bypass -File deploy/pack.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent   # 仓库根目录 f:\code\flowdesk

# 1. 确保密钥文件存在（首次运行自动生成）
$jwt = Join-Path $PSScriptRoot "jwt.env"
if (-not (Test-Path $jwt)) {
    $key = python -c "import secrets;print(secrets.token_hex(32))"
    Set-Content -Path $jwt -Value "JWT_SECRET_KEY=$key" -NoNewline
    Write-Host "已生成 jwt.env（新密钥）"
}

# 2. 确保空数据库文件存在（Docker 挂载要求文件先存在）
$dataDir = Join-Path $PSScriptRoot "data"
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
$db = Join-Path $dataDir "app.db"
if (-not (Test-Path $db)) {
    New-Item -ItemType File -Path $db | Out-Null
    Write-Host "已创建空数据库 data/app.db"
}

# 3. 暂存组包：直接取主 backend/ 最新代码，排除 .venv/__pycache__/app.db
$stage = Join-Path $env:TEMP "flowdesk-deploy-stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

robocopy (Join-Path $root "backend") (Join-Path $stage "backend") /E /XD .venv __pycache__ /XF app.db *.pyc /NFL /NDL /NJH /NJS | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy 复制 backend 失败，退出码 $LASTEXITCODE" }

New-Item -ItemType Directory -Path (Join-Path $stage "data") | Out-Null
Copy-Item (Join-Path $PSScriptRoot "docker-compose.yml") $stage
Copy-Item $jwt $stage
Copy-Item $db (Join-Path (Join-Path $stage "data") "app.db")

# 4. 压缩
$zip = Join-Path $PSScriptRoot "flowdesk-deploy.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path "$stage\backend", "$stage\docker-compose.yml", "$stage\jwt.env", "$stage\data" -DestinationPath $zip
Remove-Item $stage -Recurse -Force

$size = "{0:N1} KB" -f ((Get-Item $zip).Length / 1KB)
Write-Host "打包完成: $zip ($size)"

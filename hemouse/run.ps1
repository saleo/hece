# HEMouse 启动脚本 (PowerShell)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "HEMouse 启动脚本" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (!(Test-Path ".venv")) {
    Write-Host "❌ 虚拟环境不存在！" -ForegroundColor Red
    Write-Host "   请先运行: uv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 虚拟环境存在" -ForegroundColor Green

# 激活虚拟环境并运行
Write-Host "🔧 激活虚拟环境..." -ForegroundColor Cyan
& .venv\Scripts\Activate.ps1

Write-Host "🚀 启动 HEMouse..." -ForegroundColor Cyan
Write-Host ""

python main.py
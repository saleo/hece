@echo off
REM HEMouse 启动脚本 (CMD)

echo ============================================================
echo HEMouse 启动脚本
echo ============================================================
echo.

REM 检查虚拟环境
if not exist ".venv" (
    echo [错误] 虚拟环境不存在！
    echo    请先运行: uv venv
    exit /b 1
)

echo [成功] 虚拟环境存在
echo [执行] 激活虚拟环境...

REM 激活虚拟环境并运行
call .venv\Scripts\activate.bat

echo [执行] 启动 HEMouse...
echo.

python main.py
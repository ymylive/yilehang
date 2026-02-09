@echo off
REM 易乐航统一小程序 - 一键构建脚本 (Windows)

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0..\.."
set "MINIAPP_DIR=%PROJECT_ROOT%\apps\unified-miniapp"
set "BUILD_OUTPUT=%MINIAPP_DIR%\dist\build\mp-weixin"

echo ==========================================
echo 易乐航统一小程序 - 构建脚本
echo ==========================================

REM 检查 pnpm
where pnpm >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未安装 pnpm
    echo 请运行: npm install -g pnpm
    exit /b 1
)

echo.
echo [1/4] 检查依赖...
cd /d "%PROJECT_ROOT%"
if not exist "node_modules" (
    echo 安装依赖中...
    pnpm install
) else (
    echo 依赖已安装
)

echo.
echo [2/4] 清理旧构建...
if exist "%BUILD_OUTPUT%" (
    rmdir /s /q "%BUILD_OUTPUT%"
    echo 已清理旧构建产物
)

echo.
echo [3/4] 构建小程序...
pnpm -C "%MINIAPP_DIR%" build:mp-weixin

echo.
echo [4/4] 验证构建产物...
if exist "%BUILD_OUTPUT%\app.js" (
    if exist "%BUILD_OUTPUT%\app.json" (
        echo √ 构建成功
        echo.
        echo 构建产物位置:
        echo   %BUILD_OUTPUT%
        echo.
        echo 下一步:
        echo   1. 打开微信开发者工具
        echo   2. 导入项目: %BUILD_OUTPUT%
        echo   3. 点击上传按钮发布
    ) else (
        echo × 构建失败: 未找到 app.json
        exit /b 1
    )
) else (
    echo × 构建失败: 未找到 app.js
    exit /b 1
)

echo.
echo ==========================================
echo 构建完成
echo ==========================================

endlocal

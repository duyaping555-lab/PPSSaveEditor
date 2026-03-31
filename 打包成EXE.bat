@echo off
chcp 65001 >nul
title PPSSPP Save Editor - 打包工具
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║           PPSSPP Save Editor - 打包成Windows程序             ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [*] 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] Python 未安装
    pause
    exit /b 1
)

pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [*] 安装 PyInstaller...
    pip install pyinstaller -q
)

echo [✓] 环境就绪
echo.

echo [*] 开始打包...
echo   这会创建一个独立的 .exe 文件，无需Python环境即可运行
echo.

REM 打包GUI版本
pyinstaller ^
    --name "PPSSaveEditor" ^
    --onefile ^
    --windowed ^
    --icon NONE ^
    --add-data "psp_save_editor.py;." ^
    --clean ^
    --noconfirm ^
    gui_editor.py

if errorlevel 1 (
    echo.
    echo [✗] 打包失败
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  [✓] 打包完成！                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

if exist "dist\PPSSaveEditor.exe" (
    echo 程序位置: dist\PPSSaveEditor.exe
    echo 文件大小: 
    for %%F in (dist\PPSSaveEditor.exe) do echo          %%~zF bytes
    echo.
    echo 你可以：
    echo   1. 直接运行 dist\PPSSaveEditor.exe
    echo   2. 复制到桌面或其他位置使用
    echo   3. 分享给别人使用（无需安装Python）
    echo.
    
    REM 复制到根目录方便使用
    copy "dist\PPSSaveEditor.exe" "PPSSaveEditor.exe" >nul
    echo [✓] 已复制到当前目录: PPSSaveEditor.exe
) else (
    echo [!] 未找到生成的exe文件
    echo     请检查 dist\ 目录
)

echo.
pause

@echo off
chcp 65001 >nul
echo ===========================================
echo PPSSPP Save Editor APK Builder for Windows
echo ===========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo [1/5] 检查Python环境...
python --version

echo.
echo [2/5] 安装构建工具...
pip install -q buildozer cython kivy

echo.
echo [3/5] 检查Android SDK...
if "%ANDROID_HOME%"=="" (
    echo [警告] ANDROID_HOME 未设置
    echo 尝试查找Android SDK...
    
    if exist "%LOCALAPPDATA%\Android\Sdk" (
        set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
        echo 找到SDK: %ANDROID_HOME%
    ) else (
        echo [错误] 未找到Android SDK
        echo 请安装Android Studio或设置ANDROID_HOME
        pause
        exit /b 1
    )
)

echo SDK路径: %ANDROID_HOME%

echo.
echo [4/5] 准备构建环境...
cd mobile_app

REM 复制必要的文件
copy ..\psp_save_editor.py . >nul 2>&1

echo.
echo [5/5] 开始构建APK...
echo 注意: 首次构建需要下载大量文件，可能需要30-60分钟
echo.

buildozer android debug

if errorlevel 1 (
    echo.
    echo [错误] 构建失败
    pause
    exit /b 1
)

echo.
echo ===========================================
echo 构建成功!
echo APK位置: mobile_app\bin\
echo ===========================================
pause

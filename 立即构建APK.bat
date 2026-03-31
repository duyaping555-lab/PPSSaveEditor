@echo off
chcp 65001 >nul
title PPSSPP Save Editor APK 构建工具
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║           PPSSPP Save Editor APK Builder                       ║
echo ║           PSP存档编辑器 Android安装包构建工具                  ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM 设置环境变量
set PATH=%PATH%;C:\Users\duyp5\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts
set ANDROID_HOME=C:\Users\duyp5\AppData\Local\Android\Sdk
set ANDROID_SDK_ROOT=%ANDROID_HOME%
set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot
set BUILDOZER_WARN_ON_ROOT=0

REM 检查Java
echo [*] 检查 Java 环境...
java -version >nul 2>&1
if errorlevel 1 (
    echo [✗] 错误: Java 未安装或未配置
    echo       请安装 Java JDK 17 或更高版本
    pause
    exit /b 1
)
echo [✓] Java 已安装

REM 检查Android SDK
echo [*] 检查 Android SDK...
if not exist "%ANDROID_HOME%" (
    echo [✗] 错误: Android SDK 未找到
    echo       路径: %ANDROID_HOME%
    pause
    exit /b 1
)
echo [✓] Android SDK 已找到

REM 检查Python
echo [*] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 错误: Python 未安装
    pause
    exit /b 1
)
echo [✓] Python 已安装

cd /d "%~dp0"

REM 安装/检查依赖
echo.
echo [*] 检查并安装构建依赖...
echo       这可能需要几分钟时间，请耐心等待...
echo.

python -m pip install -q python-for-android buildozer cython kivy pycryptodome
if errorlevel 1 (
    echo [✗] 依赖安装失败
    pause
    exit /b 1
)
echo [✓] 依赖已安装

REM 准备文件
echo.
echo [*] 准备构建文件...
cd mobile_app
copy /Y ..\psp_save_editor.py . >nul 2>&1
echo [✓] 文件已准备

REM 开始构建
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  开始构建 APK                                                  ║
echo ║                                                                ║
echo ║  预计时间: 30-60 分钟 (取决于网络速度和电脑性能)               ║
echo ║  首次构建需要下载约 500MB-1GB 的依赖文件                       ║
echo ║                                                                ║
echo ║  注意:                                                         ║
echo ║  1. 请勿关闭此窗口                                             ║
echo ║  2. 如果遇到错误，请查看上方的错误信息                         ║
echo ║  3. 构建成功后 APK 将保存在当前目录                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM 尝试使用 python-for-android 构建
echo [1/2] 尝试使用 Python-for-Android 构建...
echo.

python -m pythonforandroid.toolchain apk ^
    --debug ^
    --bootstrap=sdl2 ^
    --requirements=python3,kivy,pycryptodome ^
    --arch=arm64-v8a ^
    --name=PPSSaveEditor ^
    --version=1.0.0 ^^
    --package=com.ppssaveeditor.ppssaveeditor ^
    --android_api=33 ^
    --ndk_dir="%ANDROID_HOME%\ndk" ^
    --sdk_dir="%ANDROID_HOME%" ^
    --private="%~dp0mobile_app" ^
    --orientation=portrait ^
    --permission=INTERNET ^
    --permission=READ_EXTERNAL_STORAGE ^
    --permission=WRITE_EXTERNAL_STORAGE 2>&1

set BUILD_RESULT=%ERRORLEVEL%

if %BUILD_RESULT%==0 (
    goto :build_success
)

echo.
echo [!] Python-for-Android 构建失败，尝试备用方案...
echo.

REM 备用方案: 使用 Buildozer
echo [2/2] 尝试使用 Buildozer 构建...
echo.

REM 检查 buildozer.spec
if not exist "buildozer.spec" (
    echo [✗] 错误: 缺少 buildozer.spec 配置文件
    pause
    exit /b 1
)

REM 运行 buildozer
buildozer android debug 2>&1

if errorlevel 1 (
    echo.
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║  [✗] 构建失败                                                  ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo 所有自动构建方案都失败了。建议的解决方案：
    echo.
    echo 方案 1: 使用 GitHub Actions 自动构建（最简单）
    echo   1. 将项目上传到 GitHub
    echo   2. 自动构建 APK
    echo   3. 下载生成的 APK
    echo   详细步骤见 GET_APK.md
    echo.
    echo 方案 2: 使用 Docker 构建
    echo   运行: docker run -v "%%cd%%":/src kivy/buildozer android debug
    echo.
    echo 方案 3: 使用 Android Studio
    echo   1. 安装 Android Studio
    echo   2. 打开本项目
    echo   3. 点击 Build ^> Build APK
    echo.
    pause
    exit /b 1
)

:build_success
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  [✓] 构建成功！                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM 查找APK文件
echo [*] 查找生成的 APK 文件...
set APK_FOUND=0

if exist "*.apk" (
    for %%f in (*.apk) do (
        echo [✓] 找到 APK: %%f
        copy "%%f" "..\PPSSaveEditor.apk" >nul
        set APK_FOUND=1
    )
)

if exist "bin\*.apk" (
    for %%f in (bin\*.apk) do (
        echo [✓] 找到 APK: %%f
        copy "%%f" "..\PPSSaveEditor.apk" >nul
        set APK_FOUND=1
    )
)

cd ..

if %APK_FOUND%==1 (
    if exist "PPSSaveEditor.apk" (
        echo.
        echo ╔════════════════════════════════════════════════════════════════╗
        echo ║  APK 文件已生成！                                              ║
        echo ╚════════════════════════════════════════════════════════════════╝
        echo.
        echo 文件位置: %CD%\PPSSaveEditor.apk
        echo 文件大小: 
        for %%F in (PPSSaveEditor.apk) do echo          %%~zF bytes
        echo.
        echo 安装方法：
        echo   1. 将 PPSSaveEditor.apk 传输到手机
        echo   2. 在手机上点击安装
        echo   3. 允许"未知来源"安装
        echo   4. 打开应用开始使用
        echo.
        echo 或使用 ADB 安装：
        echo   adb install PPSSaveEditor.apk
        echo.
    )
) else (
    echo [!] 未在当前目录找到 APK 文件
    echo     可能位置:
    echo       - mobile_app\*.apk
    echo       - mobile_app\bin\*.apk
    echo       - .buildozer\android\platform\build\*
)

echo.
echo 按任意键退出...
pause >nul

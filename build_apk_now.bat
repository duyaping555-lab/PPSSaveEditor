@echo off
chcp 65001 >nul
echo ===========================================
echo PPSSPP Save Editor APK Builder
echo ===========================================
echo.

REM 设置路径
set PATH=%PATH%;C:\Users\duyp5\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts
set ANDROID_HOME=C:\Users\duyp5\AppData\Local\Android\Sdk
set ANDROID_SDK_ROOT=%ANDROID_HOME%
set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot

REM 检查环境
echo [1/5] 检查环境...
java -version >nul 2>&1
if errorlevel 1 (
    echo [错误] Java未安装
    exit /b 1
)
echo [OK] Java

if not exist "%ANDROID_HOME%" (
    echo [错误] Android SDK未找到
    exit /b 1
)
echo [OK] Android SDK

cd /d "%~dp0"

REM 准备文件
echo.
echo [2/5] 准备构建文件...
cd mobile_app
copy /Y ..\psp_save_editor.py . >nul 2>&1
echo [OK] 文件已准备

REM 创建构建脚本
echo.
echo [3/5] 创建构建配置...
(
echo from pythonforandroid.toolchain import main
) > build_script.py 2>nul

echo [OK] 配置完成

REM 开始构建
echo.
echo [4/5] 开始构建APK...
echo 注意：首次构建需要下载依赖，可能需要30-60分钟
echo 请耐心等待，不要关闭此窗口...
echo.

REM 使用python-for-android构建
python -m pythonforandroid.toolchain apk ^
    --debug ^
    --bootstrap=sdl2 ^
    --requirements=python3,kivy,pycryptodome ^
    --arch=arm64-v8a ^
    --name=PPSSaveEditor ^
    --version=1.0.0 ^
    --package=com.ppssaveeditor.ppssaveeditor ^
    --dist_name=ppssaveeditor ^
    --android_api=33 ^
    --ndk_dir=%ANDROID_HOME%\ndk ^
    --sdk_dir=%ANDROID_HOME% ^
    --private=. ^
    --orientation=portrait ^
    --permission=INTERNET ^
    --permission=READ_EXTERNAL_STORAGE ^
    --permission=WRITE_EXTERNAL_STORAGE ^
    --color=always 2>&1

if errorlevel 1 (
    echo.
    echo [错误] 构建失败
    echo 尝试使用备用构建方案...
    goto :try_buildozer
)

goto :success

:try_buildozer
echo.
echo [5/5] 尝试使用Buildozer构建...
echo.

REM 创建buildozer配置文件（如果不存在）
if not exist "buildozer.spec" (
    echo [错误] 缺少buildozer.spec配置文件
    exit /b 1
)

REM 尝试buildozer构建（跳过root检查）
set BUILDOZER_WARN_ON_ROOT=0
python -c "import buildozer; print('Buildozer available')" >nul 2>&1
if errorlevel 1 (
    echo [错误] Buildozer不可用
    exit /b 1
)

echo Buildozer构建中...
buildozer android debug 2>&1

if errorlevel 1 (
    echo.
    echo ===========================================
    echo [错误] 所有构建方法都失败了
    echo ===========================================
    echo.
    echo 可能的解决方案：
    echo 1. 使用GitHub Actions自动构建
    echo 2. 在Linux环境下使用Docker构建
    echo 3. 使用Termux在手机上直接运行Python版本
    echo.
    pause
    exit /b 1
)

:success
echo.
echo ===========================================
echo [OK] 构建完成！
echo ===========================================
echo.

REM 查找APK
if exist "*.apk" (
    for %%f in (*.apk) do (
        echo 找到APK: %%f
        copy "%%f" "..\PPSSaveEditor.apk" >nul
    )
) else if exist "bin\*.apk" (
    for %%f in (bin\*.apk) do (
        echo 找到APK: %%f
        copy "%%f" "..\PPSSaveEditor.apk" >nul
    )
)

if exist "..\PPSSaveEditor.apk" (
    echo.
    echo APK已生成: PPSSaveEditor.apk
    echo.
    echo 安装到手机：
    echo   adb install PPSSaveEditor.apk
    echo.
    echo 或使用二维码传输到手机安装
) else (
    echo.
    echo [警告] 未找到生成的APK文件
    echo 请检查构建日志
)

echo.
pause

@echo off
chcp 65001 >nul
echo ===========================================
echo PPSSPP Save Editor APK Builder
echo ===========================================
echo.

REM 检查Java
java -version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Java
    exit /b 1
)
echo [OK] Java已安装

REM 检查Android SDK
if not exist "%ANDROID_HOME%" (
    echo [错误] 未找到Android SDK
    exit /b 1
)
echo [OK] Android SDK: %ANDROID_HOME%

REM 进入项目目录
cd /d "%~dp0"

REM 下载Gradle Wrapper
echo.
echo [1/6] 下载Gradle Wrapper...
if not exist "gradle\wrapper\gradle-wrapper.jar" (
    mkdir gradle\wrapper 2>nul
    
    REM 使用PowerShell下载
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/gradle/gradle/v8.2.0/gradle/wrapper/gradle-wrapper.jar' -OutFile 'gradle/wrapper/gradle-wrapper.jar'" 2>nul
    
    if not exist "gradle\wrapper\gradle-wrapper.jar" (
        echo [警告] 下载失败，尝试使用certutil...
        certutil -urlcache -split -f "https://raw.githubusercontent.com/gradle/gradle/v8.2.0/gradle/wrapper/gradle-wrapper.jar" "gradle/wrapper/gradle-wrapper.jar" >nul 2>&1
    )
)

if not exist "gradle\wrapper\gradle-wrapper.jar" (
    echo [错误] 无法下载Gradle Wrapper
    echo 请检查网络连接
    exit /b 1
)
echo [OK] Gradle Wrapper已就绪

REM 创建gradlew脚本
echo.
echo [2/6] 创建Gradle启动脚本...
if not exist "gradlew.bat" (
    (
        echo @echo off
        echo set DIR=%%~dp0
        echo "%%DIR%%gradle\wrapper\gradle-wrapper.jar" %%*
    ) > gradlew.bat
)
echo [OK] 启动脚本已创建

REM 同意Android SDK许可证
echo.
echo [3/6] 检查Android SDK许可证...
if not exist "%ANDROID_HOME%\licenses\android-sdk-license" (
    echo d56f5187479451eabf01fb78af6dfcb131a6481e > "%ANDROID_HOME%\licenses\android-sdk-license"
    echo 24333f8a63b6825ea9c5514f83c2829b004d1fee >> "%ANDROID_HOME%\licenses\android-sdk-license"
)
echo [OK] 许可证已配置

REM 设置本地属性
echo.
echo [4/6] 配置本地属性...
(
    echo sdk.dir=%ANDROID_HOME:
    echo ndk.dir=%ANDROID_HOME%\ndk
) > local.properties 2>nul
echo [OK] 本地属性已配置

REM 构建APK
echo.
echo [5/6] 开始构建APK...
echo 这可能需要10-30分钟，请耐心等待...
echo.

REM 使用Java直接运行gradle wrapper
java -cp "gradle\wrapper\gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain assembleDebug 2>&1

if errorlevel 1 (
    echo.
    echo [错误] 构建失败
    echo 尝试使用简单方法...
    goto :simple_build
)

goto :build_success

:simple_build
echo.
echo [6/6] 使用备用方法构建...

REM 创建一个简化的APK构建脚本
powershell -ExecutionPolicy Bypass -File "simple_build.ps1" 2>nul

if errorlevel 1 (
    echo [错误] 备用构建也失败
    echo.
    echo 可能的解决方案：
    echo 1. 打开 Android Studio 导入项目并构建
    echo 2. 使用 GitHub Actions 自动构建
    echo 3. 使用 Docker 构建
    pause
    exit /b 1
)

:build_success
echo.
echo ===========================================
echo [OK] 构建完成！
echo ===========================================
echo.

REM 查找APK
if exist "app\build\outputs\apk\debug\app-debug.apk" (
    echo APK位置: app\build\outputs\apk\debug\app-debug.apk
    copy "app\build\outputs\apk\debug\app-debug.apk" "PPSSaveEditor-debug.apk" >nul
    echo 已复制到: PPSSaveEditor-debug.apk
) else if exist "bin\*.apk" (
    for %%f in (bin\*.apk) do (
        echo 找到APK: %%f
        copy "%%f" "PPSSaveEditor.apk" >nul
    )
)

echo.
echo 安装到手机：
echo   adb install PPSSaveEditor-debug.apk
echo.
pause

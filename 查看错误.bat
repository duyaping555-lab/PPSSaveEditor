@echo off
chcp 65001 >nul
echo ===========================================
echo 查看构建错误日志
echo ===========================================
echo.

cd /d "%~dp0mobile_app"

echo [1/3] 检查 Python-for-Android 日志...
if exist ".buildozer\android\platform\build\build.log" (
    echo [发现] build.log 文件
    echo.
    echo 最近的错误信息：
    echo ----------------------------------------
    type .buildozer\android\platform\build\build.log | findstr /i "error fail" | tail -20
    echo ----------------------------------------
) else (
    echo [未找到] build.log
)

echo.
echo [2/3] 检查 buildozer 日志...
if exist ".buildozer\logs" (
    dir /b .buildozer\logs\*.log 2>nul
)

echo.
echo [3/3] 检查 NDK/SDK 配置...
echo ANDROID_HOME=%ANDROID_HOME%
echo JAVA_HOME=%JAVA_HOME%

echo.
echo ===========================================
echo 常见错误：
echo 1. 缺少 NDK - 下载地址：https://developer.android.com/ndk/downloads
echo 2. 内存不足 - 关闭其他程序重试
echo 3. 网络超时 - 检查网络或使用代理
echo ===========================================
pause

@echo off
chcp 65001 >nul
echo ===========================================
echo PPSSPP Save Editor - Docker Build
echo ===========================================
echo.

REM 检查Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Docker
    echo 请安装Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker已安装

REM 复制核心文件到mobile_app
echo.
echo [1/4] 准备文件...
copy /Y psp_save_editor.py mobile_app\ >nul 2>&1
echo [OK] 文件已复制

REM 创建构建脚本
echo.
echo [2/4] 创建Docker构建脚本...
(
echo #!/bin/bash
echo cd /home/user/hostcwd/mobile_app
echo pip install -q buildozer
echo buildozer android debug
) > mobile_app\docker_build.sh

echo [OK] 构建脚本已创建

REM 运行Docker构建
echo.
echo [3/4] 启动Docker构建...
echo 注意: 首次运行会下载约2GB的镜像，请耐心等待
echo.

docker run --rm -v "%CD%":/home/user/hostcwd kivy/buildozer:latest bash /home/user/hostcwd/mobile_app/docker_build.sh

if errorlevel 1 (
    echo.
    echo [错误] 构建失败
    echo 尝试使用旧版本镜像...
    
    docker run --rm -v "%CD%":/home/user/hostcwd kivy/buildozer:stable bash /home/user/hostcwd/mobile_app/docker_build.sh
    
    if errorlevel 1 (
        echo.
        echo [错误] 构建仍然失败
        pause
        exit /b 1
    )
)

echo.
echo [4/4] 构建完成!
echo.

REM 查找生成的APK
if exist "mobile_app\bin\*.apk" (
    echo [OK] APK文件已生成:
    dir /b mobile_app\bin\*.apk
    
    REM 复制到上级目录
    copy mobile_app\bin\*.apk .\PPSSaveEditor.apk >nul 2>&1
    echo.
    echo APK已复制到: PPSSaveEditor.apk
) else (
    echo [警告] 未找到APK文件，可能构建失败
)

echo.
echo ===========================================
pause

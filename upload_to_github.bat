@echo off
chcp 65001 >nul
echo ===========================================
echo PPSSaveEditor - GitHub 上传脚本
echo ===========================================
echo.
echo 此脚本将帮助你将代码上传到GitHub并自动构建APK
echo.

REM 检查git
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Git，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [OK] Git已安装

REM 检查是否有git仓库
if not exist .git (
    echo.
    echo [1/5] 初始化Git仓库...
    git init
    git config user.email "user@example.com"
    git config user.name "PPSSaveEditor User"
) else (
    echo [1/5] Git仓库已存在
)

REM 添加文件
echo.
echo [2/5] 添加文件到Git...
git add .
git commit -m "Initial commit for PPSSaveEditor" >nul 2>&1
if errorlevel 1 (
    echo [信息] 没有新文件需要提交
) else (
    echo [OK] 文件已提交
)

REM 提示用户创建GitHub仓库
echo.
echo [3/5] GitHub仓库设置
echo.
echo 请按以下步骤操作：
echo 1. 访问 https://github.com/new
echo 2. 填写仓库名称: PPSSaveEditor
echo 3. 选择 Public 或 Private
echo 4. 点击 "Create repository"
echo.
echo 创建完成后，输入你的GitHub用户名：
set /p USERNAME="GitHub用户名: "

echo.
echo 输入仓库名称（默认PPSSaveEditor）：
set /p REPO="仓库名称: "
if "%REPO%"=="" set REPO=PPSSaveEditor

REM 添加远程仓库
echo.
echo [4/5] 设置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/%USERNAME%/%REPO%.git
echo [OK] 远程仓库已设置

REM 推送代码
echo.
echo [5/5] 推送代码到GitHub...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败
    echo 可能原因：
    echo - 仓库不存在（请先创建）
    echo - 没有权限（请检查用户名）
    echo - 需要登录（会提示输入用户名密码或token）
    echo.
    echo 手动推送命令：
    echo git remote add origin https://github.com/%USERNAME%/%REPO%.git
    echo git push -u origin main
    pause
    exit /b 1
)

echo.
echo ===========================================
echo [OK] 上传成功！
echo ===========================================
echo.
echo 下一步：
echo 1. 访问 https://github.com/%USERNAME%/%REPO%/actions
echo 2. 等待构建完成（约15-30分钟）
echo 3. 下载APK文件
echo.
echo 构建完成后，你会在 Actions 页面看到绿色的勾
echo 点击进去可以下载 APK 文件
echo.
pause

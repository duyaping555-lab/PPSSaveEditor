#!/usr/bin/env python3
"""
PPSSPP 存档编辑器 APK 构建脚本
使用 Buildozer 构建 Android APK
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path


def check_buildozer():
    """检查是否安装了 buildozer"""
    if shutil.which('buildozer'):
        return True
    print("Buildozer 未安装")
    print("安装命令: pip install buildozer")
    return False


def build_apk(debug=True):
    """构建 APK"""
    mobile_app_dir = Path(__file__).parent / 'mobile_app'
    
    if not mobile_app_dir.exists():
        print(f"错误: 找不到目录 {mobile_app_dir}")
        return False
    
    os.chdir(mobile_app_dir)
    
    cmd = ['buildozer', 'android', 'debug' if debug else 'release']
    
    print(f"运行: {' '.join(cmd)}")
    print("这可能需要 10-30 分钟，请耐心等待...")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n构建失败: {e}")
        return False


def deploy_apk():
    """部署 APK 到连接的设备"""
    mobile_app_dir = Path(__file__).parent / 'mobile_app'
    os.chdir(mobile_app_dir)
    
    cmd = ['buildozer', 'android', 'debug', 'deploy', 'run']
    
    print(f"运行: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n部署成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n部署失败: {e}")
        return False


def clean_build():
    """清理构建文件"""
    mobile_app_dir = Path(__file__).parent / 'mobile_app'
    os.chdir(mobile_app_dir)
    
    cmd = ['buildozer', 'android', 'clean']
    
    print(f"运行: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n清理成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n清理失败: {e}")
        return False


def create_github_actions_workflow():
    """创建 GitHub Actions 工作流文件"""
    workflow_dir = Path(__file__).parent / '.github' / 'workflows'
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = '''name: Build Android APK

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install buildozer cython
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          git \
          zip \
          unzip \
          openjdk-17-jdk \
          python3-pip \
          autoconf \
          libtool \
          pkg-config \
          zlib1g-dev \
          libncurses5-dev \
          libncursesw5-dev \
          libtinfo5 \
          cmake \
          libffi-dev \
          libssl-dev \
          automake
    
    - name: Build APK
      run: |
        cd mobile_app
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: ppsspp-save-editor-apk
        path: mobile_app/bin/*.apk
'''
    
    workflow_file = workflow_dir / 'build.yml'
    with open(workflow_file, 'w') as f:
        f.write(workflow_content)
    
    print(f"GitHub Actions 工作流已创建: {workflow_file}")
    return True


def setup_android_sdk():
    """设置 Android SDK 指南"""
    print("""
Android SDK 设置指南:

方法 1: 使用 Android Studio
1. 下载并安装 Android Studio: https://developer.android.com/studio
2. 打开 Android Studio，安装 SDK
3. 设置环境变量:
   export ANDROID_HOME=$HOME/Android/Sdk
   export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

方法 2: 使用命令行工具
1. 下载命令行工具: https://developer.android.com/studio#command-tools
2. 解压到 ~/android-sdk
3. 安装所需组件:
   sdkmanager "platforms;android-33"
   sdkmanager "build-tools;33.0.0"
   sdkmanager "ndk;25.2.9519653"

方法 3: 使用 Docker (最简单)
   docker run --rm -v "$(pwd)":/home/user/hostcwd kivy/buildozer android debug
""")


def main():
    parser = argparse.ArgumentParser(description='PPSSPP Save Editor APK Builder')
    parser.add_argument('action', choices=['build', 'deploy', 'clean', 'setup', 'workflow'],
                       help='Action to perform')
    parser.add_argument('--release', action='store_true',
                       help='Build release version (default: debug)')
    
    args = parser.parse_args()
    
    if args.action == 'build':
        if not check_buildozer():
            setup_android_sdk()
            return 1
        success = build_apk(debug=not args.release)
        return 0 if success else 1
    
    elif args.action == 'deploy':
        if not check_buildozer():
            return 1
        success = deploy_apk()
        return 0 if success else 1
    
    elif args.action == 'clean':
        if not check_buildozer():
            return 1
        success = clean_build()
        return 0 if success else 1
    
    elif args.action == 'setup':
        setup_android_sdk()
        return 0
    
    elif args.action == 'workflow':
        create_github_actions_workflow()
        return 0
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
使用 python-for-android 构建 APK
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_cmd(cmd, cwd=None):
    """运行命令"""
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=False)
    return result.returncode == 0


def check_requirements():
    """检查依赖"""
    print("=" * 60)
    print("检查构建环境")
    print("=" * 60)
    
    # 检查Python
    if not shutil.which('python'):
        print("[错误] 未找到Python")
        return False
    
    # 检查pip
    if not shutil.which('pip'):
        print("[错误] 未找到pip")
        return False
    
    # 检查Android SDK
    android_home = os.environ.get('ANDROID_HOME')
    if not android_home:
        # 尝试常见路径
        possible_paths = [
            os.path.expandvars(r'%LOCALAPPDATA%\Android\Sdk'),
            os.path.expandvars(r'%USERPROFILE%\AppData\Local\Android\Sdk'),
            r'C:\Android\Sdk',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                android_home = path
                os.environ['ANDROID_HOME'] = path
                break
    
    if not android_home or not os.path.exists(android_home):
        print("[错误] 未找到Android SDK")
        print("请安装Android Studio或设置ANDROID_HOME环境变量")
        return False
    
    print(f"[OK] Android SDK: {android_home}")
    
    # 检查Java
    if not shutil.which('java'):
        print("[警告] 未找到Java，尝试查找...")
        # 尝试在Android Studio目录中查找
        possible_java = [
            os.path.join(android_home, 'jbr', 'bin', 'java.exe'),
            os.path.join(android_home, '..', 'jbr', 'bin', 'java.exe'),
        ]
        for java_path in possible_java:
            if os.path.exists(java_path):
                java_home = os.path.dirname(os.path.dirname(java_path))
                os.environ['JAVA_HOME'] = java_home
                os.environ['PATH'] = os.path.join(java_home, 'bin') + os.pathsep + os.environ.get('PATH', '')
                print(f"[OK] Java: {java_path}")
                break
        else:
            print("[错误] 未找到Java")
            return False
    
    return True


def install_p4a():
    """安装python-for-android"""
    print("\n" + "=" * 60)
    print("安装 python-for-android")
    print("=" * 60)
    
    # 安装依赖
    packages = [
        'python-for-android',
        'Cython',
        'kivy',
        'pycryptodome',
    ]
    
    for pkg in packages:
        print(f"\n安装 {pkg}...")
        if not run_cmd([sys.executable, '-m', 'pip', 'install', '-q', pkg]):
            print(f"[警告] {pkg} 安装可能失败")
    
    return True


def prepare_source():
    """准备源代码"""
    print("\n" + "=" * 60)
    print("准备源代码")
    print("=" * 60)
    
    mobile_app_dir = Path(__file__).parent / 'mobile_app'
    
    if not mobile_app_dir.exists():
        print(f"[错误] 找不到目录: {mobile_app_dir}")
        return False
    
    # 复制核心文件
    src_file = Path(__file__).parent / 'psp_save_editor.py'
    dst_file = mobile_app_dir / 'psp_save_editor.py'
    
    if src_file.exists():
        shutil.copy2(src_file, dst_file)
        print(f"[OK] 复制: {src_file} -> {dst_file}")
    else:
        print(f"[警告] 找不到: {src_file}")
    
    return mobile_app_dir


def build_apk(source_dir):
    """构建APK"""
    print("\n" + "=" * 60)
    print("开始构建APK")
    print("=" * 60)
    
    android_sdk = os.environ.get('ANDROID_HOME', '')
    
    # 构建命令
    cmd = [
        sys.executable, '-m', 'pythonforandroid.toolchain',
        'apk',
        '--debug',
        '--bootstrap=sdl2',
        '--requirements=python3,kivy,pycryptodome',
        '--arch=arm64-v8a',
        '--name=PPSSaveEditor',
        '--version=1.0.0',
        '--package=com.ppssaveeditor.ppssaveeditor',
        '--dist_name=ppssaveeditor',
        f'--android_api=33',
        f'--ndk_dir={os.path.join(android_sdk, "ndk")}',
        f'--sdk_dir={android_sdk}',
        f'--private={source_dir}',
        '--orientation=portrait',
        '--icon={}'.format(os.path.join(source_dir, 'icon.png') if os.path.exists(os.path.join(source_dir, 'icon.png')) else ''),
        '--permission=INTERNET',
        '--permission=READ_EXTERNAL_STORAGE',
        '--permission=WRITE_EXTERNAL_STORAGE',
    ]
    
    # 过滤空参数
    cmd = [c for c in cmd if c]
    
    print("\n构建命令:")
    print(' '.join(cmd))
    print("\n开始构建，这可能需要30-60分钟...")
    
    if run_cmd(cmd):
        print("\n[OK] 构建成功!")
        return True
    else:
        print("\n[错误] 构建失败")
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         PPSSPP Save Editor APK Builder                   ║
║         使用 python-for-android                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 检查环境
    if not check_requirements():
        print("\n环境检查失败，请安装Android SDK和Java")
        input("按回车键退出...")
        return 1
    
    # 安装p4a
    if not install_p4a():
        print("\n依赖安装失败")
        return 1
    
    # 准备源代码
    source_dir = prepare_source()
    if not source_dir:
        return 1
    
    # 构建APK
    if build_apk(str(source_dir)):
        print("\n" + "=" * 60)
        print("构建完成!")
        print("APK应该位于当前目录或dist/目录中")
        print("=" * 60)
    else:
        print("\n构建失败，请检查错误信息")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

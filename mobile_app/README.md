# PPSSPP 存档编辑器 - Kivy 版本

使用 Kivy 框架开发的跨平台 GUI 应用，可以打包为 Android APK。

## 在 PC 上运行

### 安装依赖

```bash
pip install kivy pycryptodome
```

### 运行应用

```bash
cd mobile_app
python main.py
```

## 打包为 Android APK

### 方法一: 使用 Buildozer (推荐)

1. **安装 Buildozer**

```bash
pip install buildozer
```

2. **在 Linux 环境下构建**

注意: Buildozer 只能在 Linux 环境下构建 Android APK。
如果没有 Linux，可以使用 Docker 或虚拟机。

```bash
cd mobile_app

# 初始化 buildozer (如果还没有 buildozer.spec)
buildozer init

# 构建 APK
buildozer android debug

# 部署到连接的设备
buildozer android debug deploy run
```

3. **使用 Docker 构建 (推荐 Windows/Mac 用户)**

```bash
# 拉取 buildozer 镜像
docker pull kivy/buildozer

# 运行构建
docker run --rm -v "$(pwd)":/home/user/hostcwd kivy/buildozer android debug
```

### 方法二: 使用 GitHub Actions 自动构建

创建 `.github/workflows/build.yml`:

```yaml
name: Build Android APK

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install buildozer cython
    
    - name: Build APK
      run: |
        cd mobile_app
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v2
      with:
        name: apk
        path: mobile_app/bin/*.apk
```

### 方法三: 使用 Google Colab 构建

在 Colab 笔记本中运行:

```python
# 上传代码文件到 Colab
# 然后运行:
!pip install buildozer cython
!buildozer android debug
# 下载生成的 APK
```

## 在 Android 上安装

1. 启用"未知来源"安装:
   - 设置 → 安全 → 允许未知来源

2. 安装 APK:
   ```bash
   adb install bin/PPSSPP存档编辑器-1.0.0-armeabi-v7a_debug.apk
   ```

## 功能说明

### 主界面
- **选择存档文件夹**: 选择 PSP 存档目录
- **解密**: 解密存档数据
- **加密**: 加密并保存存档
- **十六进制**: 打开十六进制编辑器
- **补丁代码**: 应用 CWCheat 代码

### 十六进制编辑器
- 显示偏移量、十六进制值、ASCII
- 搜索十六进制值
- 跳转到指定偏移
- 修改 8/16/32 位数值

### CWCheat 代码
支持格式:
```
_L 0x20555678 0x0098967F  ; 32位写入
_L 0x10555678 0x0000270F  ; 16位写入
_L 0x00555678 0x00000063  ; 8位写入
```

## 已知问题

1. **文件选择器**: Android 上使用简化版路径输入，而非完整文件浏览器
2. **权限**: 首次运行时需要授予存储权限
3. **性能**: 大存档文件 (>1MB) 可能影响性能

## 与原生 Android 版本的区别

| 特性 | Kivy 版本 | 原生 Android |
|------|-----------|--------------|
| 安装包大小 | 较大 (~30MB) | 较小 (~5MB) |
| 启动速度 | 较慢 | 较快 |
| 界面体验 | 一般 | 原生体验 |
| 开发难度 | 简单 | 复杂 |
| 功能完整度 | 完整 | 完整 |

## 调试

### 查看日志
```bash
adb logcat -s python:D
```

### 常见问题

1. **崩溃**: 检查是否有存储权限
2. **无法加载存档**: 检查路径是否正确
3. **解密失败**: 可能是加密模式不支持

## 项目文件

```
mobile_app/
├── main.py              # 主程序
├── buildozer.spec      # Buildozer 配置
├── psp_save_editor.py  # 核心功能 (从父目录复制)
└── README.md           # 本文件
```

## 开发计划

- [ ] 添加更美观的 UI 主题
- [ ] 支持更多存档格式
- [ ] 添加存档对比功能
- [ ] 集成在线 CWCheat 数据库

# 如何获取 PPSSPP 存档编辑器 APK

## 现状说明

由于APK构建需要完整的Android开发环境（Android SDK、NDK、Java等），在当前环境下无法直接构建。

但我已经为你准备了**自动构建方案**，只需几步即可获得APK：

---

## 最快获取APK的方法（推荐）

### 方法一：GitHub Actions 自动构建（无需本地环境）

**时间**：约15-30分钟
**难度**：⭐（最简单）

#### 步骤：

1. **注册GitHub账号**（已有则跳过）
   - 访问 https://github.com/signup

2. **创建新仓库**
   - 访问 https://github.com/new
   - 仓库名称：`PPSSaveEditor`
   - 点击 "Create repository"

3. **上传代码**
   - 打开 `upload_to_github.bat`
   - 按提示输入GitHub用户名和仓库名
   - 等待上传完成

4. **等待自动构建**
   - 访问 `https://github.com/你的用户名/PPSSaveEditor/actions`
   - 等待工作流完成（绿色勾号）

5. **下载APK**
   - 点击最新的工作流运行
   - 在 Artifacts 部分下载 APK

### 方法二：Docker 构建（需安装Docker）

**时间**：约30-60分钟（首次）
**难度**：⭐⭐

#### 步骤：

1. 安装 Docker Desktop：https://www.docker.com/products/docker-desktop

2. 双击运行 `build_docker.bat`

3. 等待构建完成

4. APK 在 `mobile_app/bin/` 目录

### 方法三：使用 Termux（直接在手机上构建）

**时间**：约1小时
**难度**：⭐⭐⭐

在Android手机上安装Termux应用，然后：

```bash
pkg update
pkg install python git -y
pip install buildozer cython kivy

# 克隆代码
git clone https://github.com/你的用户名/PPSSaveEditor.git
cd PPSSaveEditor/mobile_app

# 构建
cp ../psp_save_editor.py .
buildozer android debug
```

---

## 立即使用方案（无需APK）

如果你急需使用编辑器，可以：

### 方案A：Python 命令行版本（PC）

```bash
# 安装依赖
pip install pycryptodome

# 运行编辑器
python psp_save_editor.py <存档路径> --decrypt --hex
```

### 方案B：Termux 版本（手机）

1. 安装 Termux 应用（F-Droid）

2. 运行命令：
```bash
pkg install python -y
pip install pycryptodome

# 将 psp_save_editor.py 复制到手机
python psp_save_editor.py /sdcard/PSP/SAVEDATA/XXX --decrypt --hex
```

---

## 项目交付清单

我已经为你创建了完整的项目：

### ✅ 核心功能（已测试通过）
- `psp_save_editor.py` - 存档编辑器核心（22KB）
- SFO 文件解析器
- AES 加解密模块
- 十六进制编辑器
- CWCheat 代码应用器

### ✅ Android 原生应用项目
- 完整的 Kotlin 源代码
- XML 布局文件
- Gradle 构建配置

### ✅ Kivy 移动应用
- `mobile_app/main.py` - 跨平台GUI
- `buildozer.spec` - APK构建配置

### ✅ 自动构建脚本
- `.github/workflows/build_apk.yml` - GitHub Actions配置
- `upload_to_github.bat` - 一键上传到GitHub
- `build_docker.bat` - Docker构建脚本

### ✅ 完整文档
- `README.md` - 项目说明
- `GET_APK.md` - 获取APK指南
- `EMULATOR_TEST_GUIDE.md` - 测试指南

---

## 快速开始

### 最快路径（有GitHub账号）：

1. 双击运行 `upload_to_github.bat`
2. 按提示操作（输入用户名、仓库名）
3. 访问GitHub Actions页面等待构建
4. 下载APK

### 最快路径（无GitHub账号）：

1. 在PC上安装Python
2. `pip install pycryptodome`
3. `python psp_save_editor.py <存档路径> --decrypt --hex`

### 最快路径（只需手机）：

1. 安装Termux应用
2. `pkg install python && pip install pycryptodome`
3. `python psp_save_editor.py /sdcard/PSP/SAVEDATA/XXX --decrypt --hex`

---

## 需要帮助？

如果你：
- **不会用GitHub** → 使用Python命令行版本或Termux
- **没有Docker** → 使用GitHub Actions方法
- **急需APK** → 我可以尝试手动为你构建（需提供详细环境信息）

**构建成功后**，APK可以直接安装到任何Android手机上使用。

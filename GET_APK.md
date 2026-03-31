# 获取 PPSSPP 存档编辑器 APK

## 方法 1: GitHub Actions 自动构建（最简单，推荐）

### 步骤 1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库，名称如 `PPSSaveEditor`
3. 选择 "Public" 或 "Private"

### 步骤 2: 上传代码

```bash
# 在项目目录中
cd dev/PPSSaveEditor

# 初始化git仓库
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/PPSSaveEditor.git

# 推送代码
git push -u origin main
```

或者直接拖拽文件到GitHub网页上传。

### 步骤 3: 等待自动构建

1. 推送代码后，GitHub Actions 会自动开始构建
2. 访问你仓库的 "Actions" 标签页查看进度
3. 构建通常需要 15-30 分钟

### 步骤 4: 下载 APK

构建完成后：
1. 进入 "Actions" 标签页
2. 点击最新的工作流运行
3. 在 "Artifacts" 部分下载 APK 文件
4. 或者如果创建了Release，在Release页面下载

### 步骤 5: 安装到手机

1. 将下载的 APK 传输到手机
2. 在手机上允许"安装未知来源应用"
3. 点击 APK 安装

---

## 方法 2: 使用 Docker（如果你安装了Docker）

### Windows

1. 安装 Docker Desktop: https://www.docker.com/products/docker-desktop

2. 双击运行 `build_docker.bat`

3. 等待构建完成（首次约30-60分钟）

4. APK 将生成在 `mobile_app/bin/` 目录

### Linux/Mac

```bash
cd dev/PPSSaveEditor

# 运行构建
docker run --rm -v "$(pwd)":/home/user/hostcwd \
  kivy/buildozer:latest \
  bash -c "cd /home/user/hostcwd/mobile_app && buildozer android debug"

# APK 将在 mobile_app/bin/ 目录
```

---

## 方法 3: 本地构建（如果你有Android开发环境）

### 前提条件

- Python 3.7+
- Android SDK
- Java JDK 17
- 约 10GB 磁盘空间

### 步骤

1. **安装依赖**
   ```bash
   pip install buildozer cython kivy
   ```

2. **设置环境变量**
   ```bash
   # Windows
   set ANDROID_HOME=C:\Users\%USERNAME%\AppData\Local\Android\Sdk
   set JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
   
   # 添加到 PATH
   set PATH=%PATH%;%ANDROID_HOME%\tools;%ANDROID_HOME%\platform-tools
   ```

3. **构建APK**
   ```bash
   cd dev/PPSSaveEditor/mobile_app
   
   # 复制核心文件
   cp ../psp_save_editor.py .
   
   # 开始构建
   buildozer android debug
   ```

4. **获取APK**
   - APK 位于 `mobile_app/bin/` 目录
   - 文件名类似：`PPSSPP存档编辑器-1.0.0-arm64-v8a_debug.apk`

---

## 方法 4: 使用 Android Studio

1. 打开 Android Studio
2. 选择 "Open an existing project"
3. 选择 `dev/PPSSaveEditor` 文件夹
4. 等待 Gradle 同步
5. 点击菜单 "Build" → "Build Bundle(s) / APK(s)" → "Build APK(s)"
6. APK 位于 `app/build/outputs/apk/debug/app-debug.apk`

---

## 安装后使用

### 授予权限

首次打开应用时，请授予**存储权限**，否则无法读取存档文件。

### 使用步骤

1. **从PPSSPP导出存档**
   - 在PPSSPP中: 设置 → 工具 → 保存数据备份
   - 或从 `Android/data/org.ppsspp.ppsspp/files/PSP/SAVEDATA/` 复制

2. **使用编辑器**
   - 打开应用，选择存档文件夹
   - 解密（如果需要）
   - 使用十六进制编辑器或CWCheat代码修改
   - 加密并保存

3. **导回PPSSPP**
   - 将修改后的存档复制回原位置
   - 在PPSSPP中加载

---

## 常见问题

### Q: GitHub Actions构建失败？

A: 检查以下几点：
- 确保所有文件都已正确上传
- 检查Actions日志中的错误信息
- 可能需要重试（网络问题）

### Q: APK安装失败？

A: 
- 确保允许"未知来源"安装
- 检查APK是否完整下载
- 尝试其他构建版本（armeabi-v7a或x86）

### Q: 应用闪退？

A:
- 确保授予存储权限
- 检查存档路径是否正确
- 查看是否有错误日志

---

## 快速开始（推荐）

最快的获取APK方式：

1. **Fork 我的仓库**（如果我在GitHub上发布了）
2. **或创建自己的仓库并上传代码**
3. **等待自动构建完成**
4. **下载并使用APK**

如果你急需APK，也可以：
- 使用Termux直接在手机上运行Python版本
- 或先用PC上的Python版本

---

**需要帮助？**
- 查看 `EMULATOR_TEST_GUIDE.md` 获取测试指南
- 查看 `README.md` 获取使用说明

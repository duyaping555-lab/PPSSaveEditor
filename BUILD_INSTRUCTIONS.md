# 构建说明

## Android 应用构建

### 方法 1: 使用 Android Studio（推荐）

1. 下载并安装 [Android Studio](https://developer.android.com/studio)

2. 打开项目:
   ```
   File → Open → 选择 dev/PPSSaveEditor 文件夹
   ```

3. 等待 Gradle 同步完成

4. 构建 APK:
   ```
   Build → Build Bundle(s) / APK(s) → Build APK(s)
   ```

5. APK 文件将生成在:
   ```
   app/build/outputs/apk/debug/app-debug.apk
   ```

6. 安装到手机:
   - 通过 USB 连接手机
   - 启用开发者选项和 USB 调试
   - 点击 "Run" 按钮，或手动安装 APK

### 方法 2: 使用命令行

1. 确保已安装:
   - Android SDK
   - 设置 ANDROID_HOME 环境变量

2. 下载 Gradle Wrapper:
   ```
   gradle wrapper
   ```

3. 构建 APK:
   ```
   ./gradlew assembleDebug    (Linux/Mac)
   gradlew.bat assembleDebug  (Windows)
   ```

4. 安装到连接的设备:
   ```
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```

## Python 脚本使用

### 在 PC 上

1. 安装 Python 3.7+

2. 安装依赖:
   ```bash
   pip install pycryptodome
   ```

3. 运行脚本:
   ```bash
   python psp_save_editor.py <存档文件夹路径>
   ```

### 在 Android (Termux) 上

1. 安装 Termux 应用 (从 F-Droid 下载)

2. 安装必要软件:
   ```bash
   pkg update
   pkg install python
   pip install pycryptodome
   ```

3. 复制脚本到手机:
   ```bash
   # 方法 1: 直接下载
   curl -O <脚本URL>
   
   # 方法 2: 通过文件管理器复制到 /sdcard/Download/
   cp /sdcard/Download/psp_save_editor.py ~/
   ```

4. 运行脚本:
   ```bash
   python psp_save_editor.py /sdcard/PSP/SAVEDATA/<游戏ID> --decrypt --hex
   ```

## 常见问题

### Android 构建问题

**Q: Gradle 同步失败**
A: 检查:
- Android SDK 版本是否兼容
- 网络连接（需要下载依赖）
- Gradle 版本（项目使用 8.2）

**Q: 找不到 SDK**
A: 设置 ANDROID_HOME 环境变量:
```
Windows: set ANDROID_HOME=C:\Users\<用户名>\AppData\Local\Android\Sdk
Linux/Mac: export ANDROID_HOME=$HOME/Android/Sdk
```

### Python 脚本问题

**Q: 导入错误 pycryptodome**
A: 安装依赖:
```bash
pip install pycryptodome
```

**Q: 权限错误 (Android)**
A: 在 Termux 中运行:
```bash
termux-setup-storage
```

## 项目文件清单

### Android 项目
```
PPSSaveEditor/
├── build.gradle
├── settings.gradle
├── gradle/wrapper/gradle-wrapper.properties
├── app/
│   ├── build.gradle
│   ├── proguard-rules.pro
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/ppssaveeditor/*.kt (8个Kotlin文件)
│       └── res/layout/*.xml (5个布局文件)
│       └── res/values/*.xml (3个资源文件)
```

### Python 项目
```
psp_save_editor.py          # 主脚本
psp_save_editor_README.md   # 使用说明
requirements.txt            # 依赖列表
example_cheat_codes.txt     # 示例代码
```

## 调试技巧

### Android
- 使用 Logcat 查看日志
- 在 Android Studio 中设置断点
- 使用 "Debug" 模式运行

### Python
- 添加 `-v` 参数启用详细输出
- 使用 `print()` 调试
- 捕获异常查看错误详情

# Android Studio 构建指南

## 步骤 1: 打开项目
1. 打开 Android Studio
2. 选择 "Open an existing project"
3. 选择 `C:\Users\duyp5\dev\PPSSaveEditor` 文件夹
4. 等待 Gradle 同步完成

## 步骤 2: 修复代码问题（如果构建失败）

### 问题 1: DocumentFile 无法解析
如果看到 `Unresolved reference: DocumentFile` 错误：

**解决方案 A - 使用完全限定名：**
打开 `app/src/main/java/com/ppssaveeditor/MainActivity.kt`

将第 20 行:
```kotlin
import androidx.documentfile.DocumentFile
```

改为在第 127、165、177 行使用完全限定名:
```kotlin
val docFile = androidx.documentfile.DocumentFile.fromTreeUri(this@MainActivity, uri)
```

**解决方案 B - 清理并重建：**
1. 菜单栏选择 `Build > Clean Project`
2. 菜单栏选择 `File > Invalidate Caches / Restart`
3. 选择 `Invalidate and Restart`
4. 重启后等待 Gradle 同步
5. 菜单栏选择 `Build > Rebuild Project`

### 问题 2: 整数字面量溢出
打开 `app/src/main/java/com/ppssaveeditor/SFOParser.kt`

将第 142 和 153 行:
```kotlin
keyTableSize = (keyTableSize + 3) and 0xFFFFFFFC
dataTableSize = (dataTableSize + 3) and 0xFFFFFFFC
```

改为:
```kotlin
keyTableSize = (keyTableSize + 3) and 0x7FFFFFFC
dataTableSize = (dataTableSize + 3) and 0x7FFFFFFC
```

### 问题 3: HexEditorActivity 变量冲突
打开 `app/src/main/java/com/ppssaveeditor/HexEditorActivity.kt`

将第 141-143 行:
```kotlin
val adapter = android.widget.ArrayAdapter(this, android.R.layout.simple_spinner_item, types)
adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
spinnerType.adapter = adapter
```

改为:
```kotlin
val typeAdapter = android.widget.ArrayAdapter(this, android.R.layout.simple_spinner_item, types)
typeAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
spinnerType.adapter = typeAdapter
```

## 步骤 3: 构建 APK
1. 菜单栏选择 `Build > Build Bundle(s) / APK(s) > Build APK(s)`
2. 等待构建完成
3. 构建成功后，点击右下角的弹窗链接 `locate`
4. APK 文件位置：`app/build/outputs/apk/debug/app-debug.apk`

## 步骤 4: 安装到手机
1. 将 APK 文件传输到手机
2. 在手机上允许"安装未知来源应用"
3. 点击 APK 安装

## 备用方案: 使用命令行构建
如果 Android Studio 构建失败，可以使用命令行:

```bash
cd C:\Users\duyp5\dev\PPSSaveEditor
.\gradlew.bat clean
.\gradlew.bat assembleDebug
```

APK 将生成在 `app/build/outputs/apk/debug/app-debug.apk`

# PPSSPP 存档编辑器 - 项目总结

## 项目完成情况

我已经为你创建了一个完整的 **PPSSPP 存档编辑器** 项目，包含以下组件：

### 1. 核心功能模块 (Python)
- ✅ **SFO 解析器** - 读取/写入 PARAM.SFO 文件
- ✅ **加密模块** - 支持 PSP 存档 AES 加解密
- ✅ **十六进制编辑器** - 可视化编辑存档数据
- ✅ **CWCheat 应用器** - 应用标准补丁代码

### 2. 用户界面实现
- ✅ **Android 原生应用** - 完整的 Kotlin + XML 项目
- ✅ **Kivy 跨平台应用** - 可打包为 Android APK
- ✅ **命令行工具** - 支持 Windows/Mac/Linux/Android

### 3. 测试和文档
- ✅ **自动化测试** - 验证所有核心功能
- ✅ **构建脚本** - 简化 APK 构建流程
- ✅ **使用文档** - 详细的操作指南

## 项目文件清单

```
dev/PPSSaveEditor/
├── 📱 Android Native App
│   ├── app/src/main/java/com/ppssaveeditor/
│   │   ├── MainActivity.kt
│   │   ├── HexEditorActivity.kt
│   │   ├── CheatCodeActivity.kt
│   │   ├── SFOParser.kt
│   │   ├── SaveDataCrypto.kt
│   │   ├── CheatCodeApplier.kt
│   │   └── HexEditorAdapter.kt
│   ├── app/src/main/res/layout/
│   │   ├── activity_main.xml
│   │   ├── activity_hex_editor.xml
│   │   ├── activity_cheat_code.xml
│   │   ├── item_hex_row.xml
│   │   └── dialog_modify_value.xml
│   └── build.gradle
│
├── 🐍 Python Version
│   ├── psp_save_editor.py (22KB)
│   ├── test_editor.py
│   ├── requirements.txt
│   └── psp_save_editor_README.md
│
├── 📦 Kivy Mobile App
│   ├── mobile_app/
│   │   ├── main.py (Kivy GUI)
│   │   ├── buildozer.spec (APK config)
│   │   └── README.md
│   └── build_apk.py (Build script)
│
└── 📚 Documentation
    ├── README.md
    ├── BUILD_INSTRUCTIONS.md
    ├── EMULATOR_TEST_GUIDE.md
    ├── PROJECT_SUMMARY.md
    └── FINAL_SUMMARY.md (this file)
```

## 使用方法

### 方式一: Python 命令行（立即可用）

```bash
# 安装依赖
pip install pycryptodome

# 使用编辑器
cd dev/PPSSaveEditor
python psp_save_editor.py /path/to/save_folder --decrypt --hex
```

### 方式二: Android 应用（需构建）

#### 选项 A: 使用 Buildozer (推荐)

```bash
# 安装 buildozer
pip install buildozer

# 构建 APK
cd mobile_app
buildozer android debug

# 安装到设备
buildozer android deploy run
```

#### 选项 B: 使用 Android Studio

1. 打开 `dev/PPSSaveEditor` 在 Android Studio
2. 同步 Gradle 文件
3. 点击 "Run" 按钮

### 方式三: Termux (Android 终端)

```bash
# 在手机上安装 Termux
pkg install python
pip install pycryptodome

# 下载脚本并运行
python psp_save_editor.py /sdcard/PSP/SAVEDATA/XXX --decrypt --hex
```

## 核心功能演示

### 1. 修改金钱示例

```python
# 查找金钱地址
# 假设游戏中金钱是 12345 (0x3039)
# 在存档中搜索小端序: 39 30 00 00

# 使用 CWCheat 代码
_L 0x20555678 0x0098967F  # 设置为 9999999
```

### 2. 十六进制编辑

```
偏移       | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | ASCII
--------------------------------------------------------------------------------
00000000 |  4D 6F 6E 65 79 3A 20 39>39 39 39 39 00 00 00 00 | Money: 99999....
                                      ^
                                      偏移 0x07 (金钱数值)
```

### 3. 完整工作流程

```
1. 选择存档文件夹
      ↓
2. 解密存档 (如果是加密的)
      ↓
3. 十六进制编辑 / 应用补丁代码
      ↓
4. 加密存档
      ↓
5. 保存回游戏目录
      ↓
6. 在 PPSSPP 中加载
```

## 技术架构

### 加密算法
- **算法**: AES-ECB
- **密钥**: 16字节 (固定或游戏特定)
- **模式**: 1 (固定密钥), 3/5 (游戏特定密钥)

### SFO 文件格式
```
Header (20 bytes):
  - Magic: 0x46535000
  - Version
  - Key Table Offset
  - Data Table Offset
  - Entry Count

Entry (16 bytes each):
  - Key Offset
  - Format (0x0204=UTF8, 0x0404=INT)
  - Data Length
  - Max Length
  - Data Offset
```

### CWCheat 代码格式
```
_L 0xTXXXXXXX 0xYYYYYYYY
│    │          └─ Value to write
│    └─ Address (T=type: 0=8bit, 1=16bit, 2=32bit)
└─ Code marker
```

## 测试结果

运行 `python test_editor.py` 结果：

```
============================================================
Test Summary:
============================================================
  PASS: SFO Parser
  PASS: Crypto
  PASS: CWCheat
  PASS: Hex Editor
  PASS: Full Workflow
============================================================
All tests passed!
============================================================
```

## 已知限制

1. **加密支持**: 目前主要支持模式 1 (固定密钥)
   - 某些游戏使用模式 3/5 可能需要额外密钥
   
2. **校验和**: 某些游戏有额外的存档校验
   - 修改后可能需要重新计算校验和
   
3. **文件格式**: 只支持标准 DATA.BIN
   - 某些游戏可能有特殊格式 (SECURE.BIN, SDDATA.BIN)

## 未来改进

- [ ] 支持更多加密模式 (3, 5)
- [ ] 自动计算和修复校验和
- [ ] 集成在线 CWCheat 数据库
- [ ] 存档对比功能
- [ ] 游戏特定的预设修改

## 许可

MIT License - 可自由使用、修改和分发

## 致谢

- PPSSPP 开发团队
- PSP 开发者社区
- CWCheat 项目

---

**项目创建完成！** 你可以立即使用 Python 版本，或构建 Android APK。

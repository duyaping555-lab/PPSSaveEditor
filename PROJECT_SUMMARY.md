# PPSSPP 存档编辑器 - 项目总结

## 项目概述

这是一个为 PPSSPP PSP 模拟器设计的存档编辑器，提供两种实现方式:

1. **Android 原生应用** - 完整的 GUI 应用，可直接在手机上使用
2. **Python 命令行工具** - 跨平台，可在 PC 或 Android (Termux) 上运行

## 文件结构

```
dev/PPSSaveEditor/
├── README.md                      # Android 项目说明
├── build.gradle                   # 项目级 Gradle 配置
├── settings.gradle                # Gradle 设置
├── gradle/wrapper/                # Gradle Wrapper
├── app/
│   ├── build.gradle               # 应用级 Gradle 配置
│   ├── proguard-rules.pro         # ProGuard 规则
│   └── src/main/
│       ├── AndroidManifest.xml    # 应用清单
│       ├── java/com/ppssaveeditor/
│       │   ├── MainActivity.kt           # 主界面
│       │   ├── HexEditorActivity.kt      # 十六进制编辑器
│       │   ├── CheatCodeActivity.kt      # 补丁代码界面
│       │   ├── SFOParser.kt              # SFO 解析器
│       │   ├── SaveDataCrypto.kt         # 加解密模块
│       │   ├── CheatCodeApplier.kt       # 代码应用器
│       │   └── HexEditorAdapter.kt       # 十六进制适配器
│       └── res/
│           ├── layout/
│           │   ├── activity_main.xml         # 主界面布局
│           │   ├── activity_hex_editor.xml   # 十六进制编辑器布局
│           │   ├── activity_cheat_code.xml   # 补丁代码布局
│           │   ├── item_hex_row.xml          # 十六进制行项
│           │   └── dialog_modify_value.xml   # 修改数值对话框
│           └── values/
│               ├── strings.xml       # 字符串资源
│               ├── colors.xml        # 颜色资源
│               └── themes.xml        # 主题资源
├── psp_save_editor.py             # Python 命令行版本
├── psp_save_editor_README.md      # Python 版本说明
├── requirements.txt               # Python 依赖
└── example_cheat_codes.txt        # 示例代码
```

## 核心功能

### 1. SFO 文件解析 (`SFOParser.kt` / Python 中的 `SFOParser`)
- 解析 PSP 存档的元数据
- 读取游戏标题、存档标题、存档详情等
- 支持修改和写回 SFO 文件

### 2. 存档加解密 (`SaveDataCrypto.kt` / Python 中的 `SaveDataCrypto`)
- 支持 PSP 存档的三种加密模式 (1, 3, 5)
- 使用 AES-ECB 算法
- 自动检测加密模式

### 3. 十六进制编辑器 (`HexEditorActivity.kt` / Python 中的 `HexEditor`)
- 可视化显示存档数据
- 支持搜索十六进制值
- 支持跳转到指定偏移
- 支持修改 8/16/32 位数值
- 显示 ASCII 表示

### 4. 补丁代码应用 (`CheatCodeApplier.kt` / Python 中的 `CheatCodeApplier`)
- 支持标准 CWCheat 代码格式
- 支持 8/16/32 位写入
- 批量应用多个代码

## 使用方法

### Android 应用

1. 在 Android Studio 中打开项目
2. 构建并安装 APK
3. 启动应用，选择存档文件夹
4. 解密 → 编辑 → 加密 → 保存

### Python 脚本

```bash
# 安装依赖
pip install pycryptodome

# 基本用法
python psp_save_editor.py <存档文件夹> --decrypt --hex --encrypt
```

## 技术细节

### PSP 存档格式

```
SAVEDATA/
├── PARAM.SFO      # 元数据 (未加密)
├── ICON0.PNG      # 存档图标
└── DATA.BIN       # 存档数据 (AES加密)
```

### SFO 文件结构

```
Header (20 bytes):
  - Magic: 0x46535000 ("PSP\0")
  - Version
  - Key Table Offset
  - Data Table Offset
  - Entry Count

Index Table (16 bytes per entry):
  - Key Offset
  - Format (0x0204=UTF8, 0x0404=INT)
  - Data Length
  - Max Length
  - Data Offset

Key Table: null-terminated strings
Data Table: actual data values
```

### 加密算法

- 算法: AES-ECB
- 密钥: 16字节固定密钥或游戏特定密钥
- 填充: PKCS#7 或零填充到16字节倍数
- 头部: 12字节 (Magic + Version + Original Size)

## 查找游戏数值的方法

### 方法一: 已知数值搜索

1. 在游戏中记录数值（如金钱 12345 = 0x3039）
2. 搜索小端序字节: `39 30 00 00`
3. 修改并测试

### 方法二: 差分分析

1. 创建两个存档，数值相差 1
2. 用二进制比较工具找出差异
3. 确定数值存储位置

### 方法三: 使用现有 CWCheat 表

1. 搜索游戏的 CWCheat 代码
2. 将内存地址转换为存档偏移
3. 应用到存档

## 注意事项

1. **备份**: 修改前务必备份原始存档
2. **校验**: 某些游戏有额外校验，简单修改可能无法加载
3. **格式**: 确保正确理解数值存储格式（小端序）
4. **权限**: Android 应用需要存储权限

## 扩展建议

### Android 应用
- 添加存档导入/导出功能
- 集成存档分享功能
- 添加游戏特定的预设修改
- 支持更多加密模式

### Python 脚本
- 添加图形界面 (tkinter/PyQt)
- 添加存档对比功能
- 集成在线 CWCheat 数据库
- 添加批量处理功能

## 参考资源

- [PSP Savedata Format](https://www.psdevwiki.com/ps3/PSP_Savedata)
- [PPSSPP GitHub](https://github.com/hrydgard/ppsspp)
- [CWCheat Database](https://github.com/Saramagrean/CWCheat-Database-Plus-)

## 许可证

MIT License - 可自由使用、修改和分发

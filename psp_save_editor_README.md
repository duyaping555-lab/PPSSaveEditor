# PSP Save Editor - Python 版本

用于编辑 PPSSPP/PSP 存档文件的 Python 命令行工具。

## 安装依赖

```bash
pip install pycryptodome
```

## 使用方法

### 1. 显示存档信息

```bash
python psp_save_editor.py /path/to/save_folder
```

### 2. 解密存档

```bash
python psp_save_editor.py /path/to/save_folder --decrypt
```

### 3. 启动十六进制编辑器

```bash
python psp_save_editor.py /path/to/save_folder --hex
```

交互式命令:
- `s <hex>` - 搜索十六进制值，如 `s 0098967F`
- `g <offset>` - 跳转到偏移，如 `g 1000`
- `m <offset> <value> <size>` - 修改值，如 `m 0x1000 0x9999 2`
- `q` - 退出

### 4. 应用 CWCheat 代码

```bash
# 从文件读取代码
python psp_save_editor.py /path/to/save_folder --decrypt --cheat codes.txt --encrypt

# 或者直接输入
python psp_save_editor.py /path/to/save_folder --decrypt --cheat "_L 0x20555678 0x0098967F" --encrypt
```

### 5. 完整流程示例

```bash
# 1. 查看存档信息
python psp_save_editor.py ~/PSP/SAVEDATA/NPJH12345

# 2. 解密并编辑
python psp_save_editor.py ~/PSP/SAVEDATA/NPJH12345 --decrypt --hex

# 3. 加密保存
python psp_save_editor.py ~/PSP/SAVEDATA/NPJH12345 --encrypt
```

## 查找修改地址的方法

### 方法一: 搜索已知数值

1. 在游戏中记录当前数值（如金钱 12345 = 0x3039）
2. 在十六进制编辑器中搜索: `s 39300000`（小端序）
3. 找到后修改并测试

### 方法二: 差分对比

1. 存档 A: 金钱 10000
2. 存档 B: 金钱 10001
3. 用二进制比较工具对比两个存档
4. 找到差异位置

## 在 Android (Termux) 上使用

1. 安装 Termux 应用
2. 安装 Python:
   ```bash
   pkg install python
   pip install pycryptodome
   ```
3. 复制脚本到手机
4. 运行:
   ```bash
   python psp_save_editor.py /sdcard/PSP/SAVEDATA/XXXXXX --decrypt --hex
   ```

## CWCheat 代码示例

```
# 修改金钱为 9999999
_L 0x20555678 0x0098967F

# 修改 HP 为 9999
_L 0x2055567C 0x0000270F

# 修改物品数量为 99
_L 0x00555680 0x00000063
```

代码格式说明:
- `0x2XXXXXXX` = 32位写入（4字节）
- `0x1XXXXXXX` = 16位写入（2字节）
- `0x0XXXXXXX` = 8位写入（1字节）
- 地址是相对于存档起始位置的偏移

## 注意事项

- 修改前务必备份原始存档
- 某些游戏有额外校验，修改后可能无法加载
- 数值通常以小端序存储（低字节在前）

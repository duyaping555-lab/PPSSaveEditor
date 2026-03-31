# PPSSPP 存档编辑器 - 模拟器测试指南

## 测试环境准备

### 1. 安装 Android 模拟器

推荐使用以下模拟器之一:

#### Android Studio 模拟器 (推荐)
1. 下载安装 Android Studio
2. 打开 AVD Manager (Tools > Device Manager)
3. 创建虚拟设备:
   - 选择设备: Pixel 6 或其他
   - 选择系统镜像: Android 12/13 (API 31/33)
   - 完成创建

#### BlueStacks / NoxPlayer
1. 下载安装 BlueStacks 或 NoxPlayer
2. 启动模拟器

### 2. 准备测试文件

创建测试存档结构:

```bash
# 创建测试目录
mkdir -p test_save/ULJM12345

# 创建 PARAM.SFO (使用 Python 脚本)
python -c "
from psp_save_editor import SFOParser, SFOEntry, SFOData
parser = SFOParser()
entries = {
    'TITLE': SFOEntry('TITLE', 0x0204, 9, 32, b'TestGame\x00', 'TestGame'),
    'SAVEDATA_TITLE': SFOEntry('SAVEDATA_TITLE', 0x0204, 5, 128, b'Save\x00', 'Save'),
    'TITLE_ID': SFOEntry('TITLE_ID', 0x0204, 10, 16, b'ULJM12345\x00', 'ULJM12345'),
}
sfo = SFOData(entries, 'TestGame', 'Save', 'Test Detail', 'ULJM12345')
parser.write_sfo(sfo, 'test_save/ULJM12345/PARAM.SFO')
print('SFO created')
"

# 创建测试数据文件
echo -n "Money: 12345 Health: 100" > test_save/ULJM12345/DATA.BIN

# 可选: 加密数据
python -c "
from psp_save_editor import SaveDataCrypto
crypto = SaveDataCrypto()
with open('test_save/ULJM12345/DATA.BIN', 'rb') as f:
    data = f.read()
encrypted = crypto.encrypt(data, mode=1)
with open('test_save/ULJM12345/DATA.BIN', 'wb') as f:
    f.write(encrypted)
print('Data encrypted')
"
```

### 3. 推送到模拟器

```bash
# 连接模拟器 (如果是 BlueStacks/Nox，可能需要先连接)
adb connect localhost:5555  # 端口号根据模拟器而定

# 创建目录
adb shell mkdir -p /sdcard/PSP/SAVEDATA/ULJM12345

# 推送文件
adb push test_save/ULJM12345/PARAM.SFO /sdcard/PSP/SAVEDATA/ULJM12345/
adb push test_save/ULJM12345/DATA.BIN /sdcard/PSP/SAVEDATA/ULJM12345/

# 验证
adb shell ls -la /sdcard/PSP/SAVEDATA/ULJM12345/
```

## 安装 APK

### 方法 1: 通过 ADB 安装

```bash
# 安装 APK
adb install -r mobile_app/bin/PPSSPP存档编辑器-1.0.0-arm64-v8a_debug.apk

# 或安装 x86 版本 (模拟器)
adb install -r mobile_app/bin/PPSSPP存档编辑器-1.0.0-x86_debug.apk

# 启动应用
adb shell am start -n com.ppssaveeditor.ppssaveeditor/org.kivy.android.PythonActivity
```

### 方法 2: 通过文件管理器安装

1. 将 APK 复制到模拟器
2. 在模拟器中打开文件管理器
3. 点击 APK 安装

## 功能测试清单

### 测试 1: 文件选择
1. 打开应用
2. 点击"选择存档文件夹"
3. 输入路径: `/sdcard/PSP/SAVEDATA/ULJM12345`
4. 验证显示:
   - 游戏标题: TestGame
   - 存档标题: Save
   - ID: ULJM12345

### 测试 2: 解密功能
1. 点击"解密"
2. 验证显示"解密成功"
3. 解密按钮应变为禁用状态
4. 加密、十六进制、补丁代码按钮应变为可用

### 测试 3: 十六进制编辑器
1. 点击"十六进制"
2. 验证显示:
   - 偏移列
   - 十六进制值
   - ASCII 表示
3. 搜索功能:
   - 输入搜索值: `4D 6F 6E 65 79` (Money)
   - 点击搜索
   - 验证跳转到正确位置
4. 修改功能:
   - 点击"修改"
   - 偏移: 7
   - 值: 39393939 (9999)
   - 类型: 4 (32位)
   - 验证修改成功
5. 点击"保存"

### 测试 4: CWCheat 代码
1. 点击"补丁代码"
2. 输入代码:
   ```
   _L 0x20000007 0x39393939
   ```
3. 点击"应用代码"
4. 验证显示"成功应用 1 个代码"

### 测试 5: 加密功能
1. 点击"加密"
2. 验证显示"加密成功"
3. 验证文件已修改:
   ```bash
   adb shell ls -la /sdcard/PSP/SAVEDATA/ULJM12345/
   # 应该看到新的加密文件或修改后的文件
   ```

### 测试 6: 实际游戏存档测试

使用真实游戏存档测试:

1. 从手机复制存档:
   ```bash
   adb pull /sdcard/Android/data/org.ppsspp.ppsspp/files/PSP/SAVEDATA/<GAME_ID> ./real_save/
   ```

2. 使用编辑器修改

3. 推回手机:
   ```bash
   adb push ./real_save/<GAME_ID>/ /sdcard/Android/data/org.ppsspp.ppsspp/files/PSP/SAVEDATA/
   ```

4. 在 PPSSPP 中加载存档验证

## 常见问题

### Q: 应用崩溃
A: 检查:
- 是否授予存储权限
- 路径是否正确
- 存档文件是否存在

查看日志:
```bash
adb logcat -s python:D *:S
```

### Q: 解密失败
A: 可能原因:
- 数据已经是明文的
- 使用了不支持的加密模式
- 文件损坏

### Q: 修改后游戏无法加载存档
A: 可能原因:
- 游戏有额外的校验和
- 修改了错误的地址
- 数值格式不正确

## 性能测试

### 大文件测试
```bash
# 创建大测试文件 (1MB)
dd if=/dev/urandom of=test_save/LARGE/BIGDATA.BIN bs=1M count=1

# 测试在编辑器中打开和操作
```

### 内存使用
```bash
# 监控内存使用
adb shell dumpsys meminfo com.ppssaveeditor.ppssaveeditor
```

## 自动化测试脚本

```python
#!/usr/bin/env python3
"""自动化测试脚本"""

import subprocess
import time

def run_test():
    # 安装 APK
    subprocess.run(['adb', 'install', '-r', 'mobile_app/bin/*.apk'])
    
    # 启动应用
    subprocess.run([
        'adb', 'shell', 'am', 'start',
        '-n', 'com.ppssaveeditor.ppssaveeditor/org.kivy.android.PythonActivity'
    ])
    
    time.sleep(5)  # 等待启动
    
    # 截图
    subprocess.run(['adb', 'shell', 'screencap', '-p', '/sdcard/screen1.png'])
    subprocess.run(['adb', 'pull', '/sdcard/screen1.png', './test_screenshot1.png'])
    
    # ... 更多测试步骤
    
    print("Test completed!")

if __name__ == '__main__':
    run_test()
```

## 提交反馈

测试完成后，请记录:
1. 模拟器型号和 Android 版本
2. 测试的功能和结果
3. 遇到的问题和错误日志
4. 改进建议

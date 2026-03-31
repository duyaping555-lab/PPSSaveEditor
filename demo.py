#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPSSPP 存档编辑器 - 演示脚本
展示如何使用编辑器修改存档
"""

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from psp_save_editor import (
    SFOParser, SFOEntry, SFOData,
    SaveDataCrypto, CheatCodeApplier, 
    SaveDataEditor, HexEditor
)


def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def demo_sfo():
    """演示 SFO 文件处理"""
    print_header("演示 1: SFO 文件解析")
    
    parser = SFOParser()
    
    # 创建存档元数据
    entries = {
        'TITLE': SFOEntry('TITLE', 0x0204, 20, 128, 
                          'Monster Hunter'.encode('utf-8').ljust(128, b'\x00'),
                          'Monster Hunter'),
        'SAVEDATA_TITLE': SFOEntry('SAVEDATA_TITLE', 0x0204, 15, 128,
                                   'Save Data 1'.encode('utf-8').ljust(128, b'\x00'),
                                   'Save Data 1'),
        'SAVEDATA_DETAIL': SFOEntry('SAVEDATA_DETAIL', 0x0204, 30, 1024,
                                    'Player: Hunter123 - HR 5'.encode('utf-8').ljust(1024, b'\x00'),
                                    'Player: Hunter123 - HR 5'),
        'TITLE_ID': SFOEntry('TITLE_ID', 0x0204, 10, 16,
                             'ULJM12345'.encode('utf-8').ljust(16, b'\x00'),
                             'ULJM12345'),
    }
    
    sfo_data = SFOData(
        entries=entries,
        game_title='Monster Hunter',
        save_title='Save Data 1',
        save_detail='Player: Hunter123 - HR 5',
        title_id='ULJM12345'
    )
    
    print(f"游戏标题: {sfo_data.game_title}")
    print(f"存档标题: {sfo_data.save_title}")
    print(f"存档详情: {sfo_data.save_detail}")
    print(f"游戏ID: {sfo_data.title_id}")
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(suffix='.SFO', delete=False) as f:
        temp_sfo = f.name
    
    parser.write_sfo(sfo_data, temp_sfo)
    print(f"\nSFO 文件已保存: {os.path.getsize(temp_sfo)} 字节")
    
    return temp_sfo


def demo_crypto():
    """演示加密解密"""
    print_header("演示 2: 存档加密/解密")
    
    crypto = SaveDataCrypto()
    
    # 原始存档数据
    original = b'Zenny: 50000\x00\x00\x00\x00Items: 10\x00\x00\x00\x00Quests: 25'
    print(f"原始数据: {original[:50]}...")
    print(f"数据大小: {len(original)} 字节")
    
    # 加密
    encrypted = crypto.encrypt(original, mode=1)
    print(f"\n加密后大小: {len(encrypted)} 字节")
    print(f"头部信息: {encrypted[:12].hex()}")
    
    # 解密
    decrypted = crypto.decrypt(encrypted, mode=1)
    print(f"\n解密后: {decrypted[:50]}...")
    
    # 验证
    if decrypted == original:
        print("✓ 加解密验证成功!")
    
    return encrypted


def demo_hex_edit():
    """演示十六进制编辑"""
    print_header("演示 3: 十六进制编辑")
    
    # 创建模拟存档数据
    data = bytearray(256)
    
    # 写入一些游戏数据
    # 金钱: 50000 (0x0000C350) 小端序: 50 C3 00 00
    data[0x10:0x14] = bytes([0x50, 0xC3, 0x00, 0x00])
    
    # HP: 100 (0x64)
    data[0x20] = 100
    
    # MP: 50 (0x32)
    data[0x21] = 50
    
    editor = HexEditor(data)
    
    print("原始数据:")
    editor.display(start=0x00, rows=4)
    
    print("\n修改金钱 (地址 0x10):")
    print("  原始值: 50000 (0x0000C350)")
    print("  新值: 999999 (0x000F423F)")
    
    # 修改为 999999
    editor.modify(0x10, 999999, 4)
    
    print("\n修改后:")
    editor.display(start=0x00, rows=4)
    
    # 验证
    new_value = int.from_bytes(data[0x10:0x14], 'little')
    print(f"\n验证: 地址 0x10 的值现在是 {new_value}")


def demo_cheat():
    """演示 CWCheat 代码"""
    print_header("演示 4: CWCheat 代码应用")
    
    applier = CheatCodeApplier()
    
    # 模拟存档数据
    data = bytearray(0x100)
    
    # 设置初始值
    data[0x50:0x54] = (10000).to_bytes(4, 'little')  # 金钱
    data[0x60:0x62] = (100).to_bytes(2, 'little')     # HP
    data[0x70] = 10                                    # 物品数量
    
    print("初始状态:")
    print(f"  金钱: {int.from_bytes(data[0x50:0x54], 'little')}")
    print(f"  HP: {int.from_bytes(data[0x60:0x62], 'little')}")
    print(f"  物品: {data[0x70]}")
    
    # CWCheat 代码
    codes = """
; 修改金钱为 9999999
_L 0x20555550 0x0098967F

; 修改 HP 为 9999
_L 0x10555560 0x0000270F

; 修改物品为 99
_L 0x00555570 0x00000063
"""
    
    print("\n应用代码:")
    for line in codes.strip().split('\n'):
        line = line.strip()
        if line and not line.startswith(';'):
            print(f"  {line}")
    
    # 应用代码
    lines = codes.strip().split('\n')
    success, message, modified = applier.apply_codes(data, lines)
    
    print(f"\n结果: {message}")
    
    print("\n修改后:")
    print(f"  金钱: {int.from_bytes(data[0x50:0x54], 'little')}")
    print(f"  HP: {int.from_bytes(data[0x60:0x62], 'little')}")
    print(f"  物品: {data[0x70]}")


def demo_full_workflow():
    """演示完整工作流程"""
    print_header("演示 5: 完整工作流程")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    save_dir = os.path.join(temp_dir, 'ULJM12345')
    os.makedirs(save_dir)
    
    try:
        print("1. 创建测试存档...")
        
        # 创建 SFO
        parser = SFOParser()
        entries = {
            'TITLE': SFOEntry('TITLE', 0x0204, 14, 128, 
                              'Test Game'.encode('utf-8').ljust(128, b'\x00'),
                              'Test Game'),
            'SAVEDATA_TITLE': SFOEntry('SAVEDATA_TITLE', 0x0204, 10, 128,
                                       'Save 1'.encode('utf-8').ljust(128, b'\x00'),
                                       'Save 1'),
            'TITLE_ID': SFOEntry('TITLE_ID', 0x0204, 10, 16,
                                 'ULJM12345'.encode('utf-8').ljust(16, b'\x00'),
                                 'ULJM12345'),
        }
        sfo_data = SFOData(entries, 'Test Game', 'Save 1', '', 'ULJM12345')
        sfo_path = os.path.join(save_dir, 'PARAM.SFO')
        parser.write_sfo(sfo_data, sfo_path)
        print(f"   PARAM.SFO 创建成功 ({os.path.getsize(sfo_path)} 字节)")
        
        # 创建加密的存档数据
        crypto = SaveDataCrypto()
        original_data = b'Gold: 1000' + b'\x00' * 100
        encrypted_data = crypto.encrypt(original_data, mode=1)
        data_path = os.path.join(save_dir, 'DATA.BIN')
        with open(data_path, 'wb') as f:
            f.write(encrypted_data)
        print(f"   DATA.BIN 创建成功 ({len(encrypted_data)} 字节)")
        
        print(f"\n2. 存档目录: {save_dir}")
        print("   文件列表:")
        for f in os.listdir(save_dir):
            size = os.path.getsize(os.path.join(save_dir, f))
            print(f"     - {f}: {size} 字节")
        
        print("\n3. 加载存档编辑器...")
        editor = SaveDataEditor(save_dir)
        print(f"   游戏: {editor.sfo_data.game_title}")
        print(f"   存档: {editor.sfo_data.save_title}")
        
        print("\n4. 解密存档...")
        if editor.decrypt():
            print(f"   解密成功，数据大小: {len(editor.decrypted_data)} 字节")
            print(f"   内容预览: {bytes(editor.decrypted_data[:20])}")
        
        print("\n5. 应用补丁代码...")
        # 修改金钱从 1000 到 99999
        # "1000" 在偏移 6 处
        codes = ["_L 0x20000006 0x0001869F"]  # 99999
        editor.apply_cheat_codes("\n".join(codes))
        print("   代码已应用")
        
        # 查看修改结果
        modified = bytes(editor.decrypted_data[:20])
        print(f"   修改后: {modified}")
        
        print("\n6. 加密并保存...")
        output_path = os.path.join(save_dir, 'DATA_MODIFIED.BIN')
        if editor.encrypt(output_path):
            print(f"   已保存: {output_path}")
            print(f"   文件大小: {os.path.getsize(output_path)} 字节")
        
        print("\n7. 验证...")
        # 读取修改后的文件并解密验证
        with open(output_path, 'rb') as f:
            modified_encrypted = f.read()
        modified_decrypted = crypto.decrypt(modified_encrypted, mode=1)
        print(f"   重新解密验证: {modified_decrypted[:20]}")
        
        print("\n✓ 完整工作流程演示完成!")
        
    finally:
        shutil.rmtree(temp_dir)


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║         PPSSPP Save Editor - Demo                        ║
    ║         PSP/PPSSPP Save File Editor                      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    demos = [
        ("SFO 文件处理", demo_sfo),
        ("加密/解密", demo_crypto),
        ("十六进制编辑", demo_hex_edit),
        ("CWCheat 代码", demo_cheat),
        ("完整工作流程", demo_full_workflow),
    ]
    
    print("可用演示:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print("  0. 运行全部")
    print("  q. 退出")
    
    choice = input("\n选择 (0-5/q): ").strip().lower()
    
    if choice == 'q':
        return
    
    try:
        choice = int(choice)
        if choice == 0:
            for name, func in demos:
                func()
        elif 1 <= choice <= len(demos):
            demos[choice - 1][1]()
        else:
            print("无效选择")
    except ValueError:
        print("无效输入")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("演示结束!")
    print("=" * 60)


if __name__ == '__main__':
    main()

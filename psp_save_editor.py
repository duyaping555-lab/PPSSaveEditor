#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PSP/PPSSPP 存档编辑器
支持 SFO 文件解析、存档加解密、十六进制编辑和 CWCheat 代码应用

使用方法:
    python psp_save_editor.py <存档文件夹路径>

支持在 Android (Termux) 上运行
"""

import os
import sys
import struct
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple, BinaryIO
from dataclasses import dataclass, asdict

try:
    from Crypto.Cipher import AES
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("警告: pycryptodome 未安装，加密功能将不可用")
    print("安装命令: pip install pycryptodome")


@dataclass
class SFOEntry:
    """SFO 条目"""
    key: str
    format: int
    length: int
    max_length: int
    data: bytes
    string_value: str = ""


@dataclass
class SFOData:
    """SFO 数据"""
    entries: Dict[str, SFOEntry]
    game_title: str = ""
    save_title: str = ""
    save_detail: str = ""
    title_id: str = ""


class SFOParser:
    """PARAM.SFO 文件解析器"""
    
    FORMAT_UTF8 = 0x0204
    FORMAT_INT = 0x0404
    MAGIC = 0x46535000  # "PSP\0"
    
    def parse(self, file_path: str) -> Optional[SFOData]:
        """解析 SFO 文件"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            return self.parse_bytes(data)
        except Exception as e:
            print(f"解析 SFO 文件失败: {e}")
            return None
    
    def parse_bytes(self, data: bytes) -> Optional[SFOData]:
        """从字节数据解析 SFO"""
        try:
            magic = struct.unpack('<I', data[0:4])[0]
            if magic != self.MAGIC:
                print(f"无效的 SFO 文件 (magic: {hex(magic)})")
                return None
            
            version = struct.unpack('<I', data[4:8])[0]
            key_table_offset = struct.unpack('<I', data[8:12])[0]
            data_table_offset = struct.unpack('<I', data[12:16])[0]
            entry_count = struct.unpack('<I', data[16:20])[0]
            
            entries = {}
            offset = 20
            
            for i in range(entry_count):
                key_offset = struct.unpack('<H', data[offset:offset+2])[0]
                format_type = struct.unpack('<H', data[offset+2:offset+4])[0]
                length = struct.unpack('<I', data[offset+4:offset+8])[0]
                max_length = struct.unpack('<I', data[offset+8:offset+12])[0]
                data_offset = struct.unpack('<I', data[offset+12:offset+16])[0]
                
                # 读取 key
                key_start = key_table_offset + key_offset
                key_end = data.find(b'\x00', key_start)
                key = data[key_start:key_end].decode('utf-8', errors='ignore')
                
                # 读取 data
                data_start = data_table_offset + data_offset
                entry_data = data[data_start:data_start + length]
                
                string_value = ""
                if format_type == self.FORMAT_UTF8:
                    string_value = entry_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
                
                entry = SFOEntry(
                    key=key,
                    format=format_type,
                    length=length,
                    max_length=max_length,
                    data=entry_data,
                    string_value=string_value
                )
                entries[key] = entry
                offset += 16
            
            return SFOData(
                entries=entries,
                game_title=entries.get('TITLE', SFOEntry('', 0, 0, 0, b'')).string_value,
                save_title=entries.get('SAVEDATA_TITLE', SFOEntry('', 0, 0, 0, b'')).string_value,
                save_detail=entries.get('SAVEDATA_DETAIL', SFOEntry('', 0, 0, 0, b'')).string_value,
                title_id=entries.get('TITLE_ID', SFOEntry('', 0, 0, 0, b'')).string_value
            )
            
        except Exception as e:
            print(f"解析 SFO 失败: {e}")
            return None
    
    def write_sfo(self, sfo_data: SFOData, output_path: str):
        """将 SFO 数据写入文件"""
        entries = list(sfo_data.entries.values())
        
        # 计算 key table 大小
        key_table_size = 0
        key_offsets = {}
        for entry in entries:
            key_offsets[entry.key] = key_table_size
            key_table_size += len(entry.key) + 1
        key_table_size = (key_table_size + 3) & 0xFFFFFFFC  # 对齐
        
        # 计算 data table 大小
        data_table_size = 0
        data_offsets = {}
        for entry in entries:
            data_offsets[entry.key] = data_table_size
            data_table_size += entry.max_length
        data_table_size = (data_table_size + 3) & 0xFFFFFFFC  # 对齐
        
        header_size = 20
        index_size = len(entries) * 16
        total_size = header_size + index_size + key_table_size + data_table_size
        
        buffer = bytearray(total_size)
        
        # 写入头部
        struct.pack_into('<I', buffer, 0, self.MAGIC)
        struct.pack_into('<I', buffer, 4, 0x00010100)
        struct.pack_into('<I', buffer, 8, header_size + index_size)
        struct.pack_into('<I', buffer, 12, header_size + index_size + key_table_size)
        struct.pack_into('<I', buffer, 16, len(entries))
        
        # 写入索引表
        offset = 20
        for entry in entries:
            struct.pack_into('<H', buffer, offset, key_offsets[entry.key])
            struct.pack_into('<H', buffer, offset + 2, entry.format)
            struct.pack_into('<I', buffer, offset + 4, entry.length)
            struct.pack_into('<I', buffer, offset + 8, entry.max_length)
            struct.pack_into('<I', buffer, offset + 12, data_offsets[entry.key])
            offset += 16
        
        # 写入 key table
        key_offset = header_size + index_size
        for entry in entries:
            key_bytes = entry.key.encode('utf-8') + b'\x00'
            buffer[key_offset:key_offset + len(key_bytes)] = key_bytes
            key_offset += len(key_bytes)
        
        # 写入 data table
        data_offset = header_size + index_size + key_table_size
        for entry in entries:
            padded_data = entry.data.ljust(entry.max_length, b'\x00')
            buffer[data_offset:data_offset + entry.max_length] = padded_data
            data_offset += entry.max_length
        
        with open(output_path, 'wb') as f:
            f.write(buffer)


class SaveDataCrypto:
    """PSP 存档加解密"""
    
    FIXED_KEY = bytes([
        0x40, 0xE6, 0x5E, 0x5F, 0x45, 0xE4, 0x48, 0xF3,
        0x60, 0x48, 0x05, 0x2B, 0x27, 0x89, 0x67, 0x63
    ])
    
    MAGIC_ENCRYPTED = 0x50464400
    
    def __init__(self):
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("加密功能需要 pycryptodome 库")
    
    def detect_mode(self, data: bytes) -> int:
        """检测加密模式"""
        if len(data) < 12:
            return -1
        
        magic = struct.unpack('<I', data[0:4])[0]
        if magic != self.MAGIC_ENCRYPTED:
            return 0  # 未加密
        
        return 1  # 默认为模式1
    
    def decrypt(self, data: bytes, mode: int = 1, key: Optional[bytes] = None) -> bytes:
        """解密数据"""
        use_key = key if key else self.FIXED_KEY
        
        if len(data) < 12:
            raise ValueError("数据太短")
        
        magic = struct.unpack('<I', data[0:4])[0]
        if magic != self.MAGIC_ENCRYPTED:
            return data  # 可能已经是明文
        
        # 提取加密的数据
        encrypted = data[12:]
        
        # AES ECB 解密
        cipher = AES.new(use_key, AES.MODE_ECB)
        decrypted = cipher.decrypt(encrypted)
        
        # 获取原始数据大小
        original_size = struct.unpack('<I', data[8:12])[0]
        
        return decrypted[:original_size]
    
    def encrypt(self, data: bytes, mode: int = 1, key: Optional[bytes] = None) -> bytes:
        """加密数据"""
        use_key = key if key else self.FIXED_KEY
        
        # 填充到16字节倍数
        pad_len = 16 - (len(data) % 16) if len(data) % 16 else 0
        padded_data = data + bytes(pad_len)
        
        # AES ECB 加密
        cipher = AES.new(use_key, AES.MODE_ECB)
        encrypted = cipher.encrypt(padded_data)
        
        # 构建头部
        header = struct.pack('<III', self.MAGIC_ENCRYPTED, 0x00010000, len(data))
        
        return header + encrypted


class CheatCodeApplier:
    """CWCheat 代码应用器"""
    
    def parse_code(self, line: str) -> Optional[Tuple[int, int, int]]:
        """
        解析 CWCheat 代码行
        返回: (address, value, type)
        type: 0=8bit, 1=16bit, 2=32bit
        """
        line = line.strip()
        if not line.startswith('_L'):
            return None
        
        parts = line.split()
        if len(parts) < 3:
            return None
        
        try:
            addr_str = parts[1]
            val_str = parts[2]
            
            # 解析地址
            addr = int(addr_str, 16)
            
            # 解析值
            val = int(val_str, 16)
            
            # 确定类型
            addr_prefix = (addr >> 28) & 0xF
            code_type = min(addr_prefix, 2)  # 0, 1, 或 2
            
            # 清除地址的类型位
            address = addr & 0x0FFFFFFF
            
            return (address, val, code_type)
        except ValueError:
            return None
    
    def apply_codes(self, data: bytearray, code_lines: List[str]) -> Tuple[bool, str, List[int]]:
        """
        应用多个 CWCheat 代码
        返回: (success, message, modified_offsets)
        """
        modified = []
        failed = []
        
        for line in code_lines:
            code = self.parse_code(line)
            if not code:
                continue
            
            address, value, code_type = code
            
            if code_type == 0:  # 8-bit
                if address < len(data):
                    data[address] = value & 0xFF
                    modified.append(address)
                else:
                    failed.append(line)
            
            elif code_type == 1:  # 16-bit
                if address + 1 < len(data):
                    data[address] = value & 0xFF
                    data[address + 1] = (value >> 8) & 0xFF
                    modified.append(address)
                else:
                    failed.append(line)
            
            elif code_type == 2:  # 32-bit
                if address + 3 < len(data):
                    data[address] = value & 0xFF
                    data[address + 1] = (value >> 8) & 0xFF
                    data[address + 2] = (value >> 16) & 0xFF
                    data[address + 3] = (value >> 24) & 0xFF
                    modified.append(address)
                else:
                    failed.append(line)
        
        message = f"成功修改 {len(modified)} 处"
        if failed:
            message += f"，失败 {len(failed)} 处"
        
        return (len(modified) > 0, message, modified)


class HexEditor:
    """简单的十六进制编辑器"""
    
    def __init__(self, data: bytearray):
        self.data = data
        self.selected_offset = 0
    
    def display(self, start: int = 0, rows: int = 16):
        """显示十六进制数据"""
        print(f"\n{'偏移':10} | {'00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F':48} | ASCII")
        print("-" * 80)
        
        for row in range(rows):
            offset = start + row * 16
            if offset >= len(self.data):
                break
            
            # 偏移
            line = f"{offset:08X} | "
            
            # Hex
            ascii_chars = ""
            for i in range(16):
                if offset + i < len(self.data):
                    byte_val = self.data[offset + i]
                    marker = ">" if offset + i == self.selected_offset else " "
                    line += f"{marker}{byte_val:02X}"
                    ascii_chars += chr(byte_val) if 32 <= byte_val < 127 else "."
                else:
                    line += "   "
                    ascii_chars += " "
            
            line += f" | {ascii_chars}"
            print(line)
    
    def search(self, hex_string: str) -> List[int]:
        """搜索十六进制字符串"""
        # 移除空格
        hex_clean = hex_string.replace(" ", "")
        if len(hex_clean) % 2 != 0:
            return []
        
        # 转换为字节
        search_bytes = bytes.fromhex(hex_clean)
        
        results = []
        for i in range(len(self.data) - len(search_bytes) + 1):
            if self.data[i:i + len(search_bytes)] == search_bytes:
                results.append(i)
        
        return results
    
    def modify(self, offset: int, value: int, size: int = 1):
        """修改数据"""
        if size == 1:
            self.data[offset] = value & 0xFF
        elif size == 2:
            self.data[offset] = value & 0xFF
            self.data[offset + 1] = (value >> 8) & 0xFF
        elif size == 4:
            self.data[offset] = value & 0xFF
            self.data[offset + 1] = (value >> 8) & 0xFF
            self.data[offset + 2] = (value >> 16) & 0xFF
            self.data[offset + 3] = (value >> 24) & 0xFF


class SaveDataEditor:
    """PSP 存档编辑器主类"""
    
    def __init__(self, save_dir: str):
        self.save_dir = Path(save_dir)
        self.sfo_parser = SFOParser()
        self.crypto = SaveDataCrypto() if CRYPTO_AVAILABLE else None
        self.cheat_applier = CheatCodeApplier()
        
        self.sfo_data: Optional[SFOData] = None
        self.data_file: Optional[Path] = None
        self.decrypted_data: Optional[bytearray] = None
        
        self.load_save_data()
    
    def load_save_data(self):
        """加载存档数据"""
        # 加载 SFO
        sfo_path = self.save_dir / "PARAM.SFO"
        if sfo_path.exists():
            self.sfo_data = self.sfo_parser.parse(str(sfo_path))
        
        # 查找数据文件
        for name in ["DATA.BIN", "data.bin", "SECURE.BIN", "secure.bin"]:
            data_path = self.save_dir / name
            if data_path.exists():
                self.data_file = data_path
                break
    
    def print_info(self):
        """打印存档信息"""
        print("=" * 60)
        print("PSP 存档信息")
        print("=" * 60)
        
        if self.sfo_data:
            print(f"游戏标题: {self.sfo_data.game_title}")
            print(f"存档标题: {self.sfo_data.save_title}")
            print(f"存档详情: {self.sfo_data.save_detail}")
            print(f"游戏ID:   {self.sfo_data.title_id}")
        else:
            print("未找到 SFO 文件")
        
        if self.data_file:
            print(f"\n数据文件: {self.data_file.name}")
            print(f"文件大小: {self.data_file.stat().st_size} 字节")
        else:
            print("\n未找到数据文件")
        
        print("=" * 60)
    
    def decrypt(self) -> bool:
        """解密存档"""
        if not self.crypto:
            print("加密库未安装，无法解密")
            return False
        
        if not self.data_file:
            print("未找到数据文件")
            return False
        
        try:
            with open(self.data_file, 'rb') as f:
                data = f.read()
            
            decrypted = self.crypto.decrypt(data)
            self.decrypted_data = bytearray(decrypted)
            
            print(f"解密成功，数据大小: {len(self.decrypted_data)} 字节")
            return True
            
        except Exception as e:
            print(f"解密失败: {e}")
            return False
    
    def encrypt(self, output_path: Optional[str] = None) -> bool:
        """加密存档"""
        if not self.crypto:
            print("加密库未安装，无法加密")
            return False
        
        if self.decrypted_data is None:
            print("没有可加密的数据，请先解密")
            return False
        
        try:
            encrypted = self.crypto.encrypt(bytes(self.decrypted_data))
            
            save_path = output_path or str(self.data_file)
            with open(save_path, 'wb') as f:
                f.write(encrypted)
            
            print(f"加密成功，已保存到: {save_path}")
            return True
            
        except Exception as e:
            print(f"加密失败: {e}")
            return False
    
    def hex_edit(self):
        """启动十六进制编辑器"""
        if self.decrypted_data is None:
            print("请先解密存档")
            return
        
        editor = HexEditor(self.decrypted_data)
        
        while True:
            editor.display()
            
            print("\n命令:")
            print("  s <hex>    - 搜索十六进制值")
            print("  g <offset> - 跳转到偏移")
            print("  m <offset> <value> <size> - 修改值 (size=1/2/4)")
            print("  q          - 退出")
            
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'q':
                break
            
            elif cmd.startswith('s '):
                hex_str = cmd[2:].strip()
                results = editor.search(hex_str)
                if results:
                    print(f"找到 {len(results)} 处匹配")
                    editor.selected_offset = results[0]
                else:
                    print("未找到匹配")
            
            elif cmd.startswith('g '):
                try:
                    offset = int(cmd[2:].strip(), 16)
                    editor.selected_offset = offset
                except ValueError:
                    print("无效的偏移值")
            
            elif cmd.startswith('m '):
                parts = cmd[2:].split()
                if len(parts) >= 2:
                    try:
                        offset = int(parts[0], 16)
                        value = int(parts[1], 16)
                        size = int(parts[2]) if len(parts) > 2 else 1
                        editor.modify(offset, value, size)
                        print(f"已修改 0x{offset:08X} = 0x{value:0{size*2}X}")
                    except ValueError:
                        print("无效的输入")
    
    def apply_cheat_codes(self, codes_text: str):
        """应用 CWCheat 代码"""
        if self.decrypted_data is None:
            print("请先解密存档")
            return
        
        lines = codes_text.strip().split('\n')
        success, message, modified = self.cheat_applier.apply_codes(self.decrypted_data, lines)
        
        print(message)
        if modified:
            print(f"修改的偏移: {[hex(x) for x in modified]}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='PSP/PPSSPP 存档编辑器')
    parser.add_argument('save_dir', help='存档文件夹路径')
    parser.add_argument('--info', '-i', action='store_true', help='显示存档信息')
    parser.add_argument('--decrypt', '-d', action='store_true', help='解密存档')
    parser.add_argument('--encrypt', '-e', action='store_true', help='加密存档')
    parser.add_argument('--hex', '-x', action='store_true', help='启动十六进制编辑器')
    parser.add_argument('--cheat', '-c', help='应用 CWCheat 代码文件')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.save_dir):
        print(f"错误: 目录不存在: {args.save_dir}")
        sys.exit(1)
    
    editor = SaveDataEditor(args.save_dir)
    
    if args.info or not any([args.decrypt, args.encrypt, args.hex, args.cheat]):
        editor.print_info()
    
    if args.decrypt:
        editor.decrypt()
    
    if args.cheat:
        if os.path.isfile(args.cheat):
            with open(args.cheat, 'r') as f:
                codes = f.read()
            editor.apply_cheat_codes(codes)
        else:
            editor.apply_cheat_codes(args.cheat)
    
    if args.hex:
        if editor.decrypted_data is None:
            editor.decrypt()
        editor.hex_edit()
    
    if args.encrypt:
        editor.encrypt(args.output)


if __name__ == '__main__':
    main()

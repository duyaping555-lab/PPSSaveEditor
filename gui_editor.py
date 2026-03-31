#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPSSPP Save Editor - Windows GUI Version
使用 tkinter 创建图形界面
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from psp_save_editor import (
    SFOParser, SaveDataCrypto, CheatCodeApplier,
    SaveDataEditor, HexEditor
)


class PSSaveEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PPSSPP Save Editor v1.0")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # 设置主题
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("TButton", background="#404040", foreground="white")
        
        self.save_editor = None
        self.decrypted_data = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # 标题
        title = tk.Label(
            self.root,
            text="PPSSPP Save Editor",
            font=("Arial", 20, "bold"),
            bg="#2b2b2b",
            fg="#00ff00"
        )
        title.pack(pady=10)
        
        # 警告
        warning = tk.Label(
            self.root,
            text="⚠ 修改前务必备份原始存档!",
            font=("Arial", 10, "bold"),
            bg="#2b2b2b",
            fg="#ff4444"
        )
        warning.pack()
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="存档文件", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(file_frame, textvariable=self.path_var, width=70)
        path_entry.pack(side=tk.LEFT, padx=5)
        
        browse_btn = ttk.Button(file_frame, text="浏览...", command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        load_btn = ttk.Button(file_frame, text="加载", command=self.load_save)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # 存档信息区域
        info_frame = ttk.LabelFrame(main_frame, text="存档信息", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = tk.Text(
            info_frame,
            height=4,
            width=80,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 10)
        )
        self.info_text.pack(fill=tk.X)
        
        # 操作按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.decrypt_btn = ttk.Button(
            btn_frame,
            text="🔓 解密存档",
            command=self.decrypt_save,
            state=tk.DISABLED
        )
        self.decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        self.encrypt_btn = ttk.Button(
            btn_frame,
            text="🔒 加密保存",
            command=self.encrypt_save,
            state=tk.DISABLED
        )
        self.encrypt_btn.pack(side=tk.LEFT, padx=5)
        
        self.hex_btn = ttk.Button(
            btn_frame,
            text="📝 十六进制编辑",
            command=self.open_hex_editor,
            state=tk.DISABLED
        )
        self.hex_btn.pack(side=tk.LEFT, padx=5)
        
        self.cheat_btn = ttk.Button(
            btn_frame,
            text="🎮 CWCheat代码",
            command=self.open_cheat_editor,
            state=tk.DISABLED
        )
        self.cheat_btn.pack(side=tk.LEFT, padx=5)
        
        # CWCheat 代码区域
        cheat_frame = ttk.LabelFrame(main_frame, text="CWCheat 代码", padding="10")
        cheat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.cheat_text = scrolledtext.ScrolledText(
            cheat_frame,
            wrap=tk.WORD,
            width=80,
            height=10,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 10)
        )
        self.cheat_text.pack(fill=tk.BOTH, expand=True)
        
        # 示例代码
        self.cheat_text.insert(tk.END, "; 示例代码格式:\n")
        self.cheat_text.insert(tk.END, "; _L 0x2XXXXXXX 0xYYYYYYYY  ; 32位写入\n")
        self.cheat_text.insert(tk.END, "; _L 0x1XXXXXXX 0x0000YYYY  ; 16位写入\n")
        self.cheat_text.insert(tk.END, "; _L 0x0XXXXXXX 0x000000YY  ; 8位写入\n\n")
        self.cheat_text.insert(tk.END, "_L 0x20000000 0x0098967F  ; 金钱 9999999\n")
        
        # 应用代码按钮
        apply_btn = ttk.Button(
            cheat_frame,
            text="应用代码",
            command=self.apply_cheat_codes
        )
        apply_btn.pack(pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 - 请选择一个存档文件夹")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN
        )
        status_bar.pack(fill=tk.X, pady=5)
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
    
    def load_save(self):
        path = self.path_var.get()
        if not path or not os.path.isdir(path):
            messagebox.showerror("错误", "请选择有效的存档文件夹")
            return
        
        try:
            self.save_editor = SaveDataEditor(path)
            
            info = []
            if self.save_editor.sfo_data:
                sfo = self.save_editor.sfo_data
                info.append(f"游戏标题: {sfo.game_title}")
                info.append(f"存档标题: {sfo.save_title}")
                info.append(f"游戏ID: {sfo.title_id}")
            
            if self.save_editor.data_file:
                size = self.save_editor.data_file.stat().st_size
                info.append(f"数据文件: {self.save_editor.data_file.name} ({size} 字节)")
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "\n".join(info))
            
            self.decrypt_btn.config(state=tk.NORMAL)
            self.status_var.set("存档已加载，点击解密按钮")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载存档失败:\n{e}")
    
    def decrypt_save(self):
        if not self.save_editor:
            return
        
        try:
            if self.save_editor.decrypt():
                self.decrypted_data = self.save_editor.decrypted_data
                self.encrypt_btn.config(state=tk.NORMAL)
                self.hex_btn.config(state=tk.NORMAL)
                self.cheat_btn.config(state=tk.NORMAL)
                self.status_var.set(f"解密成功！数据大小: {len(self.decrypted_data)} 字节")
                messagebox.showinfo("成功", "存档解密成功！")
            else:
                messagebox.showwarning("警告", "解密可能失败，请检查存档格式")
        except Exception as e:
            messagebox.showerror("错误", f"解密失败:\n{e}")
    
    def encrypt_save(self):
        if not self.save_editor:
            return
        
        try:
            output_path = filedialog.asksaveasfilename(
                defaultextension=".bin",
                filetypes=[("BIN files", "*.bin"), ("All files", "*.*")]
            )
            
            if output_path:
                if self.save_editor.encrypt(output_path):
                    self.status_var.set(f"已保存到: {output_path}")
                    messagebox.showinfo("成功", f"加密完成！\n保存位置:\n{output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"加密失败:\n{e}")
    
    def open_hex_editor(self):
        if self.decrypted_data is None:
            messagebox.showwarning("警告", "请先解密存档")
            return
        
        hex_window = tk.Toplevel(self.root)
        hex_window.title("十六进制编辑器")
        hex_window.geometry("800x600")
        hex_window.configure(bg="#1e1e1e")
        
        # 工具栏
        toolbar = ttk.Frame(hex_window)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(toolbar, text="搜索:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(toolbar, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # 十六进制显示
        text_widget = tk.Text(
            hex_window,
            wrap=tk.NONE,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 显示数据
        data = bytes(self.decrypted_data)
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:08x}  {hex_str:<48}  {ascii_str}")
        
        text_widget.insert(tk.END, "\n".join(lines))
        text_widget.config(state=tk.DISABLED)
        
        # 修改功能
        modify_frame = ttk.Frame(hex_window)
        modify_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(modify_frame, text="偏移:").pack(side=tk.LEFT, padx=5)
        offset_entry = ttk.Entry(modify_frame, width=10)
        offset_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(modify_frame, text="值(十六进制):").pack(side=tk.LEFT, padx=5)
        value_entry = ttk.Entry(modify_frame, width=15)
        value_entry.pack(side=tk.LEFT, padx=5)
        
        def modify_data():
            try:
                offset = int(offset_entry.get(), 16)
                value = int(value_entry.get(), 16)
                
                if offset < len(self.decrypted_data):
                    self.decrypted_data[offset] = value & 0xFF
                    messagebox.showinfo("成功", f"已修改 0x{offset:08x} = 0x{value:02x}")
                else:
                    messagebox.showerror("错误", "偏移超出范围")
            except ValueError:
                messagebox.showerror("错误", "无效的十六进制值")
        
        ttk.Button(modify_frame, text="修改", command=modify_data).pack(side=tk.LEFT, padx=5)
    
    def open_cheat_editor(self):
        self.cheat_text.focus()
        self.status_var.set("在下方编辑CWCheat代码，然后点击应用代码")
    
    def apply_cheat_codes(self):
        if self.decrypted_data is None:
            messagebox.showwarning("警告", "请先解密存档")
            return
        
        codes_text = self.cheat_text.get(1.0, tk.END)
        lines = [line.strip() for line in codes_text.split('\n') if line.strip()]
        
        try:
            applier = CheatCodeApplier()
            success, message, modified = applier.apply_codes(self.decrypted_data, lines)
            
            if success:
                self.status_var.set(message)
                messagebox.showinfo("成功", f"{message}\n\n修改位置:\n" + 
                                  "\n".join([f"0x{addr:08x}" for addr in modified[:10]]))
            else:
                messagebox.showwarning("警告", message)
        except Exception as e:
            messagebox.showerror("错误", f"应用代码失败:\n{e}")


def main():
    root = tk.Tk()
    app = PSSaveEditorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

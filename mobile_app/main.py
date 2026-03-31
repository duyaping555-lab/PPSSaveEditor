#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPSSPP 存档编辑器 - Kivy 版本
可打包为 Android APK
"""

import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import BooleanProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import platform

# 设置深色主题
Window.clearcolor = (0.1, 0.1, 0.1, 1)

# 导入存档编辑器核心功能
from psp_save_editor import SFOParser, SaveDataCrypto, CheatCodeApplier, SaveDataEditor


class HexRow(RecycleDataViewBehavior, BoxLayout):
    """十六进制行视图"""
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    
    offset_text = StringProperty("")
    hex_text = StringProperty("")
    ascii_text = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 30
        
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # 偏移量标签
        self.offset_label = Label(
            text=self.offset_text,
            size_hint_x=0.2,
            font_name='monospace',
            color=(0.5, 0.5, 0.5, 1),
            font_size='12sp'
        )
        self.bind(offset_text=self.offset_label.setter('text'))
        
        # 十六进制标签
        self.hex_label = Label(
            text=self.hex_text,
            size_hint_x=0.5,
            font_name='monospace',
            color=(0, 1, 0, 1),
            font_size='12sp'
        )
        self.bind(hex_text=self.hex_label.setter('text'))
        
        # ASCII标签
        self.ascii_label = Label(
            text=self.ascii_text,
            size_hint_x=0.3,
            font_name='monospace',
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        self.bind(ascii_text=self.ascii_label.setter('text'))
        
        self.add_widget(self.offset_label)
        self.add_widget(self.hex_label)
        self.add_widget(self.ascii_label)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.offset_text = data['offset']
        self.hex_text = data['hex']
        self.ascii_text = data['ascii']
        return super().refresh_view_attrs(rv, index, data)


class HexEditorWidget(BoxLayout):
    """十六进制编辑器组件"""
    
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.data_bytes = bytearray(data)
        self.selected_offset = 0
        
        # 工具栏
        toolbar = BoxLayout(size_hint_y=None, height=50)
        
        self.search_input = TextInput(
            hint_text='搜索十六进制 (如: 00 FF)',
            multiline=False,
            size_hint_x=0.4
        )
        
        search_btn = Button(text='搜索', size_hint_x=0.15)
        search_btn.bind(on_press=self.search_hex)
        
        goto_btn = Button(text='跳转', size_hint_x=0.15)
        goto_btn.bind(on_press=self.show_goto)
        
        modify_btn = Button(text='修改', size_hint_x=0.15)
        modify_btn.bind(on_press=self.show_modify)
        
        save_btn = Button(text='保存', size_hint_x=0.15)
        save_btn.bind(on_press=self.save_data)
        
        toolbar.add_widget(self.search_input)
        toolbar.add_widget(search_btn)
        toolbar.add_widget(goto_btn)
        toolbar.add_widget(modify_btn)
        toolbar.add_widget(save_btn)
        
        self.add_widget(toolbar)
        
        # 标题行
        header = BoxLayout(size_hint_y=None, height=25)
        header.add_widget(Label(text='偏移', size_hint_x=0.2, font_name='monospace', color=(0.5, 0.5, 0.5, 1)))
        header.add_widget(Label(text='00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F', 
                                size_hint_x=0.5, font_name='monospace', color=(0, 1, 0, 1)))
        header.add_widget(Label(text='ASCII', size_hint_x=0.3, font_name='monospace', color=(1, 1, 1, 1)))
        self.add_widget(header)
        
        # 十六进制视图
        self.hex_view = RecycleView()
        self.hex_view.viewclass = HexRow
        self.hex_view.layout_manager = RecycleBoxLayout(
            default_size=(None, 30),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation='vertical'
        )
        self.hex_view.layout_manager.bind(
            minimum_height=self.hex_view.layout_manager.setter('height')
        )
        
        scroll = ScrollView()
        scroll.add_widget(self.hex_view)
        self.add_widget(scroll)
        
        # 状态栏
        self.status_label = Label(
            text='就绪',
            size_hint_y=None,
            height=30,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.status_label)
        
        self.refresh_data()
    
    def refresh_data(self):
        """刷新十六进制显示"""
        data_list = []
        bytes_per_row = 16
        
        for i in range(0, len(self.data_bytes), bytes_per_row):
            offset = i
            row_bytes = self.data_bytes[i:i+bytes_per_row]
            
            # 偏移量
            offset_str = f'{offset:08X}'
            
            # 十六进制
            hex_str = ' '.join(f'{b:02X}' for b in row_bytes)
            hex_str = hex_str.ljust(48)  # 对齐
            
            # ASCII
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row_bytes)
            
            data_list.append({
                'offset': offset_str,
                'hex': hex_str,
                'ascii': ascii_str
            })
        
        self.hex_view.data = data_list
    
    def search_hex(self, instance):
        """搜索十六进制值"""
        search_text = self.search_input.text.strip().replace(' ', '')
        if not search_text or len(search_text) % 2 != 0:
            self.status_label.text = '无效的搜索值'
            return
        
        try:
            search_bytes = bytes.fromhex(search_text)
        except ValueError:
            self.status_label.text = '无效的十六进制'
            return
        
        data = bytes(self.data_bytes)
        pos = data.find(search_bytes)
        
        if pos >= 0:
            self.selected_offset = pos
            self.status_label.text = f'找到匹配: 0x{pos:08X}'
            # 滚动到对应位置
            row = pos // 16
            self.hex_view.scroll_y = 1 - (row / len(self.hex_view.data))
        else:
            self.status_label.text = '未找到匹配'
    
    def show_goto(self, instance):
        """显示跳转对话框"""
        content = BoxLayout(orientation='vertical')
        input_field = TextInput(hint_text='输入偏移 (十六进制)', multiline=False)
        content.add_widget(input_field)
        
        popup = Popup(title='跳转到偏移', content=content, size_hint=(0.8, 0.3))
        
        def do_goto(instance):
            try:
                offset = int(input_field.text, 16)
                if 0 <= offset < len(self.data_bytes):
                    self.selected_offset = offset
                    row = offset // 16
                    self.hex_view.scroll_y = 1 - (row / len(self.hex_view.data))
                    self.status_label.text = f'当前偏移: 0x{offset:08X}'
                popup.dismiss()
            except ValueError:
                self.status_label.text = '无效的偏移值'
        
        btn = Button(text='跳转', size_hint_y=None, height=50)
        btn.bind(on_press=do_goto)
        content.add_widget(btn)
        
        popup.open()
    
    def show_modify(self, instance):
        """显示修改对话框"""
        content = GridLayout(cols=2)
        
        content.add_widget(Label(text='偏移:', color=(1, 1, 1, 1)))
        offset_input = TextInput(text=f'{self.selected_offset:08X}', multiline=False)
        content.add_widget(offset_input)
        
        content.add_widget(Label(text='值 (十六进制):', color=(1, 1, 1, 1)))
        value_input = TextInput(hint_text='如: 7F96', multiline=False)
        content.add_widget(value_input)
        
        content.add_widget(Label(text='类型:', color=(1, 1, 1, 1)))
        type_input = TextInput(text='4', hint_text='1/2/4 字节', multiline=False)
        content.add_widget(type_input)
        
        popup = Popup(title='修改数值', content=content, size_hint=(0.8, 0.4))
        
        def do_modify(instance):
            try:
                offset = int(offset_input.text, 16)
                value = int(value_input.text, 16)
                size = int(type_input.text)
                
                if offset + size > len(self.data_bytes):
                    self.status_label.text = '偏移超出范围'
                    return
                
                # 写入值（小端序）
                for i in range(size):
                    self.data_bytes[offset + i] = (value >> (i * 8)) & 0xFF
                
                self.refresh_data()
                self.status_label.text = f'已修改 0x{offset:08X} = 0x{value:0{size*2}X}'
                popup.dismiss()
            except ValueError:
                self.status_label.text = '输入无效'
        
        btn = Button(text='修改', size_hint_y=None, height=50)
        btn.bind(on_press=do_modify)
        content.add_widget(btn)
        content.add_widget(Button(text='取消', on_press=popup.dismiss, size_hint_y=None, height=50))
        
        popup.open()
    
    def save_data(self, instance):
        """保存数据"""
        # 通知父组件数据已修改
        if hasattr(self, 'on_data_changed'):
            self.on_data_changed(bytes(self.data_bytes))
        self.status_label.text = '数据已保存'
    
    def get_data(self):
        """获取当前数据"""
        return bytes(self.data_bytes)


class CheatCodeWidget(BoxLayout):
    """CWCheat 代码组件"""
    
    def __init__(self, data, on_apply=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.data = bytearray(data)
        self.on_apply = on_apply
        
        # 说明标签
        info = Label(
            text='输入 CWCheat 代码 (每行一个):\n_L 0x2XXXXXXX 0xYYYYYYYY',
            size_hint_y=None,
            height=60,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(info)
        
        # 代码输入
        self.code_input = TextInput(
            hint_text='_L 0x20555678 0x0098967F  ; 金钱\n_L 0x2055567C 0x0000270F  ; HP',
            multiline=True,
            font_name='monospace',
            foreground_color=(0, 1, 0, 1),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        self.add_widget(self.code_input)
        
        # 按钮栏
        btn_box = BoxLayout(size_hint_y=None, height=50)
        
        apply_btn = Button(text='应用代码')
        apply_btn.bind(on_press=self.apply_codes)
        
        btn_box.add_widget(apply_btn)
        self.add_widget(btn_box)
        
        # 状态标签
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=30,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.status_label)
    
    def apply_codes(self, instance):
        """应用代码"""
        codes_text = self.code_input.text
        if not codes_text.strip():
            self.status_label.text = '请输入代码'
            return
        
        applier = CheatCodeApplier()
        lines = codes_text.split('\n')
        
        success, message, modified = applier.apply_codes(self.data, lines)
        
        self.status_label.text = message
        
        if success and self.on_apply:
            self.on_apply(bytes(self.data))


class MainWidget(BoxLayout):
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.save_editor = None
        self.decrypted_data = None
        
        # 标题
        title = Label(
            text='PPSSPP 存档编辑器',
            font_size='24sp',
            bold=True,
            size_hint_y=None,
            height=50,
            color=(1, 1, 1, 1)
        )
        self.add_widget(title)
        
        # 警告
        warning = Label(
            text='警告: 修改前务必备份存档!',
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30
        )
        self.add_widget(warning)
        
        # 文件选择按钮
        self.file_btn = Button(
            text='选择存档文件夹',
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.5, 0.8, 1)
        )
        self.file_btn.bind(on_press=self.show_file_chooser)
        self.add_widget(self.file_btn)
        
        # 路径显示
        self.path_label = Label(
            text='未选择存档',
            size_hint_y=None,
            height=30,
            color=(0.7, 0.7, 0.7, 1)
        )
        self.add_widget(self.path_label)
        
        # 存档信息
        self.info_label = Label(
            text='',
            size_hint_y=None,
            height=80,
            color=(0.9, 0.9, 0.9, 1),
            markup=True
        )
        self.add_widget(self.info_label)
        
        # 操作按钮栏
        btn_box = GridLayout(cols=4, size_hint_y=None, height=50, spacing=5)
        
        self.decrypt_btn = Button(text='解密', disabled=True)
        self.decrypt_btn.bind(on_press=self.decrypt_save)
        btn_box.add_widget(self.decrypt_btn)
        
        self.encrypt_btn = Button(text='加密', disabled=True)
        self.encrypt_btn.bind(on_press=self.encrypt_save)
        btn_box.add_widget(self.encrypt_btn)
        
        self.hex_btn = Button(text='十六进制', disabled=True)
        self.hex_btn.bind(on_press=self.show_hex_editor)
        btn_box.add_widget(self.hex_btn)
        
        self.cheat_btn = Button(text='补丁代码', disabled=True)
        self.cheat_btn.bind(on_press=self.show_cheat_editor)
        btn_box.add_widget(self.cheat_btn)
        
        self.add_widget(btn_box)
        
        # 说明文字
        help_text = Label(
            text='使用说明:\n1. 选择存档文件夹\n2. 解密存档\n3. 编辑数据\n4. 加密保存',
            size_hint_y=None,
            height=100,
            color=(0.6, 0.6, 0.6, 1)
        )
        self.add_widget(help_text)
    
    def show_file_chooser(self, instance):
        """显示文件选择器"""
        # 在 Android 上直接使用路径输入
        if platform == 'android':
            self.show_path_input()
        else:
            self.show_desktop_file_chooser()
    
    def show_path_input(self):
        """显示路径输入对话框（Android）"""
        content = BoxLayout(orientation='vertical')
        
        # 常用路径按钮
        common_paths = BoxLayout(size_hint_y=None, height=100, orientation='vertical')
        
        btn_sd = Button(text='/sdcard/PSP/SAVEDATA/', size_hint_y=None, height=50)
        btn_sd.bind(on_press=lambda x: self.load_path('/sdcard/PSP/SAVEDATA/'))
        common_paths.add_widget(btn_sd)
        
        content.add_widget(Label(text='或输入完整路径:', color=(1, 1, 1, 1)))
        
        path_input = TextInput(
            hint_text='/sdcard/PSP/SAVEDATA/ULJM12345',
            multiline=False
        )
        content.add_widget(path_input)
        
        popup = Popup(title='选择存档路径', content=content, size_hint=(0.9, 0.5))
        
        def load_custom(instance):
            path = path_input.text.strip()
            if path:
                self.load_path(path)
                popup.dismiss()
        
        btn_box = BoxLayout(size_hint_y=None, height=50)
        btn_box.add_widget(Button(text='加载', on_press=load_custom))
        btn_box.add_widget(Button(text='取消', on_press=popup.dismiss))
        content.add_widget(btn_box)
        
        popup.open()
    
    def show_desktop_file_chooser(self):
        """显示桌面文件选择器"""
        content = BoxLayout(orientation='vertical')
        
        file_chooser = FileChooserListView(
            path=str(Path.home()),
            dirselect=True
        )
        content.add_widget(file_chooser)
        
        popup = Popup(title='选择存档文件夹', content=content, size_hint=(0.9, 0.8))
        
        def on_select(instance):
            if file_chooser.selection:
                self.load_path(file_chooser.selection[0])
                popup.dismiss()
        
        btn_box = BoxLayout(size_hint_y=None, height=50)
        btn_box.add_widget(Button(text='选择', on_press=on_select))
        btn_box.add_widget(Button(text='取消', on_press=popup.dismiss))
        content.add_widget(btn_box)
        
        popup.open()
    
    def load_path(self, path):
        """加载存档路径"""
        try:
            self.save_editor = SaveDataEditor(path)
            self.path_label.text = f'路径: {path}'
            
            info_text = ''
            if self.save_editor.sfo_data:
                sfo = self.save_editor.sfo_data
                info_text = f'[b]游戏:[/b] {sfo.game_title}\n'
                info_text += f'[b]存档:[/b] {sfo.save_title}\n'
                info_text += f'[b]ID:[/b] {sfo.title_id}'
            else:
                info_text = '未找到 SFO 文件'
            
            if self.save_editor.data_file:
                size = self.save_editor.data_file.stat().st_size
                info_text += f'\n[b]大小:[/b] {size} 字节'
            
            self.info_label.text = info_text
            
            self.decrypt_btn.disabled = False
            
        except Exception as e:
            self.path_label.text = f'错误: {str(e)}'
    
    def decrypt_save(self, instance):
        """解密存档"""
        if not self.save_editor:
            return
        
        try:
            if self.save_editor.decrypt():
                self.decrypted_data = self.save_editor.decrypted_data
                self.encrypt_btn.disabled = False
                self.hex_btn.disabled = False
                self.cheat_btn.disabled = False
                self.info_label.text += '\n[color=00FF00]解密成功[/color]'
        except Exception as e:
            self.info_label.text += f'\n[color=FF0000]解密失败: {e}[/color]'
    
    def encrypt_save(self, instance):
        """加密存档"""
        if not self.save_editor:
            return
        
        try:
            if self.save_editor.encrypt():
                self.info_label.text += '\n[color=00FF00]加密成功[/color]'
        except Exception as e:
            self.info_label.text += f'\n[color=FF0000]加密失败: {e}[/color]'
    
    def show_hex_editor(self, instance):
        """显示十六进制编辑器"""
        if self.decrypted_data is None:
            return
        
        content = BoxLayout()
        hex_editor = HexEditorWidget(self.decrypted_data)
        hex_editor.on_data_changed = self.on_data_changed
        content.add_widget(hex_editor)
        
        popup = Popup(
            title='十六进制编辑器',
            content=content,
            size_hint=(0.95, 0.9)
        )
        popup.open()
    
    def show_cheat_editor(self, instance):
        """显示补丁代码编辑器"""
        if self.decrypted_data is None:
            return
        
        content = BoxLayout()
        cheat_editor = CheatCodeWidget(self.decrypted_data, on_apply=self.on_data_changed)
        content.add_widget(cheat_editor)
        
        popup = Popup(
            title='CWCheat 代码',
            content=content,
            size_hint=(0.9, 0.7)
        )
        popup.open()
    
    def on_data_changed(self, new_data):
        """数据修改回调"""
        self.decrypted_data = bytearray(new_data)
        if self.save_editor:
            self.save_editor.decrypted_data = self.decrypted_data


class PPSSaveEditorApp(App):
    """Kivy 应用"""
    
    def build(self):
        self.title = 'PPSSPP 存档编辑器'
        return MainWidget()


if __name__ == '__main__':
    PPSSaveEditorApp().run()

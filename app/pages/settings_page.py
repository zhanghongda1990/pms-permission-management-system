import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
from datetime import datetime
from pathlib import Path
from ..utils.config_manager import ConfigManager
from ..utils.path_utils import PathUtils
from ..utils.logger import Logger


class SettingsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        self.create_header()
        self.create_settings_area()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='系统设置', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)

    def create_settings_area(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        path_frame = ttk.Frame(notebook)
        notebook.add(path_frame, text='路径设置')
        self.create_path_settings(path_frame)
        
        backup_frame = ttk.Frame(notebook)
        notebook.add(backup_frame, text='备份恢复')
        self.create_backup_settings(backup_frame)
        
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text='系统信息')
        self.create_system_info(info_frame)
        
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text='日志查看')
        self.create_log_viewer(log_frame)

    def create_path_settings(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text='应用根目录:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.root_dir_label = ttk.Label(frame, text='')
        self.root_dir_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text='数据目录:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.data_dir_label = ttk.Label(frame, text='')
        self.data_dir_label.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text='模板目录:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.template_dir_label = ttk.Label(frame, text='')
        self.template_dir_label.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text='导出目录:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.export_dir_label = ttk.Label(frame, text='')
        self.export_dir_label.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text='日志目录:').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.log_dir_label = ttk.Label(frame, text='')
        self.log_dir_label.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=20)
        
        ttk.Button(frame, text='打开数据目录', command=self.open_data_dir).grid(row=6, column=0, pady=5)
        ttk.Button(frame, text='打开导出目录', command=self.open_export_dir).grid(row=6, column=1, pady=5, sticky=tk.W)

    def create_backup_settings(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        backup_btn_frame = ttk.Frame(frame)
        backup_btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(backup_btn_frame, text='备份数据', command=self.backup_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_btn_frame, text='恢复数据', command=self.restore_data).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        ttk.Label(frame, text='数据初始化:').pack(anchor=tk.W)
        ttk.Label(frame, text='警告: 初始化将清除所有数据，此操作不可恢复！', foreground='red').pack(anchor=tk.W, pady=5)
        
        ttk.Button(frame, text='初始化数据', command=self.init_data).pack(anchor=tk.W, pady=10)

    def create_system_info(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        info_items = [
            ('应用名称', ConfigManager.get('app_name')),
            ('版本号', ConfigManager.get('version')),
            ('系统数量', str(len(ConfigManager.get_systems()))),
            ('运行环境', 'Python ' + self.get_python_version()),
            ('操作系统', self.get_os_info()),
        ]
        
        for i, (label, value) in enumerate(info_items):
            ttk.Label(frame, text=f'{label}:').grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Label(frame, text=value).grid(row=i, column=1, sticky=tk.W, pady=5)

    def create_log_viewer(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text='刷新日志', command=self.refresh_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='清空日志', command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        self.log_text = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_log()

    def load_settings(self):
        self.root_dir_label.config(text=ConfigManager.get_root_dir())
        self.data_dir_label.config(text=ConfigManager.get_data_dir())
        self.template_dir_label.config(text=ConfigManager.get_template_dir())
        self.export_dir_label.config(text=ConfigManager.get_export_dir())
        self.log_dir_label.config(text=ConfigManager.get_log_dir())

    def open_data_dir(self):
        import os
        data_dir = ConfigManager.get_data_dir()
        if Path(data_dir).exists():
            os.startfile(data_dir)
        else:
            messagebox.showwarning('提示', '数据目录不存在')

    def open_export_dir(self):
        import os
        export_dir = ConfigManager.get_export_dir()
        PathUtils.ensure_dir(export_dir)
        os.startfile(export_dir)

    def backup_data(self):
        file_path = filedialog.asksaveasfilename(
            title='保存备份',
            defaultextension='.zip',
            filetypes=[('ZIP文件', '*.zip')],
            initialfile=f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
        if file_path:
            try:
                data_dir = ConfigManager.get_data_dir()
                shutil.make_archive(file_path.replace('.zip', ''), 'zip', data_dir)
                messagebox.showinfo('成功', f'数据已备份到: {file_path}')
                Logger.info(f'数据备份成功: {file_path}')
            except Exception as e:
                messagebox.showerror('错误', f'备份失败: {e}')
                Logger.error(f'数据备份失败: {e}')

    def restore_data(self):
        file_path = filedialog.askopenfilename(
            title='选择备份文件',
            filetypes=[('ZIP文件', '*.zip')]
        )
        
        if file_path:
            if messagebox.askyesno('确认', '恢复数据将覆盖当前数据，是否继续？'):
                try:
                    data_dir = ConfigManager.get_data_dir()
                    shutil.unpack_archive(file_path, data_dir)
                    messagebox.showinfo('成功', '数据已恢复，请重启应用')
                    Logger.info(f'数据恢复成功: {file_path}')
                except Exception as e:
                    messagebox.showerror('错误', f'恢复失败: {e}')
                    Logger.error(f'数据恢复失败: {e}')

    def init_data(self):
        if messagebox.askyesno('警告', '确定要初始化数据吗？所有数据将被清除！'):
            if messagebox.askyesno('再次确认', '此操作不可恢复，确定继续吗？'):
                try:
                    data_dir = ConfigManager.get_data_dir()
                    for file in Path(data_dir).glob('*.parquet'):
                        file.unlink()
                    
                    from ..utils.data_manager import DataManager
                    DataManager()._init_personnel()
                    DataManager()._init_systems()
                    DataManager()._init_permissions()
                    DataManager()._init_permission_assignments()
                    DataManager()._init_permission_packages()
                    
                    messagebox.showinfo('成功', '数据已初始化')
                    Logger.info('数据初始化完成')
                except Exception as e:
                    messagebox.showerror('错误', f'初始化失败: {e}')
                    Logger.error(f'数据初始化失败: {e}')

    def refresh_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        log_file = PathUtils.get_log_file()
        if Path(log_file).exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]
                    self.log_text.insert(tk.END, ''.join(lines))
            except Exception as e:
                self.log_text.insert(tk.END, f'读取日志失败: {e}')
        else:
            self.log_text.insert(tk.END, '暂无日志')
        
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        if messagebox.askyesno('确认', '确定要清空日志吗？'):
            log_file = PathUtils.get_log_file()
            if Path(log_file).exists():
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write('')
            self.refresh_log()
            Logger.info('日志已清空')

    def get_python_version(self):
        import sys
        return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'

    def get_os_info(self):
        import platform
        return f'{platform.system()} {platform.release()}'

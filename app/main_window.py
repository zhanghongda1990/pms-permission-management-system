import tkinter as tk
from tkinter import ttk
from .utils.logger import Logger
from .utils.config_manager import ConfigManager
from .utils.data_manager import DataManager


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(ConfigManager.get('app_name', '权限管理系统'))
        self.root.geometry('1200x800')
        self.root.minsize(1000, 600)
        
        DataManager()
        
        self.setup_styles()
        self.create_widgets()
        
        self.current_page = None
        self.pages = {}
        
        Logger.info("主窗口初始化完成")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5', font=('Microsoft YaHei UI', 9))
        style.configure('TButton', font=('Microsoft YaHei UI', 9))
        style.configure('Header.TLabel', font=('Microsoft YaHei UI', 12, 'bold'))
        style.configure('Nav.TButton', font=('Microsoft YaHei UI', 10), width=15)
        
        style.configure('Nav.TFrame', background='#2c3e50')
        style.configure('Nav.TLabel', background='#2c3e50', foreground='white', font=('Microsoft YaHei UI', 11))
        style.configure('Nav.TButton', background='#2c3e50', foreground='white', borderwidth=0)
        style.map('Nav.TButton', background=[('active', '#34495e')])
        
        style.configure('Content.TFrame', background='#ffffff')
        style.configure('Status.TLabel', background='#ecf0f1', font=('Microsoft YaHei UI', 8))

    def create_widgets(self):
        self.root.configure(bg='#f5f5f5')
        
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        self.create_navigation(main_container)
        
        self.content_area = ttk.Frame(main_container, style='Content.TFrame')
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_status_bar()

    def create_navigation(self, parent):
        nav_frame = ttk.Frame(parent, style='Nav.TFrame', width=200)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        nav_frame.pack_propagate(False)
        
        title_label = ttk.Label(nav_frame, text='导航菜单', style='Nav.TLabel')
        title_label.pack(pady=(20, 10))
        
        nav_items = [
            ('首页', 'show_home'),
            ('人员管理', 'show_personnel'),
            ('系统管理', 'show_system'),
            ('权限信息', 'show_permission_info'),
            ('权限包', 'show_permission_package'),
            ('权限分配', 'show_permission_assign'),
            ('权限检查', 'show_permission_check'),
            ('统计查询', 'show_statistics'),
            ('导入与导出', 'show_import_export'),
            ('系统设置', 'show_settings')
        ]
        
        for text, command in nav_items:
            btn = ttk.Button(nav_frame, text=text, style='Nav.TButton', 
                            command=lambda c=command: self.navigate(c))
            btn.pack(fill=tk.X, padx=10, pady=5)

    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, style='Status.TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text='就绪', style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        version = ConfigManager.get('version', '1.0.0')
        version_label = ttk.Label(status_frame, text=f'版本: {version}', style='Status.TLabel')
        version_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def set_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def navigate(self, command):
        self.set_status(f'正在加载...')
        self.root.update()
        
        if self.current_page:
            self.current_page.pack_forget()
        
        if command == 'show_home':
            from .pages.home_page import HomePage
            self.current_page = HomePage(self.content_area)
        elif command == 'show_personnel':
            from .pages.personnel_page import PersonnelPage
            self.current_page = PersonnelPage(self.content_area)
        elif command == 'show_system':
            from .pages.system_page import SystemPage
            self.current_page = SystemPage(self.content_area)
        elif command == 'show_permission_info':
            from .pages.permission_info_page import PermissionInfoPage
            self.current_page = PermissionInfoPage(self.content_area)
        elif command == 'show_permission_package':
            from .pages.permission_package_page import PermissionPackagePage
            self.current_page = PermissionPackagePage(self.content_area)
        elif command == 'show_permission_assign':
            from .pages.permission_assign_page import PermissionAssignPage
            self.current_page = PermissionAssignPage(self.content_area)
        elif command == 'show_permission_check':
            from .pages.permission_check_page import PermissionCheckPage
            self.current_page = PermissionCheckPage(self.content_area)
        elif command == 'show_statistics':
            from .pages.statistics_page import StatisticsPage
            self.current_page = StatisticsPage(self.content_area)
        elif command == 'show_import_export':
            from .pages.import_export_page import ImportExportPage
            self.current_page = ImportExportPage(self.content_area)
        elif command == 'show_settings':
            from .pages.settings_page import SettingsPage
            self.current_page = SettingsPage(self.content_area)
        
        self.current_page.pack(fill=tk.BOTH, expand=True)
        self.set_status('就绪')

    def run(self):
        Logger.info("启动主窗口")
        self.navigate('show_home')
        self.root.mainloop()

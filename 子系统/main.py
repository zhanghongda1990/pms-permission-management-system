import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data_reader import DataReader
from application_manager import ApplicationManager
from datetime import datetime


class SubSystemApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('权限管理系统 - 子系统')
        self.root.geometry('1200x800')
        self.root.minsize(900, 600)
        
        self.reader = DataReader()
        self.app_manager = ApplicationManager()
        self.file_path = None
        
        self.setup_styles()
        self.create_menu()
        self.create_main_layout()
        
        self.try_auto_load()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Microsoft YaHei', 16, 'bold'))
        style.configure('SubHeader.TLabel', font=('Microsoft YaHei', 12, 'bold'))
        style.configure('Info.TLabel', font=('Microsoft YaHei', 10))
        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', font=('Microsoft YaHei', 10, 'bold'))
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='文件', menu=file_menu)
        file_menu.add_command(label='打开文件', command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.root.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='视图', menu=view_menu)
        view_menu.add_command(label='概览', command=lambda: self.show_page('overview'))
        view_menu.add_command(label='权限信息', command=lambda: self.show_page('permissions'))
        view_menu.add_command(label='权限包', command=lambda: self.show_page('packages'))
        view_menu.add_command(label='人员信息', command=lambda: self.show_page('personnel'))
        view_menu.add_command(label='授权记录', command=lambda: self.show_page('assignments'))
        view_menu.add_command(label='授权检查', command=lambda: self.show_page('authorization_check'))
        
        apply_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='操作', menu=apply_menu)
        apply_menu.add_command(label='操作权限包', command=lambda: self.show_page('apply_package'), state='disabled')
        apply_menu.add_command(label='申请授权', command=lambda: self.show_page('apply_authorization'), state='disabled')
        
    def create_main_layout(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.sidebar = ttk.Frame(self.main_frame, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar.pack_propagate(False)
        
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_sidebar()
        
    def create_sidebar(self):
        title_label = ttk.Label(self.sidebar, text='导航菜单', style='SubHeader.TLabel')
        title_label.pack(pady=10)
        
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        self.nav_buttons = {}
        nav_items = [
            ('overview', '概览'),
            ('permissions', '权限信息'),
            ('packages', '权限包'),
            ('personnel', '人员信息'),
            ('assignments', '授权记录'),
            ('authorization_check', '授权检查'),
            ('apply_package', '操作权限包'),
            ('apply_authorization', '申请授权')
        ]
        
        for key, text in nav_items:
            btn = ttk.Button(self.sidebar, text=text, command=lambda k=key: self.show_page(k))
            btn.pack(fill=tk.X, pady=2, padx=5)
            if key in ('apply_package', 'apply_authorization'):
                btn.config(state='disabled')
            self.nav_buttons[key] = btn
            
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.file_info_label = ttk.Label(self.sidebar, text='未加载文件', wraplength=180)
        self.file_info_label.pack(pady=5, padx=5)
        
        ttk.Button(self.sidebar, text='打开文件', command=self.open_file).pack(fill=tk.X, pady=5, padx=5)
    
    def try_auto_load(self):
        if self.reader.has_cached_data():
            cache_info = self.reader.get_cache_info()
            
            if self.reader.load_cached_data():
                stats = self.reader.get_statistics()
                data_type = '基础权限' if stats['data_type'] == 'permissions' else '机构信息'
                
                self.file_info_label.config(
                    text=f'已加载缓存:\n{data_type}\n缓存时间:\n{cache_info["cached_at"]}'
                )
                
                self.show_page('overview')
                self.root.after(500, lambda: messagebox.showinfo(
                    '自动加载',
                    f'已自动加载上次的数据\n\n'
                    f'数据类型: {data_type}\n'
                    f'缓存时间: {cache_info["cached_at"]}\n'
                    f'来源文件: {cache_info.get("source_file", "未知")}'
                ))
            else:
                self.create_welcome_page()
        else:
            self.create_welcome_page()
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title='选择导出文件',
            filetypes=[('YAML文件', '*.yml'), ('YAML文件', '*.yaml'), ('所有文件', '*.*')]
        )
        
        if not file_path:
            return
            
        try:
            self.reader.load_file(file_path)
            self.file_path = file_path
            
            stats = self.reader.get_statistics()
            data_type = '基础权限' if stats['data_type'] == 'permissions' else '机构信息'
            
            cache_info = self.reader.get_cache_info()
            cache_time = cache_info.get('cached_at', '') if cache_info else ''
            
            self.file_info_label.config(text=f'已加载: {data_type}\n缓存时间:\n{cache_time}')
            
            self.show_page('overview')
            messagebox.showinfo('成功', f'文件加载成功！\n数据类型: {data_type}\n已自动保存到系统存储')
            
        except Exception as e:
            messagebox.showerror('错误', f'加载文件失败: {e}')
            
    def show_page(self, page_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if self.reader.data is None:
            self.create_welcome_page()
            return
            
        if page_name == 'overview':
            self.create_overview_page()
        elif page_name == 'permissions':
            self.create_permissions_page()
        elif page_name == 'packages':
            self.create_packages_page()
        elif page_name == 'personnel':
            self.create_personnel_page()
        elif page_name == 'assignments':
            self.create_assignments_page()
        elif page_name == 'authorization_check':
            self.create_authorization_check_page()
        elif page_name == 'apply_package':
            self.create_apply_package_page()
        elif page_name == 'apply_authorization':
            self.create_apply_authorization_page()
            
    def create_welcome_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text='欢迎使用权限管理子系统', style='Header.TLabel').pack(pady=50)
        ttk.Label(frame, text='请通过"文件"菜单或左侧按钮打开导出的权限数据文件', 
                  style='Info.TLabel').pack(pady=10)
        ttk.Label(frame, text='支持的基础数据类型:', style='SubHeader.TLabel').pack(pady=20)
        
        info_frame = ttk.Frame(frame)
        info_frame.pack(pady=10)
        
        ttk.Label(info_frame, text='• 基础权限信息导出文件', style='Info.TLabel').pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text='• 机构信息导出文件', style='Info.TLabel').pack(anchor=tk.W, pady=2)
        
        cache_frame = ttk.LabelFrame(frame, text='存储信息', padding=10)
        cache_frame.pack(pady=30)
        
        cache_info = self.reader.get_cache_info()
        if cache_info:
            ttk.Label(cache_frame, text=f'缓存文件位置: {cache_info["file_path"]}', 
                      style='Info.TLabel').pack(anchor=tk.W, pady=2)
            ttk.Label(cache_frame, text=f'文件大小: {cache_info["file_size"]} 字节', 
                      style='Info.TLabel').pack(anchor=tk.W, pady=2)
        else:
            ttk.Label(cache_frame, text='暂无缓存数据，请打开导出文件', 
                      style='Info.TLabel').pack(anchor=tk.W, pady=2)
        
    def create_overview_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text='数据概览', style='Header.TLabel').pack(pady=10)
        
        stats = self.reader.get_statistics()
        
        info_frame = ttk.LabelFrame(frame, text='基本信息', padding=20)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        data_type = '基础权限信息' if stats['data_type'] == 'permissions' else '机构信息'
        
        info_items = [
            ('数据类型', data_type),
            ('导出时间', stats['export_time']),
            ('系统数量', stats['system_count']),
            ('权限数量', stats['permission_count'])
        ]
        
        if stats['data_type'] == 'organization':
            info_items.extend([
                ('机构名称', stats.get('organization', '')),
                ('权限包数量', stats.get('package_count', 0)),
                ('人员数量', stats.get('personnel_count', 0)),
                ('授权记录数', stats.get('assignment_count', 0))
            ])
            
        for i, (label, value) in enumerate(info_items):
            ttk.Label(info_frame, text=f'{label}:', style='Info.TLabel').grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=str(value), style='Info.TLabel').grid(row=i, column=1, sticky=tk.W, pady=5, padx=10)
            
        systems_frame = ttk.LabelFrame(frame, text='系统列表', padding=10)
        systems_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('name', 'code', 'permission_count')
        tree = ttk.Treeview(systems_frame, columns=columns, show='headings', height=10)
        
        tree.heading('name', text='系统名称')
        tree.heading('code', text='系统代码')
        tree.heading('permission_count', text='权限数量')
        
        tree.column('name', width=200)
        tree.column('code', width=150)
        tree.column('permission_count', width=100)
        
        for system in self.reader.get_systems():
            perm_count = self.reader._count_permissions(system.get('permissions', []))
            tree.insert('', tk.END, values=(system['name'], system.get('code', ''), perm_count))
            
        scrollbar = ttk.Scrollbar(systems_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_permissions_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text='权限信息', style='Header.TLabel').pack(side=tk.LEFT, padx=20)
        
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.LEFT, padx=20)
        ttk.Button(btn_frame, text='展开全部', command=self.expand_all_permissions).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='折叠全部', command=self.collapse_all_permissions).pack(side=tk.LEFT, padx=2)
        
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, padx=20)
        
        ttk.Label(search_frame, text='搜索:').pack(side=tk.LEFT)
        self.perm_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.perm_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text='搜索', command=self.search_permissions).pack(side=tk.LEFT)
        ttk.Button(search_frame, text='重置', command=self.reset_permissions_search).pack(side=tk.LEFT, padx=5)
        
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('code', 'level', 'status', 'description')
        self.perm_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=20)
        
        self.perm_tree.heading('#0', text='权限名称')
        self.perm_tree.heading('code', text='权限代码')
        self.perm_tree.heading('level', text='级别')
        self.perm_tree.heading('status', text='状态')
        self.perm_tree.heading('description', text='描述')
        
        self.perm_tree.column('#0', width=250)
        self.perm_tree.column('code', width=120)
        self.perm_tree.column('level', width=60)
        self.perm_tree.column('status', width=60)
        self.perm_tree.column('description', width=200)
        
        self.load_permissions_tree()
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.perm_tree.yview)
        self.perm_tree.configure(yscrollcommand=scrollbar.set)
        
        self.perm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def load_permissions_tree(self):
        for item in self.perm_tree.get_children():
            self.perm_tree.delete(item)
            
        systems = self.reader.get_systems()
        for system in systems:
            system_node = self.perm_tree.insert('', tk.END, text=f"📁 {system['name']}", open=True)
            self._add_permissions_to_tree(system.get('permissions', []), system_node, system['name'])
            
    def _add_permissions_to_tree(self, permissions, parent_node, system_name):
        for perm in permissions:
            name = perm.get('name', '')
            has_children = 'children' in perm and perm['children']
            icon = '📁' if has_children else '📄'
            node_text = f'{icon} {name}'
            
            node = self.perm_tree.insert(parent_node, tk.END, text=node_text, values=(
                perm.get('code', ''),
                perm.get('level', ''),
                perm.get('status', ''),
                perm.get('description', '')
            ), open=True)
            
            if has_children:
                self._add_permissions_to_tree(perm['children'], node, system_name)
                
    def expand_all_permissions(self):
        def expand_item(item):
            self.perm_tree.item(item, open=True)
            for child in self.perm_tree.get_children(item):
                expand_item(child)
        
        for item in self.perm_tree.get_children():
            expand_item(item)
            
    def collapse_all_permissions(self):
        def collapse_item(item):
            self.perm_tree.item(item, open=False)
            for child in self.perm_tree.get_children(item):
                collapse_item(child)
        
        for item in self.perm_tree.get_children():
            collapse_item(item)
                
    def search_permissions(self):
        keyword = self.perm_search_var.get().strip()
        if not keyword:
            self.load_permissions_tree()
            return
            
        for item in self.perm_tree.get_children():
            self.perm_tree.delete(item)
            
        results = self.reader.search_permissions(keyword)
        for result in results:
            self.perm_tree.insert('', tk.END, text=f"📄 {result['name']}", values=(
                result['code'],
                result.get('level', ''),
                result['status'],
                result['description']
            ))
            
    def reset_permissions_search(self):
        self.perm_search_var.set('')
        self.load_permissions_tree()
        
    def create_packages_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text='权限包信息', style='Header.TLabel').pack(pady=10)
        
        if self.reader.get_data_type() != 'organization':
            ttk.Label(frame, text='当前数据为"基础权限信息"，不包含权限包数据\n请加载"机构信息"导出文件', 
                      foreground='red').pack(pady=50)
            return
            
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('name', 'document_no', 'permission_count', 'description')
        self.pkg_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        self.pkg_tree.heading('name', text='权限包名称')
        self.pkg_tree.heading('document_no', text='文档编号')
        self.pkg_tree.heading('permission_count', text='权限数量')
        self.pkg_tree.heading('description', text='描述')
        
        self.pkg_tree.column('name', width=200)
        self.pkg_tree.column('document_no', width=150)
        self.pkg_tree.column('permission_count', width=100)
        self.pkg_tree.column('description', width=300)
        
        packages = self.reader.get_permission_packages()
        for pkg in packages:
            perm_count = len(pkg.get('permissions', []))
            self.pkg_tree.insert('', tk.END, values=(
                pkg['name'],
                pkg.get('document_no', ''),
                perm_count,
                pkg.get('description', '')
            ))
            
        self.pkg_tree.bind('<<TreeviewSelect>>', self.on_package_select)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.pkg_tree.yview)
        self.pkg_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pkg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        detail_frame = ttk.LabelFrame(frame, text='权限包详情', padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        detail_columns = ('permission_code', 'permission_name', 'permission_level')
        self.pkg_detail_tree = ttk.Treeview(detail_frame, columns=detail_columns, show='tree headings', height=10)
        
        self.pkg_detail_tree.heading('#0', text='系统/权限')
        self.pkg_detail_tree.heading('permission_code', text='权限编码')
        self.pkg_detail_tree.heading('permission_name', text='权限名称')
        self.pkg_detail_tree.heading('permission_level', text='级别')
        
        self.pkg_detail_tree.column('#0', width=200)
        self.pkg_detail_tree.column('permission_code', width=120)
        self.pkg_detail_tree.column('permission_name', width=150)
        self.pkg_detail_tree.column('permission_level', width=60, anchor='center')
        
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.pkg_detail_tree.yview)
        self.pkg_detail_tree.configure(yscrollcommand=detail_scrollbar.set)
        
        self.pkg_detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def on_package_select(self, event):
        for item in self.pkg_detail_tree.get_children():
            self.pkg_detail_tree.delete(item)
            
        selection = self.pkg_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.pkg_tree.item(item, 'values')
        pkg_name = values[0]
        
        packages = self.reader.get_permission_packages()
        selected_pkg = None
        for pkg in packages:
            if pkg['name'] == pkg_name:
                selected_pkg = pkg
                break
                
        if not selected_pkg:
            return
        
        permissions = selected_pkg.get('permissions', [])
        
        perms_by_system = {}
        for perm in permissions:
            system = perm.get('system', '')
            if system not in perms_by_system:
                perms_by_system[system] = []
            perms_by_system[system].append(perm)
        
        systems = self.reader.get_systems()
        systems_map = {s['name']: s for s in systems}
        
        for system_name, pkg_perms in perms_by_system.items():
            system_node = self.pkg_detail_tree.insert('', tk.END, text=f'📁 {system_name}', open=True)
            
            system_data = systems_map.get(system_name, {})
            system_permissions = system_data.get('permissions', [])
            
            perm_codes = set()
            for p in pkg_perms:
                code = p.get('permission_code', '')
                if code:
                    perm_codes.add(code)
            
            self._build_package_permission_tree(system_node, system_permissions, perm_codes)
    
    def _build_package_permission_tree(self, parent_node, permissions, perm_codes):
        for perm in permissions:
            code = perm.get('code', '')
            name = perm.get('name', '')
            level = perm.get('level', '')
            children = perm.get('children', [])
            
            has_matching_children = self._has_matching_children(children, perm_codes)
            
            if code in perm_codes or has_matching_children:
                has_children = bool(children)
                icon = '📁' if has_children else '📄'
                
                node = self.pkg_detail_tree.insert(parent_node, tk.END, text=f'{icon} {name}', 
                    values=(code, name, level), open=True)
                
                if has_children:
                    self._build_package_permission_tree(node, children, perm_codes)
    
    def _has_matching_children(self, children, perm_codes):
        for child in children:
            code = child.get('code', '')
            if code in perm_codes:
                return True
            if 'children' in child:
                if self._has_matching_children(child['children'], perm_codes):
                    return True
        return False
        
    def create_personnel_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text='人员信息', style='Header.TLabel').pack(side=tk.LEFT, padx=20)
        
        if self.reader.get_data_type() != 'organization':
            ttk.Label(frame, text='当前数据为"基础权限信息"，不包含人员数据\n请加载"机构信息"导出文件', 
                      foreground='red').pack(pady=50)
            return
            
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, padx=20)
        
        ttk.Label(search_frame, text='搜索:').pack(side=tk.LEFT)
        self.person_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.person_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text='搜索', command=self.search_personnel).pack(side=tk.LEFT)
        ttk.Button(search_frame, text='重置', command=self.reset_personnel_search).pack(side=tk.LEFT, padx=5)
        
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('name', 'employee_id', 'department', 'position', 'status', 'auth_count')
        self.person_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        self.person_tree.heading('name', text='姓名')
        self.person_tree.heading('employee_id', text='工号')
        self.person_tree.heading('department', text='部门')
        self.person_tree.heading('position', text='职位')
        self.person_tree.heading('status', text='状态')
        self.person_tree.heading('auth_count', text='授权数量')
        
        self.person_tree.column('name', width=100)
        self.person_tree.column('employee_id', width=100)
        self.person_tree.column('department', width=150)
        self.person_tree.column('position', width=120)
        self.person_tree.column('status', width=80)
        self.person_tree.column('auth_count', width=80)
        
        self.load_personnel_tree()
        
        self.person_tree.bind('<<TreeviewSelect>>', self.on_personnel_select)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.person_tree.yview)
        self.person_tree.configure(yscrollcommand=scrollbar.set)
        
        self.person_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        detail_frame = ttk.LabelFrame(frame, text='人员授权详情', padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.person_detail_text = tk.Text(detail_frame, wrap=tk.WORD, height=8, state=tk.DISABLED)
        self.person_detail_text.pack(fill=tk.BOTH, expand=True)
        
    def load_personnel_tree(self):
        for item in self.person_tree.get_children():
            self.person_tree.delete(item)
            
        personnel = self.reader.get_personnel()
        for person in personnel:
            package_auths = self.reader.get_person_package_authorizations(person)
            individual_perms = self.reader.get_person_individual_permissions(person)
            auth_count = len(package_auths) + len(individual_perms)
            self.person_tree.insert('', tk.END, values=(
                person['name'],
                person['employee_id'],
                person['department'],
                person['position'],
                person['status'],
                auth_count
            ))
            
    def search_personnel(self):
        keyword = self.person_search_var.get().strip()
        if not keyword:
            self.load_personnel_tree()
            return
            
        for item in self.person_tree.get_children():
            self.person_tree.delete(item)
            
        results = self.reader.search_personnel(keyword)
        for person in results:
            auth_count = len(person.get('authorized_permissions', []))
            self.person_tree.insert('', tk.END, values=(
                person['name'],
                person['employee_id'],
                person['department'],
                person['position'],
                person['status'],
                auth_count
            ))
            
    def reset_personnel_search(self):
        self.person_search_var.set('')
        self.load_personnel_tree()
        
    def on_personnel_select(self, event):
        selection = self.person_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.person_tree.item(item, 'values')
        person_name = values[0]
        
        personnel = self.reader.get_personnel()
        selected_person = None
        for person in personnel:
            if person['name'] == person_name:
                selected_person = person
                break
                
        if not selected_person:
            return
            
        self.person_detail_text.config(state=tk.NORMAL)
        self.person_detail_text.delete(1.0, tk.END)
        
        self.person_detail_text.insert(tk.END, f'姓名: {selected_person["name"]}  工号: {selected_person["employee_id"]}\n')
        self.person_detail_text.insert(tk.END, f'部门: {selected_person["department"]}  职位: {selected_person["position"]}  状态: {selected_person["status"]}\n')
        self.person_detail_text.insert(tk.END, '\n【权限包授权】\n')
        
        package_auths = self.reader.get_person_package_authorizations(selected_person)
        if package_auths:
            for pkg_auth in package_auths:
                self.person_detail_text.insert(tk.END, f'  📦 {pkg_auth["package_name"]}\n')
                self.person_detail_text.insert(tk.END, f'      授权时间: {pkg_auth["grant_time"]}\n')
                if pkg_auth.get('document_no'):
                    self.person_detail_text.insert(tk.END, f'      文档编号: {pkg_auth["document_no"]}\n')
                if pkg_auth.get('remark'):
                    self.person_detail_text.insert(tk.END, f'      备注: {pkg_auth["remark"]}\n')
        else:
            self.person_detail_text.insert(tk.END, '  无权限包授权\n')
        
        self.person_detail_text.insert(tk.END, '\n【单独权限授权】\n')
        individual_perms = self.reader.get_person_individual_permissions(selected_person)
        if individual_perms:
            for perm in individual_perms:
                self.person_detail_text.insert(tk.END, f'  • [{perm["system"]}] {perm["permission_name"]} - 授权时间: {perm["grant_time"]}\n')
                if perm.get('document_no'):
                    self.person_detail_text.insert(tk.END, f'    文档编号: {perm["document_no"]}\n')
        else:
            self.person_detail_text.insert(tk.END, '  无单独权限授权\n')
                
        self.person_detail_text.config(state=tk.DISABLED)
        
    def create_assignments_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text='授权记录', style='Header.TLabel').pack(pady=10)
        
        if self.reader.get_data_type() != 'organization':
            ttk.Label(frame, text='当前数据为"基础权限信息"，不包含授权记录\n请加载"机构信息"导出文件', 
                      foreground='red').pack(pady=50)
            return
            
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(filter_frame, text='按系统筛选:').pack(side=tk.LEFT)
        self.system_filter_var = tk.StringVar(value='全部')
        self.system_combo = ttk.Combobox(filter_frame, textvariable=self.system_filter_var, 
                                          state='readonly', width=30)
        self.system_combo.pack(side=tk.LEFT, padx=5)
        
        systems = ['全部'] + [s['name'] for s in self.reader.get_systems()]
        self.system_combo['values'] = systems
        self.system_combo.bind('<<ComboboxSelected>>', self.filter_assignments)
        
        ttk.Label(filter_frame, text='    ').pack(side=tk.LEFT)
        ttk.Label(filter_frame, text='查看视角:').pack(side=tk.LEFT)
        self.view_mode_var = tk.StringVar(value='expanded')
        view_combo = ttk.Combobox(filter_frame, textvariable=self.view_mode_var, 
                                   state='readonly', width=20)
        view_combo['values'] = ['排查视角(展开权限)', '权限管理视角(显示包)']
        view_combo.pack(side=tk.LEFT, padx=5)
        view_combo.bind('<<ComboboxSelected>>', self.on_view_mode_change)
        
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('personnel_name', 'employee_id', 'department', 'system', 'permission_name', 'grant_time', 'document_no', 'source')
        self.assign_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        self.assign_tree.heading('personnel_name', text='姓名')
        self.assign_tree.heading('employee_id', text='工号')
        self.assign_tree.heading('department', text='部门')
        self.assign_tree.heading('system', text='系统')
        self.assign_tree.heading('permission_name', text='权限名称')
        self.assign_tree.heading('grant_time', text='授权时间')
        self.assign_tree.heading('document_no', text='文档编号')
        self.assign_tree.heading('source', text='来源')
        
        self.assign_tree.column('personnel_name', width=80)
        self.assign_tree.column('employee_id', width=80)
        self.assign_tree.column('department', width=100)
        self.assign_tree.column('system', width=100)
        self.assign_tree.column('permission_name', width=150)
        self.assign_tree.column('grant_time', width=140)
        self.assign_tree.column('document_no', width=100)
        self.assign_tree.column('source', width=100)
        
        self.load_assignments_tree()
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.assign_tree.yview)
        self.assign_tree.configure(yscrollcommand=scrollbar.set)
        
        self.assign_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        stats_frame = ttk.LabelFrame(frame, text='统计信息', padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        expanded_assignments = self.reader.get_all_expanded_assignments()
        ttk.Label(stats_frame, text=f'总授权记录数(展开去重后): {len(expanded_assignments)}', style='Info.TLabel').pack(side=tk.LEFT, padx=20)
        
    def on_view_mode_change(self, event=None):
        self.load_assignments_tree()
        
    def load_assignments_tree(self):
        for item in self.assign_tree.get_children():
            self.assign_tree.delete(item)
        
        view_mode = self.view_mode_var.get()
        
        if view_mode == '排查视角(展开权限)':
            assignments = self.reader.get_all_expanded_assignments()
            for assign in assignments:
                source = assign.get('source_package', '') if assign.get('source_type') == 'package' else '单独授权'
                self.assign_tree.insert('', tk.END, values=(
                    assign['personnel_name'],
                    assign['employee_id'],
                    assign['department'],
                    assign['system'],
                    assign['permission_name'],
                    assign['grant_time'],
                    assign.get('document_no', ''),
                    source
                ))
        else:
            assignments = self.reader.get_all_assignments()
            for assign in assignments:
                system = assign.get('system', '')
                permission_name = assign.get('permission_name', '')
                is_package = system == '权限包' or permission_name.startswith('[权限包]')
                source = '权限包' if is_package else '单独授权'
                self.assign_tree.insert('', tk.END, values=(
                    assign['personnel_name'],
                    assign['employee_id'],
                    assign['department'],
                    system,
                    permission_name,
                    assign['grant_time'],
                    assign.get('document_no', ''),
                    source
                ))
            
    def filter_assignments(self, event=None):
        selected_system = self.system_filter_var.get()
        
        for item in self.assign_tree.get_children():
            self.assign_tree.delete(item)
        
        view_mode = self.view_mode_var.get()
        
        if view_mode == '排查视角(展开权限)':
            assignments = self.reader.get_all_expanded_assignments()
            for assign in assignments:
                if selected_system == '全部' or assign['system'] == selected_system:
                    source = assign.get('source_package', '') if assign.get('source_type') == 'package' else '单独授权'
                    self.assign_tree.insert('', tk.END, values=(
                        assign['personnel_name'],
                        assign['employee_id'],
                        assign['department'],
                        assign['system'],
                        assign['permission_name'],
                        assign['grant_time'],
                        assign.get('document_no', ''),
                        source
                    ))
        else:
            assignments = self.reader.get_all_assignments()
            for assign in assignments:
                system = assign.get('system', '')
                permission_name = assign.get('permission_name', '')
                is_package = system == '权限包' or permission_name.startswith('[权限包]')
                source = '权限包' if is_package else '单独授权'
                if selected_system == '全部' or system == selected_system:
                    self.assign_tree.insert('', tk.END, values=(
                        assign['personnel_name'],
                        assign['employee_id'],
                        assign['department'],
                        system,
                        permission_name,
                        assign['grant_time'],
                        assign.get('document_no', ''),
                        source
                    ))
                
    def create_authorization_check_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text='授权检查', style='Header.TLabel').pack(side=tk.LEFT, padx=20)
        
        if self.reader.get_data_type() != 'organization':
            ttk.Label(frame, text='当前数据为"基础权限信息"，不包含人员数据\n请加载"机构信息"导出文件', 
                      foreground='red').pack(pady=50)
            return
        
        self.auth_check_view_mode = tk.StringVar(value='list')
        
        view_btn_frame = ttk.Frame(header_frame)
        view_btn_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(view_btn_frame, text='切换到树状视图', command=self.toggle_auth_check_view).pack(side=tk.LEFT)
        
        self.auth_check_view_label = ttk.Label(header_frame, text='当前视图: 条式列表', foreground='blue')
        self.auth_check_view_label.pack(side=tk.LEFT, padx=10)
        
        select_frame = ttk.Frame(header_frame)
        select_frame.pack(side=tk.RIGHT, padx=20)
        
        ttk.Label(select_frame, text='选择人员:').pack(side=tk.LEFT)
        self.auth_check_person_var = tk.StringVar()
        self.auth_check_person_combo = ttk.Combobox(select_frame, textvariable=self.auth_check_person_var, 
                                                      state='readonly', width=30)
        self.auth_check_person_combo.pack(side=tk.LEFT, padx=5)
        self.auth_check_person_combo.bind('<<ComboboxSelected>>', self.on_auth_check_person_select)
        
        self.load_auth_check_personnel()
        
        self.auth_check_container = ttk.Frame(frame)
        self.auth_check_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.auth_check_list_frame = ttk.Frame(self.auth_check_container)
        self.auth_check_list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('permission_code', 'permission_name', 'system', 'permission_level', 'source_type', 'source_package')
        self.auth_check_tree = ttk.Treeview(self.auth_check_list_frame, columns=columns, show='headings', height=20)
        
        self.auth_check_tree.heading('permission_code', text='权限编码')
        self.auth_check_tree.heading('permission_name', text='权限名称')
        self.auth_check_tree.heading('system', text='所属系统')
        self.auth_check_tree.heading('permission_level', text='权限等级')
        self.auth_check_tree.heading('source_type', text='来源类型')
        self.auth_check_tree.heading('source_package', text='来源权限包')
        
        self.auth_check_tree.column('permission_code', width=200)
        self.auth_check_tree.column('permission_name', width=200)
        self.auth_check_tree.column('system', width=120)
        self.auth_check_tree.column('permission_level', width=80)
        self.auth_check_tree.column('source_type', width=100)
        self.auth_check_tree.column('source_package', width=150)
        
        scrollbar = ttk.Scrollbar(self.auth_check_list_frame, orient=tk.VERTICAL, command=self.auth_check_tree.yview)
        self.auth_check_tree.configure(yscrollcommand=scrollbar.set)
        
        self.auth_check_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.auth_check_tree_frame = ttk.Frame(self.auth_check_container)
        
        tree_columns = ('permission_code', 'permission_level', 'source_type', 'source_package')
        self.auth_check_perm_tree = ttk.Treeview(self.auth_check_tree_frame, columns=tree_columns, show='tree headings', height=20)
        
        self.auth_check_perm_tree.heading('#0', text='系统/权限名称')
        self.auth_check_perm_tree.heading('permission_code', text='权限编码')
        self.auth_check_perm_tree.heading('permission_level', text='权限等级')
        self.auth_check_perm_tree.heading('source_type', text='来源类型')
        self.auth_check_perm_tree.heading('source_package', text='来源权限包')
        
        self.auth_check_perm_tree.column('#0', width=250)
        self.auth_check_perm_tree.column('permission_code', width=150)
        self.auth_check_perm_tree.column('permission_level', width=80, anchor='center')
        self.auth_check_perm_tree.column('source_type', width=100)
        self.auth_check_perm_tree.column('source_package', width=150)
        
        tree_scrollbar = ttk.Scrollbar(self.auth_check_tree_frame, orient=tk.VERTICAL, command=self.auth_check_perm_tree.yview)
        self.auth_check_perm_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.auth_check_perm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        stats_frame = ttk.LabelFrame(frame, text='统计信息', padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.auth_check_stats_label = ttk.Label(stats_frame, text='请选择人员查看其所有权限', style='Info.TLabel')
        self.auth_check_stats_label.pack(side=tk.LEFT, padx=20)
        
    def toggle_auth_check_view(self):
        if self.auth_check_view_mode.get() == 'list':
            self.auth_check_view_mode.set('tree')
            self.auth_check_list_frame.pack_forget()
            self.auth_check_tree_frame.pack(fill=tk.BOTH, expand=True)
            self.auth_check_view_label.config(text='当前视图: 树状结构')
        else:
            self.auth_check_view_mode.set('list')
            self.auth_check_tree_frame.pack_forget()
            self.auth_check_list_frame.pack(fill=tk.BOTH, expand=True)
            self.auth_check_view_label.config(text='当前视图: 条式列表')
        
    def load_auth_check_personnel(self):
        personnel = self.reader.get_personnel()
        person_list = [f"{p['name']} ({p['employee_id']}) - {p['department']}" for p in personnel]
        self.auth_check_person_combo['values'] = person_list
        self._auth_check_personnel_data = personnel
        
    def on_auth_check_person_select(self, event=None):
        for item in self.auth_check_tree.get_children():
            self.auth_check_tree.delete(item)
            
        for item in self.auth_check_perm_tree.get_children():
            self.auth_check_perm_tree.delete(item)
            
        selected_text = self.auth_check_person_var.get()
        if not selected_text:
            return
            
        personnel = self._auth_check_personnel_data
        selected_person = None
        for person in personnel:
            if f"{person['name']} ({person['employee_id']}) - {person['department']}" == selected_text:
                selected_person = person
                break
                
        if not selected_person:
            return
            
        expanded_perms = self.reader.get_person_expanded_permissions(selected_person)
        
        sorted_perms = sorted(expanded_perms, key=lambda x: (x.get('system', ''), x.get('permission_code', '')))
        
        package_count = 0
        individual_count = 0
        
        for perm in sorted_perms:
            source_type = '权限包' if perm.get('source_type') == 'package' else '单独授权'
            source_package = perm.get('source_package', '')
            
            if perm.get('source_type') == 'package':
                package_count += 1
            else:
                individual_count += 1
                
            self.auth_check_tree.insert('', tk.END, values=(
                perm.get('permission_code', ''),
                perm.get('permission_name', ''),
                perm.get('system', ''),
                perm.get('permission_level', 0),
                source_type,
                source_package
            ))
        
        self._build_auth_check_tree_view(sorted_perms)
            
        total_count = len(sorted_perms)
        self.auth_check_stats_label.config(
            text=f'总权限数: {total_count} (来自权限包: {package_count}, 单独授权: {individual_count})'
        )
        
    def _build_auth_check_tree_view(self, permissions):
        perms_by_system = {}
        for perm in permissions:
            system = perm.get('system', '')
            if system not in perms_by_system:
                perms_by_system[system] = []
            perms_by_system[system].append(perm)
        
        systems = self.reader.get_systems()
        systems_map = {s['name']: s for s in systems}
        
        for system_name, system_perms in perms_by_system.items():
            system_node = self.auth_check_perm_tree.insert('', tk.END, text=f'📁 {system_name}', open=True)
            
            system_data = systems_map.get(system_name, {})
            system_permissions = system_data.get('permissions', [])
            
            perm_codes = set()
            perm_map = {}
            for p in system_perms:
                code = p.get('permission_code', '')
                if code:
                    perm_codes.add(code)
                    perm_map[code] = p
            
            self._build_auth_permission_tree(system_node, system_permissions, perm_codes, perm_map)
    
    def _build_auth_permission_tree(self, parent_node, permissions, perm_codes, perm_map):
        for perm in permissions:
            code = perm.get('code', '')
            name = perm.get('name', '')
            level = perm.get('level', '')
            children = perm.get('children', [])
            
            has_matching_children = self._has_auth_matching_children(children, perm_codes)
            
            if code in perm_codes or has_matching_children:
                has_children = bool(children)
                icon = '📁' if has_children else '📄'
                
                if code in perm_codes:
                    perm_data = perm_map.get(code, {})
                    source_type = '权限包' if perm_data.get('source_type') == 'package' else '单独授权'
                    source_package = perm_data.get('source_package', '')
                else:
                    source_type = ''
                    source_package = ''
                
                node = self.auth_check_perm_tree.insert(parent_node, tk.END, text=f'{icon} {name}', 
                    values=(code, level, source_type, source_package), open=True)
                
                if has_children:
                    self._build_auth_permission_tree(node, children, perm_codes, perm_map)
    
    def _has_auth_matching_children(self, children, perm_codes):
        for child in children:
            code = child.get('code', '')
            if code in perm_codes:
                return True
            if 'children' in child:
                if self._has_auth_matching_children(child['children'], perm_codes):
                    return True
        return False
        
    def create_apply_package_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text='操作权限包', style='Header.TLabel').pack(side=tk.LEFT, padx=20)
        
        main_paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        pkg_select_frame = ttk.LabelFrame(left_frame, text='选择权限包', padding=5)
        pkg_select_frame.pack(fill=tk.X, pady=5)
        
        pkg_btn_frame = ttk.Frame(pkg_select_frame)
        pkg_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pkg_btn_frame, text='权限包:').pack(side=tk.LEFT)
        self.package_select_var = tk.StringVar()
        self.package_select_combo = ttk.Combobox(pkg_btn_frame, textvariable=self.package_select_var, width=30)
        self.package_select_combo.pack(side=tk.LEFT, padx=5)
        self.package_select_combo.bind('<<ComboboxSelected>>', self.on_package_select_for_edit)
        
        ttk.Button(pkg_btn_frame, text='新建权限包', command=self.create_new_package).pack(side=tk.LEFT, padx=5)
        ttk.Button(pkg_btn_frame, text='删除权限包', command=self.delete_selected_package).pack(side=tk.LEFT, padx=5)
        
        perm_label_frame = ttk.LabelFrame(left_frame, text='选择权限（添加到权限包）', padding=5)
        perm_label_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tree_frame = ttk.Frame(perm_label_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.package_perm_tree = ttk.Treeview(tree_frame, show='tree', height=15)
        self.package_perm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.package_perm_tree.yview)
        self.package_perm_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.permission_tree_data = {}
        
        self._load_permission_tree_for_package()
        
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        form_frame = ttk.LabelFrame(right_frame, text='权限包信息', padding=10)
        form_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_frame, text='权限包名称:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.package_name_var = tk.StringVar()
        self.package_name_entry = ttk.Entry(form_frame, textvariable=self.package_name_var, width=40)
        self.package_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='权限包描述:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.package_desc_text = tk.Text(form_frame, width=40, height=3)
        self.package_desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='文档编号:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.package_doc_no_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.package_doc_no_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='申请人:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.package_applicant_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.package_applicant_var, width=40).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='所属部门:').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.package_dept_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.package_dept_var, width=40).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='申请机构:').grid(row=5, column=0, sticky=tk.W, pady=5)
        self.package_org_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.package_org_var, width=40).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        selected_frame = ttk.LabelFrame(right_frame, text='权限包内权限（可增删改）', padding=10)
        selected_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        list_frame = ttk.Frame(selected_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.selected_perm_listbox = tk.Listbox(list_frame, height=10)
        self.selected_perm_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.selected_perm_listbox.yview)
        self.selected_perm_listbox.configure(yscrollcommand=list_scrollbar.set)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        perm_btn_frame = ttk.Frame(selected_frame)
        perm_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(perm_btn_frame, text='添加选中权限', command=self.add_selected_permission).pack(side=tk.LEFT, padx=5)
        ttk.Button(perm_btn_frame, text='移除选中', command=self.remove_selected_permission).pack(side=tk.LEFT, padx=5)
        ttk.Button(perm_btn_frame, text='清空全部', command=self.clear_selected_permissions).pack(side=tk.LEFT, padx=5)
        ttk.Button(perm_btn_frame, text='保存修改', command=self.save_package_changes).pack(side=tk.LEFT, padx=5)
        
        export_frame = ttk.Frame(right_frame)
        export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(export_frame, text='生成申请文件（YML+DOC）', command=self.export_package_application).pack(side=tk.LEFT, padx=5)
        
        self.selected_package_permissions = []
        self.existing_packages = {}
        self.current_editing_package = None
        self.original_package_permissions = []
        self._load_existing_packages()
        
    def _load_existing_packages(self):
        self.package_select_combo['values'] = []
        self.existing_packages = {}
        
        if self.reader.data is None:
            return
            
        if self.reader.get_data_type() == 'organization':
            packages = self.reader.get_permission_packages()
            if packages:
                package_names = [pkg['name'] for pkg in packages]
                self.package_select_combo['values'] = package_names
                self.existing_packages = {pkg['name']: pkg.copy() for pkg in packages}
        self.current_editing_package = None
            
    def on_package_select_for_edit(self, event=None):
        selected_name = self.package_select_var.get()
        if not selected_name:
            return
            
        pkg = self.existing_packages.get(selected_name)
        if not pkg:
            return
            
        self.current_editing_package = pkg
        self.original_package_permissions = [p.copy() for p in pkg.get('permissions', [])]
        self.package_name_var.set(pkg['name'])
        self.package_desc_text.delete(1.0, tk.END)
        self.package_desc_text.insert(tk.END, pkg.get('description', ''))
        self.package_doc_no_var.set(pkg.get('document_no', ''))
        
        self.selected_perm_listbox.delete(0, tk.END)
        self.selected_package_permissions = []
        
        for perm in pkg.get('permissions', []):
            perm_info = {
                'system': perm.get('system', ''),
                'permission_name': perm.get('permission_name', ''),
                'permission_code': perm.get('permission_code', ''),
                'permission_level': perm.get('permission_level', 1)
            }
            self.selected_package_permissions.append(perm_info)
            self.selected_perm_listbox.insert(tk.END, f"[{perm_info['system']}] {perm_info['permission_name']} ({perm_info['permission_code']})")
            
    def create_new_package(self):
        self.current_editing_package = None
        self.original_package_permissions = []
        self.package_select_var.set('')
        self.package_name_var.set('')
        self.package_desc_text.delete(1.0, tk.END)
        self.package_doc_no_var.set('')
        self.package_applicant_var.set('')
        self.package_dept_var.set('')
        self.package_org_var.set('')
        self.selected_perm_listbox.delete(0, tk.END)
        self.selected_package_permissions = []
        self.package_name_entry.focus()
        
    def delete_selected_package(self):
        selected_name = self.package_select_var.get()
        if not selected_name:
            messagebox.showwarning('提示', '请先选择要删除的权限包')
            return
            
        if messagebox.askyesno('确认删除', f'确定要删除权限包 "{selected_name}" 吗？'):
            if selected_name in self.existing_packages:
                del self.existing_packages[selected_name]
                self.package_select_combo['values'] = list(self.existing_packages.keys())
                self.create_new_package()
                messagebox.showinfo('成功', '权限包已删除（注：此删除仅在当前会话有效，实际删除需在主系统操作）')
                
    def save_package_changes(self):
        name = self.package_name_var.get().strip()
        if not name:
            messagebox.showwarning('提示', '请输入权限包名称')
            return
            
        description = self.package_desc_text.get(1.0, tk.END).strip()
        document_no = self.package_doc_no_var.get().strip()
        
        pkg_data = {
            'name': name,
            'description': description,
            'document_no': document_no,
            'permissions': self.selected_package_permissions.copy()
        }
        
        self.existing_packages[name] = pkg_data
        self.package_select_combo['values'] = list(self.existing_packages.keys())
        self.package_select_var.set(name)
        self.current_editing_package = pkg_data
        
        messagebox.showinfo('成功', f'权限包 "{name}" 已保存（注：此保存仅在当前会话有效，实际保存需导出申请文件）')
        
    def _load_permission_tree_for_package(self):
        for item in self.package_perm_tree.get_children():
            self.package_perm_tree.delete(item)
        
        self.permission_tree_data = {}
            
        systems = self.reader.get_systems()
        for system in systems:
            system_node = self.package_perm_tree.insert('', tk.END, text=system['name'], open=False)
            self._add_permission_nodes(system.get('permissions', []), system_node, system['name'])
            
    def _add_permission_nodes(self, permissions, parent_node, system_name):
        for perm in permissions:
            node_text = f"{perm.get('name', '')} [{perm.get('code', '')}]"
            node = self.package_perm_tree.insert(parent_node, tk.END, text=node_text, open=False)
            self.permission_tree_data[node] = {
                'system': system_name,
                'code': perm.get('code', ''),
                'name': perm.get('name', ''),
                'level': perm.get('level', 1)
            }
            
            if 'children' in perm:
                self._add_permission_nodes(perm['children'], node, system_name)
                

    def add_selected_permission(self):
        selection = self.package_perm_tree.selection()
        if not selection:
            messagebox.showwarning('提示', '请先选择权限')
            return
        
        added_count = 0
        duplicate_count = 0
        skipped_count = 0
            
        for item_id in selection:
            item_text = self.package_perm_tree.item(item_id, 'text')
            
            perm_data = self.permission_tree_data.get(item_id, {})
            system = perm_data.get('system', '')
            code = perm_data.get('code', '')
            name = perm_data.get('name', '')
            
            if not system:
                system = self._get_tree_node_system(item_id)
            
            if not code and ' [' in item_text:
                code = item_text.split(' [')[1].rstrip(']')
            
            if not name and ' [' in item_text:
                name = item_text.split(' [')[0]
            
            if not code:
                skipped_count += 1
                continue
            
            perm_info = {
                'system': system,
                'permission_name': name,
                'permission_code': code,
                'permission_level': 1
            }
            
            exists = False
            for p in self.selected_package_permissions:
                if p['system'] == system and p['permission_code'] == code:
                    exists = True
                    break
            
            if not exists:
                self.selected_package_permissions.append(perm_info)
                self.selected_perm_listbox.insert(tk.END, f"[{system}] {name} ({code})")
                added_count += 1
            else:
                duplicate_count += 1
        
        msg_parts = []
        if added_count > 0:
            msg_parts.append(f"成功添加 {added_count} 个权限")
        if duplicate_count > 0:
            msg_parts.append(f"{duplicate_count} 个权限已存在，已跳过")
        if skipped_count > 0:
            msg_parts.append(f"{skipped_count} 个节点无权限代码，已跳过")
        
        if msg_parts:
            messagebox.showinfo('操作结果', '\n'.join(msg_parts))
                
    def _get_tree_node_system(self, item_id):
        parent = self.package_perm_tree.parent(item_id)
        if parent == '':
            return self.package_perm_tree.item(item_id, 'text')
        return self._get_tree_node_system(parent)
        
    def remove_selected_permission(self):
        selection = self.selected_perm_listbox.curselection()
        if not selection:
            messagebox.showwarning('提示', '请先选择要移除的权限')
            return
            
        for idx in reversed(selection):
            self.selected_perm_listbox.delete(idx)
            if idx < len(self.selected_package_permissions):
                self.selected_package_permissions.pop(idx)
                
    def clear_selected_permissions(self):
        self.selected_perm_listbox.delete(0, tk.END)
        self.selected_package_permissions = []
        
    def export_package_application(self):
        name = self.package_name_var.get().strip()
        if not name:
            messagebox.showwarning('提示', '请输入权限包名称')
            return
            
        if not self.selected_package_permissions:
            messagebox.showwarning('提示', '请至少选择一个权限')
            return
            
        description = self.package_desc_text.get(1.0, tk.END).strip()
        document_no = self.package_doc_no_var.get().strip()
        applicant = self.package_applicant_var.get().strip()
        department = self.package_dept_var.get().strip()
        organization = self.package_org_var.get().strip()
        
        operation_type = 'change' if self.current_editing_package else 'new'
        original_permissions = self.original_package_permissions if self.current_editing_package else []
        
        application = self.app_manager.create_package_application(
            name=name,
            description=description,
            permissions=self.selected_package_permissions,
            document_no=document_no,
            applicant=applicant,
            department=department,
            organization=organization,
            operation_type=operation_type,
            original_permissions=original_permissions
        )
        
        save_dir = filedialog.askdirectory(title='选择保存目录')
        if not save_dir:
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        yml_path = f"{save_dir}/权限包申请_{name}_{timestamp}.yml"
        doc_path = f"{save_dir}/权限包申请_{name}_{timestamp}.docx"
        
        try:
            self.app_manager.export_package_application_yml(application, yml_path)
            self.app_manager.export_package_application_doc(application, doc_path)
            
            messagebox.showinfo('成功', f'申请文件已生成:\n\nYML文件: {yml_path}\nDOC文件: {doc_path}\n\n可将YML文件导入主系统进行合并')
        except Exception as e:
            messagebox.showerror('错误', f'生成文件失败: {e}')
            
    def create_apply_authorization_page(self):
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text='申请授权', style='Header.TLabel').pack(side=tk.LEFT, padx=20)
        
        main_paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        personnel_frame = ttk.LabelFrame(left_frame, text='选择被授权人员', padding=10)
        personnel_frame.pack(fill=tk.X, pady=5)
        
        if self.reader.get_data_type() == 'organization':
            ttk.Label(personnel_frame, text='选择人员:').pack(anchor=tk.W)
            self.auth_personnel_var = tk.StringVar()
            personnel_combo = ttk.Combobox(personnel_frame, textvariable=self.auth_personnel_var, width=50)
            personnel_combo.pack(fill=tk.X, pady=5)
            
            personnel_list = [f"{p['name']} ({p['employee_id']}) - {p['department']}" 
                            for p in self.reader.get_personnel()]
            personnel_combo['values'] = personnel_list
            personnel_combo.bind('<<ComboboxSelected>>', self.on_auth_personnel_select)
        else:
            ttk.Label(personnel_frame, text='当前数据不包含人员信息，请手动输入', foreground='orange').pack(pady=5)
            
        manual_frame = ttk.Frame(personnel_frame)
        manual_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(manual_frame, text='姓名:').grid(row=0, column=0, sticky=tk.W, pady=2)
        self.auth_person_name_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.auth_person_name_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(manual_frame, text='工号:').grid(row=0, column=2, sticky=tk.W, pady=2)
        self.auth_person_id_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.auth_person_id_var, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(manual_frame, text='部门:').grid(row=1, column=0, sticky=tk.W, pady=2)
        self.auth_person_dept_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.auth_person_dept_var, width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(manual_frame, text='职位:').grid(row=1, column=2, sticky=tk.W, pady=2)
        self.auth_person_pos_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.auth_person_pos_var, width=15).grid(row=1, column=3, padx=5)
        
        ttk.Label(manual_frame, text='证件号码:').grid(row=2, column=0, sticky=tk.W, pady=2)
        self.auth_person_id_card_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.auth_person_id_card_var, width=15).grid(row=2, column=1, padx=5)
        
        ttk.Label(manual_frame, text='电话号码:').grid(row=2, column=2, sticky=tk.W, pady=2)
        self.auth_person_phone_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.auth_person_phone_var, width=15).grid(row=2, column=3, padx=5)
        
        ttk.Label(manual_frame, text='备注:').grid(row=3, column=0, sticky=tk.W, pady=2)
        self.auth_person_remark_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.auth_person_remark_var, width=50).grid(row=3, column=1, columnspan=3, padx=5, sticky=tk.W)
        
        current_pkg_frame = ttk.LabelFrame(left_frame, text='该人员当前已授权权限包', padding=10)
        current_pkg_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        current_list_frame = ttk.Frame(current_pkg_frame)
        current_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.auth_current_pkg_listbox = tk.Listbox(current_list_frame, height=8)
        self.auth_current_pkg_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        current_scrollbar = ttk.Scrollbar(current_list_frame, orient=tk.VERTICAL, command=self.auth_current_pkg_listbox.yview)
        self.auth_current_pkg_listbox.configure(yscrollcommand=current_scrollbar.set)
        current_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.auth_current_pkg_listbox.bind('<<ListboxSelect>>', self.on_current_pkg_select)
        
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        form_frame = ttk.LabelFrame(right_frame, text='申请信息', padding=10)
        form_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_frame, text='文档编号:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.auth_doc_no_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.auth_doc_no_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='申请人:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.auth_applicant_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.auth_applicant_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='所属部门:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.auth_dept_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.auth_dept_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='申请机构:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.auth_org_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.auth_org_var, width=40).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        available_pkg_frame = ttk.LabelFrame(right_frame, text='可选权限包（添加授权）', padding=10)
        available_pkg_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        avail_list_frame = ttk.Frame(available_pkg_frame)
        avail_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.auth_available_pkg_listbox = tk.Listbox(avail_list_frame, height=8)
        self.auth_available_pkg_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        avail_scrollbar = ttk.Scrollbar(avail_list_frame, orient=tk.VERTICAL, command=self.auth_available_pkg_listbox.yview)
        self.auth_available_pkg_listbox.configure(yscrollcommand=avail_scrollbar.set)
        avail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.auth_available_pkg_listbox.bind('<<ListboxSelect>>', self.on_available_pkg_select)
        
        pkg_btn_frame = ttk.Frame(right_frame)
        pkg_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(pkg_btn_frame, text='添加授权（选中权限包→人员）', command=self.add_auth_package_to_person).pack(side=tk.LEFT, padx=5)
        ttk.Button(pkg_btn_frame, text='移除授权（选中权限包←人员）', command=self.remove_auth_package_from_person).pack(side=tk.LEFT, padx=5)
        
        to_add_frame = ttk.LabelFrame(right_frame, text='待添加授权的权限包', padding=10)
        to_add_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        to_add_list_frame = ttk.Frame(to_add_frame)
        to_add_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.auth_to_add_listbox = tk.Listbox(to_add_list_frame, height=6)
        self.auth_to_add_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        to_add_scrollbar = ttk.Scrollbar(to_add_list_frame, orient=tk.VERTICAL, command=self.auth_to_add_listbox.yview)
        self.auth_to_add_listbox.configure(yscrollcommand=to_add_scrollbar.set)
        to_add_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        to_remove_frame = ttk.LabelFrame(right_frame, text='待移除授权的权限包', padding=10)
        to_remove_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        to_remove_list_frame = ttk.Frame(to_remove_frame)
        to_remove_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.auth_to_remove_listbox = tk.Listbox(to_remove_list_frame, height=6)
        self.auth_to_remove_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        to_remove_scrollbar = ttk.Scrollbar(to_remove_list_frame, orient=tk.VERTICAL, command=self.auth_to_remove_listbox.yview)
        self.auth_to_remove_listbox.configure(yscrollcommand=to_remove_scrollbar.set)
        to_remove_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        export_frame = ttk.Frame(right_frame)
        export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(export_frame, text='生成申请文件（YML+DOC）', command=self.export_authorization_application).pack(side=tk.LEFT, padx=5)
        
        self.selected_auth_person = None
        self.auth_current_packages = []
        self.auth_packages_to_add = []
        self.auth_packages_to_remove = []
        self.auth_all_packages = {}
        
        self._load_all_packages_for_auth()
        
    def _load_all_packages_for_auth(self):
        self.auth_all_packages = {}
        self.auth_available_pkg_listbox.delete(0, tk.END)
        
        if self.reader.get_data_type() == 'organization':
            packages = self.reader.get_permission_packages()
            for pkg in packages:
                self.auth_all_packages[pkg['name']] = pkg
                self.auth_available_pkg_listbox.insert(tk.END, f"{pkg['name']} ({len(pkg.get('permissions', []))}个权限)")
                
    def on_auth_personnel_select(self, event):
        selected = self.auth_personnel_var.get()
        if not selected:
            return
            
        personnel = self.reader.get_personnel()
        for person in personnel:
            person_str = f"{person['name']} ({person['employee_id']}) - {person['department']}"
            if person_str == selected:
                self.selected_auth_person = person
                self.auth_person_name_var.set(person['name'])
                self.auth_person_id_var.set(person['employee_id'])
                self.auth_person_dept_var.set(person['department'])
                self.auth_person_pos_var.set(person.get('position', ''))
                self.auth_person_id_card_var.set(person.get('id_card', ''))
                self.auth_person_phone_var.set(person.get('phone', ''))
                self.auth_person_remark_var.set(person.get('remark', ''))
                self._load_person_current_packages(person)
                break
                
    def _load_person_current_packages(self, person):
        self.auth_current_pkg_listbox.delete(0, tk.END)
        self.auth_current_packages = []
        self.auth_packages_to_add = []
        self.auth_packages_to_remove = []
        self.auth_to_add_listbox.delete(0, tk.END)
        self.auth_to_remove_listbox.delete(0, tk.END)
        
        package_auths = self.reader.get_person_package_authorizations(person)
        for pkg_auth in package_auths:
            pkg_name = pkg_auth['package_name']
            if pkg_name in self.auth_all_packages:
                pkg = self.auth_all_packages[pkg_name]
                self.auth_current_packages.append(pkg_name)
                self.auth_current_pkg_listbox.insert(tk.END, f"{pkg_name} ({len(pkg.get('permissions', []))}个权限)")
                
    def on_current_pkg_select(self, event=None):
        pass
        
    def on_available_pkg_select(self, event=None):
        pass
        
    def add_auth_package_to_person(self):
        if not self.selected_auth_person:
            messagebox.showwarning('提示', '请先选择人员')
            return
            
        selection = self.auth_available_pkg_listbox.curselection()
        if not selection:
            messagebox.showwarning('提示', '请先选择要添加的权限包')
            return
            
        for idx in selection:
            pkg_text = self.auth_available_pkg_listbox.get(idx)
            pkg_name = pkg_text.split(' (')[0]
            
            if pkg_name in self.auth_current_packages:
                messagebox.showinfo('提示', f'权限包 "{pkg_name}" 已在该人员的授权中')
                continue
                
            if pkg_name in self.auth_packages_to_add:
                messagebox.showinfo('提示', f'权限包 "{pkg_name}" 已在待添加列表中')
                continue
                
            if pkg_name in self.auth_packages_to_remove:
                self.auth_packages_to_remove.remove(pkg_name)
                self._refresh_to_remove_listbox()
            
            pkg = self.auth_all_packages.get(pkg_name)
            if pkg:
                self.auth_packages_to_add.append(pkg_name)
                self.auth_to_add_listbox.insert(tk.END, f"{pkg_name} ({len(pkg.get('permissions', []))}个权限)")
                
    def remove_auth_package_from_person(self):
        if not self.selected_auth_person:
            messagebox.showwarning('提示', '请先选择人员')
            return
            
        selection = self.auth_current_pkg_listbox.curselection()
        if not selection:
            messagebox.showwarning('提示', '请先选择要移除的权限包')
            return
            
        for idx in selection:
            pkg_text = self.auth_current_pkg_listbox.get(idx)
            pkg_name = pkg_text.split(' (')[0]
            
            if pkg_name in self.auth_packages_to_remove:
                messagebox.showinfo('提示', f'权限包 "{pkg_name}" 已在待移除列表中')
                continue
                
            if pkg_name in self.auth_packages_to_add:
                self.auth_packages_to_add.remove(pkg_name)
                self._refresh_to_add_listbox()
            
            pkg = self.auth_all_packages.get(pkg_name)
            if pkg:
                self.auth_packages_to_remove.append(pkg_name)
                self.auth_to_remove_listbox.insert(tk.END, f"{pkg_name} ({len(pkg.get('permissions', []))}个权限)")
                
    def _refresh_to_add_listbox(self):
        self.auth_to_add_listbox.delete(0, tk.END)
        for pkg_name in self.auth_packages_to_add:
            pkg = self.auth_all_packages.get(pkg_name)
            if pkg:
                self.auth_to_add_listbox.insert(tk.END, f"{pkg_name} ({len(pkg.get('permissions', []))}个权限)")
                
    def _refresh_to_remove_listbox(self):
        self.auth_to_remove_listbox.delete(0, tk.END)
        for pkg_name in self.auth_packages_to_remove:
            pkg = self.auth_all_packages.get(pkg_name)
            if pkg:
                self.auth_to_remove_listbox.insert(tk.END, f"{pkg_name} ({len(pkg.get('permissions', []))}个权限)")
        
    def export_authorization_application(self):
        person_name = self.auth_person_name_var.get().strip()
        if not person_name:
            messagebox.showwarning('提示', '请输入被授权人姓名')
            return
            
        if not self.auth_packages_to_add and not self.auth_packages_to_remove:
            messagebox.showwarning('提示', '请至少选择一个要添加或移除的权限包')
            return
            
        personnel_info = {
            'name': person_name,
            'employee_id': self.auth_person_id_var.get().strip(),
            'department': self.auth_person_dept_var.get().strip(),
            'position': self.auth_person_pos_var.get().strip(),
            'id_card': self.auth_person_id_card_var.get().strip(),
            'phone': self.auth_person_phone_var.get().strip(),
            'remark': self.auth_person_remark_var.get().strip()
        }
        
        document_no = self.auth_doc_no_var.get().strip()
        applicant = self.auth_applicant_var.get().strip()
        department = self.auth_dept_var.get().strip()
        organization = self.auth_org_var.get().strip()
        
        packages_to_add = [self.auth_all_packages[name] for name in self.auth_packages_to_add if name in self.auth_all_packages]
        packages_to_remove = [self.auth_all_packages[name] for name in self.auth_packages_to_remove if name in self.auth_all_packages]
        
        application = self.app_manager.create_authorization_change_application(
            personnel_info=personnel_info,
            packages_to_add=packages_to_add,
            packages_to_remove=packages_to_remove,
            document_no=document_no,
            applicant=applicant,
            department=department,
            organization=organization
        )
        
        save_dir = filedialog.askdirectory(title='选择保存目录')
        if not save_dir:
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        yml_path = f"{save_dir}/授权变更申请_{person_name}_{timestamp}.yml"
        doc_path = f"{save_dir}/授权变更申请_{person_name}_{timestamp}.docx"
        
        try:
            self.app_manager.export_authorization_change_application_yml(application, yml_path)
            self.app_manager.export_authorization_change_application_doc(application, doc_path)
            
            messagebox.showinfo('成功', f'申请文件已生成:\n\nYML文件: {yml_path}\nDOC文件: {doc_path}\n\n可将YML文件导入主系统进行合并')
        except Exception as e:
            messagebox.showerror('错误', f'生成文件失败: {e}')
                
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = SubSystemApp()
    app.run()

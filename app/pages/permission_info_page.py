import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ..utils.data_manager import DataManager
from ..utils.config_manager import ConfigManager
from ..utils.import_export import ImportExport
from ..utils.logger import Logger


class PermissionInfoPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.permission_items = {}
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.create_header()
        self.create_toolbar()
        self.create_main_content()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='权限信息管理', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)

    def create_toolbar(self):
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(toolbar_frame, text='系统筛选:').pack(side=tk.LEFT, padx=5)
        self.system_var = tk.StringVar(value='全部')
        self.system_combo = ttk.Combobox(toolbar_frame, textvariable=self.system_var, width=15, state='readonly')
        self.system_combo.pack(side=tk.LEFT, padx=5)
        self.system_combo.bind('<<ComboboxSelected>>', self.on_system_filter)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text='新增节点', command=self.add_permission).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='编辑', command=self.edit_permission).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='删除', command=self.delete_permission).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text='导入', command=self.import_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='导出', command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text='刷新', command=self.load_data).pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar_frame, text='展开全部', command=self.expand_all).pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar_frame, text='折叠全部', command=self.collapse_all).pack(side=tk.RIGHT, padx=5)

    def create_main_content(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('权限编码', '级别', '描述', '状态')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        self.tree.heading('#0', text='权限名称')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column('#0', width=250)
        self.tree.column('描述', width=200)
        
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind('<Double-1>', lambda e: self.edit_permission())
        self.tree.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label='新增子节点', command=self.add_permission)
            menu.add_command(label='编辑', command=self.edit_permission)
            menu.add_separator()
            menu.add_command(label='删除', command=self.delete_permission)
            
            menu.tk_popup(event.x_root, event.y_root)

    def load_data(self):
        expanded_items = set()
        for item in self.tree.get_children():
            self._collect_expanded_items(item, expanded_items)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.permission_items.clear()
        
        systems_df = DataManager.get_systems()
        system_list = ['全部'] + [row['name'] for _, row in systems_df.iterrows()]
        self.system_combo['values'] = system_list
        
        selected_system = self.system_var.get()
        
        if selected_system == '全部':
            for _, system in systems_df.iterrows():
                system_id = system['id']
                system_node = self.tree.insert('', tk.END, text=f'📁 {system["name"]}', open=True, tags=('system', system_id))
                self._load_permission_tree(system_node, system_id, '', expanded_items)
        else:
            system = systems_df[systems_df['name'] == selected_system]
            if not system.empty:
                system_id = system.iloc[0]['id']
                self._load_permission_tree('', system_id, '', expanded_items)

    def _collect_expanded_items(self, item, expanded_items):
        tags = self.tree.item(item, 'tags')
        if tags and len(tags) >= 2:
            item_type = tags[0]
            item_id = tags[1]
            if self.tree.item(item, 'open'):
                expanded_items.add((item_type, item_id))
        for child in self.tree.get_children(item):
            self._collect_expanded_items(child, expanded_items)

    def _load_permission_tree(self, parent_node, system_id, parent_id, expanded_items=None):
        if expanded_items is None:
            expanded_items = set()
        
        permissions_df = DataManager.get_permission_children(parent_id, system_id)
        
        for _, perm in permissions_df.iterrows():
            status = '启用' if perm['status'] == 1 else '禁用'
            is_leaf = perm.get('is_leaf', True)
            icon = '📄' if is_leaf else '📁'
            
            is_expanded = ('permission', perm['id']) in expanded_items
            
            node_text = f'{icon} {perm["name"]}'
            node = self.tree.insert(parent_node, tk.END, text=node_text, values=(
                perm['code'] or '',
                perm['level'],
                perm['description'] or '',
                status
            ), open=is_expanded, tags=('permission', perm['id']))
            
            self.permission_items[node] = {
                'id': perm['id'],
                'system_id': system_id,
                'parent_id': parent_id,
                'is_leaf': is_leaf
            }
            
            self._load_permission_tree(node, system_id, perm['id'], expanded_items)

    def on_system_filter(self, event=None):
        self.load_data()

    def expand_all(self):
        def expand_item(item):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                expand_item(child)
        
        for item in self.tree.get_children():
            expand_item(item)

    def collapse_all(self):
        def collapse_item(item):
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                collapse_item(child)
        
        for item in self.tree.get_children():
            collapse_item(item)

    def get_selected_permission(self):
        selected = self.tree.selection()
        if not selected:
            return None, None
        
        item = selected[0]
        tags = self.tree.item(item, 'tags')
        
        if not tags or len(tags) < 2:
            return None, None
        
        item_type = tags[0]
        item_id = tags[1]
        
        return item_type, item_id

    def add_permission(self):
        selected_system = self.system_var.get()
        selected = self.tree.selection()
        
        parent_id = ''
        system_id = None
        
        if selected:
            item = selected[0]
            tags = self.tree.item(item, 'tags')
            
            if tags and len(tags) >= 2:
                item_type = tags[0]
                item_id = tags[1]
                
                if item_type == 'system':
                    system_id = item_id
                    parent_id = ''
                elif item_type == 'permission':
                    perm_info = self.permission_items.get(item)
                    if perm_info:
                        system_id = perm_info['system_id']
                        parent_id = item_id
        
        if system_id is None:
            if selected_system == '全部':
                messagebox.showwarning('提示', '请先选择一个具体的系统，或在树中选择一个节点')
                return
            systems_df = DataManager.get_systems()
            system = systems_df[systems_df['name'] == selected_system]
            if system.empty:
                return
            system_id = system.iloc[0]['id']
        
        level = DataManager.calculate_permission_level(parent_id)
        code = DataManager.generate_permission_code(system_id, parent_id)
        
        dialog = PermissionDialog(self, '新增权限', system_id=system_id, parent_id=parent_id, auto_level=level, auto_code=code)
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def edit_permission(self):
        item_type, item_id = self.get_selected_permission()
        
        if item_type != 'permission':
            messagebox.showwarning('提示', '请选择一个权限节点进行编辑')
            return
        
        df = DataManager.get_permissions()
        permission = df[df['id'] == item_id]
        if permission.empty:
            return
        
        permission_data = permission.iloc[0].to_dict()
        
        dialog = PermissionDialog(self, '编辑权限', permission_data=permission_data)
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def delete_permission(self):
        item_type, item_id = self.get_selected_permission()
        
        if item_type != 'permission':
            messagebox.showwarning('提示', '请选择一个权限节点进行删除')
            return
        
        usage_info = self._check_permission_usage(item_id)
        
        if DataManager.has_permission_children(item_id):
            if not messagebox.askyesno('确认', '该节点下有子节点，删除将同时删除所有子节点，确定要删除吗？'):
                return
        
        if usage_info:
            msg = f'该权限正在被使用：\n{usage_info}\n\n删除将同时移除权限包中的引用和相关授权记录，确定继续吗？'
        else:
            msg = '确定要删除该权限吗？'
        
        if messagebox.askyesno('确认', msg):
            DataManager.delete_permission(item_id)
            messagebox.showinfo('成功', '删除成功')
            self.load_data()

    def _check_permission_usage(self, permission_id):
        import json
        packages_df = DataManager.get_permission_packages()
        package_count = 0
        for _, row in packages_df.iterrows():
            if row['permissions']:
                permissions = json.loads(row['permissions'])
                if any(p['permission_id'] == permission_id for p in permissions):
                    package_count += 1
        
        assignments_df = DataManager.get_permission_assignments()
        assign_count = len(assignments_df[assignments_df['permission_id'] == permission_id])
        
        if package_count > 0 or assign_count > 0:
            return f'- 被 {package_count} 个权限包引用\n- 有 {assign_count} 条授权记录'
        return None

    def import_data(self):
        file_path = filedialog.askopenfilename(
            title='选择导入文件',
            filetypes=[('CSV文件', '*.csv')]
        )
        if file_path:
            try:
                count = ImportExport.import_permissions_from_csv(file_path)
                messagebox.showinfo('成功', f'导入成功，共{count}条记录')
                self.load_data()
            except Exception as e:
                messagebox.showerror('错误', f'导入失败: {e}')

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            title='选择导出文件',
            defaultextension='.csv',
            filetypes=[('CSV文件', '*.csv')]
        )
        if file_path:
            try:
                count = ImportExport.export_permissions_to_csv(file_path)
                messagebox.showinfo('成功', f'导出成功，共{count}条记录')
            except Exception as e:
                messagebox.showerror('错误', f'导出失败: {e}')


class PermissionDialog(tk.Toplevel):
    def __init__(self, parent, title, permission_data=None, system_id=None, parent_id='', auto_level=1, auto_code=''):
        super().__init__(parent)
        self.title(title)
        self.geometry('500x350')
        self.resizable(False, False)
        self.result = False
        self.permission_data = permission_data
        self.system_id = system_id
        self.parent_id = parent_id
        self.auto_level = auto_level
        self.auto_code = auto_code
        
        self.create_widgets()
        if permission_data is not None:
            self.load_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text='所属系统:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.system_var = tk.StringVar()
        self.system_combo = ttk.Combobox(form_frame, textvariable=self.system_var, width=35, state='readonly')
        self.system_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        systems_df = DataManager.get_systems()
        self.system_map = {row['name']: row['id'] for _, row in systems_df.iterrows()}
        self.system_combo['values'] = list(self.system_map.keys())
        
        if self.system_id:
            for name, sid in self.system_map.items():
                if sid == self.system_id:
                    self.system_var.set(name)
                    break
        
        ttk.Label(form_frame, text='权限名称:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=38)
        self.name_entry.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        ttk.Label(form_frame, text='权限编码:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.code_label = ttk.Label(form_frame, text=self.auto_code or '(自动生成)', width=35)
        self.code_label.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        ttk.Label(form_frame, text='权限级别:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.level_label = ttk.Label(form_frame, text=str(self.auto_level), width=35)
        self.level_label.grid(row=3, column=1, pady=5, sticky=tk.W)
        
        ttk.Label(form_frame, text='描述:').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.desc_entry = ttk.Entry(form_frame, width=38)
        self.desc_entry.grid(row=4, column=1, pady=5, sticky=tk.W)
        
        ttk.Label(form_frame, text='状态:').grid(row=5, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value='1')
        status_frame = ttk.Frame(form_frame)
        status_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(status_frame, text='启用', variable=self.status_var, value='1').pack(side=tk.LEFT)
        ttk.Radiobutton(status_frame, text='禁用', variable=self.status_var, value='0').pack(side=tk.LEFT, padx=20)
        
        parent_info = ''
        if self.permission_data:
            parent_info = '编辑模式'
        elif self.parent_id:
            df = DataManager.get_permissions()
            parent = df[df['id'] == self.parent_id]
            if not parent.empty:
                parent_info = f'父节点: {parent.iloc[0]["name"]}'
        else:
            parent_info = '根节点权限'
        
        ttk.Label(form_frame, text=f'当前层级: {parent_info}').grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text='保存', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        systems_df = DataManager.get_systems()
        system = systems_df[systems_df['id'] == self.permission_data['system_id']]
        if not system.empty:
            self.system_var.set(system.iloc[0]['name'])
        
        self.name_entry.insert(0, self.permission_data['name'])
        self.code_label.config(text=self.permission_data['code'] or '')
        self.level_label.config(text=str(self.permission_data['level']))
        self.desc_entry.insert(0, self.permission_data['description'] or '')
        self.status_var.set(str(self.permission_data['status']))

    def save(self):
        system_name = self.system_var.get()
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        status = int(self.status_var.get())
        
        if not system_name or not name:
            messagebox.showwarning('提示', '所属系统和权限名称不能为空')
            return
        
        system_id = self.system_map.get(system_name)
        if not system_id:
            messagebox.showwarning('提示', '请选择有效的系统')
            return
        
        try:
            if self.permission_data is None:
                code = DataManager.generate_permission_code(system_id, self.parent_id)
                level = DataManager.calculate_permission_level(self.parent_id)
                DataManager.add_permission(name, code, level, description, system_id, self.parent_id, is_leaf=True)
            else:
                DataManager.update_permission(
                    self.permission_data['id'],
                    name=name,
                    description=description,
                    system_id=system_id,
                    status=status
                )
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'保存失败: {e}')

import tkinter as tk
from tkinter import ttk, messagebox
import json
from ..utils.data_manager import DataManager
from ..utils.logger import Logger


class PermissionPackagePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.create_header()
        self.create_toolbar()
        self.create_main_content()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='权限包管理', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        desc_label = ttk.Label(header_frame, text='将多个权限打包，可跨系统，便于批量授权', foreground='gray')
        desc_label.pack(side=tk.LEFT, padx=20)

    def create_toolbar(self):
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(toolbar_frame, text='新增权限包', command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='编辑', command=self.show_edit_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='删除', command=self.delete_package).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='复制', command=self.copy_package).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar_frame, text='授权给人员', command=self.show_assign_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar_frame, text='新增分类', command=self.add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='编辑分类', command=self.edit_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='删除分类', command=self.delete_category).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar_frame, text='刷新', command=self.load_data).pack(side=tk.LEFT, padx=5)

    def create_main_content(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        left_frame = ttk.LabelFrame(main_frame, text='权限包列表', width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        self.category_tree = ttk.Treeview(left_frame, show='tree', height=20)
        self.category_tree.heading('#0', text='分类/权限包')
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=scrollbar.set)
        
        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_tree.bind('<<TreeviewSelect>>', self.on_select)
        
        right_frame = ttk.LabelFrame(main_frame, text='权限详情', width=450)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)
        
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text='权限包名称:').grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pkg_name_label = ttk.Label(info_frame, text='', font=('', 10, 'bold'))
        self.pkg_name_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_frame, text='纸质文件编号:').grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pkg_doc_label = ttk.Label(info_frame, text='')
        self.pkg_doc_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_frame, text='描述:').grid(row=2, column=0, sticky=tk.W, pady=2)
        self.pkg_desc_label = ttk.Label(info_frame, text='')
        self.pkg_desc_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        detail_columns = ('系统', '权限编码', '权限名称', '级别')
        self.detail_tree = ttk.Treeview(right_frame, columns=detail_columns, show='headings', height=15)
        
        self.detail_tree.heading('系统', text='系统')
        self.detail_tree.heading('权限编码', text='编码')
        self.detail_tree.heading('权限名称', text='权限名称')
        self.detail_tree.heading('级别', text='级别')
        
        self.detail_tree.column('系统', width=80)
        self.detail_tree.column('权限编码', width=80)
        self.detail_tree.column('权限名称', width=120)
        self.detail_tree.column('级别', width=50, anchor='center')
        
        detail_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        self.categories = {}
        self.packages = {}

    def load_data(self):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        self.categories = {}
        self.packages = {}
        
        df = DataManager.get_permission_packages()
        
        categorized = {}
        uncategorized = []
        
        for _, row in df.iterrows():
            category = row.get('category', '') or ''
            if category:
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(row)
            else:
                uncategorized.append(row)
        
        for category, packages in categorized.items():
            cat_id = self.category_tree.insert('', tk.END, text=f'📁 {category}', open=True)
            self.categories[cat_id] = category
            
            for pkg in packages:
                permissions = json.loads(pkg['permissions']) if pkg['permissions'] else []
                perm_count = len(permissions)
                pkg_id = self.category_tree.insert(cat_id, tk.END, text=f'📦 {pkg["name"]} ({perm_count}个权限)')
                self.packages[pkg_id] = pkg.to_dict()
        
        for pkg in uncategorized:
            permissions = json.loads(pkg['permissions']) if pkg['permissions'] else []
            perm_count = len(permissions)
            pkg_id = self.category_tree.insert('', tk.END, text=f'📦 {pkg["name"]} ({perm_count}个权限)')
            self.packages[pkg_id] = pkg.to_dict()

    def on_select(self, event=None):
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        
        self.pkg_name_label.config(text='')
        self.pkg_doc_label.config(text='')
        self.pkg_desc_label.config(text='')
        
        selected = self.category_tree.selection()
        if not selected:
            return
        
        item_id = selected[0]
        
        if item_id in self.packages:
            package = self.packages[item_id]
            
            self.pkg_name_label.config(text=package['name'])
            self.pkg_doc_label.config(text=package.get('document_no', '') or '')
            self.pkg_desc_label.config(text=package.get('description', '') or '')
            
            permissions = json.loads(package['permissions']) if package['permissions'] else []
            
            systems_df = DataManager.get_systems()
            permissions_df = DataManager.get_permissions()
            
            for perm in permissions:
                system = systems_df[systems_df['id'] == perm['system_id']]
                perm_info = permissions_df[permissions_df['id'] == perm['permission_id']]
                
                system_name = system.iloc[0]['name'] if not system.empty else '未知'
                perm_name = perm_info.iloc[0]['name'] if not perm_info.empty else '未知'
                perm_code = perm_info.iloc[0]['code'] if not perm_info.empty else ''
                perm_level = perm_info.iloc[0]['level'] if not perm_info.empty else ''
                
                self.detail_tree.insert('', tk.END, values=(system_name, perm_code, perm_name, perm_level))

    def get_selected_package(self):
        selected = self.category_tree.selection()
        if not selected:
            return None
        
        item_id = selected[0]
        if item_id in self.packages:
            return self.packages[item_id]
        return None

    def show_add_dialog(self):
        selected = self.category_tree.selection()
        default_category = ''
        if selected:
            item_id = selected[0]
            if item_id in self.categories:
                default_category = self.categories[item_id]
        
        dialog = PackageDialog(self, '新增权限包', default_category=default_category)
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def show_edit_dialog(self):
        package = self.get_selected_package()
        if not package:
            messagebox.showwarning('提示', '请选择要编辑的权限包')
            return
        
        dialog = PackageDialog(self, '编辑权限包', package)
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def delete_package(self):
        package = self.get_selected_package()
        if not package:
            messagebox.showwarning('提示', '请选择要删除的权限包')
            return
        
        if messagebox.askyesno('确认', '确定要删除选中的权限包吗？'):
            DataManager.delete_permission_package(package['id'])
            messagebox.showinfo('成功', '删除成功')
            self.load_data()

    def copy_package(self):
        package = self.get_selected_package()
        if not package:
            messagebox.showwarning('提示', '请选择要复制的权限包')
            return
        
        permissions = json.loads(package['permissions']) if package['permissions'] else []
        
        new_id = DataManager.add_permission_package(
            f"{package['name']} - 副本",
            package.get('description', ''),
            permissions,
            package.get('document_no', ''),
            package.get('category', '')
        )
        
        messagebox.showinfo('成功', '权限包复制成功')
        self.load_data()

    def show_assign_dialog(self):
        package = self.get_selected_package()
        if not package:
            messagebox.showwarning('提示', '请选择要授权的权限包')
            return
        
        dialog = PackageAssignDialog(self, '权限包授权', package)
        self.wait_window(dialog)
        if dialog.result:
            messagebox.showinfo('成功', '权限包授权成功')

    def add_category(self):
        dialog = CategoryDialog(self, '新增分类')
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def edit_category(self):
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showwarning('提示', '请选择要编辑的分类')
            return
        
        item_id = selected[0]
        if item_id not in self.categories:
            messagebox.showwarning('提示', '请选择分类节点')
            return
        
        old_category = self.categories[item_id]
        dialog = CategoryDialog(self, '编辑分类', old_category)
        self.wait_window(dialog)
        if dialog.result:
            new_category = dialog.category_name
            df = DataManager.get_permission_packages()
            for _, row in df.iterrows():
                if row.get('category', '') == old_category:
                    DataManager.update_permission_package(row['id'], category=new_category)
            self.load_data()

    def delete_category(self):
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showwarning('提示', '请选择要删除的分类')
            return
        
        item_id = selected[0]
        if item_id not in self.categories:
            messagebox.showwarning('提示', '请选择分类节点')
            return
        
        category = self.categories[item_id]
        
        df = DataManager.get_permission_packages()
        has_packages = any(row.get('category', '') == category for _, row in df.iterrows())
        
        if has_packages:
            if not messagebox.askyesno('确认', f'分类"{category}"下有权限包，删除分类将把这些权限包移至未分类，确定继续吗？'):
                return
            for _, row in df.iterrows():
                if row.get('category', '') == category:
                    DataManager.update_permission_package(row['id'], category='')
        else:
            if not messagebox.askyesno('确认', f'确定要删除分类"{category}"吗？'):
                return
        
        self.load_data()


class PackageDialog(tk.Toplevel):
    def __init__(self, parent, title, package_data=None, default_category=''):
        super().__init__(parent)
        self.title(title)
        self.geometry('800x650')
        self.resizable(False, False)
        self.result = False
        self.package_data = package_data
        self.default_category = default_category
        self.selected_permissions = {}
        self.permission_items = {}
        
        self.create_widgets()
        if package_data is not None:
            self.load_data()

    def create_widgets(self):
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text='确定', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        form_frame = ttk.Frame(main_container, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text='权限包名称:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=50)
        self.name_entry.grid(row=0, column=1, pady=5, sticky=tk.W, columnspan=2)
        
        ttk.Label(form_frame, text='所属机构:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(form_frame, width=47)
        self.category_combo.grid(row=1, column=1, pady=5, sticky=tk.W, columnspan=2)
        self.load_categories()
        if self.default_category:
            self.category_combo.set(self.default_category)
        
        ttk.Label(form_frame, text='纸质文件编号:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.doc_no_entry = ttk.Entry(form_frame, width=50)
        self.doc_no_entry.grid(row=2, column=1, pady=5, sticky=tk.W, columnspan=2)
        
        ttk.Label(form_frame, text='描述:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.desc_entry = ttk.Entry(form_frame, width=50)
        self.desc_entry.grid(row=3, column=1, pady=5, sticky=tk.W, columnspan=2)
        
        ttk.Label(form_frame, text='选择权限 (点击勾选):').grid(row=4, column=0, sticky=tk.NW, pady=5)
        
        perm_frame = ttk.Frame(form_frame)
        perm_frame.grid(row=4, column=1, pady=5, sticky=tk.NSEW, columnspan=2)
        form_frame.rowconfigure(4, weight=1)
        form_frame.columnconfigure(1, weight=1)
        
        tree_frame = ttk.LabelFrame(perm_frame, text='权限树 (系统 → 权限)')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.perm_tree = ttk.Treeview(tree_frame, show='tree', height=15)
        
        style = ttk.Style()
        style.configure('Treeview', rowheight=25)
        
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.perm_tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.perm_tree.xview)
        self.perm_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        self.perm_tree.grid(row=0, column=0, sticky='nsew')
        tree_scrollbar_y.grid(row=0, column=1, sticky='ns')
        tree_scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        self.perm_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.perm_tree.bind('<Button-1>', self.on_click)
        self.perm_tree.bind('<space>', self.on_space)
        
        self.load_permission_tree()
        
        btn_frame = ttk.Frame(perm_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text='全选', command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='全不选', command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='展开全部', command=self.expand_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='折叠全部', command=self.collapse_all).pack(side=tk.LEFT, padx=5)
        
        self.selected_label = ttk.Label(perm_frame, text='已选择: 0 个权限')
        self.selected_label.pack(anchor=tk.W, pady=5)

    def load_categories(self):
        df = DataManager.get_permission_packages()
        categories = set()
        for _, row in df.iterrows():
            cat = row.get('category', '') or ''
            if cat:
                categories.add(cat)
        self.category_combo['values'] = sorted(list(categories))

    def load_permission_tree(self):
        for item in self.perm_tree.get_children():
            self.perm_tree.delete(item)
        
        self.selected_permissions = {}
        self.permission_items = {}
        
        systems_df = DataManager.get_systems()
        
        for _, system in systems_df.iterrows():
            if system['status'] == 0:
                continue
            
            system_id = system['id']
            system_node = self.perm_tree.insert('', tk.END, text=f'📁 {system["name"]}', open=False)
            
            self._load_permission_subtree(system_node, system_id, '')

    def _load_permission_subtree(self, parent_node, system_id, parent_id):
        permissions_df = DataManager.get_permission_children(parent_id, system_id)
        
        for _, perm in permissions_df.iterrows():
            if perm['status'] == 0:
                continue
            
            is_leaf = perm.get('is_leaf', True)
            icon = '📄' if is_leaf else '📁'
            
            perm_text = f'{icon} ☐ {perm.get("code", "")} - {perm["name"]} (级别: {perm["level"]})'
            perm_node = self.perm_tree.insert(parent_node, tk.END, text=perm_text, open=False)
            
            self.permission_items[perm_node] = {
                'permission_id': perm['id'],
                'system_id': system_id,
                'code': perm.get('code', ''),
                'name': perm['name'],
                'level': perm['level'],
                'is_leaf': is_leaf,
                'checked': False
            }
            
            self._load_permission_subtree(perm_node, system_id, perm['id'])

    def on_tree_select(self, event=None):
        pass

    def on_click(self, event):
        item = self.perm_tree.identify_row(event.y)
        if not item or item not in self.permission_items:
            return
        
        bbox = self.perm_tree.bbox(item, column='#0')
        if bbox:
            item_x, item_y, item_w, item_h = bbox
            click_offset = event.x - item_x
            if click_offset < 30:
                return
        
        self.toggle_item(item)
        return 'break'

    def on_space(self, event):
        selected = self.perm_tree.selection()
        for item in selected:
            if item in self.permission_items:
                self.toggle_item(item)

    def toggle_item(self, item):
        perm_info = self.permission_items[item]
        perm_info['checked'] = not perm_info['checked']
        
        is_leaf = perm_info.get('is_leaf', True)
        icon = '📄' if is_leaf else '📁'
        
        if perm_info['checked']:
            perm_key = f"{perm_info['system_id']}_{perm_info['permission_id']}"
            self.selected_permissions[perm_key] = {
                'permission_id': perm_info['permission_id'],
                'system_id': perm_info['system_id']
            }
            new_text = f'{icon} ☑ {perm_info["code"]} - {perm_info["name"]} (级别: {perm_info["level"]})'
            self._toggle_children(item, True)
        else:
            perm_key = f"{perm_info['system_id']}_{perm_info['permission_id']}"
            if perm_key in self.selected_permissions:
                del self.selected_permissions[perm_key]
            new_text = f'{icon} ☐ {perm_info["code"]} - {perm_info["name"]} (级别: {perm_info["level"]})'
            self._toggle_children(item, False)
        
        self.perm_tree.item(item, text=new_text)
        self._update_parent_states(item)
        self.update_selected_count()

    def _toggle_children(self, parent_item, checked):
        children = self.perm_tree.get_children(parent_item)
        for child in children:
            if child in self.permission_items:
                child_info = self.permission_items[child]
                child_info['checked'] = checked
                
                is_leaf = child_info.get('is_leaf', True)
                icon = '📄' if is_leaf else '📁'
                perm_key = f"{child_info['system_id']}_{child_info['permission_id']}"
                
                if checked:
                    self.selected_permissions[perm_key] = {
                        'permission_id': child_info['permission_id'],
                        'system_id': child_info['system_id']
                    }
                    new_text = f'{icon} ☑ {child_info["code"]} - {child_info["name"]} (级别: {child_info["level"]})'
                else:
                    if perm_key in self.selected_permissions:
                        del self.selected_permissions[perm_key]
                    new_text = f'{icon} ☐ {child_info["code"]} - {child_info["name"]} (级别: {child_info["level"]})'
                
                self.perm_tree.item(child, text=new_text)
                self._toggle_children(child, checked)
    
    def _update_parent_states(self, item):
        parent = self.perm_tree.parent(item)
        while parent:
            if parent in self.permission_items:
                self._update_single_parent_state(parent)
            parent = self.perm_tree.parent(parent)
    
    def _update_single_parent_state(self, parent_item):
        if parent_item not in self.permission_items:
            return
            
        children = self.perm_tree.get_children(parent_item)
        if not children:
            return
            
        checked_count = 0
        partial_count = 0
        total_count = 0
        
        for child in children:
            if child in self.permission_items:
                total_count += 1
                child_info = self.permission_items[child]
                if child_info['checked']:
                    checked_count += 1
                elif self._has_checked_descendants(child):
                    partial_count += 1
        
        parent_info = self.permission_items[parent_item]
        is_leaf = parent_info.get('is_leaf', True)
        icon = '📄' if is_leaf else '📁'
        
        if checked_count == total_count and total_count > 0:
            parent_info['checked'] = True
            perm_key = f"{parent_info['system_id']}_{parent_info['permission_id']}"
            self.selected_permissions[perm_key] = {
                'permission_id': parent_info['permission_id'],
                'system_id': parent_info['system_id']
            }
            new_text = f'{icon} ☑ {parent_info["code"]} - {parent_info["name"]} (级别: {parent_info["level"]})'
        elif checked_count > 0 or partial_count > 0:
            parent_info['checked'] = False
            perm_key = f"{parent_info['system_id']}_{parent_info['permission_id']}"
            if perm_key in self.selected_permissions:
                del self.selected_permissions[perm_key]
            new_text = f'{icon} ⊟ {parent_info["code"]} - {parent_info["name"]} (级别: {parent_info["level"]})'
        else:
            parent_info['checked'] = False
            perm_key = f"{parent_info['system_id']}_{parent_info['permission_id']}"
            if perm_key in self.selected_permissions:
                del self.selected_permissions[perm_key]
            new_text = f'{icon} ☐ {parent_info["code"]} - {parent_info["name"]} (级别: {parent_info["level"]})'
        
        self.perm_tree.item(parent_item, text=new_text)
    
    def _has_checked_descendants(self, item):
        children = self.perm_tree.get_children(item)
        for child in children:
            if child in self.permission_items:
                child_info = self.permission_items[child]
                if child_info['checked']:
                    return True
                if self._has_checked_descendants(child):
                    return True
        return False

    def update_selected_count(self):
        count = len(self.selected_permissions)
        self.selected_label.config(text=f'已选择: {count} 个权限')

    def select_all(self):
        for item in self.permission_items:
            perm_info = self.permission_items[item]
            if not perm_info['checked']:
                perm_info['checked'] = True
                perm_key = f"{perm_info['system_id']}_{perm_info['permission_id']}"
                self.selected_permissions[perm_key] = {
                    'permission_id': perm_info['permission_id'],
                    'system_id': perm_info['system_id']
                }
                is_leaf = perm_info.get('is_leaf', True)
                icon = '📄' if is_leaf else '📁'
                new_text = f'{icon} ☑ {perm_info["code"]} - {perm_info["name"]} (级别: {perm_info["level"]})'
                self.perm_tree.item(item, text=new_text)
        self.update_selected_count()

    def deselect_all(self):
        for item in self.permission_items:
            perm_info = self.permission_items[item]
            if perm_info['checked']:
                perm_info['checked'] = False
                is_leaf = perm_info.get('is_leaf', True)
                icon = '📄' if is_leaf else '📁'
                new_text = f'{icon} ☐ {perm_info["code"]} - {perm_info["name"]} (级别: {perm_info["level"]})'
                self.perm_tree.item(item, text=new_text)
        self.selected_permissions = {}
        self.update_selected_count()

    def expand_all(self):
        def expand_item(item):
            self.perm_tree.item(item, open=True)
            for child in self.perm_tree.get_children(item):
                expand_item(child)
        
        for item in self.perm_tree.get_children():
            expand_item(item)

    def collapse_all(self):
        def collapse_item(item):
            self.perm_tree.item(item, open=False)
            for child in self.perm_tree.get_children(item):
                collapse_item(child)
        
        for item in self.perm_tree.get_children():
            collapse_item(item)

    def load_data(self):
        self.name_entry.insert(0, self.package_data['name'])
        self.doc_no_entry.insert(0, self.package_data.get('document_no', '') or '')
        self.desc_entry.insert(0, self.package_data.get('description', '') or '')
        
        category = self.package_data.get('category', '') or ''
        if category:
            self.category_combo.set(category)
        
        permissions = json.loads(self.package_data['permissions']) if self.package_data['permissions'] else []
        
        for perm in permissions:
            perm_key = f"{perm['system_id']}_{perm['permission_id']}"
            self.selected_permissions[perm_key] = perm
        
        self._restore_selections()

    def _restore_selections(self):
        for item in self.permission_items:
            perm_info = self.permission_items[item]
            perm_key = f"{perm_info['system_id']}_{perm_info['permission_id']}"
            
            if perm_key in self.selected_permissions:
                perm_info['checked'] = True
                is_leaf = perm_info.get('is_leaf', True)
                icon = '📄' if is_leaf else '📁'
                new_text = f'{icon} ☑ {perm_info["code"]} - {perm_info["name"]} (级别: {perm_info["level"]})'
                self.perm_tree.item(item, text=new_text)
        
        for item in self.permission_items:
            children = self.perm_tree.get_children(item)
            if children:
                self._update_single_parent_state(item)
        
        self.update_selected_count()

    def save(self):
        name = self.name_entry.get().strip()
        doc_no = self.doc_no_entry.get().strip()
        description = self.desc_entry.get().strip()
        category = self.category_combo.get().strip()
        
        if not name:
            messagebox.showwarning('提示', '权限包名称不能为空')
            return
        
        permissions = list(self.selected_permissions.values())
        
        if not permissions:
            messagebox.showwarning('提示', '请至少选择一个权限')
            return
        
        try:
            if self.package_data is None:
                DataManager.add_permission_package(name, description, permissions, doc_no, category)
            else:
                DataManager.update_permission_package(
                    self.package_data['id'],
                    name=name,
                    description=description,
                    permissions=permissions,
                    document_no=doc_no,
                    category=category
                )
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'保存失败: {e}')


class CategoryDialog(tk.Toplevel):
    def __init__(self, parent, title, category_name=''):
        super().__init__(parent)
        self.title(title)
        self.geometry('400x150')
        self.resizable(False, False)
        self.result = False
        self.category_name = category_name
        
        self.create_widgets()
        if category_name:
            self.name_entry.insert(0, category_name)

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text='分类名称:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text='保存', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning('提示', '分类名称不能为空')
            return
        
        self.category_name = name
        self.result = True
        self.destroy()


class PackageAssignDialog(tk.Toplevel):
    def __init__(self, parent, title, package_data):
        super().__init__(parent)
        self.title(title)
        self.geometry('500x450')
        self.resizable(False, False)
        self.result = False
        self.package_data = package_data
        self.all_personnel_data = []
        
        self.create_widgets()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text=f'权限包: {self.package_data["name"]}', font=('', 11, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text='选择人员 (可多选):').grid(row=1, column=0, sticky=tk.NW, pady=5)
        
        list_container = ttk.Frame(form_frame)
        list_container.grid(row=1, column=1, pady=5, sticky=tk.NSEW)
        
        search_frame = ttk.Frame(list_container)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text='搜索类型:').pack(side=tk.LEFT)
        self.search_type_var = tk.StringVar(value='全部')
        self.search_type_combo = ttk.Combobox(search_frame, textvariable=self.search_type_var, 
                                               width=8, state='readonly')
        self.search_type_combo['values'] = ['全部', '姓名', '科室']
        self.search_type_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text='关键词:').pack(side=tk.LEFT)
        self.personnel_search_var = tk.StringVar()
        self.personnel_search_var.trace('w', self.on_personnel_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.personnel_search_var, width=15)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text='重置', command=self.reset_personnel_search).pack(side=tk.LEFT)
        
        list_frame = ttk.Frame(list_container)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.personnel_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.personnel_listbox.yview)
        self.personnel_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.personnel_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        personnel_df = DataManager.get_personnel()
        self.personnel_map = {}
        self.all_personnel_data = []
        
        sorted_df = personnel_df.sort_values('name')
        
        for _, row in sorted_df.iterrows():
            if row['status'] == 1:
                label = f"{row['name']} ({row['employee_id']}) - {row['department']}"
                self.personnel_listbox.insert(tk.END, label)
                self.personnel_map[label] = row['id']
                self.all_personnel_data.append({
                    'label': label,
                    'name': row['name'],
                    'employee_id': row['employee_id'],
                    'department': row['department']
                })
        
        ttk.Label(form_frame, text='纸质文件编号:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.doc_no_entry = ttk.Entry(form_frame, width=40)
        self.doc_no_entry.grid(row=2, column=1, pady=5, sticky=tk.W)
        self.doc_no_entry.insert(0, self.package_data.get('document_no', '') or '')
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text='授权', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.LEFT, padx=5)

    def on_personnel_search_change(self, *args):
        keyword = self.personnel_search_var.get().strip().lower()
        search_type = self.search_type_var.get()
        
        self.personnel_listbox.delete(0, tk.END)
        
        for item in self.all_personnel_data:
            if not keyword:
                self.personnel_listbox.insert(tk.END, item['label'])
            else:
                match = False
                if search_type == '全部':
                    match = (keyword in item['name'].lower() or 
                             keyword in item['department'].lower())
                elif search_type == '姓名':
                    match = keyword in item['name'].lower()
                elif search_type == '科室':
                    match = keyword in item['department'].lower()
                
                if match:
                    self.personnel_listbox.insert(tk.END, item['label'])

    def reset_personnel_search(self):
        self.search_type_var.set('全部')
        self.personnel_search_var.set('')
        self.personnel_listbox.delete(0, tk.END)
        for item in self.all_personnel_data:
            self.personnel_listbox.insert(tk.END, item['label'])

    def save(self):
        selected_indices = self.personnel_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning('提示', '请选择至少一个人员')
            return
        
        doc_no = self.doc_no_entry.get().strip()
        
        personnel_ids = []
        for idx in selected_indices:
            label = self.personnel_listbox.get(idx)
            personnel_ids.append(self.personnel_map[label])
        
        try:
            DataManager.assign_package(personnel_ids, self.package_data['id'], grantor_id='system', document_no=doc_no)
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'授权失败: {e}')

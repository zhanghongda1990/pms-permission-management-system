import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd
from ..utils.data_manager import DataManager
from ..utils.import_export import ImportExport
from ..utils.logger import Logger


class PermissionAssignPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.create_header()
        self.create_toolbar()
        self.create_treeview()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='权限分配', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)

    def create_toolbar(self):
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(toolbar_frame, text='人员筛选:').pack(side=tk.LEFT, padx=5)
        self.personnel_var = tk.StringVar(value='全部')
        self.personnel_combo = ttk.Combobox(toolbar_frame, textvariable=self.personnel_var, width=15, state='readonly')
        self.personnel_combo.pack(side=tk.LEFT, padx=5)
        self.personnel_combo.bind('<<ComboboxSelected>>', self.on_filter)
        
        ttk.Label(toolbar_frame, text='系统筛选:').pack(side=tk.LEFT, padx=5)
        self.system_var = tk.StringVar(value='全部')
        self.system_combo = ttk.Combobox(toolbar_frame, textvariable=self.system_var, width=15, state='readonly')
        self.system_combo.pack(side=tk.LEFT, padx=5)
        self.system_combo.bind('<<ComboboxSelected>>', self.on_filter)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text='新增分配', command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='权限包分配', command=self.show_package_assign_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='删除权限', command=self.revoke_permission).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text='导出申请表', command=self.export_application).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text='刷新', command=self.load_data).pack(side=tk.RIGHT, padx=5)

    def create_treeview(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('人员', '工号', '部门', '系统', '权限编码', '权限', '级别', '授权时间', '过期时间', '纸质文件编号')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        
        self.tree.column('人员', width=70)
        self.tree.column('工号', width=70)
        self.tree.column('部门', width=80)
        self.tree.column('权限编码', width=80)
        self.tree.column('授权时间', width=120)
        self.tree.column('过期时间', width=80)
        self.tree.column('纸质文件编号', width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        personnel_df = DataManager.get_personnel()
        systems_df = DataManager.get_systems()
        permissions_df = DataManager.get_permissions()
        packages_df = DataManager.get_permission_packages()
        assignments_df = DataManager.get_permission_assignments()
        
        personnel_list = ['全部'] + [f"{row['name']}({row['employee_id']})" for _, row in personnel_df.iterrows()]
        self.personnel_combo['values'] = personnel_list
        
        system_list = ['全部'] + [row['name'] for _, row in systems_df.iterrows()]
        self.system_combo['values'] = system_list
        
        package_assignments = {}
        individual_assignments = []
        
        for _, assign in assignments_df.iterrows():
            if assign['status'] != 1:
                continue
            package_id = str(assign['package_id']) if 'package_id' in assign.index and pd.notna(assign['package_id']) and str(assign['package_id']).strip() else ''
            if package_id:
                key = (assign['personnel_id'], package_id, assign.get('document_no', '') or '')
                if key not in package_assignments:
                    package_assignments[key] = {
                        'personnel_id': assign['personnel_id'],
                        'package_id': package_id,
                        'document_no': assign.get('document_no', '') or '',
                        'grant_time': assign['grant_time'],
                        'expire_time': assign['expire_time'],
                        'status': assign['status'],
                        'permission_count': 1
                    }
                else:
                    package_assignments[key]['permission_count'] += 1
            else:
                individual_assignments.append(assign)
        
        for key, pkg_assign in package_assignments.items():
            person = personnel_df[personnel_df['id'] == pkg_assign['personnel_id']]
            package = packages_df[packages_df['id'] == pkg_assign['package_id']]
            
            if person.empty or package.empty:
                continue
            
            person_name = person.iloc[0]['name']
            employee_id = person.iloc[0]['employee_id']
            department = person.iloc[0]['department']
            package_name = package.iloc[0]['name']
            
            grant_time = pkg_assign['grant_time'].strftime('%Y-%m-%d %H:%M') if pkg_assign['grant_time'] else ''
            expire_time = pkg_assign['expire_time'].strftime('%Y-%m-%d') if pkg_assign['expire_time'] else ''
            document_no = pkg_assign['document_no']
            
            self.tree.insert('', tk.END, values=(
                person_name,
                employee_id,
                department,
                '权限包',
                f"[权限包] {package_name}",
                f"包含{pkg_assign['permission_count']}个权限",
                '-',
                grant_time,
                expire_time,
                document_no
            ), tags=(f"package_{pkg_assign['package_id']}_{pkg_assign['personnel_id']}",))
        
        for assign in individual_assignments:
            person = personnel_df[personnel_df['id'] == assign['personnel_id']]
            system = systems_df[systems_df['id'] == assign['system_id']]
            perm = permissions_df[permissions_df['id'] == assign['permission_id']]
            
            if person.empty:
                continue
            
            person_name = person.iloc[0]['name']
            employee_id = person.iloc[0]['employee_id']
            department = person.iloc[0]['department']
            system_name = system.iloc[0]['name'] if not system.empty else '未知'
            perm_name = perm.iloc[0]['name'] if not perm.empty else '未知'
            perm_code = perm.iloc[0].get('code', '') if not perm.empty else ''
            perm_level = perm.iloc[0]['level'] if not perm.empty else ''
            
            grant_time = assign['grant_time'].strftime('%Y-%m-%d %H:%M') if assign['grant_time'] else ''
            expire_time = assign['expire_time'].strftime('%Y-%m-%d') if assign['expire_time'] else ''
            document_no = assign.get('document_no', '') or ''
            
            self.tree.insert('', tk.END, values=(
                person_name,
                employee_id,
                department,
                system_name,
                perm_code,
                perm_name,
                perm_level,
                grant_time,
                expire_time,
                document_no
            ), tags=(assign['id'],))

    def on_filter(self, event=None):
        personnel_filter = self.personnel_var.get()
        system_filter = self.system_var.get()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            
            personnel_match = personnel_filter == '全部' or values[0] in personnel_filter
            system_match = system_filter == '全部' or values[3] == system_filter or values[3] == '权限包'
            
            if personnel_match and system_match:
                pass
            else:
                self.tree.delete(item)

    def show_add_dialog(self):
        dialog = AssignDialog(self, '新增权限分配')
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def show_package_assign_dialog(self):
        dialog = PackageAssignDialog(self, '权限包分配')
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def revoke_permission(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('提示', '请选择要删除的权限')
            return
        
        if messagebox.askyesno('确认', '确定要删除选中的权限吗？'):
            for item in selected:
                tag = self.tree.item(item)['tags'][0]
                if tag.startswith('package_'):
                    parts = tag.split('_')
                    if len(parts) >= 3:
                        package_id = parts[1]
                        personnel_id = parts[2]
                        DataManager.revoke_package(personnel_id, package_id)
                else:
                    DataManager.revoke_permission(tag)
            messagebox.showinfo('成功', '权限已删除')
            self.load_data()

    def export_application(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('提示', '请选择要导出的人员')
            return
        
        tag = self.tree.item(selected[0])['tags'][0]
        
        if tag.startswith('package_'):
            parts = tag.split('_')
            if len(parts) >= 3:
                personnel_id = parts[2]
            else:
                messagebox.showwarning('提示', '无法获取人员信息')
                return
        else:
            assignments_df = DataManager.get_permission_assignments()
            assign = assignments_df[assignments_df['id'] == tag]
            
            if assign.empty:
                return
            
            personnel_id = assign.iloc[0]['personnel_id']
        
        file_path = filedialog.asksaveasfilename(
            title='保存权限申请表',
            defaultextension='.xlsx',
            filetypes=[('Excel文件', '*.xlsx')]
        )
        
        if file_path:
            try:
                count = ImportExport.export_permission_application(file_path, personnel_id)
                messagebox.showinfo('成功', f'导出成功，共{count}条权限记录')
            except Exception as e:
                messagebox.showerror('错误', f'导出失败: {e}')


class AssignDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry('450x450')
        self.resizable(False, False)
        self.result = False
        
        self.create_widgets()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text='选择人员:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.personnel_var = tk.StringVar()
        self.personnel_combo = ttk.Combobox(form_frame, textvariable=self.personnel_var, width=30, state='readonly')
        self.personnel_combo.grid(row=0, column=1, pady=5)
        
        personnel_df = DataManager.get_personnel()
        self.personnel_map = {}
        for _, row in personnel_df.iterrows():
            label = f"{row['name']}({row['employee_id']})"
            self.personnel_map[label] = row['id']
        self.personnel_combo['values'] = list(self.personnel_map.keys())
        
        ttk.Label(form_frame, text='选择系统:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.system_var = tk.StringVar()
        self.system_combo = ttk.Combobox(form_frame, textvariable=self.system_var, width=30, state='readonly')
        self.system_combo.grid(row=1, column=1, pady=5)
        self.system_combo.bind('<<ComboboxSelected>>', self.on_system_change)
        
        systems_df = DataManager.get_systems()
        self.system_map = {row['name']: row['id'] for _, row in systems_df.iterrows()}
        self.system_combo['values'] = list(self.system_map.keys())
        
        ttk.Label(form_frame, text='选择权限:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.permission_var = tk.StringVar()
        self.permission_combo = ttk.Combobox(form_frame, textvariable=self.permission_var, width=30, state='readonly')
        self.permission_combo.grid(row=2, column=1, pady=5)
        
        ttk.Label(form_frame, text='过期时间:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.expire_entry = ttk.Entry(form_frame, width=32)
        self.expire_entry.grid(row=3, column=1, pady=5)
        self.expire_entry.insert(0, '留空表示永久有效')
        
        ttk.Label(form_frame, text='纸质文件编号:').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.doc_no_entry = ttk.Entry(form_frame, width=32)
        self.doc_no_entry.grid(row=4, column=1, pady=5)
        
        ttk.Label(form_frame, text='备注:').grid(row=5, column=0, sticky=tk.W, pady=5)
        self.remark_entry = ttk.Entry(form_frame, width=32)
        self.remark_entry.grid(row=5, column=1, pady=5)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text='保存', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.LEFT, padx=5)

    def on_system_change(self, event=None):
        system_name = self.system_var.get()
        system_id = self.system_map.get(system_name)
        
        if not system_id:
            return
        
        permissions_df = DataManager.get_permissions(system_id=system_id)
        self.permission_map = {f"[{row['level']}] {row['name']} ({row.get('code', '')})": row['id'] for _, row in permissions_df.iterrows()}
        self.permission_combo['values'] = list(self.permission_map.keys())
        self.permission_var.set('')

    def save(self):
        personnel_label = self.personnel_var.get()
        system_name = self.system_var.get()
        permission_label = self.permission_var.get()
        expire_time_str = self.expire_entry.get().strip()
        doc_no = self.doc_no_entry.get().strip()
        remark = self.remark_entry.get().strip()
        
        if not personnel_label or not system_name or not permission_label:
            messagebox.showwarning('提示', '请选择人员、系统和权限')
            return
        
        personnel_id = self.personnel_map.get(personnel_label)
        system_id = self.system_map.get(system_name)
        permission_id = self.permission_map.get(permission_label)
        
        expire_time = None
        if expire_time_str and expire_time_str != '留空表示永久有效':
            try:
                expire_time = datetime.strptime(expire_time_str, '%Y-%m-%d')
            except ValueError:
                messagebox.showwarning('提示', '过期时间格式错误，请使用YYYY-MM-DD格式')
                return
        
        try:
            DataManager.assign_permission(
                personnel_id, system_id, permission_id,
                grantor_id='system',
                expire_time=expire_time,
                remark=remark,
                document_no=doc_no
            )
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'保存失败: {e}')


class PackageAssignDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry('500x450')
        self.resizable(False, False)
        self.result = False
        
        self.all_personnel_data = []
        self.create_widgets()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text='选择人员 (可多选):').grid(row=0, column=0, sticky=tk.NW, pady=5)
        
        list_container = ttk.Frame(form_frame)
        list_container.grid(row=0, column=1, pady=5, sticky=tk.NSEW)
        
        search_frame = ttk.Frame(list_container)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text='搜索:').pack(side=tk.LEFT)
        self.personnel_search_var = tk.StringVar()
        self.personnel_search_var.trace('w', self.on_personnel_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.personnel_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text='重置', command=self.reset_personnel_search).pack(side=tk.LEFT)
        
        list_frame = ttk.Frame(list_container)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.personnel_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=8)
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
        
        ttk.Label(form_frame, text='选择权限包:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.package_var = tk.StringVar()
        self.package_combo = ttk.Combobox(form_frame, textvariable=self.package_var, width=35, state='readonly')
        self.package_combo.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        packages_df = DataManager.get_permission_packages()
        self.package_map = {}
        for _, row in packages_df.iterrows():
            label = f"{row['name']} ({row.get('document_no', '') or '无编号'})"
            self.package_map[label] = row['id']
        self.package_combo['values'] = list(self.package_map.keys())
        
        ttk.Label(form_frame, text='纸质文件编号:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.doc_no_entry = ttk.Entry(form_frame, width=37)
        self.doc_no_entry.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text='分配', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def on_personnel_search_change(self, *args):
        keyword = self.personnel_search_var.get().strip().lower()
        
        self.personnel_listbox.delete(0, tk.END)
        
        for item in self.all_personnel_data:
            if not keyword:
                self.personnel_listbox.insert(tk.END, item['label'])
            else:
                if (keyword in item['name'].lower() or 
                    keyword in item['employee_id'].lower() or 
                    keyword in item['department'].lower()):
                    self.personnel_listbox.insert(tk.END, item['label'])
    
    def reset_personnel_search(self):
        self.personnel_search_var.set('')
        self.personnel_listbox.delete(0, tk.END)
        for item in self.all_personnel_data:
            self.personnel_listbox.insert(tk.END, item['label'])

    def save(self):
        selected_indices = self.personnel_listbox.curselection()
        package_label = self.package_var.get()
        
        if not selected_indices:
            messagebox.showwarning('提示', '请选择至少一个人员')
            return
        
        if not package_label:
            messagebox.showwarning('提示', '请选择权限包')
            return
        
        doc_no = self.doc_no_entry.get().strip()
        package_id = self.package_map.get(package_label)
        
        personnel_ids = []
        for idx in selected_indices:
            label = self.personnel_listbox.get(idx)
            personnel_ids.append(self.personnel_map[label])
        
        try:
            DataManager.assign_package(personnel_ids, package_id, grantor_id='system', document_no=doc_no)
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'分配失败: {e}')

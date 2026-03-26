import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ..utils.data_manager import DataManager
from ..utils.logger import Logger


class PermissionCheckPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.load_personnel()

    def create_widgets(self):
        self.create_header()
        self.create_search_area()
        self.create_notebook()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='个人权限检查', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        desc_label = ttk.Label(header_frame, text='查看人员当前权限及授权历史记录', foreground='gray')
        desc_label.pack(side=tk.LEFT, padx=20)

    def create_search_area(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(search_frame, text='选择人员:').pack(side=tk.LEFT, padx=5)
        
        self.personnel_var = tk.StringVar()
        self.personnel_combo = ttk.Combobox(search_frame, textvariable=self.personnel_var, width=40, state='readonly')
        self.personnel_combo.pack(side=tk.LEFT, padx=5)
        self.personnel_combo.bind('<<ComboboxSelected>>', self.on_personnel_select)
        
        ttk.Button(search_frame, text='查询', command=self.query_permissions).pack(side=tk.LEFT, padx=10)
        ttk.Button(search_frame, text='清空', command=self.clear_results).pack(side=tk.LEFT, padx=5)

    def create_notebook(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        current_frame = ttk.Frame(self.notebook)
        self.notebook.add(current_frame, text='当前权限')
        self.create_current_permissions_view(current_frame)
        
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text='授权历史')
        self.create_history_view(history_frame)
        
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text='权限汇总')
        self.create_summary_view(summary_frame)

    def create_current_permissions_view(self, parent):
        columns = ('系统', '权限编码', '权限名称', '级别', '授权时间', '过期时间', '纸质文件编号', '备注')
        self.current_tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        for col in columns:
            self.current_tree.heading(col, text=col)
            self.current_tree.column(col, width=100)
        
        self.current_tree.column('系统', width=100)
        self.current_tree.column('权限编码', width=100)
        self.current_tree.column('权限名称', width=120)
        self.current_tree.column('授权时间', width=130)
        self.current_tree.column('过期时间', width=100)
        self.current_tree.column('纸质文件编号', width=120)
        self.current_tree.column('备注', width=150)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.current_tree.yview)
        self.current_tree.configure(yscrollcommand=scrollbar.set)
        
        self.current_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        info_frame = ttk.Frame(parent)
        
        self.current_count_label = ttk.Label(parent, text='共 0 条有效权限')
        self.current_count_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=5)

    def create_history_view(self, parent):
        columns = ('系统', '权限编码', '权限名称', '级别', '授权时间', '操作', '纸质文件编号', '备注')
        self.history_tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.column('系统', width=100)
        self.history_tree.column('权限编码', width=100)
        self.history_tree.column('权限名称', width=120)
        self.history_tree.column('授权时间', width=130)
        self.history_tree.column('操作', width=60)
        self.history_tree.column('纸质文件编号', width=120)
        self.history_tree.column('备注', width=150)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_count_label = ttk.Label(parent, text='共 0 条历史记录')
        self.history_count_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=5)

    def create_summary_view(self, parent):
        self.summary_text = tk.Text(parent, wrap=tk.WORD, state=tk.DISABLED, font=('Microsoft YaHei', 10))
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=scrollbar.set)
        
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_personnel(self):
        personnel_df = DataManager.get_personnel()
        self.personnel_map = {}
        
        personnel_list = []
        for _, row in personnel_df.iterrows():
            if row['status'] == 1:
                label = f"{row['name']} ({row['employee_id']}) - {row['department']}"
                personnel_list.append(label)
                self.personnel_map[label] = row['id']
        
        self.personnel_combo['values'] = personnel_list

    def on_personnel_select(self, event=None):
        self.query_permissions()

    def query_permissions(self):
        personnel_label = self.personnel_var.get()
        if not personnel_label:
            messagebox.showwarning('提示', '请选择人员')
            return
        
        personnel_id = self.personnel_map.get(personnel_label)
        if not personnel_id:
            return
        
        self.load_current_permissions(personnel_id)
        self.load_history(personnel_id)
        self.load_summary(personnel_id, personnel_label)

    def load_current_permissions(self, personnel_id):
        for item in self.current_tree.get_children():
            self.current_tree.delete(item)
        
        current_df = DataManager.get_personnel_current_permissions(personnel_id)
        systems_df = DataManager.get_systems()
        permissions_df = DataManager.get_permissions()
        
        count = 0
        for _, assign in current_df.iterrows():
            system = systems_df[systems_df['id'] == assign['system_id']]
            perm = permissions_df[permissions_df['id'] == assign['permission_id']]
            
            system_name = system.iloc[0]['name'] if not system.empty else '未知'
            perm_name = perm.iloc[0]['name'] if not perm.empty else '未知'
            perm_code = perm.iloc[0].get('code', '') if not perm.empty else ''
            perm_level = perm.iloc[0]['level'] if not perm.empty else ''
            
            grant_time = assign['grant_time'].strftime('%Y-%m-%d %H:%M') if assign['grant_time'] else ''
            expire_time = assign['expire_time'].strftime('%Y-%m-%d') if assign['expire_time'] else '永久'
            document_no = assign.get('document_no', '') or ''
            remark = assign.get('remark', '') or ''
            
            self.current_tree.insert('', tk.END, values=(
                system_name,
                perm_code,
                perm_name,
                perm_level,
                grant_time,
                expire_time,
                document_no,
                remark
            ))
            count += 1
        
        self.current_count_label.config(text=f'共 {count} 条有效权限')

    def load_history(self, personnel_id):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history_df = DataManager.get_personnel_permission_history(personnel_id)
        systems_df = DataManager.get_systems()
        permissions_df = DataManager.get_permissions()
        
        count = 0
        for _, assign in history_df.iterrows():
            system = systems_df[systems_df['id'] == assign['system_id']]
            perm = permissions_df[permissions_df['id'] == assign['permission_id']]
            
            system_name = system.iloc[0]['name'] if not system.empty else '未知'
            perm_name = perm.iloc[0]['name'] if not perm.empty else '未知'
            perm_code = perm.iloc[0].get('code', '') if not perm.empty else ''
            perm_level = perm.iloc[0]['level'] if not perm.empty else ''
            
            grant_time = assign['grant_time'].strftime('%Y-%m-%d %H:%M') if assign['grant_time'] else ''
            operation = '授权' if assign['status'] == 1 else '撤销'
            document_no = assign.get('document_no', '') or ''
            remark = assign.get('remark', '') or ''
            
            tags = ('active',) if assign['status'] == 1 else ('inactive',)
            
            self.history_tree.insert('', tk.END, values=(
                system_name,
                perm_code,
                perm_name,
                perm_level,
                grant_time,
                operation,
                document_no,
                remark
            ), tags=tags)
            count += 1
        
        self.history_tree.tag_configure('active', foreground='green')
        self.history_tree.tag_configure('inactive', foreground='gray')
        
        self.history_count_label.config(text=f'共 {count} 条历史记录')

    def load_summary(self, personnel_id, personnel_label):
        current_df = DataManager.get_personnel_current_permissions(personnel_id)
        systems_df = DataManager.get_systems()
        permissions_df = DataManager.get_permissions()
        
        system_perms = {}
        for _, assign in current_df.iterrows():
            system = systems_df[systems_df['id'] == assign['system_id']]
            perm = permissions_df[permissions_df['id'] == assign['permission_id']]
            
            system_name = system.iloc[0]['name'] if not system.empty else '未知'
            perm_name = perm.iloc[0]['name'] if not perm.empty else '未知'
            perm_code = perm.iloc[0].get('code', '') if not perm.empty else ''
            
            if system_name not in system_perms:
                system_perms[system_name] = []
            system_perms[system_name].append({
                'name': perm_name,
                'code': perm_code,
                'document_no': assign.get('document_no', '') or ''
            })
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        self.summary_text.insert(tk.END, f"人员: {personnel_label}\n")
        self.summary_text.insert(tk.END, f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.summary_text.insert(tk.END, "=" * 60 + "\n\n")
        
        total_perms = 0
        for system_name, perms in system_perms.items():
            self.summary_text.insert(tk.END, f"【{system_name}】共 {len(perms)} 项权限:\n")
            for perm in perms:
                doc_info = f" [文件号: {perm['document_no']}]" if perm['document_no'] else ""
                self.summary_text.insert(tk.END, f"  - [{perm['code']}] {perm['name']}{doc_info}\n")
            self.summary_text.insert(tk.END, "\n")
            total_perms += len(perms)
        
        self.summary_text.insert(tk.END, "=" * 60 + "\n")
        self.summary_text.insert(tk.END, f"总计: {len(system_perms)} 个系统, {total_perms} 项有效权限\n")
        
        doc_nos = set()
        for _, assign in current_df.iterrows():
            doc_no = assign.get('document_no', '')
            if doc_no:
                doc_nos.add(doc_no)
        
        if doc_nos:
            self.summary_text.insert(tk.END, f"\n相关纸质文件编号:\n")
            for doc_no in sorted(doc_nos):
                self.summary_text.insert(tk.END, f"  - {doc_no}\n")
        
        self.summary_text.config(state=tk.DISABLED)

    def clear_results(self):
        self.personnel_var.set('')
        
        for item in self.current_tree.get_children():
            self.current_tree.delete(item)
        
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.config(state=tk.DISABLED)
        
        self.current_count_label.config(text='共 0 条有效权限')
        self.history_count_label.config(text='共 0 条历史记录')

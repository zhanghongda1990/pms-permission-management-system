import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.data_manager import DataManager
from ..utils.config_manager import ConfigManager
from ..utils.logger import Logger


class SystemPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.create_header()
        self.create_toolbar()
        self.create_treeview()
        self.create_detail_panel()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='系统管理', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)

    def create_toolbar(self):
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(toolbar_frame, text='新增', command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='编辑', command=self.show_edit_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='启用/禁用', command=self.toggle_status).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar_frame, text='刷新', command=self.load_data).pack(side=tk.LEFT, padx=5)

    def create_treeview(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('系统名称', '系统编码', '状态', '权限数量', '创建时间')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def create_detail_panel(self):
        detail_frame = ttk.LabelFrame(self, text='系统详情')
        detail_frame.pack(fill=tk.X, padx=20, pady=10)
        
        info_frame = ttk.Frame(detail_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text='系统名称:').grid(row=0, column=0, sticky=tk.W, pady=2)
        self.detail_name = ttk.Label(info_frame, text='')
        self.detail_name.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_frame, text='系统编码:').grid(row=1, column=0, sticky=tk.W, pady=2)
        self.detail_code = ttk.Label(info_frame, text='')
        self.detail_code.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_frame, text='描述:').grid(row=2, column=0, sticky=tk.W, pady=2)
        self.detail_desc = ttk.Label(info_frame, text='')
        self.detail_desc.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_frame, text='权限列表:').grid(row=3, column=0, sticky=tk.NW, pady=2)
        self.permission_list = tk.Text(info_frame, width=40, height=5, state=tk.DISABLED)
        self.permission_list.grid(row=3, column=1, sticky=tk.W, pady=2)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        df = DataManager.get_systems()
        permissions_df = DataManager.get_permissions()
        
        for _, row in df.iterrows():
            status = '启用' if row['status'] == 1 else '禁用'
            perm_count = len(permissions_df[permissions_df['system_id'] == row['id']])
            create_time = row['create_time'].strftime('%Y-%m-%d') if row['create_time'] else ''
            
            self.tree.insert('', tk.END, values=(
                row['name'],
                row['code'],
                status,
                perm_count,
                create_time
            ), tags=(row['id'],))

    def on_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        
        system_id = self.tree.item(selected[0])['tags'][0]
        df = DataManager.get_systems()
        system = df[df['id'] == system_id].iloc[0]
        
        self.detail_name.config(text=system['name'])
        self.detail_code.config(text=system['code'])
        self.detail_desc.config(text=system['description'] or '无')
        
        permissions_df = DataManager.get_permissions(system_id=system_id)
        self.permission_list.config(state=tk.NORMAL)
        self.permission_list.delete(1.0, tk.END)
        
        if permissions_df.empty:
            self.permission_list.insert(tk.END, '暂无权限')
        else:
            for _, perm in permissions_df.iterrows():
                self.permission_list.insert(tk.END, f"[{perm['level']}] {perm['name']}\n")
        
        self.permission_list.config(state=tk.DISABLED)

    def show_add_dialog(self):
        dialog = SystemDialog(self, '新增系统')
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def show_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('提示', '请选择要编辑的系统')
            return
        
        system_id = self.tree.item(selected[0])['tags'][0]
        df = DataManager.get_systems()
        system = df[df['id'] == system_id].iloc[0]
        
        dialog = SystemDialog(self, '编辑系统', system)
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def toggle_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('提示', '请选择要操作的系统')
            return
        
        system_id = self.tree.item(selected[0])['tags'][0]
        df = DataManager.get_systems()
        system = df[df['id'] == system_id].iloc[0]
        
        new_status = 0 if system['status'] == 1 else 1
        DataManager.update_system(system_id, status=new_status)
        
        status_text = '启用' if new_status == 1 else '禁用'
        messagebox.showinfo('成功', f'系统已{status_text}')
        self.load_data()


class SystemDialog(tk.Toplevel):
    def __init__(self, parent, title, system_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry('400x250')
        self.resizable(False, False)
        self.result = False
        self.system_data = system_data
        
        self.create_widgets()
        if system_data is not None:
            self.load_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text='系统名称:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text='系统编码:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.code_entry = ttk.Entry(form_frame, width=30)
        self.code_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(form_frame, text='描述:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.desc_entry = ttk.Entry(form_frame, width=30)
        self.desc_entry.grid(row=2, column=1, pady=5)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text='保存', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        self.name_entry.insert(0, self.system_data['name'])
        self.code_entry.insert(0, self.system_data['code'])
        self.desc_entry.insert(0, self.system_data['description'] or '')

    def save(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        description = self.desc_entry.get().strip()
        
        if not name or not code:
            messagebox.showwarning('提示', '系统名称和编码不能为空')
            return
        
        try:
            if self.system_data is None:
                DataManager.add_system(name, code, description)
            else:
                DataManager.update_system(
                    self.system_data['id'],
                    name=name,
                    code=code,
                    description=description
                )
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'保存失败: {e}')

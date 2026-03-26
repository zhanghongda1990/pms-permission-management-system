import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ..utils.data_manager import DataManager
from ..utils.import_export import ImportExport
from ..utils.logger import Logger


class PersonnelPage(ttk.Frame):
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
        
        title_label = ttk.Label(header_frame, text='人员管理', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)

    def create_toolbar(self):
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(toolbar_frame, text='新增', command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='编辑', command=self.show_edit_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='删除', command=self.delete_personnel).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar_frame, text='导入', command=self.import_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text='导出', command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Label(toolbar_frame, text='搜索:').pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(toolbar_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(toolbar_frame, text='刷新', command=self.refresh_data).pack(side=tk.RIGHT, padx=5)

    def create_treeview(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('姓名', '工号', '部门', '职位', '状态', '创建时间')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.column('创建时间', width=180)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Double-1>', lambda e: self.show_edit_dialog())

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        df = DataManager.get_personnel()
        
        for _, row in df.iterrows():
            status = '在职' if row['status'] == 1 else '离职'
            create_time = row['create_time'].strftime('%Y-%m-%d %H:%M') if row['create_time'] else ''
            
            self.tree.insert('', tk.END, values=(
                row['name'],
                row['employee_id'],
                row['department'],
                row['position'],
                status,
                create_time
            ), tags=(row['id'],))
        
        search_text = self.search_entry.get().strip()
        if search_text:
            self.on_search()

    def on_search(self, event=None):
        search_text = self.search_entry.get().strip().lower()
        
        if not search_text:
            for item in self.tree.get_children():
                self.tree.move(item, '', tk.END)
            return
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            match = any(search_text in str(v).lower() for v in values[:4])
            if not match:
                self.tree.detach(item)

    def refresh_data(self):
        self.search_entry.delete(0, tk.END)
        self.load_data()

    def show_add_dialog(self):
        dialog = PersonnelDialog(self, '新增人员')
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def show_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('提示', '请选择要编辑的人员')
            return
        
        personnel_id = self.tree.item(selected[0])['tags'][0]
        df = DataManager.get_personnel()
        person = df[df['id'] == personnel_id].iloc[0]
        
        dialog = PersonnelDialog(self, '编辑人员', person)
        self.wait_window(dialog)
        if dialog.result:
            self.load_data()

    def delete_personnel(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('提示', '请选择要删除的人员')
            return
        
        if messagebox.askyesno('确认', '确定要删除选中的人员吗？'):
            personnel_id = self.tree.item(selected[0])['tags'][0]
            DataManager.delete_personnel(personnel_id)
            messagebox.showinfo('成功', '删除成功')
            self.load_data()

    def import_data(self):
        file_path = filedialog.askopenfilename(
            title='选择导入文件',
            filetypes=[('Excel文件', '*.xlsx *.xls'), ('CSV文件', '*.csv')]
        )
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    ImportExport.import_personnel_from_excel(file_path)
                else:
                    ImportExport.import_personnel_from_excel(file_path)
                messagebox.showinfo('成功', '导入成功')
                self.load_data()
            except Exception as e:
                messagebox.showerror('错误', f'导入失败: {e}')

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            title='选择导出文件',
            defaultextension='.xlsx',
            filetypes=[('Excel文件', '*.xlsx')]
        )
        if file_path:
            try:
                count = ImportExport.export_personnel_to_excel(file_path)
                messagebox.showinfo('成功', f'导出成功，共{count}条记录')
            except Exception as e:
                messagebox.showerror('错误', f'导出失败: {e}')


class PersonnelDialog(tk.Toplevel):
    def __init__(self, parent, title, personnel_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry('400x300')
        self.resizable(False, False)
        self.result = False
        self.personnel_data = personnel_data
        
        self.create_widgets()
        if personnel_data is not None:
            self.load_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text='姓名:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text='工号:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.employee_id_entry = ttk.Entry(form_frame, width=30)
        self.employee_id_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(form_frame, text='部门:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.department_entry = ttk.Entry(form_frame, width=30)
        self.department_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(form_frame, text='职位:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.position_entry = ttk.Entry(form_frame, width=30)
        self.position_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(form_frame, text='状态:').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value='1')
        ttk.Radiobutton(form_frame, text='在职', variable=self.status_var, value='1').grid(row=4, column=1, sticky=tk.W)
        ttk.Radiobutton(form_frame, text='离职', variable=self.status_var, value='0').grid(row=4, column=1, sticky=tk.W, padx=60)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text='保存', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        self.name_entry.insert(0, self.personnel_data['name'])
        self.employee_id_entry.insert(0, self.personnel_data['employee_id'])
        self.department_entry.insert(0, self.personnel_data['department'])
        self.position_entry.insert(0, self.personnel_data['position'])
        self.status_var.set(str(self.personnel_data['status']))

    def save(self):
        name = self.name_entry.get().strip()
        employee_id = self.employee_id_entry.get().strip()
        department = self.department_entry.get().strip()
        position = self.position_entry.get().strip()
        status = int(self.status_var.get())
        
        if not name or not employee_id:
            messagebox.showwarning('提示', '姓名和工号不能为空')
            return
        
        try:
            if self.personnel_data is None:
                DataManager.add_personnel(name, department, position, employee_id)
            else:
                DataManager.update_personnel(
                    self.personnel_data['id'],
                    name=name,
                    department=department,
                    position=position,
                    employee_id=employee_id,
                    status=status
                )
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'保存失败: {e}')

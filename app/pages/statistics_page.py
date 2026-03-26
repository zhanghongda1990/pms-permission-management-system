import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import Counter
from ..utils.data_manager import DataManager
from ..utils.logger import Logger


class StatisticsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.load_statistics()

    def create_widgets(self):
        self.create_header()
        self.create_filter_area()
        self.create_statistics_area()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='统计查询', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text='刷新', command=self.load_statistics).pack(side=tk.RIGHT, padx=5)
        ttk.Button(header_frame, text='导出报表', command=self.export_report).pack(side=tk.RIGHT, padx=5)

    def create_filter_area(self):
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(filter_frame, text='统计维度:').pack(side=tk.LEFT, padx=5)
        self.dimension_var = tk.StringVar(value='按系统')
        dimensions = ['按系统', '按部门', '按权限级别', '按状态']
        self.dimension_combo = ttk.Combobox(filter_frame, textvariable=self.dimension_var, 
                                            values=dimensions, width=15, state='readonly')
        self.dimension_combo.pack(side=tk.LEFT, padx=5)
        self.dimension_combo.bind('<<ComboboxSelected>>', self.on_dimension_change)
        
        ttk.Separator(filter_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Label(filter_frame, text='系统筛选:').pack(side=tk.LEFT, padx=5)
        self.system_filter_var = tk.StringVar(value='全部')
        self.system_filter_combo = ttk.Combobox(filter_frame, textvariable=self.system_filter_var, 
                                                width=15, state='readonly')
        self.system_filter_combo.pack(side=tk.LEFT, padx=5)
        self.system_filter_combo.bind('<<ComboboxSelected>>', self.load_statistics)

    def create_statistics_area(self):
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        left_frame = ttk.LabelFrame(stats_frame, text='统计结果')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        columns = ('项目', '数量', '占比')
        self.stats_tree = ttk.Treeview(left_frame, columns=columns, show='headings')
        
        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        right_frame = ttk.LabelFrame(stats_frame, text='详细信息', width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        self.detail_text = tk.Text(right_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_statistics(self):
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        systems_df = DataManager.get_systems()
        system_list = ['全部'] + [row['name'] for _, row in systems_df.iterrows()]
        self.system_filter_combo['values'] = system_list
        
        dimension = self.dimension_var.get()
        system_filter = self.system_filter_var.get()
        
        personnel_df = DataManager.get_personnel()
        permissions_df = DataManager.get_permissions()
        assignments_df = DataManager.get_permission_assignments()
        
        if system_filter != '全部':
            system = systems_df[systems_df['name'] == system_filter]
            if not system.empty:
                system_id = system.iloc[0]['id']
                assignments_df = assignments_df[assignments_df['system_id'] == system_id]
        
        total = len(assignments_df[assignments_df['status'] == 1])
        
        if dimension == '按系统':
            self.show_by_system(assignments_df, systems_df, total)
        elif dimension == '按部门':
            self.show_by_department(assignments_df, personnel_df, total)
        elif dimension == '按权限级别':
            self.show_by_level(assignments_df, permissions_df, total)
        elif dimension == '按状态':
            self.show_by_status(assignments_df)

    def show_by_system(self, assignments_df, systems_df, total):
        active_assignments = assignments_df[assignments_df['status'] == 1]
        
        system_counts = Counter(active_assignments['system_id'])
        
        for system_id, count in system_counts.most_common():
            system = systems_df[systems_df['id'] == system_id]
            system_name = system.iloc[0]['name'] if not system.empty else '未知'
            percentage = f"{count/total*100:.1f}%" if total > 0 else "0%"
            
            self.stats_tree.insert('', tk.END, values=(system_name, count, percentage))
        
        self.update_detail('按系统统计', f'共{total}条有效权限分配')

    def show_by_department(self, assignments_df, personnel_df, total):
        active_assignments = assignments_df[assignments_df['status'] == 1]
        
        dept_counts = Counter()
        for _, assign in active_assignments.iterrows():
            person = personnel_df[personnel_df['id'] == assign['personnel_id']]
            if not person.empty:
                dept = person.iloc[0]['department'] or '未分配部门'
                dept_counts[dept] += 1
        
        for dept, count in dept_counts.most_common():
            percentage = f"{count/total*100:.1f}%" if total > 0 else "0%"
            self.stats_tree.insert('', tk.END, values=(dept, count, percentage))
        
        self.update_detail('按部门统计', f'共{total}条有效权限分配')

    def show_by_level(self, assignments_df, permissions_df, total):
        active_assignments = assignments_df[assignments_df['status'] == 1]
        
        level_counts = Counter()
        for _, assign in active_assignments.iterrows():
            perm = permissions_df[permissions_df['id'] == assign['permission_id']]
            if not perm.empty:
                level = f"级别{perm.iloc[0]['level']}"
                level_counts[level] += 1
        
        for level, count in sorted(level_counts.items()):
            percentage = f"{count/total*100:.1f}%" if total > 0 else "0%"
            self.stats_tree.insert('', tk.END, values=(level, count, percentage))
        
        self.update_detail('按权限级别统计', f'共{total}条有效权限分配')

    def show_by_status(self, assignments_df):
        active_count = len(assignments_df[assignments_df['status'] == 1])
        inactive_count = len(assignments_df[assignments_df['status'] == 0])
        total = active_count + inactive_count
        
        self.stats_tree.insert('', tk.END, values=('有效', active_count, f"{active_count/total*100:.1f}%" if total > 0 else "0%"))
        self.stats_tree.insert('', tk.END, values=('失效', inactive_count, f"{inactive_count/total*100:.1f}%" if total > 0 else "0%"))
        
        self.update_detail('按状态统计', f'共{total}条权限分配记录')

    def update_detail(self, title, summary):
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        self.detail_text.insert(tk.END, f"{title}\n\n")
        self.detail_text.insert(tk.END, f"{summary}\n\n")
        
        personnel_df = DataManager.get_personnel()
        systems_df = DataManager.get_systems()
        permissions_df = DataManager.get_permissions()
        assignments_df = DataManager.get_permission_assignments()
        
        self.detail_text.insert(tk.END, f"人员总数: {len(personnel_df)}\n")
        self.detail_text.insert(tk.END, f"系统总数: {len(systems_df)}\n")
        self.detail_text.insert(tk.END, f"权限总数: {len(permissions_df)}\n")
        self.detail_text.insert(tk.END, f"权限分配总数: {len(assignments_df)}\n")
        
        self.detail_text.config(state=tk.DISABLED)

    def on_dimension_change(self, event=None):
        self.load_statistics()

    def export_report(self):
        file_path = filedialog.asksaveasfilename(
            title='保存报表',
            defaultextension='.txt',
            filetypes=[('文本文件', '*.txt'), ('CSV文件', '*.csv')]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("权限管理系统统计报表\n")
                    f.write("=" * 50 + "\n\n")
                    
                    f.write(f"统计维度: {self.dimension_var.get()}\n")
                    f.write(f"系统筛选: {self.system_filter_var.get()}\n\n")
                    
                    f.write("统计结果:\n")
                    f.write("-" * 50 + "\n")
                    
                    for item in self.stats_tree.get_children():
                        values = self.stats_tree.item(item)['values']
                        f.write(f"{values[0]}: {values[1]} ({values[2]})\n")
                    
                    f.write("\n" + "=" * 50 + "\n")
                    f.write(f"导出时间: {self.get_current_time()}\n")
                
                messagebox.showinfo('成功', f'报表已保存到: {file_path}')
            except Exception as e:
                messagebox.showerror('错误', f'导出失败: {e}')

    def get_current_time(self):
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

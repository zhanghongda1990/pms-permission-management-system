import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import pandas as pd
from ..utils.data_manager import DataManager
from ..utils.logger import Logger


class HomePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.refresh_data()

    def create_widgets(self):
        self.create_header()
        self.create_stats_cards()
        self.create_recent_changes()
        self.create_expiring_permissions()
        self.create_quick_actions()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='首页', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(header_frame, text='刷新', command=self.refresh_data)
        refresh_btn.pack(side=tk.RIGHT)

    def create_stats_cards(self):
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.personnel_count_label = self.create_stat_card(cards_frame, '人员总数', '0', '#3498db')
        self.system_count_label = self.create_stat_card(cards_frame, '系统总数', '0', '#2ecc71')
        self.permission_count_label = self.create_stat_card(cards_frame, '权限总数', '0', '#e74c3c')
        self.assignment_count_label = self.create_stat_card(cards_frame, '权限分配', '0', '#f39c12')

    def create_stat_card(self, parent, title, value, color):
        card_frame = tk.Frame(parent, bg=color, padx=20, pady=15)
        card_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        
        title_label = tk.Label(card_frame, text=title, bg=color, fg='white', 
                              font=('Microsoft YaHei UI', 10))
        title_label.pack()
        
        value_label = tk.Label(card_frame, text=value, bg=color, fg='white', 
                              font=('Microsoft YaHei UI', 24, 'bold'))
        value_label.pack(pady=5)
        
        return value_label

    def create_recent_changes(self):
        frame = ttk.LabelFrame(self, text='最近权限变更')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('人员', '系统', '权限', '时间')
        self.recent_tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)
        
        self.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_expiring_permissions(self):
        frame = ttk.LabelFrame(self, text='即将过期的权限')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('人员', '系统', '权限', '过期时间')
        self.expiring_tree = ttk.Treeview(frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.expiring_tree.heading(col, text=col)
            self.expiring_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.expiring_tree.yview)
        self.expiring_tree.configure(yscrollcommand=scrollbar.set)
        
        self.expiring_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_quick_actions(self):
        frame = ttk.LabelFrame(self, text='快捷操作')
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        add_personnel_btn = ttk.Button(frame, text='添加人员', width=20, 
                                       command=self.show_personnel_page)
        add_personnel_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        assign_permission_btn = ttk.Button(frame, text='分配权限', width=20,
                                          command=self.show_permission_assign_page)
        assign_permission_btn.pack(side=tk.LEFT, padx=10, pady=10)

    def refresh_data(self):
        try:
            personnel_df = DataManager.get_personnel()
            systems_df = DataManager.get_systems()
            permissions_df = DataManager.get_permissions()
            assignments_df = DataManager.get_permission_assignments()
            
            self.personnel_count_label.config(text=str(len(personnel_df)))
            self.system_count_label.config(text=str(len(systems_df)))
            self.permission_count_label.config(text=str(len(permissions_df)))
            self.assignment_count_label.config(text=str(len(assignments_df[assignments_df['status'] == 1])))
            
            self.update_recent_changes(assignments_df, personnel_df, systems_df, permissions_df)
            self.update_expiring_permissions(assignments_df, personnel_df, systems_df, permissions_df)
            
            Logger.info("首页数据刷新完成")
        except Exception as e:
            Logger.error(f"刷新首页数据失败: {e}")

    def update_recent_changes(self, assignments_df, personnel_df, systems_df, permissions_df):
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        recent_assignments = assignments_df[assignments_df['status'] == 1].sort_values('grant_time', ascending=False).head(10)
        
        for _, assign in recent_assignments.iterrows():
            person = personnel_df[personnel_df['id'] == assign['personnel_id']]
            system = systems_df[systems_df['id'] == assign['system_id']]
            perm = permissions_df[permissions_df['id'] == assign['permission_id']]
            
            person_name = person.iloc[0]['name'] if len(person) > 0 else '未知'
            system_name = system.iloc[0]['name'] if len(system) > 0 else '未知'
            perm_name = perm.iloc[0]['name'] if len(perm) > 0 else '未知'
            grant_time = assign['grant_time'].strftime('%Y-%m-%d %H:%M') if pd.notna(assign['grant_time']) else ''
            
            self.recent_tree.insert('', tk.END, values=(person_name, system_name, perm_name, grant_time))

    def update_expiring_permissions(self, assignments_df, personnel_df, systems_df, permissions_df):
        for item in self.expiring_tree.get_children():
            self.expiring_tree.delete(item)
        
        now = datetime.now()
        week_later = now + timedelta(days=7)
        
        expiring_assignments = assignments_df[
            (assignments_df['status'] == 1) & 
            (assignments_df['expire_time'].notna()) &
            (assignments_df['expire_time'] <= week_later) &
            (assignments_df['expire_time'] > now)
        ].sort_values('expire_time')
        
        for _, assign in expiring_assignments.iterrows():
            person = personnel_df[personnel_df['id'] == assign['personnel_id']]
            system = systems_df[systems_df['id'] == assign['system_id']]
            perm = permissions_df[permissions_df['id'] == assign['permission_id']]
            
            person_name = person.iloc[0]['name'] if len(person) > 0 else '未知'
            system_name = system.iloc[0]['name'] if len(system) > 0 else '未知'
            perm_name = perm.iloc[0]['name'] if len(perm) > 0 else '未知'
            expire_time = assign['expire_time'].strftime('%Y-%m-%d') if pd.notna(assign['expire_time']) else ''
            
            self.expiring_tree.insert('', tk.END, values=(person_name, system_name, perm_name, expire_time))

    def show_personnel_page(self):
        self.master.master.navigate('show_personnel')

    def show_permission_assign_page(self):
        self.master.master.navigate('show_permission_assign')

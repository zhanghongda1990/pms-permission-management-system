import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path
import json
import pandas as pd
from ..utils.data_manager import DataManager
from ..utils.config_manager import ConfigManager
from ..utils.path_utils import PathUtils
from ..utils.logger import Logger


class ImportExportPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        self.create_header()
        self.create_main_content()

    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text='导入与导出', style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        desc_label = ttk.Label(header_frame, text='导出权限信息和机构信息为YML格式', foreground='gray')
        desc_label.pack(side=tk.LEFT, padx=20)

    def create_main_content(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        export_frame = ttk.LabelFrame(main_frame, text='导出功能', padding=20)
        export_frame.pack(fill=tk.X, pady=10)
        
        perm_export_frame = ttk.Frame(export_frame)
        perm_export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(perm_export_frame, text='导出基础权限信息:', font=('', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(perm_export_frame, text='导出所有系统的基础权限信息，以层级菜单格式保存为YML文件', 
                  foreground='gray').pack(anchor=tk.W, pady=(0, 5))
        
        perm_btn_frame = ttk.Frame(perm_export_frame)
        perm_btn_frame.pack(fill=tk.X)
        ttk.Button(perm_btn_frame, text='选择位置并导出', command=self.export_permissions).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(export_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        org_export_frame = ttk.Frame(export_frame)
        org_export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(org_export_frame, text='导出机构信息:', font=('', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(org_export_frame, text='导出指定机构的权限包、人员信息及人员权限授权情况', 
                  foreground='gray').pack(anchor=tk.W, pady=(0, 5))
        
        select_frame = ttk.Frame(org_export_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame, text='选择机构:').pack(side=tk.LEFT, padx=(0, 10))
        self.org_combo = ttk.Combobox(select_frame, width=40, state='readonly')
        self.org_combo.pack(side=tk.LEFT)
        self.load_organizations()
        
        org_btn_frame = ttk.Frame(org_export_frame)
        org_btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(org_btn_frame, text='选择位置并导出', command=self.export_organization).pack(side=tk.LEFT, padx=5)
        
        self.result_frame = ttk.LabelFrame(main_frame, text='导出结果', padding=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        result_scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_organizations(self):
        personnel_df = DataManager.get_personnel()
        organizations = set()
        for _, row in personnel_df.iterrows():
            org = row.get('department', '') or ''
            if org:
                organizations.add(org)
        
        org_list = sorted(list(organizations))
        self.org_combo['values'] = org_list
        if org_list:
            self.org_combo.current(0)

    def append_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, text + '\n')
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

    def clear_result(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)

    def export_permissions(self):
        file_path = filedialog.asksaveasfilename(
            title='选择导出位置',
            defaultextension='.yml',
            filetypes=[('YAML文件', '*.yml'), ('YAML文件', '*.yaml')],
            initialfile=f'permissions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yml'
        )
        
        if not file_path:
            return
        
        self.clear_result()
        self.append_result(f'开始导出基础权限信息...')
        self.append_result(f'目标文件: {file_path}')
        
        try:
            result = self._do_export_permissions(file_path)
            if result:
                self.append_result(f'导出成功！共导出 {result["system_count"]} 个系统，{result["permission_count"]} 个权限。')
                messagebox.showinfo('成功', f'导出成功！\n文件保存至: {file_path}')
            else:
                self.append_result('没有权限数据可导出。')
                messagebox.showwarning('提示', '没有权限数据可导出')
        except Exception as e:
            self.append_result(f'导出失败: {e}')
            messagebox.showerror('错误', f'导出失败: {e}')
            Logger.error(f'导出基础权限失败: {e}')

    def _do_export_permissions(self, file_path):
        systems_df = DataManager.get_systems()
        permissions_df = DataManager.get_permissions()
        
        if permissions_df.empty:
            return None
        
        result = {
            'system_count': 0,
            'permission_count': 0
        }
        
        yaml_content = []
        yaml_content.append('# 权限管理系统 - 基础权限信息导出')
        yaml_content.append(f'# 导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        yaml_content.append('')
        yaml_content.append('权限信息(JSON格式):')
        
        all_permissions_data = self._build_all_permissions_json(systems_df, permissions_df, result)
        json_str = json.dumps(all_permissions_data, ensure_ascii=False, indent=2)
        for line in json_str.split('\n'):
            yaml_content.append(f'  {line}')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(yaml_content))
        
        Logger.info(f'导出基础权限信息: {file_path}')
        return result

    def export_organization(self):
        org = self.org_combo.get()
        if not org:
            messagebox.showwarning('提示', '请选择要导出的机构')
            return
        
        file_path = filedialog.asksaveasfilename(
            title='选择导出位置',
            defaultextension='.yml',
            filetypes=[('YAML文件', '*.yml'), ('YAML文件', '*.yaml')],
            initialfile=f'organization_{org}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yml'
        )
        
        if not file_path:
            return
        
        self.clear_result()
        self.append_result(f'开始导出机构信息: {org}')
        self.append_result(f'目标文件: {file_path}')
        
        try:
            result = self._do_export_organization(file_path, org)
            if result:
                self.append_result(f'导出成功！')
                self.append_result(f'  - 系统数量: {result["system_count"]}')
                self.append_result(f'  - 权限数量: {result["permission_count"]}')
                self.append_result(f'  - 权限包数量: {result["package_count"]}')
                self.append_result(f'  - 人员数量: {result["personnel_count"]}')
                self.append_result(f'  - 授权记录数: {result["assignment_count"]}')
                messagebox.showinfo('成功', f'导出成功！\n文件保存至: {file_path}')
            else:
                self.append_result('该机构没有数据可导出。')
                messagebox.showwarning('提示', '该机构没有数据可导出')
        except Exception as e:
            self.append_result(f'导出失败: {e}')
            messagebox.showerror('错误', f'导出失败: {e}')
            Logger.error(f'导出机构信息失败: {e}')

    def _do_export_organization(self, file_path, org):
        packages_df = DataManager.get_permission_packages()
        personnel_df = DataManager.get_personnel()
        assignments_df = DataManager.get_permission_assignments()
        permissions_df = DataManager.get_permissions()
        systems_df = DataManager.get_systems()
        
        result = {
            'package_count': 0,
            'personnel_count': 0,
            'assignment_count': 0,
            'permission_count': 0,
            'system_count': 0
        }
        
        permissions_data = self._build_all_permissions_json(systems_df, permissions_df)
        
        org_data = {
            'export_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'organization': org,
            'permissions': permissions_data,
            'permission_packages': [],
            'personnel': []
        }
        
        result['system_count'] = len(permissions_data['systems'])
        for sys_data in permissions_data['systems']:
            result['permission_count'] += self._count_permissions(sys_data['permissions'])
        
        org_personnel = personnel_df[personnel_df['department'] == org]
        org_personnel_ids = set(str(p['id']) for _, p in org_personnel.iterrows())
        
        related_package_ids = set()
        for _, assign in assignments_df.iterrows():
            if str(assign['personnel_id']) in org_personnel_ids:
                package_id = str(assign['package_id']) if 'package_id' in assign.index and pd.notna(assign['package_id']) and str(assign['package_id']).strip() else ''
                if package_id:
                    related_package_ids.add(package_id)
        
        org_packages = packages_df[packages_df['category'] == org]
        org_package_ids = set(str(p['id']) for _, p in org_packages.iterrows())
        
        related_personnel_ids = set()
        for _, assign in assignments_df.iterrows():
            package_id = str(assign['package_id']) if 'package_id' in assign.index and pd.notna(assign['package_id']) and str(assign['package_id']).strip() else ''
            if package_id and package_id in org_package_ids:
                related_personnel_ids.add(str(assign['personnel_id']))
        
        all_personnel_ids = org_personnel_ids | related_personnel_ids
        
        for _, assign in assignments_df.iterrows():
            if str(assign['personnel_id']) in related_personnel_ids:
                package_id = str(assign['package_id']) if 'package_id' in assign.index and pd.notna(assign['package_id']) and str(assign['package_id']).strip() else ''
                if package_id:
                    related_package_ids.add(package_id)
        
        for package_id in related_package_ids:
            pkg = packages_df[packages_df['id'] == package_id]
            if pkg.empty:
                continue
            
            pkg = pkg.iloc[0]
            result['package_count'] += 1
            
            pkg_data = {
                'name': str(pkg['name']),
                'document_no': str(pkg.get('document_no', '') or ''),
                'description': str(pkg.get('description', '') or ''),
                'category': str(pkg.get('category', '') or ''),
                'permissions': []
            }
            
            permissions = json.loads(pkg['permissions']) if pkg['permissions'] else []
            for perm in permissions:
                system = systems_df[systems_df['id'] == perm['system_id']]
                perm_info = permissions_df[permissions_df['id'] == perm['permission_id']]
                
                system_name = str(system.iloc[0]['name']) if not system.empty else '未知系统'
                perm_name = str(perm_info.iloc[0]['name']) if not perm_info.empty else '未知权限'
                perm_code = str(perm_info.iloc[0].get('code', '')) if not perm_info.empty else ''
                perm_level = int(perm_info.iloc[0]['level']) if not perm_info.empty else 0
                
                pkg_data['permissions'].append({
                    'system': system_name,
                    'permission_code': perm_code,
                    'permission_name': perm_name,
                    'permission_level': perm_level
                })
            
            org_data['permission_packages'].append(pkg_data)
        
        all_personnel = personnel_df[personnel_df['id'].astype(str).isin(all_personnel_ids)]
        
        for _, person in all_personnel.iterrows():
            result['personnel_count'] += 1
            
            is_org_member = str(person['id']) in org_personnel_ids
            
            person_data = {
                'name': str(person['name']),
                'employee_id': str(person['employee_id']),
                'department': str(person['department']),
                'position': str(person['position']),
                'status': '在职' if int(person['status']) == 1 else '离职',
                'is_org_member': is_org_member,
                'authorized_permissions': []
            }
            
            person_assignments = assignments_df[
                (assignments_df['personnel_id'] == person['id']) & 
                (assignments_df['status'] == 1)
            ]
            
            package_assignments = {}
            individual_assignments = []
            
            for _, assign in person_assignments.iterrows():
                package_id = str(assign['package_id']) if 'package_id' in assign.index and pd.notna(assign['package_id']) and str(assign['package_id']).strip() else ''
                if package_id:
                    if package_id not in package_assignments:
                        package_assignments[package_id] = {
                            'package_id': package_id,
                            'grant_time': assign['grant_time'],
                            'expire_time': assign['expire_time'],
                            'remark': assign['remark'],
                            'document_no': str(assign.get('document_no', '') or ''),
                            'permission_count': 1
                        }
                    else:
                        package_assignments[package_id]['permission_count'] += 1
                else:
                    individual_assignments.append(assign)
            
            for package_id, pkg_assign in package_assignments.items():
                result['assignment_count'] += 1
                pkg = packages_df[packages_df['id'] == package_id]
                pkg_name = str(pkg.iloc[0]['name']) if not pkg.empty else '未知权限包'
                
                grant_time = pkg_assign['grant_time']
                if hasattr(grant_time, 'strftime'):
                    grant_time = grant_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    grant_time = str(grant_time)
                
                auth_data = {
                    'system': '权限包',
                    'permission_name': f"[权限包] {pkg_name}",
                    'grant_time': grant_time,
                    'document_no': pkg_assign['document_no'],
                    'remark': f"包含{pkg_assign['permission_count']}个权限"
                }
                person_data['authorized_permissions'].append(auth_data)
            
            for assign in individual_assignments:
                result['assignment_count'] += 1
                perm = permissions_df[permissions_df['id'] == assign['permission_id']]
                system = systems_df[systems_df['id'] == assign['system_id']]
                
                perm_name = str(perm.iloc[0]['name']) if not perm.empty else '未知权限'
                system_name = str(system.iloc[0]['name']) if not system.empty else '未知系统'
                
                grant_time = assign['grant_time']
                if hasattr(grant_time, 'strftime'):
                    grant_time = grant_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    grant_time = str(grant_time)
                
                auth_data = {
                    'system': system_name,
                    'permission_name': perm_name,
                    'grant_time': grant_time,
                    'document_no': str(assign.get('document_no', '') or '')
                }
                if assign.get('remark'):
                    auth_data['remark'] = str(assign['remark'])
                
                person_data['authorized_permissions'].append(auth_data)
            
            org_data['personnel'].append(person_data)
        
        yaml_content = []
        yaml_content.append('# 权限管理系统 - 机构信息导出')
        yaml_content.append(f'# 导出时间: {org_data["export_time"]}')
        yaml_content.append(f'# 机构: {org}')
        yaml_content.append('')
        yaml_content.append('机构信息(JSON格式):')
        
        json_str = json.dumps(org_data, ensure_ascii=False, indent=2)
        for line in json_str.split('\n'):
            yaml_content.append(f'  {line}')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(yaml_content))
        
        Logger.info(f'导出机构信息: {file_path}')
        return result
    
    def _count_permissions(self, permissions):
        count = 0
        for perm in permissions:
            count += 1
            if 'children' in perm:
                count += self._count_permissions(perm['children'])
        return count
    
    def _build_all_permissions_json(self, systems_df, permissions_df, result=None):
        all_data = {
            'systems': []
        }
        
        for _, system in systems_df.iterrows():
            if int(system['status']) == 0:
                continue
            
            system_perms = permissions_df[permissions_df['system_id'] == system['id']]
            if system_perms.empty:
                continue
            
            if result is not None:
                result['system_count'] += 1
            
            system_data = {
                'name': str(system['name']),
                'code': str(system['code']),
                'description': str(system.get('description', '') or ''),
                'permissions': []
            }
            
            tree = DataManager.get_permission_tree(system['id'])
            system_data['permissions'] = self._build_permission_tree_json(tree, result)
            
            all_data['systems'].append(system_data)
        
        return all_data
    
    def _build_permission_tree_json(self, nodes, result=None):
        permissions_list = []
        
        for node in nodes:
            if result is not None:
                result['permission_count'] += 1
            
            perm_data = {
                'name': str(node['name']),
                'code': str(node.get('code', '') or ''),
                'level': int(node['level']),
                'status': '启用' if int(node.get('status', 1)) == 1 else '禁用',
                'description': str(node.get('description', '') or '')
            }
            
            children = node.get('children', [])
            if children:
                perm_data['children'] = self._build_permission_tree_json(children, result)
            
            permissions_list.append(perm_data)
        
        return permissions_list

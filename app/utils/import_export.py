import pandas as pd
import csv
from pathlib import Path
from .path_utils import PathUtils
from .config_manager import ConfigManager
from .logger import Logger


class ImportExport:
    @staticmethod
    def export_permission_template():
        template_dir = ConfigManager.get_template_dir()
        PathUtils.ensure_dir(template_dir)
        
        template_file = PathUtils.get_permission_template_file(template_dir)
        
        systems = ConfigManager.get_systems()
        
        with open(template_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['系统编码', '权限编码', '权限名称', '权限级别', '权限描述', '状态'])
            for system in systems:
                writer.writerow([system['code'], '', '', '', '', '1'])
        
        Logger.info(f"导出权限模板: {template_file}")
        return template_file

    @staticmethod
    def import_permissions_from_csv(file_path):
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            required_columns = ['系统编码', '权限编码', '权限名称', '权限级别']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必要列: {col}")
            
            data = []
            for _, row in df.iterrows():
                system = ConfigManager.get_system_by_code(row['系统编码'])
                if not system:
                    Logger.warning(f"系统编码不存在: {row['系统编码']}")
                    continue
                
                data.append({
                    '权限名称': row['权限名称'],
                    '权限编码': row['权限编码'],
                    '权限级别': int(row['权限级别']),
                    '权限描述': row.get('权限描述', ''),
                    'system_id': system['id'],
                    '状态': int(row.get('状态', 1))
                })
            
            from .data_manager import DataManager
            DataManager.import_permissions(data)
            Logger.info(f"从CSV导入权限: {len(data)}条")
            return len(data)
        except Exception as e:
            Logger.error(f"导入权限失败: {e}")
            raise

    @staticmethod
    def export_permissions_to_csv(file_path):
        try:
            from .data_manager import DataManager
            df = DataManager.get_permissions()
            
            if df.empty:
                Logger.warning("没有权限数据可导出")
                return 0
            
            export_data = []
            for _, row in df.iterrows():
                system = ConfigManager.get_system_by_id(row['system_id'])
                system_code = system['code'] if system else ''
                
                export_data.append({
                    '系统编码': system_code,
                    '权限编码': row['code'],
                    '权限名称': row['name'],
                    '权限级别': row['level'],
                    '权限描述': row['description'],
                    '状态': row['status']
                })
            
            export_df = pd.DataFrame(export_data)
            export_df.to_csv(file_path, index=False, encoding='utf-8-sig')
            Logger.info(f"导出权限到CSV: {file_path}")
            return len(export_df)
        except Exception as e:
            Logger.error(f"导出权限失败: {e}")
            raise

    @staticmethod
    def export_personnel_to_excel(file_path):
        try:
            from .data_manager import DataManager
            df = DataManager.get_personnel()
            
            if df.empty:
                Logger.warning("没有人员数据可导出")
                return 0
            
            export_df = df.copy()
            export_df['状态'] = export_df['status'].apply(lambda x: '在职' if x == 1 else '离职')
            
            export_df.to_excel(file_path, index=False, engine='openpyxl')
            Logger.info(f"导出人员到Excel: {file_path}")
            return len(export_df)
        except Exception as e:
            Logger.error(f"导出人员失败: {e}")
            raise

    @staticmethod
    def import_personnel_from_excel(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            
            required_columns = ['姓名', '工号', '部门', '职位']
            column_mapping = {
                '姓名': 'name',
                '工号': 'employee_id',
                '部门': 'department',
                '职位': 'position'
            }
            
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必要列: {col}")
            
            from .data_manager import DataManager
            count = 0
            for _, row in df.iterrows():
                DataManager.add_personnel(
                    name=row['姓名'],
                    employee_id=str(row['工号']),
                    department=row.get('部门', ''),
                    position=row.get('职位', '')
                )
                count += 1
            
            Logger.info(f"从Excel导入人员: {count}条")
            return count
        except Exception as e:
            Logger.error(f"导入人员失败: {e}")
            raise

    @staticmethod
    def export_permission_application(file_path, personnel_id):
        try:
            from .data_manager import DataManager
            assignments = DataManager.get_permission_assignments(personnel_id=personnel_id)
            
            if assignments.empty:
                Logger.warning("该人员没有权限数据")
                return 0
            
            personnel = DataManager.get_personnel()
            person = personnel[personnel['id'] == personnel_id].iloc[0]
            
            permissions = DataManager.get_permissions()
            systems = DataManager.get_systems()
            packages = DataManager.get_permission_packages()
            
            package_assignments = {}
            individual_assignments = []
            
            for _, assign in assignments.iterrows():
                if assign['status'] == 0:
                    continue
                    
                package_id = str(assign['package_id']) if 'package_id' in assign.index and pd.notna(assign['package_id']) and str(assign['package_id']).strip() else ''
                if package_id:
                    if package_id not in package_assignments:
                        package_assignments[package_id] = {
                            'package_id': package_id,
                            'grant_time': assign['grant_time'],
                            'expire_time': assign['expire_time'],
                            'remark': assign['remark'],
                            'permission_count': 1
                        }
                    else:
                        package_assignments[package_id]['permission_count'] += 1
                else:
                    individual_assignments.append(assign)
            
            data = []
            
            for package_id, pkg_assign in package_assignments.items():
                pkg = packages[packages['id'] == package_id]
                if pkg.empty:
                    continue
                    
                data.append({
                    '姓名': person['name'],
                    '工号': person['employee_id'],
                    '部门': person['department'],
                    '职位': person['position'],
                    '系统': '权限包',
                    '权限名称': f"[权限包] {pkg.iloc[0]['name']}",
                    '权限级别': '-',
                    '授权时间': pkg_assign['grant_time'],
                    '过期时间': pkg_assign['expire_time'],
                    '备注': f"包含{pkg_assign['permission_count']}个权限"
                })
            
            for assign in individual_assignments:
                perm = permissions[permissions['id'] == assign['permission_id']]
                if perm.empty:
                    continue
                    
                sys = systems[systems['id'] == assign['system_id']]
                
                data.append({
                    '姓名': person['name'],
                    '工号': person['employee_id'],
                    '部门': person['department'],
                    '职位': person['position'],
                    '系统': sys.iloc[0]['name'] if not sys.empty else '',
                    '权限名称': perm.iloc[0]['name'],
                    '权限级别': perm.iloc[0]['level'],
                    '授权时间': assign['grant_time'],
                    '过期时间': assign['expire_time'],
                    '备注': assign['remark']
                })
            
            if data:
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False, engine='openpyxl')
                Logger.info(f"导出权限申请表: {file_path}")
                return len(df)
            return 0
        except Exception as e:
            Logger.error(f"导出权限申请表失败: {e}")
            raise

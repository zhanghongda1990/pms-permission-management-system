import pandas as pd
import json
import uuid
from datetime import datetime
from pathlib import Path
from .path_utils import PathUtils
from .config_manager import ConfigManager
from .logger import Logger


class DataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._init_data()
        return cls._instance

    def _init_data(self):
        data_dir = ConfigManager.get_data_dir()
        PathUtils.ensure_dir(data_dir)
        self._init_personnel()
        self._init_systems()
        self._init_permissions()
        self._init_permission_assignments()
        self._init_permission_packages()
        Logger.info("数据管理模块初始化完成")

    def _init_personnel(self):
        personnel_file = PathUtils.get_personnel_file()
        if not Path(personnel_file).exists():
            df = pd.DataFrame(columns=[
                'id', 'name', 'department', 'position', 
                'employee_id', 'status', 'create_time', 'update_time'
            ])
            df.to_parquet(personnel_file, index=False)
            Logger.info("人员信息表初始化完成")

    def _init_systems(self):
        systems_file = PathUtils.get_systems_file()
        if not Path(systems_file).exists():
            systems = ConfigManager.get_systems()
            now = datetime.now()
            data = []
            for system in systems:
                data.append({
                    'id': system['id'],
                    'name': system['name'],
                    'code': system['code'],
                    'description': '',
                    'status': 1,
                    'create_time': now,
                    'update_time': now
                })
            df = pd.DataFrame(data)
            df.to_parquet(systems_file, index=False)
            Logger.info("系统信息表初始化完成")

    def _init_permissions(self):
        permissions_file = PathUtils.get_permissions_file()
        if not Path(permissions_file).exists():
            df = pd.DataFrame(columns=[
                'id', 'name', 'code', 'level', 'description',
                'system_id', 'parent_id', 'is_leaf', 'status', 'create_time', 'update_time'
            ])
            df.to_parquet(permissions_file, index=False)
            Logger.info("权限信息表初始化完成")
        else:
            df = pd.read_parquet(permissions_file)
            updated = False
            if 'parent_id' not in df.columns:
                df['parent_id'] = ''
                updated = True
            if 'is_leaf' not in df.columns:
                df['is_leaf'] = True
                updated = True
            if updated:
                df.to_parquet(permissions_file, index=False)

    def _init_permission_assignments(self):
        assignments_file = PathUtils.get_permission_assignments_file()
        if not Path(assignments_file).exists():
            df = pd.DataFrame(columns=[
                'id', 'personnel_id', 'system_id', 'permission_id',
                'grantor_id', 'grant_time', 'expire_time', 'status', 'remark',
                'document_no', 'package_id'
            ])
            df.to_parquet(assignments_file, index=False)
            Logger.info("权限分配表初始化完成")
        else:
            df = pd.read_parquet(assignments_file)
            updated = False
            if 'document_no' not in df.columns:
                df['document_no'] = ''
                updated = True
            if 'package_id' not in df.columns:
                df['package_id'] = ''
                updated = True
            if updated:
                df.to_parquet(assignments_file, index=False)

    def _init_permission_packages(self):
        packages_file = PathUtils.get_permission_packages_file()
        if not Path(packages_file).exists():
            df = pd.DataFrame(columns=[
                'id', 'name', 'description', 'permissions',
                'document_no', 'category', 'create_time', 'update_time'
            ])
            df.to_parquet(packages_file, index=False)
            Logger.info("权限包表初始化完成")
        else:
            df = pd.read_parquet(packages_file)
            updated = False
            if 'document_no' not in df.columns:
                df['document_no'] = ''
                updated = True
            if 'category' not in df.columns:
                df['category'] = ''
                updated = True
            if updated:
                df.to_parquet(packages_file, index=False)

    @classmethod
    def get_personnel(cls):
        df = pd.read_parquet(PathUtils.get_personnel_file())
        return df

    @classmethod
    def add_personnel(cls, name, department, position, employee_id):
        df = cls.get_personnel()
        now = datetime.now()
        new_row = {
            'id': str(uuid.uuid4()),
            'name': name,
            'department': department,
            'position': position,
            'employee_id': employee_id,
            'status': 1,
            'create_time': now,
            'update_time': now
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_parquet(PathUtils.get_personnel_file(), index=False)
        Logger.info(f"添加人员: {name}")
        return new_row['id']

    @classmethod
    def update_personnel(cls, personnel_id, **kwargs):
        df = cls.get_personnel()
        idx = df[df['id'] == personnel_id].index
        if len(idx) > 0:
            for key, value in kwargs.items():
                df.at[idx[0], key] = value
            df.at[idx[0], 'update_time'] = datetime.now()
            df.to_parquet(PathUtils.get_personnel_file(), index=False)
            Logger.info(f"更新人员: {personnel_id}")

    @classmethod
    def delete_personnel(cls, personnel_id):
        df = cls.get_personnel()
        df = df[df['id'] != personnel_id]
        df.to_parquet(PathUtils.get_personnel_file(), index=False)
        Logger.info(f"删除人员: {personnel_id}")

    @classmethod
    def get_systems(cls):
        df = pd.read_parquet(PathUtils.get_systems_file())
        return df

    @classmethod
    def add_system(cls, name, code, description=''):
        df = cls.get_systems()
        now = datetime.now()
        new_row = {
            'id': str(uuid.uuid4()),
            'name': name,
            'code': code,
            'description': description,
            'status': 1,
            'create_time': now,
            'update_time': now
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_parquet(PathUtils.get_systems_file(), index=False)
        Logger.info(f"添加系统: {name}")
        return new_row['id']

    @classmethod
    def update_system(cls, system_id, **kwargs):
        df = cls.get_systems()
        idx = df[df['id'] == system_id].index
        if len(idx) > 0:
            for key, value in kwargs.items():
                df.at[idx[0], key] = value
            df.at[idx[0], 'update_time'] = datetime.now()
            df.to_parquet(PathUtils.get_systems_file(), index=False)
            Logger.info(f"更新系统: {system_id}")

    @classmethod
    def get_permissions(cls, system_id=None):
        df = pd.read_parquet(PathUtils.get_permissions_file())
        if system_id:
            df = df[df['system_id'] == system_id]
        return df

    @classmethod
    def add_permission(cls, name, code, level, description, system_id, parent_id='', is_leaf=True):
        df = cls.get_permissions()
        now = datetime.now()
        new_row = {
            'id': str(uuid.uuid4()),
            'name': name,
            'code': code,
            'level': level,
            'description': description,
            'system_id': system_id,
            'parent_id': parent_id,
            'is_leaf': is_leaf,
            'status': 1,
            'create_time': now,
            'update_time': now
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_parquet(PathUtils.get_permissions_file(), index=False)
        Logger.info(f"添加权限: {name}")
        return new_row['id']

    @classmethod
    def update_permission(cls, permission_id, **kwargs):
        df = cls.get_permissions()
        idx = df[df['id'] == permission_id].index
        if len(idx) > 0:
            for key, value in kwargs.items():
                df.at[idx[0], key] = value
            df.at[idx[0], 'update_time'] = datetime.now()
            df.to_parquet(PathUtils.get_permissions_file(), index=False)
            Logger.info(f"更新权限: {permission_id}")

    @classmethod
    def delete_permission(cls, permission_id):
        packages_df = cls.get_permission_packages()
        for idx, row in packages_df.iterrows():
            if row['permissions']:
                permissions = json.loads(row['permissions'])
                original_count = len(permissions)
                permissions = [p for p in permissions if p['permission_id'] != permission_id]
                if len(permissions) < original_count:
                    cls.update_permission_package(row['id'], permissions=permissions)
                    Logger.info(f"从权限包 {row['id']} 中移除权限 {permission_id}")
        
        assignments_df = cls.get_permission_assignments()
        assignments_to_delete = assignments_df[assignments_df['permission_id'] == permission_id]
        for _, assign in assignments_to_delete.iterrows():
            cls.revoke_permission(assign['id'])
            Logger.info(f"删除授权记录 {assign['id']} (权限 {permission_id})")
        
        children = cls.get_permission_children(permission_id)
        for _, child in children.iterrows():
            cls.delete_permission(child['id'])
        
        df = cls.get_permissions()
        df = df[df['id'] != permission_id]
        df.to_parquet(PathUtils.get_permissions_file(), index=False)
        Logger.info(f"删除权限: {permission_id}")

    @classmethod
    def import_permissions(cls, data):
        df = cls.get_permissions()
        now = datetime.now()
        new_rows = []
        for row in data:
            new_rows.append({
                'id': str(uuid.uuid4()),
                'name': row['权限名称'],
                'code': row['权限编码'],
                'level': row['权限级别'],
                'description': row['权限描述'],
                'system_id': row['system_id'],
                'parent_id': row.get('parent_id', ''),
                'is_leaf': row.get('is_leaf', True),
                'status': row.get('状态', 1),
                'create_time': now,
                'update_time': now
            })
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_parquet(PathUtils.get_permissions_file(), index=False)
        Logger.info(f"导入权限: {len(new_rows)}条")

    @classmethod
    def get_permission_children(cls, parent_id, system_id=None):
        df = cls.get_permissions(system_id=system_id)
        df = df[df['parent_id'] == parent_id]
        return df

    @classmethod
    def has_permission_children(cls, permission_id):
        df = cls.get_permissions()
        return len(df[df['parent_id'] == permission_id]) > 0

    @classmethod
    def get_permission_tree(cls, system_id):
        df = cls.get_permissions(system_id=system_id)
        return cls._build_permission_tree(df, '')

    @classmethod
    def _build_permission_tree(cls, df, parent_id):
        children = df[df['parent_id'] == parent_id]
        tree = []
        for _, row in children.iterrows():
            node = row.to_dict()
            node['children'] = cls._build_permission_tree(df, row['id'])
            tree.append(node)
        return tree

    @classmethod
    def calculate_permission_level(cls, parent_id):
        if not parent_id:
            return 1
        df = cls.get_permissions()
        parent = df[df['id'] == parent_id]
        if parent.empty:
            return 1
        return int(parent.iloc[0]['level']) + 1

    @classmethod
    def generate_permission_code(cls, system_id, parent_id):
        systems_df = cls.get_systems()
        system = systems_df[systems_df['id'] == system_id]
        if system.empty:
            return ''
        
        system_code = system.iloc[0]['code']
        level = cls.calculate_permission_level(parent_id)
        
        df = cls.get_permissions(system_id=system_id)
        siblings = df[df['parent_id'] == parent_id]
        
        max_seq = 0
        for _, sibling in siblings.iterrows():
            code = sibling.get('code', '')
            if code:
                parts = code.split('-')
                if level == 1:
                    seq_index = 1
                else:
                    seq_index = level
                if len(parts) > seq_index:
                    try:
                        seq = int(parts[seq_index])
                        if seq > max_seq:
                            max_seq = seq
                    except (ValueError, IndexError):
                        pass
        
        new_seq = max_seq + 1
        
        if parent_id:
            parent_perm = df[df['id'] == parent_id]
            if not parent_perm.empty:
                parent_code = parent_perm.iloc[0].get('code', '')
                if parent_code:
                    return f"{parent_code}-{new_seq:02d}"
        
        return f"{system_code}-{new_seq:02d}"

    @classmethod
    def get_permission_assignments(cls, personnel_id=None, system_id=None):
        df = pd.read_parquet(PathUtils.get_permission_assignments_file())
        if personnel_id:
            df = df[df['personnel_id'] == personnel_id]
        if system_id:
            df = df[df['system_id'] == system_id]
        return df

    @classmethod
    def assign_permission(cls, personnel_id, system_id, permission_id, grantor_id, expire_time=None, remark='', document_no='', package_id=''):
        df = cls.get_permission_assignments()
        now = datetime.now()
        new_row = {
            'id': str(uuid.uuid4()),
            'personnel_id': personnel_id,
            'system_id': system_id,
            'permission_id': permission_id,
            'grantor_id': grantor_id,
            'grant_time': now,
            'expire_time': expire_time,
            'status': 1,
            'remark': remark,
            'document_no': document_no,
            'package_id': package_id
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_parquet(PathUtils.get_permission_assignments_file(), index=False)
        Logger.info(f"分配权限: 人员{personnel_id} -> 系统{system_id} -> 权限{permission_id}")
        return new_row['id']

    @classmethod
    def revoke_permission(cls, assignment_id):
        df = cls.get_permission_assignments()
        df = df[df['id'] != assignment_id]
        df.to_parquet(PathUtils.get_permission_assignments_file(), index=False)
        Logger.info(f"删除权限分配: {assignment_id}")

    @classmethod
    def revoke_package(cls, personnel_id, package_id):
        df = cls.get_permission_assignments()
        mask = (df['personnel_id'] == personnel_id) & (df['package_id'] == package_id)
        df = df[~mask]
        df.to_parquet(PathUtils.get_permission_assignments_file(), index=False)
        Logger.info(f"删除权限包授权: 人员{personnel_id} -> 权限包{package_id}")

    @classmethod
    def get_permission_packages(cls):
        df = pd.read_parquet(PathUtils.get_permission_packages_file())
        return df

    @classmethod
    def add_permission_package(cls, name, description, permissions, document_no='', category=''):
        df = cls.get_permission_packages()
        now = datetime.now()
        new_row = {
            'id': str(uuid.uuid4()),
            'name': name,
            'description': description,
            'permissions': json.dumps(permissions, ensure_ascii=False),
            'document_no': document_no,
            'category': category,
            'create_time': now,
            'update_time': now
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_parquet(PathUtils.get_permission_packages_file(), index=False)
        Logger.info(f"添加权限包: {name}")
        return new_row['id']

    @classmethod
    def update_permission_package(cls, package_id, **kwargs):
        df = cls.get_permission_packages()
        idx = df[df['id'] == package_id].index
        if len(idx) > 0:
            for key, value in kwargs.items():
                if key == 'permissions':
                    df.at[idx[0], key] = json.dumps(value, ensure_ascii=False)
                else:
                    df.at[idx[0], key] = value
            df.at[idx[0], 'update_time'] = datetime.now()
            df.to_parquet(PathUtils.get_permission_packages_file(), index=False)
            Logger.info(f"更新权限包: {package_id}")

    @classmethod
    def delete_permission_package(cls, package_id):
        df = cls.get_permission_packages()
        df = df[df['id'] != package_id]
        df.to_parquet(PathUtils.get_permission_packages_file(), index=False)
        Logger.info(f"删除权限包: {package_id}")

    @classmethod
    def assign_package(cls, personnel_ids, package_id, grantor_id, document_no=''):
        package_df = cls.get_permission_packages()
        package = package_df[package_df['id'] == package_id]
        if len(package) == 0:
            return
        
        permissions = json.loads(package.iloc[0]['permissions'])
        package_name = package.iloc[0]['name']
        
        if isinstance(personnel_ids, str):
            personnel_ids = [personnel_ids]
        
        for personnel_id in personnel_ids:
            for perm in permissions:
                cls.assign_permission(
                    personnel_id, perm['system_id'], perm['permission_id'],
                    grantor_id, remark=f"通过权限包: {package_name}",
                    document_no=document_no,
                    package_id=package_id
                )
        Logger.info(f"分配权限包: {package_id} -> {len(personnel_ids)}人")

    @classmethod
    def get_personnel_current_permissions(cls, personnel_id):
        df = cls.get_permission_assignments(personnel_id=personnel_id)
        df = df[df['status'] == 1]
        return df

    @classmethod
    def get_personnel_permission_history(cls, personnel_id):
        df = cls.get_permission_assignments(personnel_id=personnel_id)
        df = df.sort_values('grant_time', ascending=False)
        return df

    @classmethod
    def get_permission_by_code(cls, code):
        df = cls.get_permissions()
        result = df[df['code'] == code]
        if not result.empty:
            return result.iloc[0]
        return None

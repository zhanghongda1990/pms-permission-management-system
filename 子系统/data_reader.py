import json
import re
from pathlib import Path
from datetime import datetime
from storage_manager import StorageManager


class DataReader:
    def __init__(self):
        self.data = None
        self.data_type = None
        self.source_file = None
        self.storage_manager = StorageManager()
    
    def load_file(self, file_path):
        self.data = None
        self.data_type = None
        self.source_file = None
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f'文件不存在: {file_path}')
        
        if not path.suffix.lower() in ['.yml', '.yaml']:
            raise ValueError('只支持YML/YAML格式的文件')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        json_match = re.search(r'(?:权限信息|机构信息)\(JSON格式\):\s*\n([\s\S]+)', content)
        
        if json_match:
            json_str = json_match.group(1)
            lines = json_str.split('\n')
            cleaned_lines = []
            for line in lines:
                if line.strip().startswith('#'):
                    continue
                if line.startswith('  '):
                    cleaned_lines.append(line[2:])
                else:
                    cleaned_lines.append(line)
            
            json_content = '\n'.join(cleaned_lines)
            self.data = json.loads(json_content)
            
            if 'organization' in self.data:
                self.data_type = 'organization'
            else:
                self.data_type = 'permissions'
            
            self.source_file = str(path)
            
            self.storage_manager.save_data(self.data, self.data_type, self.source_file)
        else:
            raise ValueError('无法解析文件内容，请确保是正确的导出文件格式')
        
        return self.data
    
    def load_cached_data(self):
        cache_data = self.storage_manager.load_cached_data()
        
        if cache_data is None:
            return False
        
        self.data = cache_data.get('data')
        self.data_type = cache_data.get('data_type')
        self.source_file = cache_data.get('source_file')
        
        return True
    
    def has_cached_data(self):
        return self.storage_manager.has_cached_data()
    
    def get_cache_info(self):
        return self.storage_manager.get_cache_info()
    
    def get_data_type(self):
        return self.data_type
    
    def get_export_time(self):
        if self.data is None:
            return None
        
        return self.data.get('export_time', '')
    
    def get_permissions_data(self):
        if self.data is None or self.data_type != 'permissions':
            return None
        
        return self.data
    
    def get_organization_data(self):
        if self.data is None or self.data_type != 'organization':
            return None
        
        return self.data
    
    def get_systems(self):
        if self.data is None:
            return []
        
        if self.data_type == 'permissions':
            return self.data.get('systems', [])
        elif self.data_type == 'organization':
            permissions = self.data.get('permissions', {})
            return permissions.get('systems', [])
        
        return []
    
    def get_system_count(self):
        return len(self.get_systems())
    
    def get_permission_count(self):
        count = 0
        systems = self.get_systems()
        for system in systems:
            count += self._count_permissions(system.get('permissions', []))
        return count
    
    def _count_permissions(self, permissions):
        count = 0
        for perm in permissions:
            count += 1
            if 'children' in perm:
                count += self._count_permissions(perm['children'])
        return count
    
    def get_permission_packages(self):
        if self.data is None or self.data_type != 'organization':
            return []
        
        return self.data.get('permission_packages', [])
    
    def get_package_count(self):
        return len(self.get_permission_packages())
    
    def get_personnel(self):
        if self.data is None or self.data_type != 'organization':
            return []
        
        return self.data.get('personnel', [])
    
    def get_personnel_count(self):
        return len(self.get_personnel())
    
    def get_assignment_count(self):
        count = 0
        for person in self.get_personnel():
            count += len(person.get('authorized_permissions', []))
        return count
    
    def get_all_assignments(self):
        assignments = []
        for person in self.get_personnel():
            for auth in person.get('authorized_permissions', []):
                assignments.append({
                    'personnel_name': person['name'],
                    'employee_id': person['employee_id'],
                    'department': person['department'],
                    **auth
                })
        return assignments
    
    def is_package_authorization(self, auth):
        system = auth.get('system', '')
        permission_name = auth.get('permission_name', '')
        return system == '权限包' or permission_name.startswith('[权限包]')
    
    def get_package_name_from_auth(self, auth):
        permission_name = auth.get('permission_name', '')
        if permission_name.startswith('[权限包] '):
            return permission_name.replace('[权限包] ', '').strip()
        return permission_name.strip()
    
    def get_person_package_authorizations(self, person):
        package_auths = []
        for auth in person.get('authorized_permissions', []):
            if self.is_package_authorization(auth):
                pkg_name = self.get_package_name_from_auth(auth)
                package_auths.append({
                    'package_name': pkg_name,
                    'grant_time': auth.get('grant_time', ''),
                    'document_no': auth.get('document_no', ''),
                    'remark': auth.get('remark', '')
                })
        return package_auths
    
    def get_person_individual_permissions(self, person):
        individual_perms = []
        for auth in person.get('authorized_permissions', []):
            if not self.is_package_authorization(auth):
                individual_perms.append({
                    'system': auth.get('system', ''),
                    'permission_name': auth.get('permission_name', ''),
                    'permission_code': auth.get('permission_code', ''),
                    'grant_time': auth.get('grant_time', ''),
                    'document_no': auth.get('document_no', ''),
                    'remark': auth.get('remark', '')
                })
        return individual_perms
    
    def get_all_permission_packages_map(self):
        packages_map = {}
        packages = self.get_permission_packages()
        for pkg in packages:
            pkg_name = pkg.get('name', '')
            packages_map[pkg_name] = pkg
        return packages_map
    
    def get_person_expanded_permissions(self, person):
        expanded_perms = []
        seen_perms = set()
        
        packages_map = self.get_all_permission_packages_map()
        
        for auth in person.get('authorized_permissions', []):
            if self.is_package_authorization(auth):
                pkg_name = self.get_package_name_from_auth(auth)
                pkg = packages_map.get(pkg_name)
                if pkg:
                    for perm in pkg.get('permissions', []):
                        perm_key = f"{perm.get('system', '')}_{perm.get('permission_code', '')}"
                        if perm_key not in seen_perms:
                            seen_perms.add(perm_key)
                            expanded_perms.append({
                                'system': perm.get('system', ''),
                                'permission_name': perm.get('permission_name', ''),
                                'permission_code': perm.get('permission_code', ''),
                                'permission_level': perm.get('permission_level', 0),
                                'grant_time': auth.get('grant_time', ''),
                                'document_no': auth.get('document_no', ''),
                                'source_package': pkg_name,
                                'source_type': 'package'
                            })
            else:
                perm_key = f"{auth.get('system', '')}_{auth.get('permission_code', '')}"
                if perm_key not in seen_perms:
                    seen_perms.add(perm_key)
                    expanded_perms.append({
                        'system': auth.get('system', ''),
                        'permission_name': auth.get('permission_name', ''),
                        'permission_code': auth.get('permission_code', ''),
                        'permission_level': auth.get('permission_level', 0),
                        'grant_time': auth.get('grant_time', ''),
                        'document_no': auth.get('document_no', ''),
                        'source_package': '',
                        'source_type': 'individual'
                    })
        
        return expanded_perms
    
    def get_all_expanded_assignments(self):
        assignments = []
        for person in self.get_personnel():
            expanded_perms = self.get_person_expanded_permissions(person)
            for perm in expanded_perms:
                assignments.append({
                    'personnel_name': person['name'],
                    'employee_id': person['employee_id'],
                    'department': person['department'],
                    **perm
                })
        return assignments
    
    def search_permissions(self, keyword):
        results = []
        keyword_lower = keyword.lower()
        
        systems = self.get_systems()
        for system in systems:
            self._search_in_permissions(
                system.get('permissions', []),
                system['name'],
                keyword_lower,
                results
            )
        
        return results
    
    def _search_in_permissions(self, permissions, system_name, keyword, results, parent_path=''):
        for perm in permissions:
            name = perm.get('name', '')
            code = perm.get('code', '')
            desc = perm.get('description', '')
            
            current_path = f'{parent_path}/{name}' if parent_path else name
            
            if keyword in name.lower() or keyword in code.lower() or keyword in desc.lower():
                results.append({
                    'system': system_name,
                    'path': current_path,
                    'name': name,
                    'code': code,
                    'status': perm.get('status', ''),
                    'description': desc
                })
            
            if 'children' in perm:
                self._search_in_permissions(
                    perm['children'],
                    system_name,
                    keyword,
                    results,
                    current_path
                )
    
    def search_personnel(self, keyword):
        results = []
        keyword_lower = keyword.lower()
        
        for person in self.get_personnel():
            name = person.get('name', '').lower()
            employee_id = person.get('employee_id', '').lower()
            department = person.get('department', '').lower()
            
            if (keyword_lower in name or 
                keyword_lower in employee_id or 
                keyword_lower in department):
                results.append(person)
        
        return results
    
    def get_personnel_by_system(self, system_name):
        results = []
        
        for person in self.get_personnel():
            has_system = False
            for auth in person.get('authorized_permissions', []):
                if auth.get('system') == system_name:
                    has_system = True
                    break
            
            if has_system:
                results.append(person)
        
        return results
    
    def get_statistics(self):
        stats = {
            'data_type': self.data_type,
            'export_time': self.get_export_time(),
            'system_count': self.get_system_count(),
            'permission_count': self.get_permission_count()
        }
        
        if self.data_type == 'organization':
            stats['organization'] = self.data.get('organization', '')
            stats['package_count'] = self.get_package_count()
            stats['personnel_count'] = self.get_personnel_count()
            stats['assignment_count'] = self.get_assignment_count()
        
        return stats

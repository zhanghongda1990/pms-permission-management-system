import os
import platform
from pathlib import Path


class PathUtils:
    APP_NAME = "权限管理系统"

    @staticmethod
    def get_system_drive():
        system_drive = os.environ.get('SystemDrive', 'C:')
        if not system_drive.endswith('\\') and not system_drive.endswith('/'):
            system_drive = system_drive + '\\'
        return system_drive

    @staticmethod
    def get_app_root_dir():
        system_drive = PathUtils.get_system_drive()
        app_root = Path(system_drive) / PathUtils.APP_NAME
        return str(app_root)

    @staticmethod
    def ensure_dir(directory):
        Path(directory).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_data_dir(root_dir=None):
        if root_dir is None:
            root_dir = PathUtils.get_app_root_dir()
        return str(Path(root_dir) / "data")

    @staticmethod
    def get_template_dir(root_dir=None):
        if root_dir is None:
            root_dir = PathUtils.get_app_root_dir()
        return str(Path(root_dir) / "templates")

    @staticmethod
    def get_export_dir(root_dir=None):
        if root_dir is None:
            root_dir = PathUtils.get_app_root_dir()
        return str(Path(root_dir) / "exports")

    @staticmethod
    def get_log_dir(root_dir=None):
        if root_dir is None:
            root_dir = PathUtils.get_app_root_dir()
        return str(Path(root_dir) / "logs")

    @staticmethod
    def get_config_path(root_dir=None):
        if root_dir is None:
            root_dir = PathUtils.get_app_root_dir()
        return str(Path(root_dir) / "config.json")

    @staticmethod
    def get_personnel_file(data_dir=None):
        if data_dir is None:
            data_dir = PathUtils.get_data_dir()
        return str(Path(data_dir) / "personnel.parquet")

    @staticmethod
    def get_systems_file(data_dir=None):
        if data_dir is None:
            data_dir = PathUtils.get_data_dir()
        return str(Path(data_dir) / "systems.parquet")

    @staticmethod
    def get_permissions_file(data_dir=None):
        if data_dir is None:
            data_dir = PathUtils.get_data_dir()
        return str(Path(data_dir) / "permissions.parquet")

    @staticmethod
    def get_permission_assignments_file(data_dir=None):
        if data_dir is None:
            data_dir = PathUtils.get_data_dir()
        return str(Path(data_dir) / "permission_assignments.parquet")

    @staticmethod
    def get_permission_packages_file(data_dir=None):
        if data_dir is None:
            data_dir = PathUtils.get_data_dir()
        return str(Path(data_dir) / "permission_packages.parquet")

    @staticmethod
    def get_log_file(log_dir=None):
        if log_dir is None:
            log_dir = PathUtils.get_log_dir()
        return str(Path(log_dir) / "app.log")

    @staticmethod
    def get_permission_template_file(template_dir=None):
        if template_dir is None:
            template_dir = PathUtils.get_template_dir()
        return str(Path(template_dir) / "permission_template.csv")

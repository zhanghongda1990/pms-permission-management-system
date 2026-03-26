import json
from pathlib import Path
from .path_utils import PathUtils
from .logger import Logger


class ConfigManager:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        root_dir = PathUtils.get_app_root_dir()
        config_path = PathUtils.get_config_path(root_dir)
        
        PathUtils.ensure_dir(root_dir)
        
        if Path(config_path).exists():
            self._load_config(config_path)
        else:
            self._create_default_config(config_path)
        
        Logger.info(f"配置文件加载完成: {config_path}")

    def _load_config(self, config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            Logger.info("配置文件加载成功")
        except Exception as e:
            Logger.error(f"加载配置文件失败: {e}")
            self._create_default_config(config_path)

    def _create_default_config(self, config_path):
        root_dir = PathUtils.get_app_root_dir()
        self._config = {
            "app_name": "权限管理系统",
            "version": "1.0.0",
            "root_dir": root_dir,
            "data_dir": PathUtils.get_data_dir(root_dir),
            "template_dir": PathUtils.get_template_dir(root_dir),
            "export_dir": PathUtils.get_export_dir(root_dir),
            "log_dir": PathUtils.get_log_dir(root_dir),
            "systems": [
                {"id": "sys001", "name": "系统一", "code": "SYS1"},
                {"id": "sys002", "name": "系统二", "code": "SYS2"},
                {"id": "sys003", "name": "系统三", "code": "SYS3"},
                {"id": "sys004", "name": "系统四", "code": "SYS4"}
            ]
        }
        self._save_config(config_path)
        Logger.info("创建默认配置文件")

    def _save_config(self, config_path):
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
            Logger.info("配置文件保存成功")
        except Exception as e:
            Logger.error(f"保存配置文件失败: {e}")

    @classmethod
    def get(cls, key, default=None):
        return cls()._config.get(key, default)

    @classmethod
    def set(cls, key, value):
        cls()._config[key] = value
        cls().save()

    @classmethod
    def save(cls):
        root_dir = cls().get('root_dir')
        config_path = PathUtils.get_config_path(root_dir)
        cls()._save_config(config_path)

    @classmethod
    def get_systems(cls):
        return cls().get('systems', [])

    @classmethod
    def get_system_by_id(cls, system_id):
        systems = cls().get_systems()
        for system in systems:
            if system['id'] == system_id:
                return system
        return None

    @classmethod
    def get_system_by_code(cls, code):
        systems = cls().get_systems()
        for system in systems:
            if system['code'] == code:
                return system
        return None

    @classmethod
    def get_data_dir(cls):
        return cls().get('data_dir')

    @classmethod
    def get_template_dir(cls):
        return cls().get('template_dir')

    @classmethod
    def get_export_dir(cls):
        return cls().get('export_dir')

    @classmethod
    def get_log_dir(cls):
        return cls().get('log_dir')

    @classmethod
    def get_root_dir(cls):
        return cls().get('root_dir')

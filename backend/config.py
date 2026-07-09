import os
import sys
import yaml


def get_base_dir():
    """获取基础目录，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的临时目录
        return sys._MEIPASS
    return os.path.abspath(os.path.dirname(__file__))


BASE_DIR = get_base_dir()


def load_yaml_config():
    """加载YAML配置文件"""
    config_path = os.path.join(BASE_DIR, 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


_yaml_config = load_yaml_config()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", _yaml_config['security']['secret_key'])
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, _yaml_config['database']['path'])}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", _yaml_config['jwt']['secret_key'])
    JWT_ACCESS_TOKEN_EXPIRES = _yaml_config['jwt']['access_token_expires']
    MAX_CONTENT_LENGTH = _yaml_config['upload']['max_content_length']
    ALLOWED_EXTENSIONS = _yaml_config['upload']['allowed_extensions']
    UPLOAD_FOLDER = os.path.join(BASE_DIR, _yaml_config['upload']['folder'])


def get_server_config():
    """获取服务器配置"""
    return _yaml_config['server']

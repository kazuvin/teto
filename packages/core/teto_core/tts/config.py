"""Google Cloud TTS 設定管理"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class GoogleTTSConfigManager:
    """Google Cloud TTS の設定とAPIキーを管理するクラス"""

    ENV_CREDENTIALS_PATH = "GOOGLE_APPLICATION_CREDENTIALS"
    ENV_PROJECT_ID = "GOOGLE_CLOUD_PROJECT"

    def __init__(self, env_file: Optional[Path] = None):
        """
        Args:
            env_file: .envファイルのパス(Noneの場合は自動検索)
        """
        self._load_env(env_file)

    def _load_env(self, env_file: Optional[Path] = None):
        """環境変数を読み込み

        Args:
            env_file: .envファイルのパス
        """
        if load_dotenv is None:
            # python-dotenvがない場合はスキップ
            return

        if env_file:
            load_dotenv(dotenv_path=env_file, override=True)
        else:
            load_dotenv(verbose=False)

    def get_credentials_path(self) -> Optional[Path]:
        """Google Cloud の認証情報ファイルパスを取得

        Returns:
            認証情報ファイルのパス
        """
        path_str = os.getenv(self.ENV_CREDENTIALS_PATH)
        if path_str:
            return Path(path_str)
        return None

    def get_project_id(self) -> Optional[str]:
        """Google Cloud プロジェクトIDを取得

        Returns:
            プロジェクトID
        """
        return os.getenv(self.ENV_PROJECT_ID)

    def validate_credentials(self) -> bool:
        """認証情報が設定されているか確認

        Returns:
            認証情報が設定されていればTrue
        """
        credentials_path = self.get_credentials_path()

        if credentials_path and credentials_path.exists():
            return True

        # Application Default Credentials が設定されている可能性
        # (実際のバリデーションはGoogle Cloud SDKに任せる)
        return False


# シングルトンインスタンス(キャッシュ)
@lru_cache(maxsize=1)
def get_config_manager(env_file: Optional[str] = None) -> GoogleTTSConfigManager:
    """設定マネージャーのシングルトンインスタンスを取得

    Args:
        env_file: .envファイルのパス

    Returns:
        GoogleTTSConfigManager インスタンス
    """
    env_path = Path(env_file) if env_file else None
    return GoogleTTSConfigManager(env_file=env_path)

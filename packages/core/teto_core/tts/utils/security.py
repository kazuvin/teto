"""セキュリティ関連ユーティリティ"""

import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def mask_credentials_path(path: Path) -> str:
    """認証情報ファイルパスをマスク表示

    Args:
        path: ファイルパス

    Returns:
        マスクされたパス文字列
    """
    if not path:
        return "***"

    # ファイル名のみ表示し、ディレクトリは隠す
    return f".../{path.name}"


def sanitize_for_logging(text: str, max_length: int = 100) -> str:
    """ログ出力用にテキストをサニタイズ

    Args:
        text: 元のテキスト
        max_length: 最大長

    Returns:
        サニタイズされたテキスト
    """
    # 改行を削除
    sanitized = text.replace("\n", " ").replace("\r", " ")

    # 最大長に切り詰め
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized


class SecureLogger:
    """認証情報を含まない安全なロガー"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_request(self, text: str, voice_name: str):
        """リクエストをログに記録

        Args:
            text: テキスト
            voice_name: 音声名
        """
        self.logger.info(
            f"TTS request - Voice: {voice_name}, Text: {sanitize_for_logging(text)}"
        )

    def log_credentials_loaded(self, credentials_path: Path):
        """認証情報読み込みをログに記録

        Args:
            credentials_path: 認証情報ファイルパス
        """
        self.logger.debug(
            f"Google Cloud credentials loaded: {mask_credentials_path(credentials_path)}"
        )

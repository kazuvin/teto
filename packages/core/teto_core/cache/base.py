"""Base cache manager - Abstract base class for asset caching"""

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Base cache directory
DEFAULT_BASE_CACHE_DIR = Path.home() / ".cache" / "teto"


@dataclass
class CacheInfo:
    """キャッシュ情報"""

    total_files: int
    total_size_bytes: int
    cache_dir: Path
    asset_type: str

    @property
    def total_size_mb(self) -> float:
        """サイズをMB単位で取得"""
        return self.total_size_bytes / (1024 * 1024)

    def __str__(self) -> str:
        return (
            f"{self.asset_type}: {self.total_files} files, "
            f"{self.total_size_mb:.2f} MB ({self.cache_dir})"
        )


class AssetCacheManager(ABC):
    """アセットキャッシュマネージャーの基底クラス

    TTS、画像、動画などのキャッシュを管理するための抽象クラス。
    サブクラスで _compute_cache_key メソッドを実装する。
    """

    # サブクラスでオーバーライド
    ASSET_TYPE: str = "asset"
    DEFAULT_CACHE_SUBDIR: str = "assets"

    def __init__(self, cache_dir: Path | str | None = None):
        """
        Args:
            cache_dir: キャッシュディレクトリ（Noneの場合はデフォルト）
        """
        if cache_dir:
            self._cache_dir = Path(cache_dir)
        else:
            self._cache_dir = DEFAULT_BASE_CACHE_DIR / self.DEFAULT_CACHE_SUBDIR
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def cache_dir(self) -> Path:
        """キャッシュディレクトリを取得"""
        return self._cache_dir

    @staticmethod
    def compute_hash(data: dict[str, Any]) -> str:
        """辞書データからハッシュ値を計算

        Args:
            data: ハッシュ化するデータ

        Returns:
            16文字のハッシュ値
        """
        cache_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(cache_data.encode()).hexdigest()[:16]

    @abstractmethod
    def _compute_cache_key(self, *args: Any, **kwargs: Any) -> str:
        """キャッシュキーを計算（サブクラスで実装）

        Returns:
            キャッシュキー（ハッシュ値）
        """
        pass

    def _get_cache_path(self, cache_key: str, ext: str) -> Path:
        """キャッシュファイルのパスを取得

        Args:
            cache_key: キャッシュキー
            ext: 拡張子

        Returns:
            キャッシュファイルのパス
        """
        # サブディレクトリを作成してファイル数を分散
        subdir = cache_key[:2]
        cache_subdir = self._cache_dir / subdir
        cache_subdir.mkdir(parents=True, exist_ok=True)
        return cache_subdir / f"{cache_key}{ext}"

    def get_by_key(self, cache_key: str, ext: str) -> bytes | None:
        """キャッシュキーでデータを取得

        Args:
            cache_key: キャッシュキー
            ext: 拡張子

        Returns:
            キャッシュされたデータ、なければ None
        """
        cache_path = self._get_cache_path(cache_key, ext)
        if cache_path.exists():
            return cache_path.read_bytes()
        return None

    def put_by_key(self, cache_key: str, ext: str, data: bytes) -> Path:
        """キャッシュキーでデータを保存

        Args:
            cache_key: キャッシュキー
            ext: 拡張子
            data: 保存するデータ

        Returns:
            キャッシュファイルのパス
        """
        cache_path = self._get_cache_path(cache_key, ext)
        cache_path.write_bytes(data)
        return cache_path

    def has_by_key(self, cache_key: str, ext: str) -> bool:
        """キャッシュキーでキャッシュが存在するか確認

        Args:
            cache_key: キャッシュキー
            ext: 拡張子

        Returns:
            キャッシュが存在すれば True
        """
        cache_path = self._get_cache_path(cache_key, ext)
        return cache_path.exists()

    def clear(self) -> int:
        """全キャッシュをクリア

        Returns:
            削除したファイル数
        """
        if not self._cache_dir.exists():
            return 0

        count = 0
        for item in self._cache_dir.iterdir():
            if item.is_dir():
                for file in item.iterdir():
                    if file.is_file():
                        file.unlink()
                        count += 1
                # 空のディレクトリを削除
                try:
                    item.rmdir()
                except OSError:
                    pass  # ディレクトリが空でない場合はスキップ
            elif item.is_file():
                item.unlink()
                count += 1

        return count

    def get_info(self) -> CacheInfo:
        """キャッシュ情報を取得

        Returns:
            キャッシュ情報
        """
        total_files = 0
        total_size = 0

        if self._cache_dir.exists():
            for item in self._cache_dir.rglob("*"):
                if item.is_file():
                    total_files += 1
                    total_size += item.stat().st_size

        return CacheInfo(
            total_files=total_files,
            total_size_bytes=total_size,
            cache_dir=self._cache_dir,
            asset_type=self.ASSET_TYPE,
        )

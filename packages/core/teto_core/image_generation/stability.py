"""Stability AI REST API クライアント"""

import base64
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

try:
    import httpx
except ImportError:
    httpx = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if TYPE_CHECKING:
    from ..script.models import StabilityImageConfig


# アスペクト比から解像度へのマッピング（SDXL 推奨サイズ）
ASPECT_RATIO_TO_SIZE: dict[str, tuple[int, int]] = {
    "1:1": (1024, 1024),
    "16:9": (1344, 768),
    "9:16": (768, 1344),
    "21:9": (1536, 640),
    "4:3": (1152, 896),
}


class StabilityAIClient:
    """Stability AI REST API クライアント

    SDXL モデルを使用した画像生成を行います。
    """

    BASE_URL = "https://api.stability.ai"
    DEFAULT_ENGINE = "stable-diffusion-xl-1024-v1-0"

    def __init__(self, api_key: str | None = None):
        """
        Args:
            api_key: Stability AI API キー
                    (Noneの場合は環境変数 STABILITY_API_KEY から取得)
        """
        if httpx is None:
            raise ImportError(
                "httpx package is not installed. "
                "Please install it with: pip install httpx"
            )

        # .envファイルを読み込み
        if load_dotenv is not None and not api_key:
            self._load_env_file()

        self.api_key = api_key or os.getenv("STABILITY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Stability AI API key is required. "
                "Set STABILITY_API_KEY environment variable or pass api_key parameter."
            )

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            },
            timeout=120.0,
        )

    def _load_env_file(self) -> None:
        """環境変数ファイルを読み込み"""
        env_candidates = [
            Path.cwd() / ".env",
            Path.cwd() / "packages" / "core" / ".env",
            Path(__file__).parent.parent.parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ]

        for env_path in env_candidates:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=False)
                break

    def generate(
        self,
        prompt: str,
        config: "StabilityImageConfig",
    ) -> bytes:
        """プロンプトから画像を生成

        Args:
            prompt: 画像生成プロンプト
            config: 画像生成設定

        Returns:
            生成された画像データ（PNG形式）

        Raises:
            httpx.HTTPStatusError: API呼び出しに失敗した場合
        """
        # アスペクト比から解像度を取得
        width, height = ASPECT_RATIO_TO_SIZE.get(config.aspect_ratio.value, (1344, 768))

        # リクエストボディを構築
        body: dict = {
            "text_prompts": [{"text": prompt, "weight": 1.0}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
        }

        # スタイルプリセット
        if config.style_preset.value != "none":
            body["style_preset"] = config.style_preset.value

        # ネガティブプロンプト
        if config.negative_prompt:
            body["text_prompts"].append(
                {"text": config.negative_prompt, "weight": -1.0}
            )

        # シード値
        if config.seed is not None:
            body["seed"] = config.seed

        # リトライロジック（レート制限対応）
        max_retries = 5
        retry_delay = 3.0

        for attempt in range(max_retries):
            try:
                response = self.client.post(
                    f"/v1/generation/{self.DEFAULT_ENGINE}/text-to-image",
                    json=body,
                )
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(
                            f"  レート制限に達しました。{wait_time:.1f}秒待機してリトライします..."
                        )
                        time.sleep(wait_time)
                    else:
                        raise
                else:
                    raise

        # レスポンスから画像データを取得
        result = response.json()
        artifacts = result.get("artifacts", [])

        if not artifacts:
            raise ValueError("No image generated from API response")

        # Base64デコードして画像データを返す
        image_base64 = artifacts[0].get("base64")
        if not image_base64:
            raise ValueError("No base64 image data in API response")

        return base64.b64decode(image_base64)

    def get_balance(self) -> float:
        """残りクレジットを取得

        Returns:
            残りクレジット数
        """
        response = self.client.get("/v1/user/balance")
        response.raise_for_status()
        return response.json().get("credits", 0.0)

    def close(self) -> None:
        """クライアントを閉じる"""
        self.client.close()

    def __enter__(self) -> "StabilityAIClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()

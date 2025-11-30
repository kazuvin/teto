"""TTS (Text-to-Speech) 関連のデータモデル"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from pathlib import Path


class GoogleTTSVoiceConfig(BaseModel):
    """Google Cloud TTS 音声設定"""

    language_code: str = Field(default="ja-JP")
    """言語コード(BCP-47形式) 例: "ja-JP", "en-US" """

    voice_name: str = Field(default="ja-JP-Wavenet-A")
    """音声名(例: "ja-JP-Wavenet-A", "ja-JP-Neural2-B")"""

    ssml_gender: Literal["NEUTRAL", "MALE", "FEMALE"] = "FEMALE"
    """SSML 性別(通常は音声名から自動決定)"""


class GoogleTTSAudioConfig(BaseModel):
    """Google Cloud TTS 音声出力設定"""

    audio_encoding: Literal["MP3", "LINEAR16", "OGG_OPUS"] = "MP3"
    """音声エンコーディング形式"""

    speaking_rate: float = Field(default=1.0, ge=0.25, le=4.0)
    """話す速度(0.25～4.0倍速)"""

    pitch: float = Field(default=0.0, ge=-20.0, le=20.0)
    """ピッチ調整(-20.0～20.0セミトーン)"""

    volume_gain_db: float = Field(default=0.0, ge=-96.0, le=16.0)
    """音量調整(dB)"""

    sample_rate_hertz: int = Field(default=24000, ge=8000)
    """サンプリングレート(Hz)"""

    effects_profile_id: list[str] = Field(default_factory=list)
    """音声効果プロファイル(例: ["headphone-class-device"])"""


class TTSRequest(BaseModel):
    """TTS リクエストデータ"""

    text: str = Field(min_length=1, max_length=5000)
    """変換するテキスト(1～5000文字)"""

    voice_config: GoogleTTSVoiceConfig = Field(default_factory=GoogleTTSVoiceConfig)
    """音声設定"""

    audio_config: GoogleTTSAudioConfig = Field(default_factory=GoogleTTSAudioConfig)
    """音声出力設定"""

    output_path: Optional[Path] = None
    """出力先パス(Noneの場合は一時ファイル)"""

    use_ssml: bool = False
    """SSMLとして解釈するか"""

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """テキストの基本的なバリデーション"""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class TTSResult(BaseModel):
    """TTS 処理結果"""

    audio_path: Path
    """生成された音声ファイルのパス"""

    duration_seconds: float
    """音声の長さ(秒)"""

    text: str
    """元のテキスト"""

    voice_config: GoogleTTSVoiceConfig
    """使用した音声設定"""

    audio_config: GoogleTTSAudioConfig
    """使用した音声出力設定"""

    character_count: int
    """文字数(課金計算用)"""

    estimated_cost_usd: float
    """推定コスト(USD)"""


class TTSSegment(BaseModel):
    """長文を分割した場合のセグメント"""

    text: str
    """セグメントテキスト"""

    start_time: float
    """このセグメントの開始時間(秒)"""

    end_time: float
    """このセグメントの終了時間(秒)"""

    audio_path: Optional[Path] = None
    """セグメント音声ファイル"""

"""Google TTS プロセッサー"""

from pathlib import Path
from typing import Optional
import tempfile
import uuid

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

from .base import ProcessorBase
from ..models.tts import TTSRequest, TTSResult
from ..tts.google_tts import GoogleTTSClient
from ..tts.utils.text_utils import normalize_text
from ..tts.utils.ssml import wrap_ssml


class GoogleTTSProcessor(ProcessorBase[TTSRequest, TTSResult]):
    """Google TTS プロセッサー(Template Method パターン)"""

    # 価格設定(USD per 1M characters)
    COST_PER_MILLION_CHARS = {
        "Standard": 4.0,
        "WaveNet": 16.0,
        "Neural2": 16.0,
    }

    def __init__(self, credentials_path: Optional[Path] = None):
        """
        Args:
            credentials_path: Google Cloud サービスアカウント認証情報のパス
        """
        self.client = GoogleTTSClient(credentials_path)

    def validate(self, data: TTSRequest, **kwargs) -> bool:
        """リクエストのバリデーション

        Args:
            data: TTSリクエスト

        Returns:
            バリデーション結果
        """
        # テキストの長さチェック
        if not data.text or len(data.text) > 5000:
            return False

        # 音声名の妥当性チェック(簡易的)
        if not data.voice_config.voice_name:
            return False

        return True

    def preprocess(self, data: TTSRequest, **kwargs) -> TTSRequest:
        """前処理: テキスト正規化など

        Args:
            data: TTSリクエスト

        Returns:
            前処理されたリクエスト
        """
        # テキストの正規化
        normalized_text = normalize_text(data.text)

        # SSMLへの変換(必要な場合)
        if data.use_ssml:
            normalized_text = wrap_ssml(
                normalized_text,
                language=data.voice_config.language_code,
                pitch=data.audio_config.pitch,
                rate=data.audio_config.speaking_rate,
            )

        # 新しいリクエストを作成(immutable)
        return data.model_copy(update={"text": normalized_text})

    def process(self, data: TTSRequest, **kwargs) -> TTSResult:
        """メイン処理: 音声生成

        Args:
            data: TTSリクエスト

        Returns:
            処理結果
        """
        # 音声データの生成
        audio_bytes = self.client.synthesize(
            text=data.text,
            voice_config=data.voice_config,
            audio_config=data.audio_config,
            use_ssml=data.use_ssml,
        )

        # 音声ファイルの保存
        output_path = data.output_path or self._generate_temp_path(
            data.audio_config.audio_encoding.lower()
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio_bytes)

        # 音声の長さを取得
        duration = self._get_audio_duration(output_path)

        # コストの推定
        cost = self._estimate_cost(data.text, data.voice_config.voice_name)

        # 結果を返す
        return TTSResult(
            audio_path=output_path,
            duration_seconds=duration,
            text=data.text,
            voice_config=data.voice_config,
            audio_config=data.audio_config,
            character_count=len(data.text),
            estimated_cost_usd=cost,
        )

    def postprocess(self, result: TTSResult, **kwargs) -> TTSResult:
        """後処理: 音量正規化など

        Args:
            result: 処理結果

        Returns:
            後処理された結果
        """
        # 音量の正規化(必要な場合)
        if result.audio_config.volume_gain_db != 0:
            self._apply_volume_gain(
                result.audio_path, result.audio_config.volume_gain_db
            )

        return result

    def _generate_temp_path(self, format: str) -> Path:
        """一時ファイルパスを生成"""
        temp_dir = Path(tempfile.gettempdir()) / "teto_tts"
        temp_dir.mkdir(exist_ok=True)

        filename = f"tts_{uuid.uuid4().hex}.{format}"
        return temp_dir / filename

    def _get_audio_duration(self, path: Path) -> float:
        """音声ファイルの長さを取得"""
        if AudioSegment is None:
            # pydubがない場合は推定値を返す
            return 0.0

        audio = AudioSegment.from_file(str(path))
        return len(audio) / 1000.0  # ms -> seconds

    def _apply_volume_gain(self, path: Path, gain_db: float):
        """音量調整を適用"""
        if AudioSegment is None:
            # pydubがない場合はスキップ
            return

        audio = AudioSegment.from_file(str(path))
        adjusted = audio + gain_db

        # 元のフォーマットで保存
        format = path.suffix[1:]  # ".mp3" -> "mp3"
        adjusted.export(str(path), format=format)

    def _estimate_cost(self, text: str, voice_name: str) -> float:
        """コストを推定

        Args:
            text: テキスト
            voice_name: 音声名

        Returns:
            推定コスト(USD)
        """
        char_count = len(text)

        # 音声タイプを判定
        if "Wavenet" in voice_name:
            voice_type = "WaveNet"
        elif "Neural2" in voice_name:
            voice_type = "Neural2"
        else:
            voice_type = "Standard"

        cost_per_million = self.COST_PER_MILLION_CHARS.get(voice_type, 4.0)
        return (char_count / 1_000_000) * cost_per_million

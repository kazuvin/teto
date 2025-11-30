# テキスト音声変換機能の追加（Google Cloud TTS）

## 概要
Google Cloud Text-to-Speech API を使用して、テキストから音声を生成する機能を `packages/core` に追加します。この機能は独立したモジュールとして実装し、既存のビデオ生成パイプラインとは疎結合に保ちます。将来的には `AudioLayer` として動画プロジェクトに統合可能な設計とします。

## 背景と目的

### ユースケース
1. **ナレーション自動生成**: スクリプトから自動的にナレーション音声を生成
2. **多言語対応**: 複数言語での音声生成による国際化対応
3. **アクセシビリティ向上**: 視覚障害者向けの音声ガイド生成
4. **効率化**: 人による録音作業の削減、反復作業の自動化

### なぜ Google Cloud TTS を選んだか

**選定理由**:
1. **無料枠が大きい**: 月100万文字まで無料（月300本以上の10分動画に相当）
2. **高品質**: WaveNet/Neural2 で自然な音声
3. **日本語対応**: 落ち着いたお姉さんボイス（ja-JP-Wavenet-A）が利用可能
4. **細かい制御**: SSML でピッチ・速度・読み方を制御可能
5. **コスパ**: 無料枠超過後も $16/100万文字と安価

**価格**:
- 無料枠: 月100万文字（Standard）
- Standard: $4/100万文字
- WaveNet/Neural2: $16/100万文字

### 要件
- テキスト入力から音声ファイル（MP3, WAV等）を生成
- Google Cloud TTS の WaveNet/Neural2 音声を使用
- 音声のパラメータ調整（速度、ピッチ、音量など）
- SSML による細かい制御
- 既存の動画生成パイプラインとの統合が容易な設計

## 前提条件
- Python 3.11+
- Pydantic 2.0+ でのモデル定義
- 既存の `ProcessorBase` パターンに準拠
- Builder パターンによる直感的なAPI提供
- Google Cloud のサービスアカウント認証

---

## アーキテクチャとデザインパターン

### 採用するデザインパターン

#### 1. Template Method パターン（処理フローの統一）
既存の `ProcessorBase` を継承し、TTS 処理の共通フローを定義します。

**理由**:
- 既存のプロセッサー（VideoProcessor, AudioProcessor等）との一貫性
- バリデーション、前処理、後処理のフックを活用
- テストやデバッグが容易

```python
class GoogleTTSProcessor(ProcessorBase[TTSRequest, TTSResult]):
    def validate(self, data: TTSRequest, **kwargs) -> bool:
        """テキストの妥当性チェック"""
        pass

    def preprocess(self, data: TTSRequest, **kwargs) -> TTSRequest:
        """テキストの正規化、SSML変換など"""
        pass

    def process(self, data: TTSRequest, **kwargs) -> TTSResult:
        """Google Cloud TTS で音声生成"""
        pass

    def postprocess(self, result: TTSResult, **kwargs) -> TTSResult:
        """音量正規化、フォーマット変換など"""
        pass
```

#### 2. Builder パターン（直感的なAPI）
既存の `ProjectBuilder` と同様に、TTS リクエストを段階的に構築できるようにします。

**理由**:
- 複雑なパラメータ設定を直感的に
- デフォルト値の一元管理
- メソッドチェーンによる可読性向上

```python
tts = TTSBuilder() \
    .text("こんにちは、世界") \
    .voice("ja-JP-Wavenet-A") \
    .pitch(-2.0) \
    .speed(0.9) \
    .output_format("mp3") \
    .output_path("output/narration.mp3") \
    .build()

result = processor.execute(tts)
```

### 設計の単純化

**Strategy/Factory パターンは不要**:
- Google Cloud TTS のみを使用するため、複数エンジンの抽象化は不要
- シンプルな実装で保守性向上
- テストとデバッグが容易

---

## ディレクトリ構造

```
packages/core/teto_core/
├── models/
│   ├── tts.py              # TTS関連のPydanticモデル
│   └── builders/
│       └── tts.py          # TTSBuilder
│
├── processors/
│   └── tts.py              # GoogleTTSProcessor（Template Method）
│
├── tts/                    # TTS専用モジュール（新規）
│   ├── __init__.py
│   ├── google_tts.py       # Google Cloud TTS クライアント
│   ├── config.py           # 環境変数管理
│   │
│   └── utils/
│       ├── __init__.py
│       ├── ssml.py         # SSML生成ユーティリティ
│       ├── audio_utils.py  # 音声処理ユーティリティ
│       ├── text_utils.py   # テキスト正規化
│       └── security.py     # セキュリティ（APIキーマスキング等）
│
└── tests/
    └── test_tts/
        ├── test_processor.py
        ├── test_google_tts.py
        ├── test_builder.py
        ├── test_ssml.py
        └── fixtures/
            └── sample_texts.txt
```

---

## データモデル定義

### models/tts.py

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from pathlib import Path


class GoogleTTSVoiceConfig(BaseModel):
    """Google Cloud TTS 音声設定"""

    language_code: str = Field(default="ja-JP")
    """言語コード（BCP-47形式）例: "ja-JP", "en-US" """

    voice_name: str = Field(default="ja-JP-Wavenet-A")
    """音声名（例: "ja-JP-Wavenet-A", "ja-JP-Neural2-B"）"""

    ssml_gender: Literal["NEUTRAL", "MALE", "FEMALE"] = "FEMALE"
    """SSML 性別（通常は音声名から自動決定）"""


class GoogleTTSAudioConfig(BaseModel):
    """Google Cloud TTS 音声出力設定"""

    audio_encoding: Literal["MP3", "LINEAR16", "OGG_OPUS"] = "MP3"
    """音声エンコーディング形式"""

    speaking_rate: float = Field(default=1.0, ge=0.25, le=4.0)
    """話す速度（0.25～4.0倍速）"""

    pitch: float = Field(default=0.0, ge=-20.0, le=20.0)
    """ピッチ調整（-20.0～20.0セミトーン）"""

    volume_gain_db: float = Field(default=0.0, ge=-96.0, le=16.0)
    """音量調整（dB）"""

    sample_rate_hertz: int = Field(default=24000, ge=8000)
    """サンプリングレート（Hz）"""

    effects_profile_id: list[str] = Field(default_factory=list)
    """音声効果プロファイル（例: ["headphone-class-device"]）"""


class TTSRequest(BaseModel):
    """TTS リクエストデータ"""

    text: str = Field(min_length=1, max_length=5000)
    """変換するテキスト（1～5000文字）"""

    voice_config: GoogleTTSVoiceConfig = Field(default_factory=GoogleTTSVoiceConfig)
    """音声設定"""

    audio_config: GoogleTTSAudioConfig = Field(default_factory=GoogleTTSAudioConfig)
    """音声出力設定"""

    output_path: Optional[Path] = None
    """出力先パス（Noneの場合は一時ファイル）"""

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
    """音声の長さ（秒）"""

    text: str
    """元のテキスト"""

    voice_config: GoogleTTSVoiceConfig
    """使用した音声設定"""

    audio_config: GoogleTTSAudioConfig
    """使用した音声出力設定"""

    character_count: int
    """文字数（課金計算用）"""

    estimated_cost_usd: float
    """推定コスト（USD）"""


class TTSSegment(BaseModel):
    """長文を分割した場合のセグメント"""

    text: str
    """セグメントテキスト"""

    start_time: float
    """このセグメントの開始時間（秒）"""

    end_time: float
    """このセグメントの終了時間（秒）"""

    audio_path: Optional[Path] = None
    """セグメント音声ファイル"""
```

---

## 実装詳細

### Phase 1: Google Cloud TTS クライアントの実装

**ファイル**: `teto_core/tts/google_tts.py`

```python
from google.cloud import texttospeech
from typing import Optional
from pathlib import Path
import os

from ..models.tts import TTSRequest, GoogleTTSVoiceConfig, GoogleTTSAudioConfig


class GoogleTTSClient:
    """Google Cloud Text-to-Speech API クライアント"""

    def __init__(self, credentials_path: Optional[Path] = None):
        """
        Args:
            credentials_path: サービスアカウント認証情報のパス
                             （Noneの場合は環境変数から取得）
        """
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

        self.client = texttospeech.TextToSpeechClient()

    def synthesize(
        self,
        text: str,
        voice_config: GoogleTTSVoiceConfig,
        audio_config: GoogleTTSAudioConfig,
        use_ssml: bool = False
    ) -> bytes:
        """テキストから音声データを生成

        Args:
            text: 変換するテキスト
            voice_config: 音声設定
            audio_config: 音声出力設定
            use_ssml: SSMLとして解釈するか

        Returns:
            音声データ（バイト列）

        Raises:
            GoogleCloudError: API呼び出しに失敗した場合
        """
        # 入力テキストの設定
        if use_ssml:
            synthesis_input = texttospeech.SynthesisInput(ssml=text)
        else:
            synthesis_input = texttospeech.SynthesisInput(text=text)

        # 音声設定
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config.language_code,
            name=voice_config.voice_name,
            ssml_gender=self._convert_gender(voice_config.ssml_gender),
        )

        # 音声出力設定
        audio_config_proto = texttospeech.AudioConfig(
            audio_encoding=self._convert_encoding(audio_config.audio_encoding),
            speaking_rate=audio_config.speaking_rate,
            pitch=audio_config.pitch,
            volume_gain_db=audio_config.volume_gain_db,
            sample_rate_hertz=audio_config.sample_rate_hertz,
            effects_profile_id=audio_config.effects_profile_id,
        )

        # API呼び出し
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config_proto,
        )

        return response.audio_content

    def list_voices(self, language_code: Optional[str] = None) -> list[dict]:
        """利用可能な音声のリストを取得

        Args:
            language_code: 言語コード（Noneの場合は全言語）

        Returns:
            音声情報のリスト
        """
        response = self.client.list_voices(language_code=language_code)

        voices = []
        for voice in response.voices:
            voices.append({
                "name": voice.name,
                "language_codes": voice.language_codes,
                "ssml_gender": voice.ssml_gender.name,
                "natural_sample_rate_hertz": voice.natural_sample_rate_hertz,
            })

        return voices

    def estimate_duration(
        self,
        text: str,
        audio_config: GoogleTTSAudioConfig
    ) -> float:
        """生成される音声の推定長さ

        Args:
            text: テキスト
            audio_config: 音声出力設定

        Returns:
            推定長さ（秒）
        """
        # 日本語の場合は約5文字/秒、英語の場合は約15文字/秒として推定
        is_japanese = any(ord(c) > 0x3000 for c in text)
        chars_per_second = 5.0 if is_japanese else 15.0

        base_duration = len(text) / chars_per_second
        return base_duration / audio_config.speaking_rate

    def _convert_gender(self, gender: str) -> texttospeech.SsmlVoiceGender:
        """SSML性別を変換"""
        gender_map = {
            "NEUTRAL": texttospeech.SsmlVoiceGender.NEUTRAL,
            "MALE": texttospeech.SsmlVoiceGender.MALE,
            "FEMALE": texttospeech.SsmlVoiceGender.FEMALE,
        }
        return gender_map.get(gender, texttospeech.SsmlVoiceGender.NEUTRAL)

    def _convert_encoding(self, encoding: str) -> texttospeech.AudioEncoding:
        """音声エンコーディングを変換"""
        encoding_map = {
            "MP3": texttospeech.AudioEncoding.MP3,
            "LINEAR16": texttospeech.AudioEncoding.LINEAR16,
            "OGG_OPUS": texttospeech.AudioEncoding.OGG_OPUS,
        }
        return encoding_map.get(encoding, texttospeech.AudioEncoding.MP3)
```

---

### Phase 2: プロセッサーの実装（Template Method パターン）

**ファイル**: `teto_core/processors/tts.py`

```python
from pathlib import Path
from typing import Optional
import tempfile
from pydub import AudioSegment

from .base import ProcessorBase
from ..models.tts import TTSRequest, TTSResult
from ..tts.google_tts import GoogleTTSClient
from ..tts.utils.text_utils import normalize_text
from ..tts.utils.ssml import wrap_ssml


class GoogleTTSProcessor(ProcessorBase[TTSRequest, TTSResult]):
    """Google TTS プロセッサー（Template Method パターン）"""

    # 価格設定（USD per 1M characters）
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

        # 音声名の妥当性チェック（簡易的）
        if not data.voice_config.voice_name:
            return False

        return True

    def preprocess(self, data: TTSRequest, **kwargs) -> TTSRequest:
        """前処理：テキスト正規化など

        Args:
            data: TTSリクエスト

        Returns:
            前処理されたリクエスト
        """
        # テキストの正規化
        normalized_text = normalize_text(data.text)

        # SSMLへの変換（必要な場合）
        if data.use_ssml:
            normalized_text = wrap_ssml(
                normalized_text,
                language=data.voice_config.language_code,
                pitch=data.audio_config.pitch,
                rate=data.audio_config.speaking_rate,
            )

        # 新しいリクエストを作成（immutable）
        return data.model_copy(update={"text": normalized_text})

    def process(self, data: TTSRequest, **kwargs) -> TTSResult:
        """メイン処理：音声生成

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
        """後処理：音量正規化など

        Args:
            result: 処理結果

        Returns:
            後処理された結果
        """
        # 音量の正規化（必要な場合）
        if result.audio_config.volume_gain_db != 0:
            self._apply_volume_gain(
                result.audio_path,
                result.audio_config.volume_gain_db
            )

        return result

    def _generate_temp_path(self, format: str) -> Path:
        """一時ファイルパスを生成"""
        temp_dir = Path(tempfile.gettempdir()) / "teto_tts"
        temp_dir.mkdir(exist_ok=True)

        import uuid
        filename = f"tts_{uuid.uuid4().hex}.{format}"
        return temp_dir / filename

    def _get_audio_duration(self, path: Path) -> float:
        """音声ファイルの長さを取得"""
        audio = AudioSegment.from_file(str(path))
        return len(audio) / 1000.0  # ms -> seconds

    def _apply_volume_gain(self, path: Path, gain_db: float):
        """音量調整を適用"""
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
            推定コスト（USD）
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
```

---

### Phase 3: Builder の実装

**ファイル**: `teto_core/models/builders/tts.py`

```python
from pathlib import Path
from typing import Optional, Literal
from ..tts import TTSRequest, GoogleTTSVoiceConfig, GoogleTTSAudioConfig


class TTSBuilder:
    """TTS リクエストのビルダー（Builder パターン）"""

    def __init__(self):
        self._text: Optional[str] = None
        self._voice_config = GoogleTTSVoiceConfig()
        self._audio_config = GoogleTTSAudioConfig()
        self._output_path: Optional[Path] = None
        self._use_ssml = False

    def text(self, text: str) -> 'TTSBuilder':
        """変換するテキストを設定

        Args:
            text: テキスト（1～5000文字）
        """
        self._text = text
        return self

    def voice(self, voice_name: str) -> 'TTSBuilder':
        """音声を設定

        Args:
            voice_name: 音声名（例: "ja-JP-Wavenet-A"）
        """
        self._voice_config.voice_name = voice_name

        # 音声名から言語コードを推測
        if "-" in voice_name:
            lang_code = "-".join(voice_name.split("-")[:2])
            self._voice_config.language_code = lang_code

        return self

    def language(self, language_code: str) -> 'TTSBuilder':
        """言語を設定

        Args:
            language_code: 言語コード（例: "ja-JP", "en-US"）
        """
        self._voice_config.language_code = language_code
        return self

    def speed(self, rate: float) -> 'TTSBuilder':
        """話す速度を設定

        Args:
            rate: 速度（0.25～4.0倍速）
        """
        self._audio_config.speaking_rate = rate
        return self

    def pitch(self, pitch: float) -> 'TTSBuilder':
        """ピッチを設定

        Args:
            pitch: ピッチ調整（-20.0～20.0セミトーン）
        """
        self._audio_config.pitch = pitch
        return self

    def volume(self, gain_db: float) -> 'TTSBuilder':
        """音量を設定

        Args:
            gain_db: 音量調整（dB）
        """
        self._audio_config.volume_gain_db = gain_db
        return self

    def sample_rate(self, rate: int) -> 'TTSBuilder':
        """サンプリングレートを設定

        Args:
            rate: サンプリングレート（Hz）
        """
        self._audio_config.sample_rate_hertz = rate
        return self

    def output_format(self, format: Literal["mp3", "wav", "ogg"]) -> 'TTSBuilder':
        """出力フォーマットを設定

        Args:
            format: 音声フォーマット
        """
        format_map = {
            "mp3": "MP3",
            "wav": "LINEAR16",
            "ogg": "OGG_OPUS",
        }
        self._audio_config.audio_encoding = format_map.get(format, "MP3")
        return self

    def output_path(self, path: str | Path) -> 'TTSBuilder':
        """出力先パスを設定

        Args:
            path: 出力先ファイルパス
        """
        self._output_path = Path(path) if isinstance(path, str) else path
        return self

    def effects_profile(self, profiles: list[str]) -> 'TTSBuilder':
        """音声効果プロファイルを設定

        Args:
            profiles: プロファイルリスト（例: ["headphone-class-device"]）
        """
        self._audio_config.effects_profile_id = profiles
        return self

    def ssml(self, use_ssml: bool = True) -> 'TTSBuilder':
        """SSMLモードを設定

        Args:
            use_ssml: SSMLとして解釈するか
        """
        self._use_ssml = use_ssml
        return self

    def build(self) -> TTSRequest:
        """TTSRequestを構築

        Returns:
            構築されたTTSRequest

        Raises:
            ValueError: テキストが設定されていない場合
        """
        if not self._text:
            raise ValueError("Text is required")

        return TTSRequest(
            text=self._text,
            voice_config=self._voice_config,
            audio_config=self._audio_config,
            output_path=self._output_path,
            use_ssml=self._use_ssml,
        )
```

---

### Phase 4: 環境変数とAPIキーの管理

**ファイル**: `teto_core/tts/config.py`

```python
import os
from pathlib import Path
from typing import Optional
from functools import lru_cache
from dotenv import load_dotenv


class GoogleTTSConfigManager:
    """Google Cloud TTS の設定とAPIキーを管理するクラス"""

    ENV_CREDENTIALS_PATH = "GOOGLE_APPLICATION_CREDENTIALS"
    ENV_PROJECT_ID = "GOOGLE_CLOUD_PROJECT"

    def __init__(self, env_file: Optional[Path] = None):
        """
        Args:
            env_file: .envファイルのパス（Noneの場合は自動検索）
        """
        self._load_env(env_file)

    def _load_env(self, env_file: Optional[Path] = None):
        """環境変数を読み込み

        Args:
            env_file: .envファイルのパス
        """
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
        # （実際のバリデーションはGoogle Cloud SDKに任せる）
        return False


# シングルトンインスタンス（キャッシュ）
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
```

**.env ファイルのテンプレート** (`packages/core/.env.example`):

```bash
# Google Cloud Text-to-Speech 設定

# サービスアカウントの認証情報ファイルパス（必須）
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Google Cloud プロジェクトID（オプション）
GOOGLE_CLOUD_PROJECT=your-project-id
```

**.gitignore に追加**:

```gitignore
# 環境変数ファイル
.env
.env.local
.env.*.local

# Google Cloud 認証情報
*-key.json
service-account*.json
credentials.json
```

---

### Phase 5: ユーティリティの実装

#### 5.1 SSML ヘルパー

**ファイル**: `teto_core/tts/utils/ssml.py`

```python
from typing import Optional


def wrap_ssml(
    text: str,
    language: str = "ja-JP",
    pitch: Optional[float] = None,
    rate: Optional[float] = None,
) -> str:
    """テキストをSSMLでラップ

    Args:
        text: テキスト
        language: 言語コード
        pitch: ピッチ調整（セミトーン）
        rate: 話す速度

    Returns:
        SSML形式のテキスト
    """
    # prosodyタグの属性を構築
    prosody_attrs = []
    if pitch is not None:
        prosody_attrs.append(f'pitch="{pitch:+.1f}st"')
    if rate is not None:
        prosody_attrs.append(f'rate="{rate:.2f}"')

    if prosody_attrs:
        prosody_start = f'<prosody {" ".join(prosody_attrs)}>'
        prosody_end = '</prosody>'
        text = f'{prosody_start}{text}{prosody_end}'

    return f'<speak version="1.0" xml:lang="{language}">{text}</speak>'


def add_break(milliseconds: int = 500) -> str:
    """ポーズ（間）を追加するSSMLタグ

    Args:
        milliseconds: ポーズの長さ（ミリ秒）

    Returns:
        SSMLのbreakタグ
    """
    return f'<break time="{milliseconds}ms"/>'


def emphasize(text: str, level: str = "moderate") -> str:
    """テキストを強調するSSMLタグ

    Args:
        text: 強調するテキスト
        level: 強調レベル（"strong", "moderate", "reduced"）

    Returns:
        強調されたSSML
    """
    return f'<emphasis level="{level}">{text}</emphasis>'


def say_as(text: str, interpret_as: str) -> str:
    """テキストの解釈方法を指定

    Args:
        text: テキスト
        interpret_as: 解釈タイプ（"cardinal", "ordinal", "date" など）

    Returns:
        say-asタグ付きSSML
    """
    return f'<say-as interpret-as="{interpret_as}">{text}</say-as>'


def phoneme(text: str, ph: str, alphabet: str = "ipa") -> str:
    """発音記号で読み方を指定

    Args:
        text: テキスト
        ph: 発音記号
        alphabet: 発音記号体系（"ipa" or "x-sampa"）

    Returns:
        phonemeタグ付きSSML
    """
    return f'<phoneme alphabet="{alphabet}" ph="{ph}">{text}</phoneme>'
```

#### 5.2 テキスト正規化

**ファイル**: `teto_core/tts/utils/text_utils.py`

```python
import re


def normalize_text(text: str) -> str:
    """テキストを正規化

    Args:
        text: 元のテキスト

    Returns:
        正規化されたテキスト
    """
    # 全角スペース→半角
    text = text.replace("\u3000", " ")

    # 連続する空白を1つに
    text = re.sub(r"\s+", " ", text)

    # 前後の空白を削除
    text = text.strip()

    return text


def split_long_text(text: str, max_length: int = 5000) -> list[str]:
    """長いテキストを分割

    Args:
        text: 長いテキスト
        max_length: 最大文字数

    Returns:
        分割されたテキストのリスト
    """
    if len(text) <= max_length:
        return [text]

    segments = []
    current = ""

    # 文単位で分割（句点で区切る）
    sentences = re.split(r'([。．！？\n])', text)

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""

        if len(current) + len(sentence) + len(delimiter) > max_length:
            if current:
                segments.append(current.strip())
            current = sentence + delimiter
        else:
            current += sentence + delimiter

    if current:
        segments.append(current.strip())

    return segments
```

#### 5.3 セキュリティユーティリティ

**ファイル**: `teto_core/tts/utils/security.py`

```python
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
            f"TTS request - Voice: {voice_name}, "
            f"Text: {sanitize_for_logging(text)}"
        )

    def log_credentials_loaded(self, credentials_path: Path):
        """認証情報読み込みをログに記録

        Args:
            credentials_path: 認証情報ファイルパス
        """
        self.logger.debug(
            f"Google Cloud credentials loaded: {mask_credentials_path(credentials_path)}"
        )
```

---

## タスク詳細

### Phase 1: 基盤の構築（Week 1）
- [ ] `teto_core/tts/` ディレクトリ作成
- [ ] `teto_core/tts/google_tts.py` - GoogleTTSClient 実装
- [ ] Google Cloud Text-to-Speech SDK のインストールとテスト
- [ ] 基本的なユニットテスト作成

### Phase 2: データモデル（Week 1-2）
- [ ] `teto_core/models/tts.py` - Pydantic モデル定義
  - [ ] GoogleTTSVoiceConfig
  - [ ] GoogleTTSAudioConfig
  - [ ] TTSRequest
  - [ ] TTSResult
  - [ ] TTSSegment
- [ ] モデルのバリデーションテスト

### Phase 3: プロセッサーの実装（Week 2）
- [ ] `teto_core/processors/tts.py` - GoogleTTSProcessor 実装
- [ ] Template Method パターンの実装
  - [ ] validate()
  - [ ] preprocess()
  - [ ] process()
  - [ ] postprocess()
- [ ] コスト推定機能
- [ ] プロセッサーのテスト作成

### Phase 4: Builder パターン（Week 2-3）
- [ ] `teto_core/models/builders/tts.py` - TTSBuilder 実装
- [ ] メソッドチェーンの実装
- [ ] デフォルト値の設定
- [ ] Builder のテスト作成

### Phase 5: 環境変数管理（Week 3）
- [ ] `python-dotenv` パッケージの追加
- [ ] `teto_core/tts/config.py` - GoogleTTSConfigManager 実装
- [ ] `.env.example` ファイルの作成
- [ ] `.gitignore` への追加（.env, *-key.json等）
- [ ] 認証情報のバリデーション
- [ ] 環境変数管理のテスト作成

### Phase 6: ユーティリティの実装（Week 3）
- [ ] `teto_core/tts/utils/ssml.py` - SSML生成ユーティリティ
  - [ ] wrap_ssml()
  - [ ] add_break()
  - [ ] emphasize()
  - [ ] say_as()
  - [ ] phoneme()
- [ ] `teto_core/tts/utils/text_utils.py` - テキスト正規化
  - [ ] normalize_text()
  - [ ] split_long_text()
- [ ] `teto_core/tts/utils/security.py` - セキュリティユーティリティ
  - [ ] mask_credentials_path()
  - [ ] sanitize_for_logging()
  - [ ] SecureLogger
- [ ] ユーティリティのテスト

### Phase 7: 統合と最適化（Week 4）
- [ ] 長文の自動分割機能
- [ ] バッチ処理機能
- [ ] キャッシュ機構（同じテキストの再利用）
- [ ] 音声品質の最適化
- [ ] パフォーマンステスト
- [ ] エラーハンドリングの改善

### Phase 8: ドキュメントとサンプル（Week 5）
- [ ] README の作成
- [ ] APIドキュメントの作成
- [ ] サンプルスクリプトの作成
  - [ ] 基本的な使い方
  - [ ] SSML の使用例
  - [ ] バッチ処理の例
- [ ] ユースケース別のチュートリアル
- [ ] Google Cloud セットアップガイド
  - [ ] サービスアカウントの作成方法
  - [ ] 認証情報ファイルの取得方法
  - [ ] 環境変数の設定方法

### Phase 9: 動画パイプラインとの統合（Week 6）
- [ ] AudioLayer との統合
- [ ] ProjectBuilder への TTS サポート追加
- [ ] 字幕とナレーションの同期機能
- [ ] エンドツーエンドのサンプル作成

---

## 使用例

### 基本的な使い方

```python
from teto_core.models.builders.tts import TTSBuilder
from teto_core.processors.tts import GoogleTTSProcessor

# ビルダーでリクエストを構築
request = TTSBuilder() \
    .text("こんにちは、世界。これはテストです。") \
    .voice("ja-JP-Wavenet-A") \
    .pitch(-2.0) \
    .speed(0.9) \
    .output_format("mp3") \
    .output_path("output/narration.mp3") \
    .build()

# プロセッサーで実行
processor = GoogleTTSProcessor()
result = processor.execute(request)

print(f"音声を生成しました: {result.audio_path}")
print(f"長さ: {result.duration_seconds}秒")
print(f"推定コスト: ${result.estimated_cost_usd:.6f}")
```

### 落ち着いたお姉さんボイスの設定

```python
request = TTSBuilder() \
    .text("本日は、テキスト音声変換についてご説明いたします。") \
    .voice("ja-JP-Wavenet-A") \
    .pitch(-2.0) \
    .speed(0.9) \
    .effects_profile(["headphone-class-device"]) \
    .build()

processor = GoogleTTSProcessor()
result = processor.execute(request)
```

### SSML を使った細かい制御

```python
from teto_core.tts.utils.ssml import wrap_ssml, add_break, emphasize

# SSMLテキストの構築
text = f"""
こんにちは。
{add_break(500)}
本日は{emphasize("重要な", "strong")}お知らせがあります。
"""

request = TTSBuilder() \
    .text(text) \
    .voice("ja-JP-Wavenet-A") \
    .ssml(True) \
    .build()

processor = GoogleTTSProcessor()
result = processor.execute(request)
```

### 動画プロジェクトへの統合

```python
from teto_core.models.builders import ProjectBuilder
from teto_core.models.builders.tts import TTSBuilder
from teto_core.processors.tts import GoogleTTSProcessor
from teto_core.video_generator import VideoGenerator

# ナレーション音声を生成
tts_request = TTSBuilder() \
    .text("この動画は自動生成されたナレーション付きです。") \
    .voice("ja-JP-Wavenet-A") \
    .pitch(-2.0) \
    .speed(0.9) \
    .output_path("output/narration.mp3") \
    .build()

tts_processor = GoogleTTSProcessor()
tts_result = tts_processor.execute(tts_request)

# 動画プロジェクトに統合
project = ProjectBuilder("output.mp4") \
    .output(width=1920, height=1080, fps=30) \
    .add_video("main.mp4").build() \
    .add_audio(str(tts_result.audio_path)).with_volume(0.8).build() \
    .add_subtitle_layer() \
        .add_item(tts_result.text, 0, tts_result.duration_seconds) \
        .font(size="lg", color="white") \
        .style(position="bottom") \
        .build() \
    .build()

# 動画を生成
generator = VideoGenerator()
generator.generate(project)
```

### バッチ処理

```python
from teto_core.models.builders.tts import TTSBuilder
from teto_core.processors.tts import GoogleTTSProcessor

# スクリプトリスト
scripts = [
    {"text": "第1章：はじめに", "output": "chapter1.mp3"},
    {"text": "第2章：基礎知識", "output": "chapter2.mp3"},
    {"text": "第3章：応用編", "output": "chapter3.mp3"},
]

processor = GoogleTTSProcessor()
total_cost = 0.0

for script in scripts:
    request = TTSBuilder() \
        .text(script["text"]) \
        .voice("ja-JP-Wavenet-A") \
        .output_path(f"output/{script['output']}") \
        .build()

    result = processor.execute(request)
    total_cost += result.estimated_cost_usd
    print(f"生成完了: {result.audio_path}")

print(f"合計コスト: ${total_cost:.6f}")
```

---

## 依存パッケージ

pyproject.toml に以下を追加:

```toml
[project]
dependencies = [
    # ... 既存の依存関係 ...
    "pydub>=0.25.0",                      # 音声処理
    "python-dotenv>=1.0.0",               # 環境変数管理
    "google-cloud-texttospeech>=2.14.0",  # Google Cloud TTS
]

[dependency-groups]
dev = [
    # ... 既存の開発用依存関係 ...
]
```

---

## Google Cloud のセットアップ

### 1. Google Cloud プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. プロジェクトIDをメモ

### 2. Text-to-Speech API の有効化

1. Google Cloud Console のナビゲーションメニューから「APIとサービス」→「ライブラリ」
2. "Cloud Text-to-Speech API" を検索
3. 「有効にする」をクリック

### 3. サービスアカウントの作成

1. 「IAMと管理」→「サービスアカウント」
2. 「サービスアカウントを作成」
3. 名前を入力（例: "teto-tts"）
4. ロールを選択: "Cloud Text-to-Speech 管理者" または "Cloud Text-to-Speech ユーザー"
5. 「完了」

### 4. 認証情報ファイルのダウンロード

1. 作成したサービスアカウントをクリック
2. 「キー」タブ → 「鍵を追加」→「新しい鍵を作成」
3. JSON形式を選択
4. ダウンロードされたJSONファイルを安全な場所に保存（例: `~/.config/gcloud/teto-tts-key.json`）

### 5. 環境変数の設定

`.env` ファイルを作成:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/teto-tts-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

または、環境変数として設定:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/teto-tts-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

---

## 設計上の考慮事項

### 1. 疎結合の維持
- TTS機能は独立したモジュールとして実装
- 既存のビデオ生成パイプラインへの影響を最小限に
- `teto_core/tts/` 配下で完結させる

### 2. シンプルな設計
- Google Cloud TTS のみに特化してStrategy/Factoryパターンを削除
- 必要最小限の抽象化で保守性向上
- テストとデバッグが容易

### 3. テスタビリティ
- ProcessorBase を継承することで既存のテストパターンを活用
- 依存性注入によりモックが可能
- ユーティリティ関数は純粋関数として実装

### 4. エラーハンドリング
- Google Cloud API エラー（認証失敗、クォータ超過など）の適切な処理
- ネットワークエラーのリトライ機構
- バリデーションエラーの明確なメッセージ

### 5. パフォーマンス
- 長文の自動分割とバッチ処理
- 同じテキストのキャッシュ機能（将来的に）
- 音声ファイルの効率的な保存

---

## セキュリティとプライバシー

### 認証情報の管理
- **環境変数からの読み込みを優先**: `.env` ファイルまたは環境変数を使用
- **認証情報ファイルをコミットしない**: `.gitignore` に追加
- **ログに認証情報を出力しない**: `mask_credentials_path()` でマスキング
- **Application Default Credentials のサポート**: Google Cloud SDK の標準認証も利用可能

### データの扱い
- 生成された音声ファイルの保存場所を明確に
- 一時ファイルの適切なクリーンアップ
- ユーザーデータの外部送信についての透明性
- ログ出力時のテキストのサニタイズ（個人情報保護）

---

## 今後の拡張案

### フェーズ2（将来的な機能）
- [ ] 感情表現のサポート（SSMLのprosody活用）
- [ ] 複数話者の会話生成
- [ ] 自動的なイントネーション調整
- [ ] 音声の事前プレビュー機能
- [ ] カスタム辞書（読み方の登録）

### 統合機能
- [ ] 字幕タイミングの自動調整
- [ ] ナレーションとBGMの自動ミキシング
- [ ] 音声認識との連携（生成音声の検証）
- [ ] 多言語字幕の自動生成

---

## マイルストーン

1. **Week 1**: 基盤構築とデータモデル
2. **Week 2**: プロセッサーとBuilder実装
3. **Week 3**: 環境変数管理とユーティリティ
4. **Week 4**: 統合と最適化
5. **Week 5**: ドキュメントとサンプル
6. **Week 6**: 動画パイプラインとの統合

---

## 参考資料

### デザインパターン
- **Template Method パターン**: "Design Patterns" (GoF) - 処理フローの定義
- **Builder パターン**: "Effective Java" - 複雑なオブジェクト構築

### Google Cloud TTS
- Google Cloud Text-to-Speech Documentation: https://cloud.google.com/text-to-speech/docs
- Supported Voices and Languages: https://cloud.google.com/text-to-speech/docs/voices
- SSML Reference: https://cloud.google.com/text-to-speech/docs/ssml
- Pricing: https://cloud.google.com/text-to-speech/pricing
- Python Client Library: https://cloud.google.com/python/docs/reference/texttospeech/latest

### 音声処理
- Pydub Documentation: https://github.com/jiaaro/pydub
- SSML W3C Specification: https://www.w3.org/TR/speech-synthesis11/

### 環境変数管理
- python-dotenv Documentation: https://pypi.org/project/python-dotenv/
- The Twelve-Factor App - Config: https://12factor.net/config
- Google Cloud Authentication: https://cloud.google.com/docs/authentication/getting-started

### Google Cloud セットアップ
- Service Accounts: https://cloud.google.com/iam/docs/service-accounts
- Application Default Credentials: https://cloud.google.com/docs/authentication/production

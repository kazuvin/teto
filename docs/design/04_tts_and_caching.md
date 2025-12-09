# TTS システムとキャッシング戦略

このドキュメントでは、Text-to-Speech (TTS) システムの設計とインテリジェントキャッシング戦略について詳しく説明します。

---

## 目次

1. [TTS システム概要](#tts-システム概要)
2. [TTS プロバイダー](#tts-プロバイダー)
3. [キャッシュシステム](#キャッシュシステム)
4. [音声設定の解決](#音声設定の解決)
5. [パフォーマンス最適化](#パフォーマンス最適化)

---

## TTS システム概要

### 目的

Teto の TTS システムは、ナレーションテキストから音声ファイルを生成します。主な要件：

1. **複数プロバイダー対応**: Google、ElevenLabs、Gemini などを統一的に扱う
2. **コスト削減**: API 呼び出しを最小限に抑える
3. **高品質**: 各プロバイダーの高品質音声を活用
4. **柔軟性**: シーン毎に異なる音声を使用可能
5. **キャッシング**: 同じテキスト+設定を再利用

### アーキテクチャ

**Strategy パターン**による TTS プロバイダーの抽象化：

```
TTSProvider (Interface)
├── GoogleTTSProvider
├── ElevenLabsTTSProvider
├── GeminiTTSProvider
└── MockTTSProvider (テスト用)
```

---

## TTS プロバイダー

**場所**:
- `packages/core/teto_core/tts/` (低レベル TTS クライアント)
- `packages/core/teto_core/script/providers/tts.py` (高レベル TTS プロバイダー)

### TTSProvider インターフェース

```python
class TTSProvider(ABC):
    """TTS プロバイダーインターフェース（Strategy）"""

    @abstractmethod
    def generate(self, text: str, config: VoiceConfig) -> TTSResult:
        """テキストから音声を生成する

        Args:
            text: 変換するテキスト
            config: 音声設定

        Returns:
            TTSResult: 生成された音声データと情報
        """
        ...

    @abstractmethod
    def estimate_duration(self, text: str, config: VoiceConfig) -> float:
        """音声の長さを推定する（秒）

        Args:
            text: テキスト
            config: 音声設定

        Returns:
            float: 推定される音声の長さ（秒）
        """
        ...
```

### TTSResult

```python
@dataclass
class TTSResult:
    """TTS生成結果"""

    audio_content: bytes                    # 音声データ（MP3/WAV）
    duration: float                         # 音声の長さ（秒）
    text: str                               # 元のテキスト
    path: str | None = None                 # 保存先パス（オプション）

    def save(self, output_path: str | Path) -> None:
        """音声ファイルを保存する"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            f.write(self.audio_content)
        self.path = str(path)
```

---

### Google Cloud TTS Provider

**場所**: `packages/core/teto_core/tts/google_tts.py`

#### 特徴

- **高品質音声**: WaveNet、Neural2 エンジン
- **SSML サポート**: 発音、ポーズ、音量などを細かく制御
- **多言語対応**: 40+ 言語、220+ 音声
- **コスト**: 100 万文字あたり $4〜$16

#### 実装

```python
class GoogleTTSProvider(TTSProvider):
    """Google Cloud TTS プロバイダー"""

    def __init__(self, credentials_path: Path | None = None):
        from ...tts.google_tts import GoogleTTSClient
        from ...tts.models import GoogleTTSVoiceConfig, GoogleTTSAudioConfig

        self._client = GoogleTTSClient(credentials_path=credentials_path)
        self._voice_config_cls = GoogleTTSVoiceConfig
        self._audio_config_cls = GoogleTTSAudioConfig

    def generate(self, text: str, config: VoiceConfig) -> TTSResult:
        """テキストから音声を生成する"""
        voice_config = self._voice_config_cls(
            language_code=config.language_code,
            voice_name=config.voice_id or "ja-JP-Wavenet-A",
        )
        audio_config = self._audio_config_cls(
            speaking_rate=config.speed,
            pitch=config.pitch,
        )

        # 音声データを生成
        audio_content = self._client.synthesize(
            text=text,
            voice_config=voice_config,
            audio_config=audio_config,
        )

        # 音声の長さを推定
        duration = self.estimate_duration(text, config)

        return TTSResult(
            audio_content=audio_content,
            duration=duration,
            text=text,
        )

    def estimate_duration(self, text: str, config: VoiceConfig) -> float:
        """音声の長さを推定する"""
        # 日本語: 約 5 文字/秒
        # 英語: 約 15 文字/秒
        if config.language_code.startswith("ja"):
            chars_per_second = 5.0
        else:
            chars_per_second = 15.0

        # 話速を考慮
        base_duration = len(text) / chars_per_second
        return base_duration / config.speed
```

#### 音声一覧

```python
# WaveNet 音声（高品質）
"ja-JP-Wavenet-A"  # 女性
"ja-JP-Wavenet-B"  # 女性
"ja-JP-Wavenet-C"  # 男性
"ja-JP-Wavenet-D"  # 男性

# Neural2 音声（最新、最高品質）
"ja-JP-Neural2-A"  # 女性
"ja-JP-Neural2-B"  # 女性
"ja-JP-Neural2-C"  # 男性
"ja-JP-Neural2-D"  # 男性
```

---

### ElevenLabs TTS Provider

**場所**: `packages/core/teto_core/script/providers/tts.py`

#### 特徴

- **超高品質**: 人間らしい自然な音声
- **ボイスクローニング**: カスタム音声の作成
- **多言語モデル**: 29 言語対応
- **コスト**: 月額 $5〜$330（プランによる）

#### 実装

```python
class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs TTS プロバイダー"""

    def __init__(self, api_key: str | None = None):
        from elevenlabs.client import ElevenLabs

        self._client = ElevenLabs(api_key=api_key or os.getenv("ELEVENLABS_API_KEY"))

    def generate(self, text: str, config: VoiceConfig) -> TTSResult:
        """テキストから音声を生成する"""
        # ElevenLabs API を呼び出し
        response = self._client.generate(
            text=text,
            voice=config.voice_id or "21m00Tcm4TlvDq8ikWAM",  # デフォルト音声
            model=config.model_id,
            output_format=config.output_format,
        )

        # 音声データを取得
        audio_content = b"".join(response)

        # 音声の長さを推定
        duration = self.estimate_duration(text, config)

        return TTSResult(
            audio_content=audio_content,
            duration=duration,
            text=text,
        )

    def estimate_duration(self, text: str, config: VoiceConfig) -> float:
        """音声の長さを推定する"""
        # ElevenLabs は高品質なので、より正確な推定
        # 実際の音声長は API レスポンスから取得可能（将来の改善）
        chars_per_second = 15.0 if config.language_code.startswith("en") else 5.0
        return len(text) / chars_per_second / config.speed
```

#### モデル一覧

```python
# Multilingual v2（推奨）
"eleven_multilingual_v2"

# Turbo v2（高速）
"eleven_turbo_v2"

# Multilingual v1
"eleven_multilingual_v1"
```

---

### Gemini TTS Provider

**場所**: `packages/core/teto_core/tts/gemini_tts.py`

#### 特徴

- **表現力**: 感情表現、スタイル制御
- **スタイルプロンプト**: テキストで音声のスタイルを指示
- **無料枠**: 1 日 1500 リクエスト
- **出力形式**: WAV（PCM）

#### 実装

```python
class GeminiTTSProvider(TTSProvider):
    """Gemini TTS プロバイダー"""

    def __init__(self, api_key: str | None = None):
        from ...tts.gemini_tts import GeminiTTSClient

        self._client = GeminiTTSClient(api_key=api_key or os.getenv("GOOGLE_API_KEY"))

    def generate(self, text: str, config: VoiceConfig) -> TTSResult:
        """テキストから音声を生成する"""
        # Gemini API を呼び出し
        audio_content = self._client.synthesize(
            text=text,
            voice_name=config.voice_name,
            model_id=config.gemini_model_id,
            style_prompt=config.style_prompt,
            speed=config.speed,
        )

        # 音声の長さを推定
        duration = self.estimate_duration(text, config)

        return TTSResult(
            audio_content=audio_content,
            duration=duration,
            text=text,
        )

    def estimate_duration(self, text: str, config: VoiceConfig) -> float:
        """音声の長さを推定する"""
        chars_per_second = 5.0  # 日本語ベース
        return len(text) / chars_per_second / config.speed
```

#### 音声一覧

```python
# Gemini 音声名
"Aoede"   # 女性、落ち着いた
"Charon"  # 男性、深い
"Fenrir"  # 男性、力強い
"Kore"    # 女性、明るい（デフォルト）
"Puck"    # 中性、軽やか
```

#### スタイルプロンプト

```json
{
  "voice_name": "Kore",
  "style_prompt": "元気で明るく、親しみやすい口調で話してください"
}
```

---

## キャッシュシステム

**場所**: `packages/core/teto_core/cache/`

### キャッシュの目的

1. **API コスト削減**: 同じテキスト+設定を再利用
2. **生成速度向上**: TTS API 呼び出しをスキップ
3. **プロジェクト間共有**: 異なるプロジェクトでもキャッシュを活用

### キャッシュアーキテクチャ

```
TTSCacheManager
├── キャッシュディレクトリ: ~/.cache/teto/tts/
├── キー生成: SHA256(text + VoiceConfig)[:16]
├── ストレージ: ファイルシステム
└── 構造: AB/ab1234567890cdef.mp3
```

### TTSCacheManager

**場所**: `packages/core/teto_core/cache/tts.py`

```python
class TTSCacheManager(CacheManager):
    """TTS キャッシュマネージャー"""

    def __init__(self, cache_dir: Path | None = None):
        cache_dir = cache_dir or self._get_default_cache_dir()
        super().__init__(cache_dir)

    @staticmethod
    def _get_default_cache_dir() -> Path:
        """デフォルトキャッシュディレクトリを取得"""
        if platform.system() == "Windows":
            base = Path(os.getenv("LOCALAPPDATA", "~/.cache"))
        else:
            base = Path(os.getenv("XDG_CACHE_HOME", "~/.cache"))

        return base.expanduser() / "teto" / "tts"

    def get(
        self,
        text: str,
        voice_config: "VoiceConfig",
        audio_ext: str = ".mp3",
    ) -> bytes | None:
        """キャッシュから音声データを取得

        Args:
            text: テキスト
            voice_config: 音声設定
            audio_ext: 音声ファイル拡張子

        Returns:
            bytes | None: 音声データ（キャッシュヒット時）、None（キャッシュミス時）
        """
        cache_key = self._compute_cache_key(text, voice_config)
        cache_path = self._get_cache_path(cache_key, audio_ext)

        if cache_path.exists():
            with open(cache_path, "rb") as f:
                return f.read()

        return None

    def put(
        self,
        text: str,
        voice_config: "VoiceConfig",
        audio_ext: str,
        audio_content: bytes,
    ) -> None:
        """キャッシュに音声データを保存

        Args:
            text: テキスト
            voice_config: 音声設定
            audio_ext: 音声ファイル拡張子
            audio_content: 音声データ
        """
        cache_key = self._compute_cache_key(text, voice_config)
        cache_path = self._get_cache_path(cache_key, audio_ext)

        # ディレクトリを作成
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # ファイルに書き込み
        with open(cache_path, "wb") as f:
            f.write(audio_content)

    def _compute_cache_key(self, text: str, voice_config: "VoiceConfig") -> str:
        """キャッシュキーを計算"""
        # 音声設定から関連するフィールドを抽出
        config_dict = {
            "provider": voice_config.provider,
            "voice_id": voice_config.voice_id,
            "language_code": voice_config.language_code,
            "speed": voice_config.speed,
            "pitch": voice_config.pitch,
            # ElevenLabs
            "model_id": voice_config.model_id,
            "output_format": voice_config.output_format,
            # Gemini
            "voice_name": voice_config.voice_name,
            "gemini_model_id": voice_config.gemini_model_id,
            "style_prompt": voice_config.style_prompt,
        }

        # テキストと設定を結合してハッシュ化
        return self.compute_hash({"text": text, "config": config_dict})

    def _get_cache_path(self, cache_key: str, audio_ext: str) -> Path:
        """キャッシュファイルパスを取得"""
        # サブディレクトリを作成（最初の2文字）
        subdir = cache_key[:2]
        return self.cache_dir / subdir / f"{cache_key}{audio_ext}"
```

### キャッシュキー生成

**重要**: キャッシュキーは以下の要素から生成されます：

```python
cache_data = {
    "text": "こんにちは",
    "config": {
        "provider": "google",
        "voice_id": "ja-JP-Wavenet-A",
        "language_code": "ja-JP",
        "speed": 1.0,
        "pitch": 0.0,
        "model_id": "eleven_multilingual_v2",
        "output_format": "mp3_44100_128",
        "voice_name": "Kore",
        "gemini_model_id": "gemini-2.5-flash-preview-tts",
        "style_prompt": None,
    }
}

# JSON シリアライズ（キーをソート）
json_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)

# SHA256 ハッシュを計算して最初の16文字を使用
cache_key = hashlib.sha256(json_str.encode()).hexdigest()[:16]
# 例: "a1b2c3d4e5f6g7h8"

# ファイルパス
# ~/.cache/teto/tts/a1/a1b2c3d4e5f6g7h8.mp3
```

**キャッシュヒット条件**:
- テキストが完全一致
- **全ての音声設定パラメータが一致**

**例**:
```python
# キャッシュヒット
text1 = "こんにちは"
voice1 = VoiceConfig(provider="google", voice_id="ja-JP-Wavenet-A", speed=1.0, pitch=0.0)

text2 = "こんにちは"
voice2 = VoiceConfig(provider="google", voice_id="ja-JP-Wavenet-A", speed=1.0, pitch=0.0)
# → 同じキャッシュキー

# キャッシュミス
text3 = "こんにちは"
voice3 = VoiceConfig(provider="google", voice_id="ja-JP-Wavenet-B", speed=1.0, pitch=0.0)
# → 異なるキャッシュキー（voice_id が異なる）
```

### キャッシュディレクトリ構造

```
~/.cache/teto/tts/
├── a1/
│   ├── a1b2c3d4e5f6g7h8.mp3
│   └── a1234567890abcde.mp3
├── b2/
│   └── b2345678901bcdef.mp3
└── ...

各ファイル:
- ファイル名: キャッシュキー（16文字）+ 拡張子
- サブディレクトリ: キャッシュキーの最初の2文字
```

### キャッシュ管理

```python
# キャッシュマネージャーを取得（シングルトン）
cache_manager = get_tts_cache_manager()

# キャッシュ情報を取得
info = cache_manager.get_info()
print(f"キャッシュサイズ: {info['size']} MB")
print(f"ファイル数: {info['count']}")

# キャッシュをクリア
cache_manager.clear()
```

---

## 音声設定の解決

**場所**: `ScriptCompiler._resolve_scene_voice()`

### 優先順位

シーン毎に異なる音声を使用できる機能：

```
1. scene.voice（直接指定）
   ↓ なければ
2. scene.voice_profile（プロファイル参照）
   ↓ なければ
3. script.voice（グローバルデフォルト）
```

### 実装

```python
def _resolve_scene_voice(self, script: Script, scene: Scene):
    """シーンに適用する音声設定を解決"""

    # 1. 直接指定
    if scene.voice is not None:
        return scene.voice

    # 2. プロファイル参照
    if scene.voice_profile is not None:
        if script.voice_profiles is None or scene.voice_profile not in script.voice_profiles:
            raise ValueError(
                f"ボイスプロファイル '{scene.voice_profile}' が見つかりません"
            )
        return script.voice_profiles[scene.voice_profile]

    # 3. グローバルデフォルト
    return script.voice
```

### キャッシュへの影響

**重要**: プロファイル名は関係なく、実際の音声設定値でキャッシュされます。

```python
# プロファイル定義
voice_profiles = {
    "narrator_1": VoiceConfig(provider="google", voice_id="ja-JP-Wavenet-A"),
    "narrator_2": VoiceConfig(provider="google", voice_id="ja-JP-Wavenet-A"),  # 同じ設定
}

# シーン1: narrator_1 で "こんにちは"
# → キャッシュキー: hash("こんにちは" + VoiceConfig(ja-JP-Wavenet-A))

# シーン2: narrator_2 で "こんにちは"
# → キャッシュキー: 同じ（設定値が同じため）
# → キャッシュヒット！
```

---

## パフォーマンス最適化

### キャッシュヒット率の向上

**戦略**:
1. **プロファイルの再利用**: 同じ音声設定を複数シーンで使用
2. **テキストの正規化**: 空白や改行を統一
3. **プロジェクト間共有**: グローバルキャッシュを活用

**例**:
```json
{
  "voice_profiles": {
    "narrator": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"}
  },
  "scenes": [
    {"narrations": [{"text": "こんにちは"}], "voice_profile": "narrator"},
    {"narrations": [{"text": "さようなら"}], "voice_profile": "narrator"},
    {"narrations": [{"text": "こんにちは"}], "voice_profile": "narrator"}
  ]
}

結果:
- シーン1: "こんにちは" → API 呼び出し、キャッシュに保存
- シーン2: "さようなら" → API 呼び出し、キャッシュに保存
- シーン3: "こんにちは" → キャッシュヒット（API 呼び出しなし）
```

### キャッシュ統計

```python
# コンパイル時にキャッシュ統計を表示
"""
生成中...
  TTS キャッシュ: 15/20 ヒット (75%)

説明:
- 20 個のナレーションセグメント
- 15 個がキャッシュヒット（75%）
- 5 個が新規生成（25%）
- API コストを 75% 削減！
"""
```

### 並列 TTS 生成（将来の拡張）

```python
from concurrent.futures import ThreadPoolExecutor

def _generate_all_narrations_parallel(self, script: Script):
    """複数シーンの TTS を並列生成"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for scene in script.scenes:
            for segment in scene.narrations:
                future = executor.submit(self._generate_narration, segment, scene)
                futures.append(future)

        # 結果を待つ
        results = [f.result() for f in futures]

    return results
```

---

## トラブルシューティング

### よくある問題

#### 1. キャッシュミスが多い

**原因**: 音声設定が微妙に異なる

**解決策**:
```python
# 悪い例（毎回異なるキャッシュキー）
for scene in scenes:
    scene.voice = VoiceConfig(provider="google", voice_id="ja-JP-Wavenet-A")

# 良い例（同じ設定を再利用）
voice_profiles = {
    "narrator": VoiceConfig(provider="google", voice_id="ja-JP-Wavenet-A")
}
for scene in scenes:
    scene.voice_profile = "narrator"
```

#### 2. キャッシュが大きすぎる

**原因**: 多数のプロジェクトでキャッシュが蓄積

**解決策**:
```bash
# キャッシュ情報を確認
teto cache info

# 古いキャッシュをクリア
teto cache clear --older-than 30d

# 全キャッシュをクリア
teto cache clear
```

#### 3. API エラー

**原因**: 認証情報が設定されていない

**解決策**:
```bash
# Google Cloud TTS
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# ElevenLabs
export ELEVENLABS_API_KEY=your_api_key

# Gemini
export GOOGLE_API_KEY=your_api_key
```

---

## まとめ

TTS システムとキャッシング戦略の特徴：

- ✅ **マルチプロバイダー**: Google、ElevenLabs、Gemini を統一的に扱う
- ✅ **インテリジェントキャッシュ**: テキスト + 音声設定でキャッシュ
- ✅ **コスト削減**: API 呼び出しを最小限に抑える
- ✅ **高速生成**: キャッシュヒットで即座に音声取得
- ✅ **プロジェクト間共有**: グローバルキャッシュで効率化
- ✅ **柔軟性**: シーン毎に異なる音声を使用可能

このシステムにより、高品質な音声生成とコスト効率の両立が実現されています。

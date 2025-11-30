# テキスト音声変換(TTS)機能

Google Cloud Text-to-Speech APIを使用して、テキストから音声を生成する機能です。

## 機能概要

- テキスト入力から音声ファイル(MP3, WAV等)を生成
- Google Cloud TTS の WaveNet/Neural2 音声を使用
- 音声のパラメータ調整(速度、ピッチ、音量など)
- SSML による細かい制御
- Builder パターンによる直感的なAPI
- Template Method パターンによる統一的な処理フロー

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd packages/core
uv sync
```

### 2. Google Cloud のセットアップ

#### 2.1 Google Cloud プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. プロジェクトIDをメモ

#### 2.2 Text-to-Speech API の有効化

1. Google Cloud Console のナビゲーションメニューから「APIとサービス」→「ライブラリ」
2. "Cloud Text-to-Speech API" を検索
3. 「有効にする」をクリック

#### 2.3 サービスアカウントの作成

1. 「IAMと管理」→「サービスアカウント」
2. 「サービスアカウントを作成」
3. 名前を入力(例: "teto-tts")
4. ロールを選択: "Cloud Text-to-Speech 管理者" または "Cloud Text-to-Speech ユーザー"
5. 「完了」

#### 2.4 認証情報ファイルのダウンロード

1. 作成したサービスアカウントをクリック
2. 「キー」タブ → 「鍵を追加」→「新しい鍵を作成」
3. JSON形式を選択
4. ダウンロードされたJSONファイルを安全な場所に保存

#### 2.5 環境変数の設定

`.env` ファイルを作成:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

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

## API リファレンス

### TTSBuilder

テキスト音声変換リクエストを構築するビルダークラス。

#### メソッド

- `text(text: str)` - 変換するテキストを設定
- `voice(voice_name: str)` - 音声を設定(例: "ja-JP-Wavenet-A")
- `language(language_code: str)` - 言語を設定(例: "ja-JP", "en-US")
- `speed(rate: float)` - 話す速度を設定(0.25～4.0倍速)
- `pitch(pitch: float)` - ピッチを設定(-20.0～20.0セミトーン)
- `volume(gain_db: float)` - 音量を設定(dB)
- `sample_rate(rate: int)` - サンプリングレートを設定(Hz)
- `output_format(format: str)` - 出力フォーマットを設定("mp3", "wav", "ogg")
- `output_path(path: str | Path)` - 出力先パスを設定
- `effects_profile(profiles: list[str])` - 音声効果プロファイルを設定
- `ssml(use_ssml: bool)` - SSMLモードを設定
- `build()` - TTSRequestを構築

### GoogleTTSProcessor

Google Cloud TTS を使用して音声を生成するプロセッサー。

#### メソッド

- `execute(request: TTSRequest)` - 音声生成を実行

## 料金

- 無料枠: 月100万文字(Standard)
- Standard: $4/100万文字
- WaveNet/Neural2: $16/100万文字

無料枠は月300本以上の10分動画に相当します。

## ディレクトリ構造

```
packages/core/teto_core/
├── models/
│   ├── tts.py              # TTS関連のPydanticモデル
│   └── builders/
│       └── tts.py          # TTSBuilder
│
├── processors/
│   └── tts.py              # GoogleTTSProcessor
│
└── tts/                    # TTS専用モジュール
    ├── __init__.py
    ├── google_tts.py       # Google Cloud TTS クライアント
    ├── config.py           # 環境変数管理
    └── utils/
        ├── ssml.py         # SSML生成ユーティリティ
        ├── text_utils.py   # テキスト正規化
        └── security.py     # セキュリティ
```

## セキュリティ

- 認証情報ファイルは `.gitignore` に追加されています
- 環境変数から認証情報を読み込みます
- ログに認証情報を出力しません

## 参考資料

- [Google Cloud Text-to-Speech Documentation](https://cloud.google.com/text-to-speech/docs)
- [Supported Voices and Languages](https://cloud.google.com/text-to-speech/docs/voices)
- [SSML Reference](https://cloud.google.com/text-to-speech/docs/ssml)
- [Pricing](https://cloud.google.com/text-to-speech/pricing)

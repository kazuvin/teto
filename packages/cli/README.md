# Teto CLI

コマンドラインインターフェース

## Installation

```bash
cd packages/cli
uv pip install -e .
```

## Usage

### 基本コマンド

```bash
# システム情報を表示
teto info

# プロジェクトファイルから動画を生成
teto generate project.json

# 新規プロジェクトファイルを作成
teto init project.json
```

### テキスト音声変換 (TTS)

#### 音声生成

```bash
# 基本的な使い方
teto tts "こんにちは、世界" -o output.mp3

# 音声設定のカスタマイズ
teto tts "本日は良い天気ですね" -o narration.mp3 \
  --voice ja-JP-Wavenet-A \
  --pitch -2.0 \
  --speed 0.9 \
  --volume 0.0 \
  --format mp3

# WAV形式で出力
teto tts "これはテストです" -o test.wav --format wav

# SSMLを使用
teto tts "<speak>これは<emphasis level='strong'>重要</emphasis>です</speak>" \
  -o important.mp3 --ssml
```

#### 利用可能な音声の一覧を表示

```bash
# 日本語の音声を表示
teto tts-voices --language ja-JP

# 英語の音声を表示
teto tts-voices --language en-US
```

### オプション

#### `tts` コマンド

- `TEXT`: 変換するテキスト (必須)
- `-o, --output`: 出力ファイルパス (必須)
- `-v, --voice`: 音声名 (デフォルト: ja-JP-Wavenet-A)
- `--pitch`: ピッチ調整 (-20.0～20.0) (デフォルト: 0.0)
- `--speed`: 話す速度 (0.25～4.0) (デフォルト: 1.0)
- `--volume`: 音量調整 (dB) (デフォルト: 0.0)
- `--format`: 出力フォーマット (mp3, wav, ogg) (デフォルト: mp3)
- `--ssml`: テキストをSSMLとして解釈

#### `tts-voices` コマンド

- `--language`: 言語コード (デフォルト: ja-JP)

## Google Cloud TTS のセットアップ

テキスト音声変換を使用するには、Google Cloud のセットアップが必要です。

1. Google Cloud プロジェクトを作成
2. Text-to-Speech API を有効化
3. サービスアカウントを作成し、認証情報ファイルをダウンロード
4. 環境変数を設定:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

詳細は `packages/core/docs/TTS_README.md` を参照してください。

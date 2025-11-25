# プロジェクトファイルの例

## simple_video.json

基本的な動画生成の例。以下の機能を含みます:

- 画像イントロ（3秒）
- メインの動画コンテンツ
- 画像アウトロ（3秒）
- ナレーション音声
- 背景音楽
- 字幕（焼き込み）

### 使い方

1. 素材ファイルを準備:
```bash
mkdir -p assets
# assets/ ディレクトリに以下を配置:
# - intro.png (イントロ画像)
# - main_content.mp4 (メイン動画)
# - outro.png (アウトロ画像)
# - narration.mp3 (ナレーション音声)
# - background_music.mp3 (BGM)
```

2. 動画を生成:
```bash
teto generate docs/examples/simple_video.json
```

## プロジェクトファイルの構造

### output (出力設定)

| フィールド | 説明 | デフォルト |
|----------|------|----------|
| `path` | 出力ファイルパス | 必須 |
| `width` | 動画の幅 | 1920 |
| `height` | 動画の高さ | 1080 |
| `fps` | フレームレート | 30 |
| `codec` | 動画コーデック | libx264 |
| `audio_codec` | 音声コーデック | aac |
| `bitrate` | ビットレート | null (自動) |
| `subtitle_mode` | 字幕モード: `burn`/`srt`/`vtt`/`none` | burn |

### timeline.video_layers (動画・画像レイヤー)

#### VideoLayer
```json
{
  "type": "video",
  "path": "video.mp4",
  "start_time": 0.0,
  "duration": null,
  "volume": 1.0
}
```

#### ImageLayer
```json
{
  "type": "image",
  "path": "image.png",
  "start_time": 0.0,
  "duration": 3.0
}
```

### timeline.audio_layers (音声レイヤー)

```json
{
  "type": "audio",
  "path": "audio.mp3",
  "start_time": 0.0,
  "duration": null,
  "volume": 1.0
}
```

### timeline.subtitle_layers (字幕レイヤー)

```json
{
  "type": "subtitle",
  "items": [
    {
      "text": "字幕テキスト",
      "start_time": 0.0,
      "end_time": 2.0
    }
  ],
  "font_size": 48,
  "font_color": "white",
  "bg_color": "black@0.5",
  "position": "bottom"
}
```

## Tips

### duration の扱い

- `null`: 素材の長さをそのまま使用
- 数値: 指定した秒数で切り取り

### start_time の扱い

- 動画・画像レイヤーは順番に配置される
- 音声レイヤーは絶対時間で配置され、複数を同時に再生可能

### 字幕の位置

- `bottom`: 下部
- `top`: 上部
- `center`: 中央

### 背景色の透明度

`bg_color` は `color@opacity` の形式:
- `black@0.5`: 50%透明な黒
- `white@0.8`: 80%透明な白

# レイヤードキャラクター サンプル

このディレクトリには、動く立ち絵機能のサンプルキャラクター素材と設定ファイルが含まれています。

## ファイル構成

```
examples/
├── assets/characters/
│   ├── README.md                    # このファイル
│   ├── create_simple_character.py   # 簡易キャラクター素材生成スクリプト
│   └── teto/                        # テトキャラクター素材
│       ├── README.md                # 素材作成ガイド
│       ├── base.png                 # 顔の輪郭・体
│       ├── eyes_open.png            # 開いた目
│       ├── eyes_closed.png          # 閉じた目
│       ├── eyes_smile.png           # 笑顔の目
│       ├── mouth_closed.png         # 閉じた口
│       ├── mouth_open.png           # 開いた口
│       ├── hair.png                 # 前髪
│       └── preview.png              # プレビュー画像
└── scripts/
    ├── 21_script_layered_character_simple.json    # 基本サンプル
    └── 22_script_layered_character_advanced.json  # 高度なサンプル
```

## 使い方

### 1. サンプルキャラクター素材の生成

簡易的なキャラクター素材を生成する場合:

```bash
cd examples/assets/characters
python3 create_simple_character.py
```

これにより、`teto/` ディレクトリに全パーツが生成されます。

### 2. サンプルJSON設定ファイルの使用

サンプルスクリプトは `examples/scripts/` ディレクトリにあります:
- `21_script_layered_character_simple.json` - 基本的な使用例
- `22_script_layered_character_advanced.json` - 高度な使用例(複数シーン、表情変化、位置・スケール変更)

#### 基本構造

```json
{
  "layered_characters": {
    "teto": {
      "id": "teto",
      "name": "テト",
      "parts": { ... },
      "default_parts": { ... },
      "lip_sync": { ... },
      "blink": { ... },
      "position": "bottom-right",
      "scale": 0.8
    }
  },
  "scenes": [
    {
      "narrations": [
        {
          "text": "こんにちは！",
          "layered_character_states": [ ... ]
        }
      ]
    }
  ]
}
```

### 3. スクリプトでの使用

Tetoコマンドラインツールを使用して動画を生成:

```bash
# 基本サンプル
teto generate examples/scripts/21_script_layered_character_simple.json output_simple.mp4

# 高度なサンプル
teto generate examples/scripts/22_script_layered_character_advanced.json output_advanced.mp4
```

## 機能説明

### リップシンク

シンプルなパクパクアニメーション(MVP):

```json
{
  "lip_sync": {
    "mode": "simple_paku_paku",
    "paku_interval": 0.15,
    "paku_open_shape": "open",
    "paku_closed_shape": "closed"
  }
}
```

- `mode`: `"simple_paku_paku"` (MVP) または `"phoneme_mapping"` (将来実装)
- `paku_interval`: 口の開閉間隔(秒)
- `paku_open_shape`: 開いた口の形状名
- `paku_closed_shape`: 閉じた口の形状名

### 自動瞬き

ランダムな間隔で自然な瞬きを生成:

```json
{
  "blink": {
    "enabled": true,
    "blink_interval_min": 2.0,
    "blink_interval_max": 4.5,
    "blink_duration": 0.12,
    "suppress_during_speech": true
  }
}
```

- `enabled`: 瞬きを有効にするか
- `blink_interval_min`: 最小瞬き間隔(秒)
- `blink_interval_max`: 最大瞬き間隔(秒)
- `blink_duration`: 瞬きの持続時間(秒)
- `suppress_during_speech`: 発話中の瞬きを抑制するか

### セグメント単位での表情制御

各ナレーションセグメントで表情を変更できます:

```json
{
  "text": "こんにちは！",
  "layered_character_states": [
    {
      "character_id": "teto",
      "part_states": [
        {
          "part_type": "eyes",
          "state_name": "eyes.smile"
        }
      ],
      "lip_sync_enabled": true,
      "blink_enabled": true
    }
  ]
}
```

### パーツの種類

- `base`: 顔の輪郭、体(Z-index: 0)
- `eyes`: 目(Z-index: 2)
  - `eyes.open`: 開いた目
  - `eyes.closed`: 閉じた目
  - `eyes.smile`: 笑顔の目
- `mouth`: 口(Z-index: 3)
  - `mouth.closed`: 閉じた口
  - `mouth.open`: 開いた口
- `hair`: 髪(Z-index: 4)

Z-indexが大きいほど前面に表示されます。

### 配置位置のプリセット

- `"bottom-right"`: 右下
- `"bottom-left"`: 左下
- `"bottom-center"`: 下中央
- `"right"`: 右中央
- `"left"`: 左中央
- `"center"`: 中央

カスタム位置も指定可能:

```json
{
  "custom_position": [100, 200]  // (x, y) ピクセル座標
}
```

### スケールと不透明度

```json
{
  "scale": 0.8,      // 0.0 ~ 1.0+
  "opacity": 1.0     // 0.0 ~ 1.0
}
```

## 高度な使用例

### 複数キャラクターの表示

```json
{
  "layered_characters": {
    "teto": { ... },
    "friend": { ... }
  },
  "scenes": [
    {
      "narrations": [
        {
          "text": "こんにちは！",
          "layered_character_states": [
            {
              "character_id": "teto",
              "position": "bottom-left",
              "part_states": [
                {"part_type": "eyes", "state_name": "eyes.smile"}
              ]
            },
            {
              "character_id": "friend",
              "position": "bottom-right",
              "part_states": [
                {"part_type": "eyes", "state_name": "eyes.open"}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### キャラクターの登場・退場

不透明度を使用してフェードイン・フェードアウト効果を実現:

```json
{
  "narrations": [
    {
      "text": "登場",
      "layered_character_states": [
        {
          "character_id": "teto",
          "opacity": 0.0  // 最初は透明
        }
      ]
    },
    {
      "text": "こんにちは",
      "layered_character_states": [
        {
          "character_id": "teto",
          "opacity": 1.0  // 徐々に表示
        }
      ]
    },
    {
      "text": "さようなら",
      "layered_character_states": [
        {
          "character_id": "teto",
          "opacity": 0.0  // 徐々に消える
        }
      ]
    }
  ]
}
```

### リップシンクのON/OFF

特定のセグメントでリップシンクを無効化:

```json
{
  "text": "このセグメントでは口を動かさない",
  "layered_character_states": [
    {
      "character_id": "teto",
      "lip_sync_enabled": false,
      "part_states": [
        {"part_type": "mouth", "state_name": "mouth.closed"}
      ]
    }
  ]
}
```

## 独自キャラクターの作成

独自のキャラクター素材を作成する方法については、`teto/README.md` を参照してください。

### 基本的な手順

1. **キャンバスサイズを決定** (推奨: 512x512px または 1024x1024px)
2. **ベースパーツを作成** (顔の輪郭、体)
3. **表情パーツを作成** (目、口のバリエーション)
4. **装飾パーツを作成** (髪、アクセサリー)
5. **JSON設定ファイルを作成**
6. **プレビューで確認**

### 必須ファイル

最小限の構成:
- `base.png` - ベース
- `eyes_open.png` - 開いた目
- `eyes_closed.png` - 閉じた目
- `mouth_open.png` - 開いた口
- `mouth_closed.png` - 閉じた口

## トラブルシューティング

### パーツがずれる

すべてのパーツが同じキャンバスサイズで作成されているか確認してください。

### 口パクが速すぎる/遅すぎる

`paku_interval` の値を調整してください:
- 速くする: 値を小さく (例: 0.1)
- 遅くする: 値を大きく (例: 0.2)

### 瞬きが不自然

以下のパラメータを調整してください:
- `blink_interval_min/max`: 瞬きの頻度
- `blink_duration`: 瞬きの速さ

### パーツが表示されない

1. パスが正しいか確認
2. PNG形式(RGBA)で保存されているか確認
3. Z-indexの設定が正しいか確認

## 参考リンク

- [動く立ち絵機能 実装計画](../../../docs/plan/07_live_character_lip_sync.md)
- [実装完了サマリー](../../../docs/plan/07_implementation_summary.md)
- [素材作成ガイド](teto/README.md)

# テトキャラクター素材

このディレクトリには、動く立ち絵機能のサンプルキャラクター「テト」のパーツ画像を配置します。

## 必要なパーツ画像

### 基本構成
すべての画像は **PNG形式(透過対応)** で、**同じサイズ** である必要があります。

推奨サイズ: 512x512px または 1024x1024px

### パーツリスト

#### 1. ベース (base.png)
- 顔の輪郭、体
- Z-index: 0 (最背面)

#### 2. 目パーツ
- `eyes_open.png` - 開いた目 (Z-index: 2)
- `eyes_closed.png` - 閉じた目 (Z-index: 2)
- `eyes_smile.png` - 笑顔の目 (目を細める) (Z-index: 2)

#### 3. 口パーツ (MVP用)
- `mouth_closed.png` - 閉じた口 (Z-index: 3)
- `mouth_open.png` - 開いた口 (Z-index: 3)

#### 4. 髪パーツ
- `hair.png` - 前髪 (Z-index: 4, 最前面)

## パーツ作成ガイドライン

### 画像形式
- **フォーマット**: PNG (RGBA)
- **透過**: 必須 (背景を透明に)
- **サイズ**: 全パーツ同一サイズ
- **解像度**: 512x512px 以上推奨

### 位置合わせ
- すべてのパーツは **同じキャンバスサイズ** で作成
- パーツの位置は **ピクセル単位で揃える**
- 基準点は左上(0, 0)

例:
```
base.png        (512x512px)
eyes_open.png   (512x512px) ← baseと同じサイズ
mouth_open.png  (512x512px) ← baseと同じサイズ
```

### レイヤー順序
```
4. hair.png      (最前面)
3. mouth_*.png
2. eyes_*.png
0. base.png      (最背面)
```

### パーツ切り替えの注意点

#### 目パーツ
- `eyes_open.png`: 通常時
- `eyes_closed.png`: 瞬き時
- `eyes_smile.png`: 笑顔時

これらは **同じ位置** に配置される想定で作成してください。

#### 口パーツ
- `mouth_closed.png`: 口を閉じている
- `mouth_open.png`: 口を開けている

リップシンクで交互に切り替わります。

## サンプルJSON

この素材を使用する場合のJSON例:

\`\`\`json
{
  "layered_characters": {
    "teto": {
      "id": "teto",
      "name": "テト",
      "parts": {
        "base": [
          {
            "type": "base",
            "name": "body",
            "path": "examples/assets/characters/teto/base.png",
            "z_index": 0
          }
        ],
        "eyes.open": [
          {
            "type": "eyes",
            "name": "eyes_open",
            "path": "examples/assets/characters/teto/eyes_open.png",
            "z_index": 2
          }
        ],
        "eyes.closed": [
          {
            "type": "eyes",
            "name": "eyes_closed",
            "path": "examples/assets/characters/teto/eyes_closed.png",
            "z_index": 2
          }
        ],
        "eyes.smile": [
          {
            "type": "eyes",
            "name": "eyes_smile",
            "path": "examples/assets/characters/teto/eyes_smile.png",
            "z_index": 2
          }
        ],
        "mouth.closed": [
          {
            "type": "mouth",
            "name": "mouth_closed",
            "path": "examples/assets/characters/teto/mouth_closed.png",
            "z_index": 3
          }
        ],
        "mouth.open": [
          {
            "type": "mouth",
            "name": "mouth_open",
            "path": "examples/assets/characters/teto/mouth_open.png",
            "z_index": 3
          }
        ],
        "hair": [
          {
            "type": "hair",
            "name": "hair_front",
            "path": "examples/assets/characters/teto/hair.png",
            "z_index": 4
          }
        ]
      },
      "default_parts": {
        "base": "base",
        "eyes": "eyes.open",
        "mouth": "mouth.closed",
        "hair": "hair"
      },
      "lip_sync": {
        "mode": "simple_paku_paku",
        "paku_interval": 0.15,
        "paku_open_shape": "open",
        "paku_closed_shape": "closed"
      },
      "blink": {
        "enabled": true,
        "blink_interval_min": 2.0,
        "blink_interval_max": 4.5,
        "blink_duration": 0.12,
        "suppress_during_speech": true
      },
      "position": "bottom-right",
      "scale": 0.8
    }
  }
}
\`\`\`

## 素材作成ツール

### 推奨ツール
- **CLIP STUDIO PAINT** - レイヤー機能が便利
- **Krita** - 無料、透過PNG対応
- **Photoshop** - プロ向け
- **GIMP** - 無料、オープンソース

### 作成手順

1. **ベースレイヤー作成**
   - 512x512pxのキャンバスを作成
   - 顔の輪郭、体を描画
   - `base.png` として書き出し

2. **目パーツ作成**
   - 同じキャンバスで目のみ描画
   - 他は透明
   - 開き目、閉じ目、笑顔目の3パターン作成
   - それぞれ書き出し

3. **口パーツ作成**
   - 同じキャンバスで口のみ描画
   - 閉じ口、開き口の2パターン作成
   - それぞれ書き出し

4. **髪パーツ作成**
   - 前髪を描画
   - 目や口を隠す部分は髪が前面に

### プレビュー方法
```python
from PIL import Image

# パーツを読み込み
base = Image.open("base.png")
eyes = Image.open("eyes_open.png")
mouth = Image.open("mouth_closed.png")
hair = Image.open("hair.png")

# 重ね合わせ
composite = Image.new("RGBA", base.size)
composite.paste(base, (0, 0), base)
composite.paste(eyes, (0, 0), eyes)
composite.paste(mouth, (0, 0), mouth)
composite.paste(hair, (0, 0), hair)

# 保存
composite.save("preview.png")
```

## 簡易素材の生成

実際のイラストがない場合、シンプルな図形で動作確認用の素材を作成できます。

詳細は `create_simple_character.py` を参照してください。

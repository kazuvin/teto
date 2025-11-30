# ウォーターマーク追加機能

## 概要
動画に透かし（ロゴや著作権表示）を追加する機能を実装する。

## 背景
動画コンテンツの著作権保護やブランディングのために、ウォーターマーク機能は一般的なニーズである。既存の `StampLayer` を拡張することで、効率的に実装できる。

## 目標
- 画像ウォーターマークの配置（四隅指定）
- 透明度の調整
- サイズのスケーリング

---

## タスク詳細

### やること
- [ ] `StampLayer` モデルに `opacity` フィールドを追加
- [ ] `StampLayer` モデルに `position_preset` フィールドを追加（top-left, top-right, bottom-left, bottom-right）
- [ ] `StampLayerProcessor` に透明度適用ロジックを追加
- [ ] `StampLayerProcessor` にプリセット位置からの座標計算ロジックを追加
- [ ] ユニットテストを追加
- [ ] 動作確認

### 変更対象ファイル
- `packages/core/teto_core/layer/models.py` - StampLayer モデル
- `packages/core/teto_core/layer/processors/video.py` - StampLayerProcessor
- `packages/core/tests/` - テストファイル

---

## 実装メモ

### StampLayer モデルの拡張案
```python
class PositionPreset(str, Enum):
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CUSTOM = "custom"  # x, y を直接指定

class StampLayer(BaseModel):
    image_path: str
    x: int = 0
    y: int = 0
    scale: float = 1.0
    opacity: float = 1.0  # 新規追加: 0.0〜1.0
    position_preset: PositionPreset | None = None  # 新規追加
    margin: int = 20  # 新規追加: プリセット使用時の端からの余白
```

### 透明度適用ロジック（moviepy）
```python
def apply_opacity(clip: ImageClip, opacity: float) -> ImageClip:
    """クリップに透明度を適用する"""
    if opacity < 1.0:
        return clip.with_opacity(opacity)
    return clip
```

### プリセット位置計算ロジック
```python
def calculate_position(
    video_size: tuple[int, int],
    stamp_size: tuple[int, int],
    preset: PositionPreset,
    margin: int
) -> tuple[int, int]:
    """プリセットから実際の座標を計算する"""
    video_w, video_h = video_size
    stamp_w, stamp_h = stamp_size

    positions = {
        PositionPreset.TOP_LEFT: (margin, margin),
        PositionPreset.TOP_RIGHT: (video_w - stamp_w - margin, margin),
        PositionPreset.BOTTOM_LEFT: (margin, video_h - stamp_h - margin),
        PositionPreset.BOTTOM_RIGHT: (video_w - stamp_w - margin, video_h - stamp_h - margin),
    }
    return positions.get(preset, (0, 0))
```

---

## 確認事項
- [ ] テストが通ること
- [ ] 既存の StampLayer 機能に影響がないこと（後方互換性）
- [ ] opacity が 0.0〜1.0 の範囲でバリデーションされること
- [ ] position_preset と x, y の併用時の優先順位が明確であること

---

> **Note**: すべてのタスクが完了したら、このファイルを `tasks/completed/` ディレクトリに移動してください。

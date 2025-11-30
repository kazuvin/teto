# AnimationProcessor のリファクタリング - Strategy/Command パターンへの変更

## 概要
現在の `AnimationProcessor` は巨大な if-elif チェーンを使用しており、新しいエフェクトの追加や既存エフェクトの修正が困難です。Strategy パターンまたは Command パターンを導入して、各エフェクトを独立したクラスとして実装します。

## 現在の問題点

**場所**: `packages/core/teto_core/processors/animation.py:26-52`

```python
def apply_effects(clip, effects, video_size):
    for effect in effects:
        if effect.type == "fadein":
            clip = AnimationProcessor._apply_fadein(clip, effect)
        elif effect.type == "fadeout":
            clip = AnimationProcessor._apply_fadeout(clip, effect)
        elif effect.type == "slideIn":
            clip = AnimationProcessor._apply_slide_in(clip, effect, video_size)
        # ... 12個のエフェクトタイプをチェック
    return clip
```

### 問題
- 新しいエフェクト追加時に `AnimationProcessor` クラスを毎回修正が必要
- if-elif チェーンが長く、可読性が低い
- 各エフェクトの独立したテストが困難
- Open/Closed Principle に違反（拡張に開いていない）

## 目標設計

### Strategy パターンによる実装

```python
from abc import ABC, abstractmethod
from moviepy import VideoClip, ImageClip
from ..models.effects import AnimationEffect

class EffectStrategy(ABC):
    """エフェクト適用戦略の基底クラス"""

    @abstractmethod
    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """エフェクトを適用する

        Args:
            clip: 元のクリップ
            effect: エフェクト設定
            video_size: 動画サイズ

        Returns:
            エフェクトを適用したクリップ
        """
        pass


class FadeInEffect(EffectStrategy):
    """フェードインエフェクト"""

    def apply(self, clip, effect, video_size):
        easing_fn = self._get_easing_function(effect.easing)

        def fadein_frame(get_frame, t):
            frame = get_frame(t)
            if t > effect.duration:
                return frame
            # ... 既存のロジック

        return clip.transform(fadein_frame)

    @staticmethod
    def _get_easing_function(easing: str | None):
        # イージング関数の実装
        pass


class SlideInEffect(EffectStrategy):
    """スライドインエフェクト"""

    def apply(self, clip, effect, video_size):
        # ... 既存のロジック
        pass


class AnimationProcessor:
    """アニメーション処理を担当するプロセッサー"""

    # エフェクト戦略のレジストリ
    _effect_strategies: dict[str, EffectStrategy] = {
        "fadein": FadeInEffect(),
        "fadeout": FadeOutEffect(),
        "slideIn": SlideInEffect(),
        "slideOut": SlideOutEffect(),
        "zoom": ZoomEffect(),
        "kenBurns": KenBurnsEffect(),
        "blur": BlurEffect(),
        "colorGrade": ColorGradeEffect(),
        "vignette": VignetteEffect(),
        "glitch": GlitchEffect(),
        "parallax": ParallaxEffect(),
        "bounce": BounceEffect(),
        "rotate": RotateEffect(),
    }

    @classmethod
    def register_effect(cls, name: str, strategy: EffectStrategy) -> None:
        """カスタムエフェクトを登録

        Args:
            name: エフェクト名
            strategy: エフェクト戦略インスタンス
        """
        cls._effect_strategies[name] = strategy

    @staticmethod
    def apply_effects(
        clip: VideoClip | ImageClip,
        effects: list[AnimationEffect],
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """クリップにアニメーション効果を適用

        Args:
            clip: 元のクリップ
            effects: 適用する効果のリスト
            video_size: 動画サイズ

        Returns:
            効果を適用したクリップ
        """
        for effect in effects:
            strategy = AnimationProcessor._effect_strategies.get(effect.type)
            if strategy:
                clip = strategy.apply(clip, effect, video_size)
            else:
                print(f"Warning: Unknown effect type '{effect.type}'")

        return clip
```

## タスク詳細

### Phase 1: 基盤の作成
- [ ] `processors/effects/` ディレクトリを作成
- [ ] `processors/effects/base.py` に `EffectStrategy` 基底クラスを作成
- [ ] `processors/effects/__init__.py` でエクスポート設定

### Phase 2: エフェクトクラスの実装
各エフェクトを個別のファイルに分割:

- [ ] `processors/effects/fade.py` - `FadeInEffect`, `FadeOutEffect`
- [ ] `processors/effects/slide.py` - `SlideInEffect`, `SlideOutEffect`
- [ ] `processors/effects/zoom.py` - `ZoomEffect`, `KenBurnsEffect`
- [ ] `processors/effects/blur.py` - `BlurEffect`
- [ ] `processors/effects/color.py` - `ColorGradeEffect`, `VignetteEffect`
- [ ] `processors/effects/glitch.py` - `GlitchEffect`
- [ ] `processors/effects/motion.py` - `ParallaxEffect`, `BounceEffect`
- [ ] `processors/effects/rotate.py` - `RotateEffect`

### Phase 3: AnimationProcessor のリファクタリング
- [ ] `AnimationProcessor` を新しい設計に変更
- [ ] `_effect_strategies` レジストリの実装
- [ ] `register_effect()` メソッドの追加（プラグインサポート）
- [ ] 既存の static メソッドを削除

### Phase 4: ユーティリティの共通化
- [ ] `processors/effects/utils.py` を作成
- [ ] イージング関数を共通ユーティリティとして移動
- [ ] 各エフェクトで共通化できる処理を抽出

### Phase 5: テストとドキュメント
- [ ] 各エフェクトクラスの単体テストを作成
- [ ] カスタムエフェクトの追加方法をドキュメント化
- [ ] 既存のテストが引き続き動作することを確認

## 期待される効果

### メリット
1. **拡張性向上**: 新しいエフェクトの追加が容易（新しいクラスを作成して登録するだけ）
2. **テスタビリティ向上**: 各エフェクトを独立してテスト可能
3. **可読性向上**: if-elif チェーンの排除
4. **プラグインサポート**: `register_effect()` でユーザーがカスタムエフェクトを追加可能
5. **責任の分離**: 各エフェクトが独立したクラスとして実装される

### デメリット
1. ファイル数の増加（13個のエフェクト → 8個のファイル）
2. 若干のボイラープレートコード増加

## 検討事項
- イージング関数は全エフェクトで共通なので、基底クラスに実装するか、ユーティリティとして分離するか
- エフェクトパラメータのバリデーションを基底クラスで行うべきか
- 非同期エフェクト処理が必要になった場合の設計

## 参考
- Strategy パターン: 字幕レンダラー (`processors/subtitle_renderers.py`) が良い実装例
- Command パターンとの比較: undo/redo が不要なのでStrategy パターンが適切

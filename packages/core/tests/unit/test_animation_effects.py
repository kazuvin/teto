"""エフェクトシステムのテスト"""

import pytest
from teto_core.processors.effect import EffectProcessor, AnimationProcessor
from teto_core.processors.effect.strategies import (
    EffectStrategy,
    FadeInEffect,
    ZoomEffect,
)
from teto_core.models.effects import AnimationEffect


class TestEffectProcessor:
    """EffectProcessor のテスト"""

    def test_animation_processor_alias(self):
        """AnimationProcessor は EffectProcessor のエイリアスとして動作する"""
        assert AnimationProcessor is EffectProcessor
        # 後方互換性のため、同じクラスを指している
        assert AnimationProcessor.list_effects() == EffectProcessor.list_effects()

class TestEffectProcessorCore:
    """EffectProcessor のコア機能テスト"""

    def test_list_effects(self):
        """登録されているエフェクトのリストを取得できる"""
        effects = EffectProcessor.list_effects()
        assert isinstance(effects, list)
        assert len(effects) > 0
        assert "fadein" in effects
        assert "fadeout" in effects
        assert "zoom" in effects

    def test_register_custom_effect(self):
        """カスタムエフェクトを登録できる"""

        class CustomEffect(EffectStrategy):
            def apply(self, clip, effect, video_size):
                return clip

        # カスタムエフェクトを登録
        EffectProcessor.register_effect("custom_test", CustomEffect())

        # 登録されたことを確認
        effects = EffectProcessor.list_effects()
        assert "custom_test" in effects

        # クリーンアップ
        EffectProcessor.unregister_effect("custom_test")

    def test_unregister_effect(self):
        """エフェクトの登録を解除できる"""

        class TempEffect(EffectStrategy):
            def apply(self, clip, effect, video_size):
                return clip

        # 登録
        EffectProcessor.register_effect("temp_effect", TempEffect())
        assert "temp_effect" in EffectProcessor.list_effects()

        # 解除
        result = EffectProcessor.unregister_effect("temp_effect")
        assert result is True
        assert "temp_effect" not in EffectProcessor.list_effects()

    def test_unregister_nonexistent_effect(self):
        """存在しないエフェクトの解除は False を返す"""
        result = EffectProcessor.unregister_effect("nonexistent")
        assert result is False

    def test_apply_effects_skips_when_strategy_removed(self, capsys):
        """エフェクト戦略が削除された場合は警告を出力してスキップ"""
        # 注: AnimationEffect の type は Literal で定義されているため、
        # 既存のタイプのエフェクトを一時的に削除するケースをテスト

        # モックのクリップ
        class MockClip:
            pass

        # 既存のエフェクト（fadein）を一時的に削除
        original_fadein = EffectProcessor._effect_strategies.get("fadein")
        EffectProcessor.unregister_effect("fadein")

        # fadein エフェクトを適用しようとする
        clip = MockClip()
        effect = AnimationEffect(type="fadein", duration=1.0)
        result = EffectProcessor.apply_effects(clip, [effect], (1920, 1080))

        # 警告メッセージが出力されることを確認
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "fadein" in captured.out

        # 元に戻す
        if original_fadein:
            EffectProcessor.register_effect("fadein", original_fadein)

    def test_effect_strategies_are_registered(self):
        """すべてのデフォルトエフェクトが登録されている"""
        expected_effects = [
            "fadein",
            "fadeout",
            "slideIn",
            "slideOut",
            "zoom",
            "kenBurns",
            "blur",
            "colorGrade",
            "vignette",
            "glitch",
            "parallax",
            "bounce",
            "rotate",
        ]

        effects = EffectProcessor.list_effects()
        for effect in expected_effects:
            assert effect in effects, f"{effect} should be registered"


class TestEffectStrategies:
    """個別のエフェクト戦略のテスト"""

    def test_fade_in_effect_instance(self):
        """FadeInEffect のインスタンスを作成できる"""
        effect = FadeInEffect()
        assert isinstance(effect, EffectStrategy)

    def test_zoom_effect_instance(self):
        """ZoomEffect のインスタンスを作成できる"""
        effect = ZoomEffect()
        assert isinstance(effect, EffectStrategy)

    def test_effect_has_apply_method(self):
        """すべてのエフェクトは apply メソッドを持つ"""
        from teto_core.processors.effect.strategies import (
            FadeInEffect,
            FadeOutEffect,
            SlideInEffect,
            ZoomEffect,
        )

        effects = [
            FadeInEffect(),
            FadeOutEffect(),
            SlideInEffect(),
            ZoomEffect(),
        ]

        for effect in effects:
            assert hasattr(effect, "apply")
            assert callable(effect.apply)


class TestEasingFunctions:
    """イージング関数のテスト"""

    def test_get_easing_function_linear(self):
        """線形イージング関数"""
        from teto_core.processors.effect.utils import get_easing_function

        easing = get_easing_function("linear")
        assert easing(0.0) == 0.0
        assert easing(0.5) == 0.5
        assert easing(1.0) == 1.0

    def test_get_easing_function_ease_in(self):
        """イーズインイージング関数"""
        from teto_core.processors.effect.utils import get_easing_function

        easing = get_easing_function("easeIn")
        assert easing(0.0) == 0.0
        assert easing(0.5) == 0.25  # 0.5^2
        assert easing(1.0) == 1.0

    def test_get_easing_function_ease_out(self):
        """イーズアウトイージング関数"""
        from teto_core.processors.effect.utils import get_easing_function

        easing = get_easing_function("easeOut")
        assert easing(0.0) == 0.0
        assert easing(1.0) == 1.0

    def test_get_easing_function_ease_in_out(self):
        """イーズインアウトイージング関数"""
        from teto_core.processors.effect.utils import get_easing_function

        easing = get_easing_function("easeInOut")
        assert easing(0.0) == 0.0
        assert easing(1.0) == 1.0

    def test_get_easing_function_default_to_linear(self):
        """未知のイージングタイプは線形にフォールバック"""
        from teto_core.processors.effect.utils import get_easing_function

        easing = get_easing_function("unknown")
        assert easing(0.5) == 0.5


class TestAnimationEffectModel:
    """AnimationEffect モデルのテスト"""

    def test_animation_effect_creation_fadein(self):
        """フェードインエフェクトを作成できる"""
        effect = AnimationEffect(type="fadein", duration=1.0)
        assert effect.type == "fadein"
        assert effect.duration == 1.0

    def test_animation_effect_with_easing(self):
        """イージング付きエフェクトを作成できる"""
        effect = AnimationEffect(
            type="fadeout", duration=1.5, easing="easeInOut"
        )
        assert effect.type == "fadeout"
        assert effect.duration == 1.5
        assert effect.easing == "easeInOut"

    def test_animation_effect_slide_with_direction(self):
        """方向指定付きスライドエフェクト"""
        effect = AnimationEffect(
            type="slideIn", duration=1.0, direction="left"
        )
        assert effect.type == "slideIn"
        assert effect.direction == "left"

    def test_animation_effect_zoom_with_scales(self):
        """スケール指定付きズームエフェクト"""
        effect = AnimationEffect(
            type="zoom",
            duration=2.0,
            start_scale=1.0,
            end_scale=1.5
        )
        assert effect.type == "zoom"
        assert effect.start_scale == 1.0
        assert effect.end_scale == 1.5

    def test_animation_effect_ken_burns_with_pan(self):
        """パン指定付き Ken Burns エフェクト"""
        effect = AnimationEffect(
            type="kenBurns",
            duration=3.0,
            pan_start=(0.0, 0.0),
            pan_end=(0.1, 0.1)
        )
        assert effect.type == "kenBurns"
        assert effect.pan_start == (0.0, 0.0)
        assert effect.pan_end == (0.1, 0.1)

    def test_animation_effect_blur_with_amount(self):
        """ブラー量指定付きブラーエフェクト"""
        effect = AnimationEffect(
            type="blur",
            duration=1.0,
            blur_amount=5.0
        )
        assert effect.type == "blur"
        assert effect.blur_amount == 5.0

    def test_animation_effect_color_grade_with_params(self):
        """パラメータ指定付きカラーグレーディングエフェクト"""
        effect = AnimationEffect(
            type="colorGrade",
            duration=1.0,
            color_temp=0.2,
            saturation=1.2,
            contrast=1.1,
            brightness=1.0
        )
        assert effect.type == "colorGrade"
        assert effect.color_temp == 0.2
        assert effect.saturation == 1.2
        assert effect.contrast == 1.1
        assert effect.brightness == 1.0

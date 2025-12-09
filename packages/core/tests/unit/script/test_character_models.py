"""キャラクターモデルのテスト"""

import pytest
from teto_core.script.models import (
    CharacterDefinition,
    CharacterExpression,
    CharacterAnimation,
    CharacterAnimationType,
    CharacterPosition,
    CharacterState,
    SceneCharacterConfig,
    NarrationSegment,
    Scene,
    Script,
    Visual,
)


class TestCharacterExpression:
    """CharacterExpression のテスト"""

    def test_create_expression(self):
        """表情を作成できる"""
        expr = CharacterExpression(name="normal", path="assets/teto/normal.png")
        assert expr.name == "normal"
        assert expr.path == "assets/teto/normal.png"


class TestCharacterAnimation:
    """CharacterAnimation のテスト"""

    def test_default_animation(self):
        """デフォルトアニメーションを作成できる"""
        anim = CharacterAnimation()
        assert anim.type == CharacterAnimationType.NONE
        assert anim.intensity == 1.0
        assert anim.speed == 1.0

    def test_custom_animation(self):
        """カスタムアニメーションを作成できる"""
        anim = CharacterAnimation(
            type=CharacterAnimationType.BOUNCE,
            intensity=1.5,
            speed=0.8,
        )
        assert anim.type == CharacterAnimationType.BOUNCE
        assert anim.intensity == 1.5
        assert anim.speed == 0.8

    def test_animation_intensity_validation(self):
        """アニメーション強度のバリデーション"""
        with pytest.raises(ValueError):
            CharacterAnimation(intensity=0.1)  # 0.5 未満
        with pytest.raises(ValueError):
            CharacterAnimation(intensity=3.0)  # 2.0 より大きい


class TestCharacterDefinition:
    """CharacterDefinition のテスト"""

    def test_create_character(self):
        """キャラクターを作成できる"""
        char = CharacterDefinition(
            id="teto",
            name="テト",
            expressions=[
                CharacterExpression(name="normal", path="assets/teto/normal.png"),
                CharacterExpression(name="smile", path="assets/teto/smile.png"),
            ],
            default_expression="normal",
        )
        assert char.id == "teto"
        assert char.name == "テト"
        assert len(char.expressions) == 2
        assert char.default_expression == "normal"
        assert char.position == CharacterPosition.BOTTOM_RIGHT

    def test_default_expression_validation(self):
        """デフォルト表情が存在しない場合はエラー"""
        with pytest.raises(ValueError, match="default_expression"):
            CharacterDefinition(
                id="teto",
                name="テト",
                expressions=[
                    CharacterExpression(name="smile", path="assets/teto/smile.png"),
                ],
                default_expression="normal",  # 存在しない
            )

    def test_character_with_voice_profile(self):
        """voice_profile を指定できる"""
        char = CharacterDefinition(
            id="teto",
            name="テト",
            expressions=[
                CharacterExpression(name="normal", path="assets/teto/normal.png"),
            ],
            default_expression="normal",
            voice_profile="teto_voice",
        )
        assert char.voice_profile == "teto_voice"


class TestCharacterState:
    """CharacterState のテスト"""

    def test_create_state(self):
        """キャラクター状態を作成できる"""
        state = CharacterState(
            character_id="teto",
            expression="smile",
        )
        assert state.character_id == "teto"
        assert state.expression == "smile"
        assert state.visible is True

    def test_state_with_animation(self):
        """アニメーション付き状態を作成できる"""
        state = CharacterState(
            character_id="teto",
            expression="surprise",
            animation=CharacterAnimation(
                type=CharacterAnimationType.BOUNCE,
                intensity=1.5,
            ),
        )
        assert state.animation.type == CharacterAnimationType.BOUNCE


class TestSceneCharacterConfig:
    """SceneCharacterConfig のテスト"""

    def test_create_config(self):
        """シーンキャラクター設定を作成できる"""
        config = SceneCharacterConfig(character_id="teto")
        assert config.character_id == "teto"
        assert config.visible is True

    def test_config_with_overrides(self):
        """上書き設定を指定できる"""
        config = SceneCharacterConfig(
            character_id="teto",
            position=CharacterPosition.BOTTOM_LEFT,
            scale=0.8,
        )
        assert config.position == CharacterPosition.BOTTOM_LEFT
        assert config.scale == 0.8


class TestNarrationSegmentWithCharacter:
    """NarrationSegment のキャラクター状態テスト"""

    def test_segment_with_character_states(self):
        """キャラクター状態付きセグメントを作成できる"""
        segment = NarrationSegment(
            text="こんにちは",
            character_states=[
                CharacterState(character_id="teto", expression="smile"),
            ],
        )
        assert len(segment.character_states) == 1
        assert segment.character_states[0].character_id == "teto"


class TestSceneWithCharacter:
    """Scene のキャラクター設定テスト"""

    def test_scene_with_characters(self):
        """キャラクター付きシーンを作成できる"""
        scene = Scene(
            visual=Visual(path="bg.jpg"),
            characters=[
                SceneCharacterConfig(character_id="teto"),
            ],
            narrations=[
                NarrationSegment(
                    text="こんにちは",
                    character_states=[
                        CharacterState(character_id="teto", expression="smile"),
                    ],
                ),
            ],
        )
        assert len(scene.characters) == 1
        assert scene.characters[0].character_id == "teto"


class TestScriptWithCharacters:
    """Script のキャラクター定義テスト"""

    def test_script_with_characters(self):
        """キャラクター定義付きスクリプトを作成できる"""
        script = Script(
            title="テスト動画",
            characters={
                "teto": CharacterDefinition(
                    id="teto",
                    name="テト",
                    expressions=[
                        CharacterExpression(
                            name="normal", path="assets/teto/normal.png"
                        ),
                    ],
                    default_expression="normal",
                ),
            },
            scenes=[
                Scene(
                    visual=Visual(path="bg.jpg"),
                    characters=[
                        SceneCharacterConfig(character_id="teto"),
                    ],
                    narrations=[
                        NarrationSegment(text="こんにちは"),
                    ],
                ),
            ],
        )
        assert "teto" in script.characters
        assert script.characters["teto"].name == "テト"

    def test_script_without_characters(self):
        """キャラクターなしスクリプトも作成できる（後方互換性）"""
        script = Script(
            title="テスト動画",
            scenes=[
                Scene(
                    visual=Visual(path="bg.jpg"),
                    narrations=[
                        NarrationSegment(text="こんにちは"),
                    ],
                ),
            ],
        )
        assert script.characters is None

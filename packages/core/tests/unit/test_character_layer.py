"""CharacterLayer と CharacterLayerProcessor のテスト"""

from teto_core.layer.models import (
    CharacterLayer,
    CharacterPositionPreset,
    CharacterAnimationConfig,
    CharacterAnimationType,
)


class TestCharacterLayer:
    """CharacterLayer のテスト"""

    def test_create_character_layer(self):
        """キャラクターレイヤーを作成できる"""
        layer = CharacterLayer(
            character_id="teto",
            character_name="テト",
            expression="normal",
            path="assets/teto/normal.png",
            start_time=0.0,
            end_time=3.0,
        )
        assert layer.character_id == "teto"
        assert layer.character_name == "テト"
        assert layer.expression == "normal"
        assert layer.path == "assets/teto/normal.png"
        assert layer.start_time == 0.0
        assert layer.end_time == 3.0
        assert layer.position == CharacterPositionPreset.BOTTOM_RIGHT
        assert layer.scale == 1.0

    def test_character_layer_with_animation(self):
        """アニメーション付きレイヤーを作成できる"""
        layer = CharacterLayer(
            character_id="teto",
            character_name="テト",
            expression="smile",
            path="assets/teto/smile.png",
            start_time=0.0,
            end_time=3.0,
            animation=CharacterAnimationConfig(
                type=CharacterAnimationType.BOUNCE,
                intensity=1.5,
            ),
        )
        assert layer.animation.type == CharacterAnimationType.BOUNCE
        assert layer.animation.intensity == 1.5

    def test_character_layer_positions(self):
        """各配置位置を指定できる"""
        positions = [
            CharacterPositionPreset.BOTTOM_LEFT,
            CharacterPositionPreset.BOTTOM_RIGHT,
            CharacterPositionPreset.BOTTOM_CENTER,
            CharacterPositionPreset.LEFT,
            CharacterPositionPreset.RIGHT,
            CharacterPositionPreset.CENTER,
        ]
        for pos in positions:
            layer = CharacterLayer(
                character_id="teto",
                character_name="テト",
                expression="normal",
                path="assets/teto/normal.png",
                start_time=0.0,
                end_time=3.0,
                position=pos,
            )
            assert layer.position == pos

    def test_character_layer_custom_position(self):
        """カスタム位置を指定できる"""
        layer = CharacterLayer(
            character_id="teto",
            character_name="テト",
            expression="normal",
            path="assets/teto/normal.png",
            start_time=0.0,
            end_time=3.0,
            custom_position=(100, 200),
        )
        assert layer.custom_position == (100, 200)


class TestCharacterAnimationConfig:
    """CharacterAnimationConfig のテスト"""

    def test_animation_types(self):
        """全アニメーションタイプを作成できる"""
        types = [
            CharacterAnimationType.NONE,
            CharacterAnimationType.BOUNCE,
            CharacterAnimationType.SHAKE,
            CharacterAnimationType.NOD,
            CharacterAnimationType.SWAY,
            CharacterAnimationType.BREATHE,
            CharacterAnimationType.FLOAT,
            CharacterAnimationType.PULSE,
        ]
        for anim_type in types:
            config = CharacterAnimationConfig(type=anim_type)
            assert config.type == anim_type

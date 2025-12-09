"""Default composite preset library"""

from .base import SubtitleStyleConfig
from .composite import PresetConfig, PresetRegistry


# 循環インポートを避けるため、実行時にインポート
def _get_timing_config():
    from ..models import TimingConfig

    return TimingConfig


def _get_bgm_config():
    from ..models import BGMConfig

    return BGMConfig


# 遅延初期化を使用
_PRESETS_INITIALIZED = False


def _create_presets():
    """プリセットを作成（循環インポート回避のため遅延初期化）"""
    TimingConfig = _get_timing_config()

    # フック（動画の冒頭で視聴者の注意を引く）
    hook_preset = PresetConfig(
        effect="dramatic",  # 既存のdramaticプリセットを使用
        subtitle_style=SubtitleStyleConfig(
            font_size="xl",  # 大きめ
            font_weight="bold",
            appearance="drop-shadow",
        ),
        timing_override=TimingConfig(
            default_segment_gap=0.2,  # 速いテンポ
            subtitle_padding=0.05,
        ),
    )

    # 概要（トピックの全体像を説明）
    overview_preset = PresetConfig(
        effect="kenburns-zoom-in",  # Ken Burnsエフェクトを使用
        subtitle_style=SubtitleStyleConfig(
            font_size="lg",
            appearance="background",
        ),
        timing_override=TimingConfig(
            default_segment_gap=0.3,
        ),
    )

    # 本編（メインコンテンツ）
    main_content_preset = PresetConfig(
        effect="default",  # デフォルトプリセット（シンプル）
        subtitle_style=SubtitleStyleConfig(
            font_size="base",
            appearance="background",
        ),
    )

    # CTA（行動喚起、チャンネル登録など）
    cta_preset = PresetConfig(
        effect="dramatic",
        subtitle_style=SubtitleStyleConfig(
            font_size="xl",
            font_weight="bold",
            font_color="yellow",
            appearance="drop-shadow",
        ),
        timing_override=TimingConfig(
            default_segment_gap=0.4,
            subtitle_padding=0.1,
        ),
    )

    return {
        "hook": hook_preset,
        "overview": overview_preset,
        "main_content": main_content_preset,
        "cta": cta_preset,
    }


def register_default_composite_presets() -> None:
    """デフォルト複合プリセットを登録する

    このfunction は ScriptCompiler の初期化時に呼ばれる。
    """
    global _PRESETS_INITIALIZED
    if _PRESETS_INITIALIZED:
        return

    # Forward referenceを解決するため、modelsをインポートしてからrebuildする
    from ..models import TimingConfig, BGMConfig, VoiceConfig

    PresetConfig.model_rebuild(
        _types_namespace={
            "TimingConfig": TimingConfig,
            "BGMConfig": BGMConfig,
            "VoiceConfig": VoiceConfig,
        }
    )

    presets = _create_presets()
    for name, preset in presets.items():
        PresetRegistry.register(name, preset)

    _PRESETS_INITIALIZED = True

"""プロセッサーモジュール

動画、音声、字幕、エフェクトの各処理を担当するプロセッサークラス。
"""

from .base import ProcessorBase
from .video import (
    VideoLayerProcessor,
    ImageLayerProcessor,
    StampLayerProcessor,
    VideoProcessor,
)
from .audio import (
    AudioLayerProcessor,
    AudioProcessor,
)
from .subtitle import (
    SubtitleBurnProcessor,
    SubtitleExportProcessor,
)
from .effect import EffectProcessor
from .tts import GoogleTTSProcessor

__all__ = [
    # 基底クラス
    "ProcessorBase",
    # 動画処理
    "VideoLayerProcessor",
    "ImageLayerProcessor",
    "StampLayerProcessor",
    "VideoProcessor",
    # 音声処理
    "AudioLayerProcessor",
    "AudioProcessor",
    # 字幕処理
    "SubtitleBurnProcessor",
    "SubtitleExportProcessor",
    # エフェクト処理
    "EffectProcessor",
    # TTS処理
    "GoogleTTSProcessor",
]

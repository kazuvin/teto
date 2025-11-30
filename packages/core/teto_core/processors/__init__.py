"""プロセッサーモジュール

動画、音声、字幕、エフェクトの各処理を担当するプロセッサークラス。
"""

from .video import VideoProcessor
from .audio import AudioProcessor
from .subtitle import SubtitleProcessor
from .effect import EffectProcessor, AnimationProcessor

__all__ = [
    "VideoProcessor",
    "AudioProcessor",
    "SubtitleProcessor",
    "EffectProcessor",
    "AnimationProcessor",  # 後方互換性のため
]

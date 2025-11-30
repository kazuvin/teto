"""
Teto Core - Video generation core library
"""

__version__ = "0.1.0"

from .project.models import Project, Timeline
from .layer.models import (
    VideoLayer,
    ImageLayer,
    AudioLayer,
    SubtitleLayer,
    SubtitleItem,
    StampLayer,
)
from .output_config.models import OutputConfig
from .effect.models import AnimationEffect
from .tts.models import (
    GoogleTTSVoiceConfig,
    GoogleTTSAudioConfig,
    TTSRequest,
    TTSResult,
    TTSSegment,
)
from .project.builders import ProjectBuilder
from .layer.builders import (
    VideoLayerBuilder,
    ImageLayerBuilder,
    AudioLayerBuilder,
    SubtitleLayerBuilder,
    SubtitleItemBuilder,
    StampLayerBuilder,
)
from .tts.builders import TTSBuilder
from .video_generator import VideoGenerator

__all__ = [
    "Project",
    "Timeline",
    "VideoLayer",
    "ImageLayer",
    "AudioLayer",
    "SubtitleLayer",
    "SubtitleItem",
    "StampLayer",
    "OutputConfig",
    "AnimationEffect",
    "GoogleTTSVoiceConfig",
    "GoogleTTSAudioConfig",
    "TTSRequest",
    "TTSResult",
    "TTSSegment",
    "ProjectBuilder",
    "VideoLayerBuilder",
    "ImageLayerBuilder",
    "AudioLayerBuilder",
    "SubtitleLayerBuilder",
    "SubtitleItemBuilder",
    "StampLayerBuilder",
    "TTSBuilder",
    "VideoGenerator",
]

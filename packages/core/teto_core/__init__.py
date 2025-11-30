"""
Teto Core - Video generation core library
"""

__version__ = "0.1.0"

from .models import (
    Project,
    VideoLayer,
    ImageLayer,
    AudioLayer,
    SubtitleLayer,
    SubtitleItem,
    OutputConfig,
)
from .video_generator import VideoGenerator

__all__ = [
    "Project",
    "VideoLayer",
    "ImageLayer",
    "AudioLayer",
    "SubtitleLayer",
    "SubtitleItem",
    "OutputConfig",
    "VideoGenerator",
]

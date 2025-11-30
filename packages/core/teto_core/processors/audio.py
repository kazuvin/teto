"""音声処理プロセッサー"""

from pathlib import Path
from moviepy import AudioFileClip, CompositeAudioClip
from ..models.layers import AudioLayer
from .base import ProcessorBase


class AudioLayerProcessor(ProcessorBase[AudioLayer, AudioFileClip]):
    """音声レイヤー処理プロセッサー"""

    def validate(self, layer: AudioLayer, **kwargs) -> bool:
        """音声ファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Audio file not found: {layer.path}")
            return False
        return True

    def process(self, layer: AudioLayer, **kwargs) -> AudioFileClip:
        """音声レイヤーを読み込む"""
        clip = AudioFileClip(layer.path)

        # 音量調整
        if layer.volume != 1.0:
            clip = clip.with_volume_scaled(layer.volume)

        # 継続時間の調整
        if layer.duration is not None:
            clip = clip.subclipped(0, min(layer.duration, clip.duration))

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip


class AudioProcessor(ProcessorBase[list[AudioLayer], CompositeAudioClip | None]):
    """音声タイムライン処理プロセッサー"""

    def __init__(self, audio_processor: AudioLayerProcessor = None):
        self.audio_processor = audio_processor or AudioLayerProcessor()

    def validate(self, layers: list[AudioLayer], **kwargs) -> bool:
        """レイヤーリストのバリデーション"""
        # 空の場合も許可（Noneを返すため）
        return True

    def process(self, layers: list[AudioLayer], **kwargs) -> CompositeAudioClip | None:
        """音声レイヤーを処理して合成"""
        if not layers:
            return None

        audio_clips = [self.audio_processor.execute(layer) for layer in layers]

        # 複数の音声を合成
        if len(audio_clips) == 1:
            return audio_clips[0]
        else:
            return CompositeAudioClip(audio_clips)

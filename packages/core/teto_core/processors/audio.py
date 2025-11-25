"""音声処理プロセッサー"""

from moviepy import AudioFileClip, CompositeAudioClip
from ..models.layers import AudioLayer


class AudioProcessor:
    """音声処理を担当するプロセッサー"""

    @staticmethod
    def load_audio_layer(layer: AudioLayer) -> AudioFileClip:
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

    @staticmethod
    def process_audio_timeline(layers: list[AudioLayer]) -> CompositeAudioClip | None:
        """音声レイヤーを処理して合成"""
        if not layers:
            return None

        audio_clips = [AudioProcessor.load_audio_layer(layer) for layer in layers]

        # 複数の音声を合成
        if len(audio_clips) == 1:
            return audio_clips[0]
        else:
            return CompositeAudioClip(audio_clips)

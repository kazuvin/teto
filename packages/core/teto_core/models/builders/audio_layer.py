from ..layers import AudioLayer


class AudioLayerBuilder:
    """音声レイヤーのビルダー"""

    def __init__(self, path: str):
        self._path = path
        self._start_time = 0.0
        self._duration = None
        self._volume = 1.0

    def at(self, start_time: float) -> 'AudioLayerBuilder':
        """開始時間を設定"""
        self._start_time = start_time
        return self

    def for_duration(self, duration: float) -> 'AudioLayerBuilder':
        """継続時間を設定"""
        self._duration = duration
        return self

    def with_volume(self, volume: float) -> 'AudioLayerBuilder':
        """音量を設定"""
        self._volume = volume
        return self

    def build(self) -> AudioLayer:
        """AudioLayer を構築"""
        return AudioLayer(
            path=self._path,
            start_time=self._start_time,
            duration=self._duration,
            volume=self._volume,
        )

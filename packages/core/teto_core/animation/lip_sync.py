"""Lip sync engine for character animation"""

from abc import ABC, abstractmethod
from ..layer.models import MouthKeyframe
from ..script.models import LipSyncConfig, LipSyncMode


class LipSyncEngine(ABC):
    """リップシンクエンジンの抽象基底クラス"""

    @abstractmethod
    def generate_mouth_keyframes(
        self,
        audio_path: str,
        text: str,
        start_time: float,
        duration: float,
        config: LipSyncConfig,
    ) -> list[MouthKeyframe]:
        """口のキーフレームを生成

        Args:
            audio_path: 音声ファイルパス
            text: テキスト
            start_time: 開始時刻(秒)
            duration: 継続時間(秒)
            config: リップシンク設定

        Returns:
            口のキーフレームリスト
        """
        pass


class SimplePakuPakuEngine(LipSyncEngine):
    """シンプルなパクパク方式のリップシンクエンジン(MVP)

    音素解析を行わず、発話中に一定間隔で口を開閉する。
    """

    def generate_mouth_keyframes(
        self,
        audio_path: str,
        text: str,
        start_time: float,
        duration: float,
        config: LipSyncConfig,
    ) -> list[MouthKeyframe]:
        """口のキーフレームを生成

        Args:
            audio_path: 音声ファイルパス(未使用)
            text: テキスト(未使用)
            start_time: 開始時刻(秒)
            duration: 継続時間(秒)
            config: リップシンク設定

        Returns:
            口のキーフレームリスト
        """
        keyframes = []
        current_time = start_time
        is_open = False

        # 開始時は閉じ口
        keyframes.append(
            MouthKeyframe(
                time=current_time, shape=config.paku_closed_shape, opacity=1.0
            )
        )

        # パクパクアニメーション
        while current_time < start_time + duration:
            # 次のキーフレーム時刻
            current_time += config.paku_interval / 2

            if current_time >= start_time + duration:
                break

            # 開閉を交互に
            is_open = not is_open
            shape = config.paku_open_shape if is_open else config.paku_closed_shape

            keyframes.append(MouthKeyframe(time=current_time, shape=shape, opacity=1.0))

        # 終了時は閉じ口
        keyframes.append(
            MouthKeyframe(
                time=start_time + duration, shape=config.paku_closed_shape, opacity=1.0
            )
        )

        return keyframes


class AudioVolumeLipSyncEngine(LipSyncEngine):
    """音量ベースのリップシンクエンジン

    音声の音量を解析して、音量が閾値を超えたときに口を開く。
    simple_paku_pakuより自然で、音声に同期したリップシンクを実現。
    """

    def generate_mouth_keyframes(
        self,
        audio_path: str,
        text: str,
        start_time: float,
        duration: float,
        config: LipSyncConfig,
    ) -> list[MouthKeyframe]:
        """音量ベースで口のキーフレームを生成

        Args:
            audio_path: 音声ファイルパス
            text: テキスト(未使用)
            start_time: 開始時刻(秒)
            duration: 継続時間(秒)
            config: リップシンク設定

        Returns:
            口のキーフレームリスト
        """
        try:
            import librosa
            import numpy as np
        except ImportError:
            raise ImportError(
                "音量ベースのリップシンクにはlibrosaが必要です。"
                "pip install librosa でインストールしてください。"
            )

        # 音声を読み込み
        y, sr = librosa.load(audio_path, sr=None)

        # フレーム長を設定（秒 → サンプル数）
        frame_length = int(sr * config.volume_frame_length)
        hop_length = frame_length // 2  # 50%オーバーラップ

        # RMS（Root Mean Square）で音量を計算
        rms = librosa.feature.rms(
            y=y, frame_length=frame_length, hop_length=hop_length
        )[0]

        # スムージング
        if config.volume_smoothing:
            # 移動平均でスムージング
            window_size = 3
            rms = np.convolve(rms, np.ones(window_size) / window_size, mode="same")

        # 音量を0-1に正規化
        if rms.max() > 0:
            rms = rms / rms.max()

        # キーフレーム生成（パクパク処理付き）
        keyframes = []
        prev_is_open = False
        last_open_time = None
        paku_interval = config.paku_interval  # パクパク間隔

        for i, volume in enumerate(rms):
            frame_time = start_time + (i * hop_length / sr)

            # 継続時間を超えたら終了
            if frame_time >= start_time + duration:
                break

            # 閾値判定
            should_be_open = volume > config.volume_threshold

            # パクパク処理：音量が閾値を超えている間も定期的に閉じる
            if should_be_open:
                if last_open_time is None:
                    # 最初に開く
                    is_open = True
                    last_open_time = frame_time
                else:
                    # 前回開いてからの経過時間
                    elapsed = frame_time - last_open_time
                    # paku_intervalの半分で開閉を交互に
                    cycle_position = (elapsed % paku_interval) / paku_interval
                    is_open = cycle_position < 0.5  # 前半で開、後半で閉
            else:
                # 音量が小さいときは閉じる
                is_open = False
                last_open_time = None

            # 状態が変化したときだけキーフレームを追加
            if i == 0 or is_open != prev_is_open:
                shape = config.paku_open_shape if is_open else config.paku_closed_shape
                keyframes.append(
                    MouthKeyframe(time=frame_time, shape=shape, opacity=1.0)
                )
                prev_is_open = is_open

        # 開始キーフレームがない場合は追加
        if not keyframes or keyframes[0].time > start_time:
            keyframes.insert(
                0,
                MouthKeyframe(
                    time=start_time, shape=config.paku_closed_shape, opacity=1.0
                ),
            )

        # 終了キーフレームを追加
        end_time = start_time + duration
        if not keyframes or keyframes[-1].time < end_time:
            keyframes.append(
                MouthKeyframe(
                    time=end_time, shape=config.paku_closed_shape, opacity=1.0
                )
            )

        return keyframes


class PhonemeMappingEngine(LipSyncEngine):
    """音素マッピング方式のリップシンクエンジン(将来実装)

    音素情報に基づいて正確な口の形状を生成する。
    """

    def generate_mouth_keyframes(
        self,
        audio_path: str,
        text: str,
        start_time: float,
        duration: float,
        config: LipSyncConfig,
    ) -> list[MouthKeyframe]:
        """口のキーフレームを生成

        Args:
            audio_path: 音声ファイルパス
            text: テキスト
            start_time: 開始時刻(秒)
            duration: 継続時間(秒)
            config: リップシンク設定

        Returns:
            口のキーフレームリスト
        """
        # TODO: 将来実装
        # 1. 音素情報の抽出
        # 2. 音素→口の形状マッピング
        # 3. キーフレーム生成
        raise NotImplementedError(
            "音素マッピング方式は将来実装予定です。現在はsimple_paku_pakuモードを使用してください。"
        )


def create_lip_sync_engine(mode: LipSyncMode) -> LipSyncEngine:
    """リップシンクエンジンのファクトリー

    Args:
        mode: リップシンクモード

    Returns:
        リップシンクエンジンのインスタンス

    Raises:
        ValueError: 未対応のモードの場合
    """
    if mode == LipSyncMode.SIMPLE_PAKU_PAKU:
        return SimplePakuPakuEngine()
    elif mode == LipSyncMode.AUDIO_VOLUME:
        return AudioVolumeLipSyncEngine()
    elif mode == LipSyncMode.PHONEME_MAPPING:
        return PhonemeMappingEngine()
    elif mode == LipSyncMode.DISABLED:
        # リップシンク無効の場合は空のキーフレームを返すエンジン
        class DisabledEngine(LipSyncEngine):
            def generate_mouth_keyframes(
                self, audio_path, text, start_time, duration, config
            ):
                return []

        return DisabledEngine()
    else:
        raise ValueError(f"未対応のリップシンクモード: {mode}")

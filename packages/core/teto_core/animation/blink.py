"""Blink animation engine for character eyes"""

import random
from ..layer.models import EyeKeyframe, EyeState
from ..script.models import BlinkConfig


def generate_blink_keyframes(
    start_time: float,
    end_time: float,
    config: BlinkConfig,
    is_speaking: bool = False,
    seed: int | None = None,
    default_eye_state: EyeState = EyeState.OPEN,
) -> list[EyeKeyframe]:
    """瞬きキーフレームを生成

    Args:
        start_time: 開始時刻(秒)
        end_time: 終了時刻(秒)
        config: 瞬き設定
        is_speaking: 発話中かどうか
        seed: ランダムシード(再現性確保用)
        default_eye_state: デフォルトの目の状態（瞬きしていない時の状態）

    Returns:
        目のキーフレームリスト
    """
    if not config.enabled:
        # 瞬き無効の場合はデフォルト状態のまま
        return [
            EyeKeyframe(time=start_time, state=default_eye_state, opacity=1.0),
            EyeKeyframe(time=end_time, state=default_eye_state, opacity=1.0),
        ]

    # シード値が指定されている場合は設定
    if seed is not None:
        random.seed(seed)

    keyframes = []
    current_time = start_time

    # 開始時はデフォルト状態
    keyframes.append(EyeKeyframe(time=start_time, state=default_eye_state, opacity=1.0))

    while current_time < end_time:
        # 次の瞬きタイミングをランダムに決定
        interval = random.uniform(config.blink_interval_min, config.blink_interval_max)

        # 発話中は瞬き頻度を下げる
        if is_speaking and config.suppress_during_speech:
            interval *= 1.5

        next_blink = current_time + interval

        if next_blink >= end_time:
            break

        # 瞬き開始
        keyframes.append(
            EyeKeyframe(time=next_blink, state=EyeState.CLOSED, opacity=1.0)
        )

        # 瞬き終了(デフォルト状態に戻す)
        keyframes.append(
            EyeKeyframe(
                time=next_blink + config.blink_duration,
                state=default_eye_state,
                opacity=1.0,
            )
        )

        current_time = next_blink + config.blink_duration

    # 終了時はデフォルト状態
    keyframes.append(EyeKeyframe(time=end_time, state=default_eye_state, opacity=1.0))

    return keyframes

"""エフェクト用共通ユーティリティ"""

from typing import Callable


def get_easing_function(easing: str | None) -> Callable[[float], float]:
    """イージング関数を取得

    Args:
        easing: イージングタイプ ("linear", "easeIn", "easeOut", "easeInOut")

    Returns:
        イージング関数
    """
    if easing == "easeIn":
        return lambda t: t * t
    elif easing == "easeOut":
        return lambda t: t * (2 - t)
    elif easing == "easeInOut":
        return lambda t: t * t * (3 - 2 * t)
    else:  # linear
        return lambda t: t

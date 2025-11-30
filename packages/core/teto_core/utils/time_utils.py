"""時間フォーマット関連のユーティリティ関数"""


def format_srt_time(seconds: float) -> str:
    """秒をSRT形式のタイムコードに変換 (HH:MM:SS,mmm)

    Args:
        seconds: 秒数

    Returns:
        SRT形式のタイムコード

    Examples:
        >>> format_srt_time(3661.5)
        '01:01:01,500'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = round((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_vtt_time(seconds: float) -> str:
    """秒をVTT形式のタイムコードに変換 (HH:MM:SS.mmm)

    Args:
        seconds: 秒数

    Returns:
        VTT形式のタイムコード

    Examples:
        >>> format_vtt_time(3661.5)
        '01:01:01.500'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = round((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

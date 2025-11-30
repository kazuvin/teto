"""TTS ユーティリティモジュール"""

from .ssml import (
    wrap_ssml,
    add_break,
    emphasize,
    say_as,
    phoneme,
)
from .text_utils import normalize_text, split_long_text
from .security import (
    mask_credentials_path,
    sanitize_for_logging,
    SecureLogger,
)

__all__ = [
    # SSML
    "wrap_ssml",
    "add_break",
    "emphasize",
    "say_as",
    "phoneme",
    # Text utilities
    "normalize_text",
    "split_long_text",
    # Security
    "mask_credentials_path",
    "sanitize_for_logging",
    "SecureLogger",
]

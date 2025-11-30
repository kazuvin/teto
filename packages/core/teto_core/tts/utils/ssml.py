"""SSML (Speech Synthesis Markup Language) ヘルパー関数"""

from typing import Optional


def wrap_ssml(
    text: str,
    language: str = "ja-JP",
    pitch: Optional[float] = None,
    rate: Optional[float] = None,
) -> str:
    """テキストをSSMLでラップ

    Args:
        text: テキスト
        language: 言語コード
        pitch: ピッチ調整(セミトーン)
        rate: 話す速度

    Returns:
        SSML形式のテキスト
    """
    # prosodyタグの属性を構築
    prosody_attrs = []
    if pitch is not None:
        prosody_attrs.append(f'pitch="{pitch:+.1f}st"')
    if rate is not None:
        prosody_attrs.append(f'rate="{rate:.2f}"')

    if prosody_attrs:
        prosody_start = f'<prosody {" ".join(prosody_attrs)}>'
        prosody_end = "</prosody>"
        text = f"{prosody_start}{text}{prosody_end}"

    return f'<speak version="1.0" xml:lang="{language}">{text}</speak>'


def add_break(milliseconds: int = 500) -> str:
    """ポーズ(間)を追加するSSMLタグ

    Args:
        milliseconds: ポーズの長さ(ミリ秒)

    Returns:
        SSMLのbreakタグ
    """
    return f'<break time="{milliseconds}ms"/>'


def emphasize(text: str, level: str = "moderate") -> str:
    """テキストを強調するSSMLタグ

    Args:
        text: 強調するテキスト
        level: 強調レベル("strong", "moderate", "reduced")

    Returns:
        強調されたSSML
    """
    return f'<emphasis level="{level}">{text}</emphasis>'


def say_as(text: str, interpret_as: str) -> str:
    """テキストの解釈方法を指定

    Args:
        text: テキスト
        interpret_as: 解釈タイプ("cardinal", "ordinal", "date" など)

    Returns:
        say-asタグ付きSSML
    """
    return f'<say-as interpret-as="{interpret_as}">{text}</say-as>'


def phoneme(text: str, ph: str, alphabet: str = "ipa") -> str:
    """発音記号で読み方を指定

    Args:
        text: テキスト
        ph: 発音記号
        alphabet: 発音記号体系("ipa" or "x-sampa")

    Returns:
        phonemeタグ付きSSML
    """
    return f'<phoneme alphabet="{alphabet}" ph="{ph}">{text}</phoneme>'

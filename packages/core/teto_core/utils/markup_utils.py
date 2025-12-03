"""マークアップテキストのパース・処理ユーティリティ

字幕テキスト内のXMLライクなマークアップを解析し、
スタイル適用単位（スパン）に分割する。

例:
    "<A>こんにちは</A><B>世界</B>" -> [
        TextSpan(text="こんにちは", style_name="A"),
        TextSpan(text="世界", style_name="B")
    ]
"""

import re
from dataclasses import dataclass


@dataclass
class TextSpan:
    """テキストスパン（スタイル適用単位）"""

    text: str
    style_name: str | None = None  # None の場合はデフォルトスタイル


# マークアップパターン: <TagName>content</TagName>
# タグ名は英字またはアンダースコアで始まり、英数字・アンダースコア・ハイフンを含む
MARKUP_PATTERN = re.compile(r"<([A-Za-z_][A-Za-z0-9_-]*)>(.*?)</\1>", re.DOTALL)


def parse_styled_text(text: str) -> list[TextSpan]:
    """
    マークアップテキストをスパンのリストに変換

    Args:
        text: マークアップを含む可能性のあるテキスト

    Returns:
        TextSpanのリスト

    Examples:
        >>> parse_styled_text("<A>hello</A><B>world</B>")
        [TextSpan(text='hello', style_name='A'), TextSpan(text='world', style_name='B')]

        >>> parse_styled_text("plain text")
        [TextSpan(text='plain text', style_name=None)]

        >>> parse_styled_text("<emphasis>重要:</emphasis> 説明文")
        [TextSpan(text='重要:', style_name='emphasis'), TextSpan(text=' 説明文', style_name=None)]
    """
    spans: list[TextSpan] = []
    last_end = 0

    for match in MARKUP_PATTERN.finditer(text):
        # マークアップ前のプレーンテキスト
        if match.start() > last_end:
            plain_text = text[last_end : match.start()]
            if plain_text:
                spans.append(TextSpan(text=plain_text, style_name=None))

        # マークアップ内のテキスト
        style_name = match.group(1)
        content = match.group(2)
        if content:
            spans.append(TextSpan(text=content, style_name=style_name))

        last_end = match.end()

    # 残りのプレーンテキスト
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            spans.append(TextSpan(text=remaining, style_name=None))

    # マークアップがない場合は元のテキストを単一スパンとして返す
    if not spans:
        spans.append(TextSpan(text=text, style_name=None))

    return spans


def strip_markup(text: str) -> str:
    """
    マークアップを除去して素のテキストを返す

    音声生成など、プレーンテキストが必要な場面で使用する。

    Args:
        text: マークアップを含む可能性のあるテキスト

    Returns:
        マークアップを除去したプレーンテキスト

    Examples:
        >>> strip_markup("<A>hello</A><B>world</B>")
        'helloworld'

        >>> strip_markup("plain text")
        'plain text'

        >>> strip_markup("<emphasis>重要:</emphasis> 説明文")
        '重要: 説明文'
    """
    return MARKUP_PATTERN.sub(r"\2", text)


def has_markup(text: str) -> bool:
    """
    テキストにマークアップが含まれているかチェック

    Args:
        text: チェック対象のテキスト

    Returns:
        マークアップが含まれていればTrue

    Examples:
        >>> has_markup("<A>hello</A>")
        True

        >>> has_markup("plain text")
        False
    """
    return bool(MARKUP_PATTERN.search(text))

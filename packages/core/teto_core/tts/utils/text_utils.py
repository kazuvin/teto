"""テキスト処理ユーティリティ"""

import re


def normalize_text(text: str) -> str:
    """テキストを正規化

    Args:
        text: 元のテキスト

    Returns:
        正規化されたテキスト
    """
    # 全角スペース→半角
    text = text.replace("\u3000", " ")

    # 連続する空白を1つに
    text = re.sub(r"\s+", " ", text)

    # 前後の空白を削除
    text = text.strip()

    return text


def split_long_text(text: str, max_length: int = 5000) -> list[str]:
    """長いテキストを分割

    Args:
        text: 長いテキスト
        max_length: 最大文字数

    Returns:
        分割されたテキストのリスト
    """
    if len(text) <= max_length:
        return [text]

    segments = []
    current = ""

    # 文単位で分割(句点で区切る)
    sentences = re.split(r"([。．！？\n])", text)

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""

        if len(current) + len(sentence) + len(delimiter) > max_length:
            if current:
                segments.append(current.strip())
            current = sentence + delimiter
        else:
            current += sentence + delimiter

    if current:
        segments.append(current.strip())

    return segments

"""画像処理関連のユーティリティ関数"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ..core.constants import PUNCTUATION_CHARS, COLOR_MAP


def create_rounded_rectangle(
    size: tuple[int, int], radius: int, color: tuple[int, int, int], opacity: float
) -> np.ndarray:
    """角丸矩形の画像を作成

    Args:
        size: 画像サイズ (幅, 高さ)
        radius: 角丸の半径
        color: RGB色
        opacity: 不透明度 (0.0-1.0)

    Returns:
        RGBA画像のnumpy配列
    """
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [(0, 0), (size[0], size[1])], radius=radius, fill=(*color, int(opacity * 255))
    )

    return np.array(img)


def wrap_text_japanese_aware(
    text: str, font: ImageFont.FreeTypeFont, max_width: int
) -> str:
    """日本語対応のテキスト折り返し

    Args:
        text: 折り返すテキスト
        font: フォント
        max_width: 最大幅

    Returns:
        折り返されたテキスト（改行文字を含む）
    """
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    # 1行の幅をチェック
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    # 折り返しが不要な場合
    if text_width <= max_width:
        return text

    # 日本語が含まれるかチェック（簡易的に全角文字の有無で判定）
    has_japanese = any(ord(c) > 127 for c in text)

    if has_japanese:
        return _wrap_japanese_text(text, font, max_width, dummy_draw)
    else:
        return _wrap_english_text(text, font, max_width, dummy_draw)


def _wrap_japanese_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw
) -> str:
    """日本語テキストの折り返し処理"""
    lines = []
    current_line = ""

    # 句読点で分割候補を作る
    segments = []
    temp = ""

    for char in text:
        temp += char
        if char in PUNCTUATION_CHARS:
            segments.append(temp)
            temp = ""

    if temp:
        segments.append(temp)

    # 各セグメントを幅に収まるように処理
    for segment in segments:
        test_line = current_line + segment
        test_bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = test_bbox[2] - test_bbox[0]

        if test_width <= max_width:
            current_line = test_line
        else:
            # 現在の行を確定
            if current_line:
                lines.append(current_line)

            # セグメントを文字単位で分割
            current_line = ""
            for char in segment:
                test_line = current_line + char
                test_bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = test_bbox[2] - test_bbox[0]

                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


def _wrap_english_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw
) -> str:
    """英語テキストの折り返し処理"""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        test_bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = test_bbox[2] - test_bbox[0]

        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


def create_text_image_with_pil(
    text: str,
    font_path: str | None,
    font_size: int,
    color: str,
    max_width: int,
    font_weight: str = "normal",
    stroke_width: int = 0,
    stroke_color: str = "black",
    outer_stroke_width: int = 0,
    outer_stroke_color: str = "white",
    video_height: int = 1080,
    load_font_func=None,
) -> tuple[np.ndarray, tuple[int, int]]:
    """PILを使ってテキスト画像を作成し、正確なサイズを取得

    Args:
        text: テキスト
        font_path: フォントファイルパス
        font_size: フォントサイズ（ピクセル値）
        color: 色名
        max_width: 最大幅
        font_weight: フォントの太さ
        stroke_width: 縁取りの幅（ピクセル値）
        stroke_color: 縁取りの色
        outer_stroke_width: 外側縁取りの幅（ピクセル値）
        outer_stroke_color: 外側縁取りの色
        video_height: 動画の高さ（レスポンシブ定数計算用）
        load_font_func: フォント読み込み関数（指定しない場合はデフォルト）

    Returns:
        (画像のnumpy配列, (幅, 高さ))のタプル
    """
    # レスポンシブな定数を取得
    from .size_utils import get_responsive_constants
    constants = get_responsive_constants(video_height)

    # フォントを読み込み
    if load_font_func:
        font = load_font_func(font_path, font_size, font_weight)
    else:
        from .font_utils import load_font
        font = load_font(font_path, font_size, font_weight)

    # 色をRGBに変換
    from .color_utils import parse_color
    text_color = parse_color(color)
    stroke_color_rgb = parse_color(stroke_color)
    outer_stroke_color_rgb = parse_color(outer_stroke_color)

    # 日本語対応の折り返し処理
    wrapped_text = wrap_text_japanese_aware(text, font, max_width)

    # テキストのbounding boxを取得（正確なサイズ計算）
    # 縁取りがある場合は追加のスペースを確保（最大の縁取り幅を使用）
    max_stroke = max(stroke_width, outer_stroke_width)
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.multiline_textbbox(
        (0, 0), wrapped_text, font=font, spacing=constants["LINE_SPACING"], stroke_width=max_stroke
    )
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 実際の描画用の画像を作成（余白を含む、レスポンシブ）
    img_width = text_width + constants["TEXT_PADDING"] * 2
    img_height = text_height + constants["TEXT_PADDING"] * 2
    img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # テキスト描画位置
    text_position = (constants["TEXT_PADDING"] - bbox[0], constants["TEXT_PADDING"] - bbox[1])

    # 二重縁取りの場合は3層で描画
    if outer_stroke_width > 0:
        # 第1層: 外側縁取り（最も太い）
        draw.multiline_text(
            text_position,
            wrapped_text,
            font=font,
            fill=(*outer_stroke_color_rgb, 255),
            align="center",
            spacing=constants["LINE_SPACING"],
            stroke_width=outer_stroke_width,
            stroke_fill=(*outer_stroke_color_rgb, 255),
        )
        # 第2層: 内側縁取り
        if stroke_width > 0:
            draw.multiline_text(
                text_position,
                wrapped_text,
                font=font,
                fill=(*stroke_color_rgb, 255),
                align="center",
                spacing=constants["LINE_SPACING"],
                stroke_width=stroke_width,
                stroke_fill=(*stroke_color_rgb, 255),
            )
        # 第3層: テキスト本体
        draw.multiline_text(
            text_position,
            wrapped_text,
            font=font,
            fill=(*text_color, 255),
            align="center",
            spacing=constants["LINE_SPACING"],
            stroke_width=0,
            stroke_fill=None,
        )
    else:
        # 従来の単一縁取りまたは縁取りなし
        draw.multiline_text(
            text_position,
            wrapped_text,
            font=font,
            fill=(*text_color, 255),
            align="center",
            spacing=constants["LINE_SPACING"],
            stroke_width=stroke_width,
            stroke_fill=(*stroke_color_rgb, 255),
        )

    return np.array(img), (img_width, img_height)

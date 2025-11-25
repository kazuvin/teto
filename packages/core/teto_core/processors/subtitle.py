"""字幕処理プロセッサー"""

from pathlib import Path
from moviepy import VideoClip, TextClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from ..models.layers import SubtitleLayer, SubtitleItem


# カラーマッピングの定数
COLOR_MAP = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "gray": (128, 128, 128),
}

# 各種パラメータの定数
LINE_SPACING = 28  # 行間（ピクセル）
TEXT_PADDING = 10  # テキスト画像の余白
BG_PADDING_X = 20  # 背景の横パディング
BG_PADDING_Y = 20  # 背景の縦パディング
BG_RADIUS = 15  # 背景の角丸半径
MARGIN_BOTTOM = 60  # 下部マージン
MARGIN_TOP = 50  # 上部マージン
MAX_TEXT_WIDTH_OFFSET = 200  # テキスト最大幅のオフセット
PUNCTUATION_CHARS = "。！？、，"  # 日本語の句読点


class SubtitleProcessor:
    """字幕処理を担当するプロセッサー"""

    @staticmethod
    def _load_font(font_path: str | None, font_size: int) -> ImageFont.FreeTypeFont:
        """フォントを読み込む"""
        try:
            if font_path and Path(font_path).exists():
                return ImageFont.truetype(font_path, font_size)
            else:
                return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    @staticmethod
    def _find_system_font() -> str | None:
        """システムに応じた日本語フォントを探す"""
        import platform

        system = platform.system()
        font_paths = []

        if system == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/Library/Fonts/Arial Unicode.ttf",
            ]
        elif system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/yugothic.ttf",
                "C:/Windows/Fonts/msgothic.ttc",
            ]
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]

        for font_path in font_paths:
            if Path(font_path).exists():
                return font_path

        return None

    @staticmethod
    def create_rounded_rectangle(size: tuple[int, int], radius: int, color: tuple[int, int, int], opacity: float) -> np.ndarray:
        """角丸矩形の画像を作成"""
        # RGBA画像を作成
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 角丸矩形を描画
        draw.rounded_rectangle(
            [(0, 0), (size[0], size[1])],
            radius=radius,
            fill=(*color, int(opacity * 255))
        )

        return np.array(img)

    @staticmethod
    def wrap_text_japanese_aware(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
        """日本語対応のテキスト折り返し"""
        dummy_img = Image.new('RGBA', (1, 1))
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
            # 日本語の場合：意味の区切りで改行
            # 句読点での分割を優先
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
                # セグメント全体を試す
                test_line = current_line + segment
                test_bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
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
                        test_bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
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

        else:
            # 英語の場合：単語単位で改行
            words = text.split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
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

    @staticmethod
    def create_text_image_with_pil(text: str, font_path: str | None, font_size: int, color: str, max_width: int) -> tuple[np.ndarray, tuple[int, int]]:
        """PILを使ってテキスト画像を作成し、正確なサイズを取得"""
        # フォントを読み込み
        font = SubtitleProcessor._load_font(font_path, font_size)

        # 色をRGBに変換
        text_color = COLOR_MAP.get(color.lower(), (255, 255, 255))

        # 日本語対応の折り返し処理
        wrapped_text = SubtitleProcessor.wrap_text_japanese_aware(text, font, max_width)

        # テキストのbounding boxを取得（正確なサイズ計算）
        dummy_img = Image.new('RGBA', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=LINE_SPACING)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 実際の描画用の画像を作成（余白を含む）
        img_width = text_width + TEXT_PADDING * 2
        img_height = text_height + TEXT_PADDING * 2
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # テキストを描画（bbox[0], bbox[1]のオフセットを考慮）
        draw.multiline_text(
            (TEXT_PADDING - bbox[0], TEXT_PADDING - bbox[1]),
            wrapped_text,
            font=font,
            fill=(*text_color, 255),
            align='center',
            spacing=LINE_SPACING
        )

        return np.array(img), (img_width, img_height)

    @staticmethod
    def _parse_background_color(bg_color: str | None) -> tuple[tuple[int, int, int], float]:
        """背景色と不透明度をパースする

        Args:
            bg_color: 背景色の文字列 (例: "black@0.5")

        Returns:
            (RGB色, 不透明度)のタプル
        """
        if not bg_color:
            bg_color = "black@0.5"

        opacity = 0.5
        color_part = bg_color

        if "@" in bg_color:
            color_part, opacity_part = bg_color.split("@")
            opacity = float(opacity_part)

        color_rgb = COLOR_MAP.get(color_part.lower(), (0, 0, 0))
        return color_rgb, opacity

    @staticmethod
    def _calculate_position(layer: SubtitleLayer, clip_height: int, video_size: tuple[int, int]) -> tuple:
        """レイヤー設定に基づいてクリップの位置を計算する

        Args:
            layer: 字幕レイヤー
            clip_height: クリップの高さ
            video_size: 動画のサイズ (幅, 高さ)

        Returns:
            位置のタプル
        """
        if layer.position == "bottom":
            return ("center", video_size[1] - clip_height - MARGIN_BOTTOM)
        elif layer.position == "top":
            return ("center", MARGIN_TOP)
        else:  # center
            return ("center", "center")

    @staticmethod
    def _create_plain_subtitle_clip(
        item: SubtitleItem, layer: SubtitleLayer, video_size: tuple[int, int], font: str | None, duration: float
    ) -> VideoClip:
        """通常テキスト（背景なし）の字幕クリップを作成"""
        try:
            txt_clip = TextClip(
                text=item.text,
                font=font,
                font_size=layer.font_size,
                color=layer.font_color,
                size=(video_size[0] - MAX_TEXT_WIDTH_OFFSET, None),
                method="caption",
            )
        except Exception as e:
            # フォント指定でエラーが出た場合はデフォルトフォントで再試行
            print(f"Warning: Font error, using default font: {e}")
            txt_clip = TextClip(
                text=item.text,
                font_size=layer.font_size,
                color=layer.font_color,
                size=(video_size[0] - MAX_TEXT_WIDTH_OFFSET, None),
                method="caption",
            )

        position = SubtitleProcessor._calculate_position(layer, txt_clip.h, video_size)
        return txt_clip.with_position(position).with_start(item.start_time).with_duration(duration)

    @staticmethod
    def _create_rounded_bg_subtitle_clip(
        item: SubtitleItem, layer: SubtitleLayer, video_size: tuple[int, int], font: str | None, duration: float
    ) -> VideoClip:
        """角丸背景付きテキストの字幕クリップを作成"""
        max_width = video_size[0] - MAX_TEXT_WIDTH_OFFSET

        # PILを使ってテキスト画像を作成
        text_img, (text_width, text_height) = SubtitleProcessor.create_text_image_with_pil(
            text=item.text,
            font_path=font,
            font_size=layer.font_size,
            color=layer.font_color,
            max_width=max_width
        )

        # 背景色と透明度を取得
        color_rgb, opacity = SubtitleProcessor._parse_background_color(layer.bg_color)

        # パディングを追加した背景サイズ
        bg_width = text_width + BG_PADDING_X * 2
        bg_height = text_height + BG_PADDING_Y * 2

        # 角丸背景を作成
        bg_array = SubtitleProcessor.create_rounded_rectangle(
            size=(bg_width, bg_height),
            radius=BG_RADIUS,
            color=color_rgb,
            opacity=opacity
        )
        bg_clip = ImageClip(bg_array).with_duration(duration)

        # テキスト画像をImageClipに変換
        txt_clip = ImageClip(text_img).with_duration(duration)

        # テキストを背景内に配置（中央に配置）
        txt_clip = txt_clip.with_position((BG_PADDING_X, BG_PADDING_Y))

        # 背景とテキストを合成
        composite = CompositeVideoClip([bg_clip, txt_clip], size=(bg_width, bg_height))

        # 位置の計算
        position = SubtitleProcessor._calculate_position(layer, bg_height, video_size)
        return composite.with_position(position).with_start(item.start_time).with_duration(duration)

    @staticmethod
    def create_subtitle_clip(
        item: SubtitleItem, layer: SubtitleLayer, video_size: tuple[int, int]
    ) -> VideoClip:
        """字幕アイテムからテキストクリップを作成"""
        duration = item.end_time - item.start_time

        # 日本語対応フォントを指定
        font = SubtitleProcessor._find_system_font()

        # variantに基づいて処理を分岐
        if layer.variant == "plain":
            return SubtitleProcessor._create_plain_subtitle_clip(item, layer, video_size, font, duration)
        elif layer.variant == "rounded_bg":
            return SubtitleProcessor._create_rounded_bg_subtitle_clip(item, layer, video_size, font, duration)
        else:
            # デフォルトはplainとして扱う
            return SubtitleProcessor._create_plain_subtitle_clip(item, layer, video_size, font, duration)

    @staticmethod
    def burn_subtitles(
        video: VideoClip, subtitle_layers: list[SubtitleLayer]
    ) -> VideoClip:
        """動画に字幕を焼き込む"""
        if not subtitle_layers:
            return video

        subtitle_clips = []

        for layer in subtitle_layers:
            for item in layer.items:
                try:
                    clip = SubtitleProcessor.create_subtitle_clip(
                        item, layer, (video.w, video.h)
                    )
                    subtitle_clips.append(clip)
                except Exception as e:
                    print(f"Warning: Failed to create subtitle clip: {e}")
                    continue

        if subtitle_clips:
            return CompositeVideoClip([video] + subtitle_clips)
        else:
            return video

    @staticmethod
    def export_srt(subtitle_layers: list[SubtitleLayer], output_path: str) -> None:
        """SRT形式で字幕をエクスポート"""
        if not subtitle_layers:
            return

        with open(output_path, "w", encoding="utf-8") as f:
            index = 1
            for layer in subtitle_layers:
                for item in layer.items:
                    # SRT形式: インデックス、タイムコード、テキスト
                    start = SubtitleProcessor._format_srt_time(item.start_time)
                    end = SubtitleProcessor._format_srt_time(item.end_time)

                    f.write(f"{index}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{item.text}\n\n")

                    index += 1

    @staticmethod
    def export_vtt(subtitle_layers: list[SubtitleLayer], output_path: str) -> None:
        """VTT形式で字幕をエクスポート"""
        if not subtitle_layers:
            return

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")

            for layer in subtitle_layers:
                for item in layer.items:
                    # VTT形式: タイムコード、テキスト
                    start = SubtitleProcessor._format_vtt_time(item.start_time)
                    end = SubtitleProcessor._format_vtt_time(item.end_time)

                    f.write(f"{start} --> {end}\n")
                    f.write(f"{item.text}\n\n")

    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        """秒をSRT形式のタイムコードに変換 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _format_vtt_time(seconds: float) -> str:
        """秒をVTT形式のタイムコードに変換 (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

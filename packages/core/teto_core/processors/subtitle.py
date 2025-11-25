"""字幕処理プロセッサー"""

from pathlib import Path
from moviepy import VideoClip, TextClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from ..models.layers import SubtitleLayer, SubtitleItem


class SubtitleProcessor:
    """字幕処理を担当するプロセッサー"""

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
    def create_text_image_with_pil(text: str, font_path: str | None, font_size: int, color: str, max_width: int) -> tuple[np.ndarray, tuple[int, int]]:
        """PILを使ってテキスト画像を作成し、正確なサイズを取得"""
        # フォントを読み込み
        try:
            if font_path and Path(font_path).exists():
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # 色をRGBに変換
        color_map = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "gray": (128, 128, 128),
        }
        text_color = color_map.get(color.lower(), (255, 255, 255))

        # テキストのbounding boxを取得（正確なサイズ計算）
        dummy_img = Image.new('RGBA', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)

        # getbboxを使って正確なテキストサイズを取得
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # テキストが長すぎる場合は改行
        if text_width > max_width:
            # 簡易的な改行処理
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

            # 複数行のテキストのサイズを計算
            max_line_width = 0
            total_height = 0
            for line in lines:
                line_bbox = dummy_draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                line_height = line_bbox[3] - line_bbox[1]
                max_line_width = max(max_line_width, line_width)
                total_height += line_height

            text_width = max_line_width
            text_height = total_height
            text = "\n".join(lines)

            # 改行を含むテキストの正確なbboxを再取得
            bbox = dummy_draw.multiline_textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

        # 実際の描画用の画像を作成（余白を含む）
        padding = 10  # 少し余白を持たせる
        img_width = text_width + padding * 2
        img_height = text_height + padding * 2
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # テキストを描画（bbox[0], bbox[1]のオフセットを考慮）
        draw.multiline_text(
            (padding - bbox[0], padding - bbox[1]),
            text,
            font=font,
            fill=(*text_color, 255),
            align='center'
        )

        return np.array(img), (img_width, img_height)

    @staticmethod
    def create_subtitle_clip(
        item: SubtitleItem, layer: SubtitleLayer, video_size: tuple[int, int]
    ) -> VideoClip:
        """字幕アイテムからテキストクリップを作成"""
        duration = item.end_time - item.start_time

        # 日本語対応フォントを指定
        import platform
        from pathlib import Path

        font = None
        system = platform.system()

        # システムごとにフォントパスを探す
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

        # 存在するフォントを探す
        for font_path in font_paths:
            if Path(font_path).exists():
                font = font_path
                break

        # variantに基づいて処理を分岐
        if layer.variant == "plain":
            # 通常テキスト（背景なし）
            try:
                txt_clip = TextClip(
                    text=item.text,
                    font=font,
                    font_size=layer.font_size,
                    color=layer.font_color,
                    size=(video_size[0] - 200, None),
                    method="caption",
                )
            except Exception as e:
                # フォント指定でエラーが出た場合はデフォルトフォントで再試行
                print(f"Warning: Font error, using default font: {e}")
                txt_clip = TextClip(
                    text=item.text,
                    font_size=layer.font_size,
                    color=layer.font_color,
                    size=(video_size[0] - 200, None),
                    method="caption",
                )

            # 位置の計算
            if layer.position == "bottom":
                position = ("center", video_size[1] - txt_clip.h - 60)
            elif layer.position == "top":
                position = ("center", 50)
            else:  # center
                position = ("center", "center")

            txt_clip = txt_clip.with_position(position).with_start(item.start_time).with_duration(duration)
            return txt_clip

        elif layer.variant == "rounded_bg":
            # 角丸背景付きテキスト（PILを使って正確に描画）
            max_width = video_size[0] - 200

            # PILを使ってテキスト画像を作成
            text_img, (text_width, text_height) = SubtitleProcessor.create_text_image_with_pil(
                text=item.text,
                font_path=font,
                font_size=layer.font_size,
                color=layer.font_color,
                max_width=max_width
            )

            # 背景色と透明度を取得
            bg_color = layer.bg_color or "black@0.5"
            opacity = 0.5
            color_rgb = (0, 0, 0)  # デフォルトは黒

            if "@" in bg_color:
                color_part, opacity_part = bg_color.split("@")
                opacity = float(opacity_part)
            else:
                color_part = bg_color

            # 色名をRGBに変換
            color_map = {
                "black": (0, 0, 0),
                "white": (255, 255, 255),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "yellow": (255, 255, 0),
                "gray": (128, 128, 128),
            }
            color_rgb = color_map.get(color_part.lower(), (0, 0, 0))

            # パディングを追加した背景サイズ
            padding_x = 20
            padding_y = 20
            bg_width = text_width + padding_x * 2
            bg_height = text_height + padding_y * 2

            # 角丸背景を作成
            bg_array = SubtitleProcessor.create_rounded_rectangle(
                size=(bg_width, bg_height),
                radius=15,
                color=color_rgb,
                opacity=opacity
            )
            bg_clip = ImageClip(bg_array).with_duration(duration)

            # テキスト画像をImageClipに変換
            txt_clip = ImageClip(text_img).with_duration(duration)

            # テキストを背景内に配置（中央に配置）
            text_x = padding_x
            text_y = padding_y
            txt_clip = txt_clip.with_position((text_x, text_y))

            # 背景とテキストを合成
            composite = CompositeVideoClip([bg_clip, txt_clip], size=(bg_width, bg_height))

            # 位置の計算
            if layer.position == "bottom":
                position = ("center", video_size[1] - bg_height - 60)
            elif layer.position == "top":
                position = ("center", 50)
            else:  # center
                position = ("center", "center")

            composite = composite.with_position(position).with_start(item.start_time).with_duration(duration)
            return composite

        # デフォルト（後方互換性のため）
        return txt_clip

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

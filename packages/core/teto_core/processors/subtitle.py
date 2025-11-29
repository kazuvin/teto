"""字幕処理プロセッサー"""

from pathlib import Path
from moviepy import VideoClip, CompositeVideoClip, ImageClip
from ..models.layers import SubtitleLayer, SubtitleItem
from ..utils.color_utils import parse_background_color
from ..utils.font_utils import find_system_font
from ..utils.image_utils import create_rounded_rectangle, create_text_image_with_pil
from ..utils.time_utils import format_srt_time, format_vtt_time
from ..utils.size_utils import get_responsive_constants, calculate_font_size, calculate_stroke_width


class SubtitleProcessor:
    """字幕処理を担当するプロセッサー"""

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
        # レスポンシブな定数を取得
        constants = get_responsive_constants(video_size[1])

        if layer.position == "bottom":
            return ("center", video_size[1] - clip_height - constants["MARGIN_BOTTOM"])
        elif layer.position == "top":
            return ("center", constants["MARGIN_TOP"])
        else:  # center
            return ("center", "center")

    @staticmethod
    def _create_plain_subtitle_clip(
        item: SubtitleItem, layer: SubtitleLayer, video_size: tuple[int, int], font: str | None, duration: float
    ) -> VideoClip:
        """通常テキスト（背景なし）の字幕クリップを作成"""
        # レスポンシブな定数を取得
        constants = get_responsive_constants(video_size[1])
        max_width = video_size[0] - constants["MAX_TEXT_WIDTH_OFFSET"]

        # レスポンシブサイズを計算
        font_size = calculate_font_size(layer.font_size, video_size[1])
        stroke_width = calculate_stroke_width(layer.stroke_width, video_size[1])
        outer_stroke_width = calculate_stroke_width(layer.outer_stroke_width, video_size[1])

        # PILを使ってテキスト画像を作成
        text_img, (text_width, text_height) = create_text_image_with_pil(
            text=item.text,
            font_path=font,
            font_size=font_size,
            color=layer.font_color,
            max_width=max_width,
            font_weight=layer.font_weight,
            stroke_width=stroke_width,
            stroke_color=layer.stroke_color,
            outer_stroke_width=outer_stroke_width,
            outer_stroke_color=layer.outer_stroke_color,
            video_height=video_size[1]
        )

        # テキスト画像をImageClipに変換
        txt_clip = ImageClip(text_img).with_duration(duration)

        # 位置の計算
        position = SubtitleProcessor._calculate_position(layer, text_height, video_size)
        return txt_clip.with_position(position).with_start(item.start_time).with_duration(duration)

    @staticmethod
    def _create_background_subtitle_clip(
        item: SubtitleItem, layer: SubtitleLayer, video_size: tuple[int, int], font: str | None, duration: float
    ) -> VideoClip:
        """角丸背景付きテキストの字幕クリップを作成"""
        # レスポンシブな定数を取得
        constants = get_responsive_constants(video_size[1])
        max_width = video_size[0] - constants["MAX_TEXT_WIDTH_OFFSET"]

        # レスポンシブサイズを計算
        font_size = calculate_font_size(layer.font_size, video_size[1])
        stroke_width = calculate_stroke_width(layer.stroke_width, video_size[1])
        outer_stroke_width = calculate_stroke_width(layer.outer_stroke_width, video_size[1])

        # PILを使ってテキスト画像を作成
        text_img, (text_width, text_height) = create_text_image_with_pil(
            text=item.text,
            font_path=font,
            font_size=font_size,
            color=layer.font_color,
            max_width=max_width,
            font_weight=layer.font_weight,
            stroke_width=stroke_width,
            stroke_color=layer.stroke_color,
            outer_stroke_width=outer_stroke_width,
            outer_stroke_color=layer.outer_stroke_color,
            video_height=video_size[1]
        )

        # 背景色と透明度を取得
        color_rgb, opacity = parse_background_color(layer.bg_color)

        # パディングを追加した背景サイズ（レスポンシブ）
        bg_width = text_width + constants["BG_PADDING_X"] * 2
        bg_height = text_height + constants["BG_PADDING_Y"] * 2

        # 角丸背景を作成（レスポンシブ）
        bg_array = create_rounded_rectangle(
            size=(bg_width, bg_height),
            radius=constants["BG_RADIUS"],
            color=color_rgb,
            opacity=opacity
        )
        bg_clip = ImageClip(bg_array).with_duration(duration)

        # テキスト画像をImageClipに変換
        txt_clip = ImageClip(text_img).with_duration(duration)

        # テキストを背景内に配置（中央に配置、レスポンシブ）
        txt_clip = txt_clip.with_position((constants["BG_PADDING_X"], constants["BG_PADDING_Y"]))

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

        # フォントを決定（font_familyが指定されていればそれを使用、なければシステムフォント）
        font = layer.font_family if layer.font_family else find_system_font(layer.font_weight)

        # appearanceに基づいて処理を分岐
        if layer.appearance == "plain":
            return SubtitleProcessor._create_plain_subtitle_clip(item, layer, video_size, font, duration)
        elif layer.appearance == "background":
            return SubtitleProcessor._create_background_subtitle_clip(item, layer, video_size, font, duration)
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
                    start = format_srt_time(item.start_time)
                    end = format_srt_time(item.end_time)

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
                    start = format_vtt_time(item.start_time)
                    end = format_vtt_time(item.end_time)

                    f.write(f"{start} --> {end}\n")
                    f.write(f"{item.text}\n\n")

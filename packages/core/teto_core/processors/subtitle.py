"""字幕処理プロセッサー"""

from pathlib import Path
from moviepy import VideoClip, TextClip, CompositeVideoClip
from ..models.layers import SubtitleLayer, SubtitleItem


class SubtitleProcessor:
    """字幕処理を担当するプロセッサー"""

    @staticmethod
    def create_subtitle_clip(
        item: SubtitleItem, layer: SubtitleLayer, video_size: tuple[int, int]
    ) -> TextClip:
        """字幕アイテムからテキストクリップを作成"""
        duration = item.end_time - item.start_time

        # 背景色と透明度を分離
        bg_color = layer.bg_color
        opacity = 1.0
        if bg_color and "@" in bg_color:
            # "black@0.6" のような形式をパース
            color_part, opacity_part = bg_color.split("@")
            bg_color = color_part
            opacity = float(opacity_part)

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

        # テキストクリップを作成
        try:
            txt_clip = TextClip(
                text=item.text,
                font=font,
                font_size=layer.font_size,
                color=layer.font_color,
                bg_color=bg_color,
                size=(video_size[0] - 200, None),  # 左右に余白（100→200に増加）
                method="caption",
            )
        except Exception as e:
            # フォント指定でエラーが出た場合はデフォルトフォントで再試行
            print(f"Warning: Font error, using default font: {e}")
            txt_clip = TextClip(
                text=item.text,
                font_size=layer.font_size,
                color=layer.font_color,
                bg_color=bg_color,
                size=(video_size[0] - 200, None),
                method="caption",
            )

        # 透明度を適用
        if opacity < 1.0:
            txt_clip = txt_clip.with_opacity(opacity)

        # 位置の計算（テキストクリップのサイズを考慮）
        if layer.position == "bottom":
            # 下から150ピクセルの位置に配置（見切れ防止）
            position = ("center", video_size[1] - txt_clip.h - 150)
        elif layer.position == "top":
            position = ("center", 50)
        else:  # center
            position = ("center", "center")

        txt_clip = txt_clip.with_position(position).with_start(item.start_time).with_duration(duration)

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

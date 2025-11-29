"""字幕スタイルレンダラー（Strategy パターン）"""

from abc import ABC, abstractmethod
from moviepy import VideoClip, ImageClip, CompositeVideoClip
from ..models.layers import SubtitleLayer, SubtitleItem
from ..utils.color_utils import parse_background_color
from ..utils.image_utils import create_rounded_rectangle, create_text_image_with_pil
from ..utils.size_utils import get_responsive_constants, calculate_font_size, calculate_stroke_width


class SubtitleStyleRenderer(ABC):
    """字幕スタイルレンダラーの基底クラス"""

    @abstractmethod
    def render(
        self,
        item: SubtitleItem,
        layer: SubtitleLayer,
        video_size: tuple[int, int],
        font_path: str | None,
        duration: float,
    ) -> tuple[VideoClip, int]:
        """字幕クリップをレンダリングする

        Args:
            item: 字幕アイテム
            layer: 字幕レイヤー
            video_size: 動画のサイズ (幅, 高さ)
            font_path: フォントファイルのパス
            duration: 表示時間

        Returns:
            (VideoClip, クリップの高さ) のタプル
        """
        pass

    def _prepare_rendering_params(
        self, layer: SubtitleLayer, video_size: tuple[int, int]
    ) -> dict:
        """レンダリングに必要なパラメータを準備する

        Args:
            layer: 字幕レイヤー
            video_size: 動画のサイズ (幅, 高さ)

        Returns:
            レンダリングパラメータの辞書
        """
        # レスポンシブな定数を取得
        constants = get_responsive_constants(video_size[1])
        max_width = video_size[0] - constants["MAX_TEXT_WIDTH_OFFSET"]

        # レスポンシブサイズを計算
        font_size = calculate_font_size(layer.font_size, video_size[1])
        stroke_width = calculate_stroke_width(layer.stroke_width, video_size[1])
        outer_stroke_width = calculate_stroke_width(layer.outer_stroke_width, video_size[1])

        return {
            "constants": constants,
            "max_width": max_width,
            "font_size": font_size,
            "stroke_width": stroke_width,
            "outer_stroke_width": outer_stroke_width,
        }

    def _create_text_image(
        self,
        item: SubtitleItem,
        layer: SubtitleLayer,
        font_path: str | None,
        params: dict,
        video_size: tuple[int, int],
    ) -> tuple:
        """テキスト画像を作成する

        Args:
            item: 字幕アイテム
            layer: 字幕レイヤー
            font_path: フォントファイルのパス
            params: レンダリングパラメータ
            video_size: 動画のサイズ (幅, 高さ)

        Returns:
            (text_img, (text_width, text_height)) のタプル
        """
        return create_text_image_with_pil(
            text=item.text,
            font_path=font_path,
            font_size=params["font_size"],
            color=layer.font_color,
            max_width=params["max_width"],
            font_weight=layer.font_weight,
            stroke_width=params["stroke_width"],
            stroke_color=layer.stroke_color,
            outer_stroke_width=params["outer_stroke_width"],
            outer_stroke_color=layer.outer_stroke_color,
            video_height=video_size[1],
        )


class PlainStyleRenderer(SubtitleStyleRenderer):
    """通常テキスト（背景なし）のレンダラー"""

    def render(
        self,
        item: SubtitleItem,
        layer: SubtitleLayer,
        video_size: tuple[int, int],
        font_path: str | None,
        duration: float,
    ) -> tuple[VideoClip, int]:
        """通常テキスト（背景なし）の字幕クリップを作成"""
        # レンダリングパラメータを準備
        params = self._prepare_rendering_params(layer, video_size)

        # PILを使ってテキスト画像を作成
        text_img, (text_width, text_height) = self._create_text_image(
            item, layer, font_path, params, video_size
        )

        # テキスト画像をImageClipに変換
        txt_clip = ImageClip(text_img).with_duration(duration)

        return txt_clip, text_height


class BackgroundStyleRenderer(SubtitleStyleRenderer):
    """角丸背景付きテキストのレンダラー"""

    def render(
        self,
        item: SubtitleItem,
        layer: SubtitleLayer,
        video_size: tuple[int, int],
        font_path: str | None,
        duration: float,
    ) -> tuple[VideoClip, int]:
        """角丸背景付きテキストの字幕クリップを作成"""
        # レンダリングパラメータを準備
        params = self._prepare_rendering_params(layer, video_size)

        # PILを使ってテキスト画像を作成
        text_img, (text_width, text_height) = self._create_text_image(
            item, layer, font_path, params, video_size
        )

        # 背景色と透明度を取得
        color_rgb, opacity = parse_background_color(layer.bg_color)

        # パディングを追加した背景サイズ（レスポンシブ）
        constants = params["constants"]
        bg_width = text_width + constants["BG_PADDING_X"] * 2
        bg_height = text_height + constants["BG_PADDING_Y"] * 2

        # 角丸背景を作成（レスポンシブ）
        bg_array = create_rounded_rectangle(
            size=(bg_width, bg_height),
            radius=constants["BG_RADIUS"],
            color=color_rgb,
            opacity=opacity,
        )
        bg_clip = ImageClip(bg_array).with_duration(duration)

        # テキスト画像をImageClipに変換
        txt_clip = ImageClip(text_img).with_duration(duration)

        # テキストを背景内に配置（中央に配置、レスポンシブ）
        txt_clip = txt_clip.with_position((constants["BG_PADDING_X"], constants["BG_PADDING_Y"]))

        # 背景とテキストを合成
        composite = CompositeVideoClip([bg_clip, txt_clip], size=(bg_width, bg_height))

        return composite, bg_height


# 将来の拡張用のサンプル
# class ShadowStyleRenderer(SubtitleStyleRenderer):
#     """シャドウ付きテキストのレンダラー"""
#     def render(self, item, layer, video_size, font_path, duration):
#         # シャドウエフェクトの実装
#         pass
#
# class ThreeDStyleRenderer(SubtitleStyleRenderer):
#     """3Dエフェクト付きテキストのレンダラー"""
#     def render(self, item, layer, video_size, font_path, duration):
#         # 3Dエフェクトの実装
#         pass

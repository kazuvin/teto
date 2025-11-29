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


class ShadowStyleRenderer(SubtitleStyleRenderer):
    """シャドウ付きテキストのレンダラー"""

    def render(
        self,
        item: SubtitleItem,
        layer: SubtitleLayer,
        video_size: tuple[int, int],
        font_path: str | None,
        duration: float,
    ) -> tuple[VideoClip, int]:
        """シャドウ付きテキストの字幕クリップを作成"""
        # レンダリングパラメータを準備
        params = self._prepare_rendering_params(layer, video_size)
        constants = params["constants"]

        # PILを使ってテキスト画像を作成
        text_img, (text_width, text_height) = self._create_text_image(
            item, layer, font_path, params, video_size
        )

        # シャドウのオフセット（レスポンシブ）
        shadow_offset_x = constants.get("SHADOW_OFFSET_X", int(video_size[1] * 0.003))
        shadow_offset_y = constants.get("SHADOW_OFFSET_Y", int(video_size[1] * 0.003))

        # シャドウ用のテキスト画像を作成（黒で半透明）
        shadow_img, _ = self._create_text_image(
            item, layer, font_path, params, video_size
        )

        # 合成サイズを計算（テキスト + シャドウのオフセット分）
        composite_width = text_width + abs(shadow_offset_x)
        composite_height = text_height + abs(shadow_offset_y)

        # シャドウクリップを作成（黒で半透明に）
        import numpy as np
        shadow_array = np.array(shadow_img)
        # 透明度を調整（アルファチャンネルを50%に）
        if shadow_array.shape[2] == 4:  # RGBA
            shadow_array[:, :, 3] = (shadow_array[:, :, 3] * 0.5).astype(np.uint8)
            # RGBを黒に変更（アルファ値が0でない部分のみ）
            mask = shadow_array[:, :, 3] > 0
            shadow_array[mask, 0:3] = [0, 0, 0]

        shadow_clip = ImageClip(shadow_array).with_duration(duration)
        shadow_clip = shadow_clip.with_position((shadow_offset_x, shadow_offset_y))

        # テキスト画像をImageClipに変換
        txt_clip = ImageClip(text_img).with_duration(duration)
        txt_clip = txt_clip.with_position((0, 0))

        # シャドウとテキストを合成
        composite = CompositeVideoClip(
            [shadow_clip, txt_clip], size=(composite_width, composite_height)
        )

        return composite, composite_height


class DropShadowStyleRenderer(SubtitleStyleRenderer):
    """ドロップシャドウ付きテキストのレンダラー（filter: drop-shadow風のぼかし効果）"""

    def render(
        self,
        item: SubtitleItem,
        layer: SubtitleLayer,
        video_size: tuple[int, int],
        font_path: str | None,
        duration: float,
    ) -> tuple[VideoClip, int]:
        """ドロップシャドウ付きテキストの字幕クリップを作成"""
        # レンダリングパラメータを準備
        params = self._prepare_rendering_params(layer, video_size)
        constants = params["constants"]

        # PILを使ってテキスト画像を作成
        text_img, (text_width, text_height) = self._create_text_image(
            item, layer, font_path, params, video_size
        )

        # シャドウのオフセット（デフォルトは0、0でぼかしのみ）
        shadow_offset_x = constants.get("SHADOW_OFFSET_X", 0)
        shadow_offset_y = constants.get("SHADOW_OFFSET_Y", 0)

        # ぼかし半径（0.75remに相当する値を計算、1rem ≈ 16pxとして）
        blur_radius = int(video_size[1] * 0.75 / 100)  # 動画高さの0.75%程度
        blur_radius = max(blur_radius, 3)  # 最小値を3pxに設定

        # シャドウ用のテキスト画像を作成（黒で半透明）
        shadow_img, _ = self._create_text_image(
            item, layer, font_path, params, video_size
        )

        # ぼかしを適用するためのパディング
        blur_padding = blur_radius * 2

        # 合成サイズを計算（テキスト + シャドウのオフセット + ぼかし分）
        composite_width = text_width + abs(shadow_offset_x) + blur_padding * 2
        composite_height = text_height + abs(shadow_offset_y) + blur_padding * 2

        # シャドウクリップを作成（黒で半透明に）
        import numpy as np
        from PIL import Image, ImageFilter

        shadow_array = np.array(shadow_img)
        # 透明度を調整（アルファチャンネルを50%に）
        if shadow_array.shape[2] == 4:  # RGBA
            shadow_array[:, :, 3] = (shadow_array[:, :, 3] * 0.5).astype(np.uint8)
            # RGBを黒に変更（アルファ値が0でない部分のみ）
            mask = shadow_array[:, :, 3] > 0
            shadow_array[mask, 0:3] = [0, 0, 0]

        # PIL Imageに変換してGaussianブラーを適用
        shadow_pil = Image.fromarray(shadow_array, 'RGBA')
        shadow_pil = shadow_pil.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # NumPy配列に戻す
        shadow_blurred = np.array(shadow_pil)

        shadow_clip = ImageClip(shadow_blurred).with_duration(duration)
        shadow_clip = shadow_clip.with_position((shadow_offset_x + blur_padding, shadow_offset_y + blur_padding))

        # テキスト画像をImageClipに変換
        txt_clip = ImageClip(text_img).with_duration(duration)
        txt_clip = txt_clip.with_position((blur_padding, blur_padding))

        # シャドウとテキストを合成
        composite = CompositeVideoClip(
            [shadow_clip, txt_clip], size=(composite_width, composite_height)
        )

        return composite, composite_height


# 将来の拡張用のサンプル
# class ThreeDStyleRenderer(SubtitleStyleRenderer):
#     """3Dエフェクト付きテキストのレンダラー"""
#     def render(self, item, layer, video_size, font_path, duration):
#         # 3Dエフェクトの実装
#         pass

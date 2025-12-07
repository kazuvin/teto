"""Resize with padding tests"""

import numpy as np
from moviepy import ImageClip
from teto_core.layer.processors.video import resize_with_padding


class TestResizeWithPadding:
    """resize_with_padding tests"""

    def test_landscape_to_portrait(self):
        """横長画像を縦長に変換（アスペクト比保持）"""
        # 横長画像（16:9）
        clip = ImageClip(np.zeros((1080, 1920, 3), dtype=np.uint8), duration=1.0)

        # 縦長フォーマット（9:16）に変換
        result = resize_with_padding(clip, (1080, 1920))

        # 出力サイズが正しいこと
        assert result.size == (1080, 1920)

        # 元のアスペクト比が保持されていること（黒い余白が上下にある）
        # 元の16:9が横幅1080に収まる場合、高さは1080/16*9=607.5
        # 上下に余白ができる

    def test_portrait_to_landscape(self):
        """縦長画像を横長に変換（アスペクト比保持）"""
        # 縦長画像（9:16）
        clip = ImageClip(np.zeros((1920, 1080, 3), dtype=np.uint8), duration=1.0)

        # 横長フォーマット（16:9）に変換
        result = resize_with_padding(clip, (1920, 1080))

        # 出力サイズが正しいこと
        assert result.size == (1920, 1080)

    def test_square_to_portrait(self):
        """正方形画像を縦長に変換"""
        # 正方形画像（1:1）
        clip = ImageClip(np.zeros((1080, 1080, 3), dtype=np.uint8), duration=1.0)

        # 縦長フォーマット（9:16）に変換
        result = resize_with_padding(clip, (1080, 1920))

        # 出力サイズが正しいこと
        assert result.size == (1080, 1920)

    def test_square_to_landscape(self):
        """正方形画像を横長に変換"""
        # 正方形画像（1:1）
        clip = ImageClip(np.zeros((1080, 1080, 3), dtype=np.uint8), duration=1.0)

        # 横長フォーマット（16:9）に変換
        result = resize_with_padding(clip, (1920, 1080))

        # 出力サイズが正しいこと
        assert result.size == (1920, 1080)

    def test_same_aspect_ratio(self):
        """同じアスペクト比の場合"""
        # 16:9画像
        clip = ImageClip(np.zeros((1080, 1920, 3), dtype=np.uint8), duration=1.0)

        # 16:9フォーマットに変換
        result = resize_with_padding(clip, (1920, 1080))

        # 出力サイズが正しいこと
        assert result.size == (1920, 1080)

    def test_preserves_duration(self):
        """継続時間が保持されること"""
        clip = ImageClip(np.zeros((1080, 1920, 3), dtype=np.uint8), duration=5.0)

        result = resize_with_padding(clip, (1080, 1920))

        # 継続時間が保持されること
        assert result.duration == 5.0

    def test_custom_bg_color(self):
        """背景色を指定できること"""
        clip = ImageClip(np.zeros((1080, 1920, 3), dtype=np.uint8), duration=1.0)

        # 白い背景
        result = resize_with_padding(clip, (1080, 1920), bg_color=(255, 255, 255))

        # サイズが正しいこと
        assert result.size == (1080, 1920)

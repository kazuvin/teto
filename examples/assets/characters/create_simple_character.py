#!/usr/bin/env python3
"""簡易キャラクター素材生成スクリプト

実際のイラストがない場合に、動作確認用の簡易的なキャラクター素材を生成します。
シンプルな図形を使用してパーツを作成します。
"""

from PIL import Image, ImageDraw
import os


def create_base_part(size: int = 512) -> Image.Image:
    """ベースパーツ(顔の輪郭・体)を生成"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 顔の輪郭(円)
    face_center = (size // 2, size // 2 - size // 8)
    face_radius = size // 3
    draw.ellipse(
        [
            face_center[0] - face_radius,
            face_center[1] - face_radius,
            face_center[0] + face_radius,
            face_center[1] + face_radius,
        ],
        fill=(255, 220, 177, 255),  # 肌色
        outline=(0, 0, 0, 255),
        width=3,
    )

    # 体(台形)
    body_top_y = face_center[1] + face_radius
    body_points = [
        (size // 2 - size // 6, body_top_y),  # 左上
        (size // 2 + size // 6, body_top_y),  # 右上
        (size // 2 + size // 4, size - size // 8),  # 右下
        (size // 2 - size // 4, size - size // 8),  # 左下
    ]
    draw.polygon(body_points, fill=(100, 150, 255, 255), outline=(0, 0, 0, 255))

    return img


def create_eyes_open(size: int = 512) -> Image.Image:
    """開いた目パーツを生成（通常の眉毛込み）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目
    left_eye_x = face_center[0] - eye_spacing
    draw.ellipse(
        [left_eye_x - 20, eye_y - 15, left_eye_x + 20, eye_y + 15],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [left_eye_x - 8, eye_y - 8, left_eye_x + 8, eye_y + 8],
        fill=(0, 0, 0, 255),
    )
    # 左眉毛（通常）
    draw.arc(
        [left_eye_x - 25, eye_y - 35, left_eye_x + 25, eye_y - 20],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    # 右目
    right_eye_x = face_center[0] + eye_spacing
    draw.ellipse(
        [right_eye_x - 20, eye_y - 15, right_eye_x + 20, eye_y + 15],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [right_eye_x - 8, eye_y - 8, right_eye_x + 8, eye_y + 8],
        fill=(0, 0, 0, 255),
    )
    # 右眉毛（通常）
    draw.arc(
        [right_eye_x - 25, eye_y - 35, right_eye_x + 25, eye_y - 20],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    return img


def create_eyes_closed(size: int = 512) -> Image.Image:
    """閉じた目パーツを生成（通常の眉毛込み）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目(線)
    left_eye_x = face_center[0] - eye_spacing
    draw.arc(
        [left_eye_x - 20, eye_y - 15, left_eye_x + 20, eye_y + 15],
        start=0,
        end=180,
        fill=(0, 0, 0, 255),
        width=3,
    )
    # 左眉毛（通常）
    draw.arc(
        [left_eye_x - 25, eye_y - 35, left_eye_x + 25, eye_y - 20],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    # 右目(線)
    right_eye_x = face_center[0] + eye_spacing
    draw.arc(
        [right_eye_x - 20, eye_y - 15, right_eye_x + 20, eye_y + 15],
        start=0,
        end=180,
        fill=(0, 0, 0, 255),
        width=3,
    )
    # 右眉毛（通常）
    draw.arc(
        [right_eye_x - 25, eye_y - 35, right_eye_x + 25, eye_y - 20],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    return img


def create_eyes_smile(size: int = 512) -> Image.Image:
    """笑顔の目パーツを生成（上がった眉毛込み）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目(^の形)
    left_eye_x = face_center[0] - eye_spacing
    draw.arc(
        [left_eye_x - 20, eye_y - 5, left_eye_x + 20, eye_y + 25],
        start=180,
        end=0,
        fill=(0, 0, 0, 255),
        width=3,
    )
    # 左眉毛（笑顔・上がった形）
    draw.arc(
        [left_eye_x - 25, eye_y - 40, left_eye_x + 25, eye_y - 25],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    # 右目(^の形)
    right_eye_x = face_center[0] + eye_spacing
    draw.arc(
        [right_eye_x - 20, eye_y - 5, right_eye_x + 20, eye_y + 25],
        start=180,
        end=0,
        fill=(0, 0, 0, 255),
        width=3,
    )
    # 右眉毛（笑顔・上がった形）
    draw.arc(
        [right_eye_x - 25, eye_y - 40, right_eye_x + 25, eye_y - 25],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    return img


def create_eyes_serious(size: int = 512) -> Image.Image:
    """真剣な目パーツを生成（下がった眉毛込み）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目（やや細め）
    left_eye_x = face_center[0] - eye_spacing
    draw.ellipse(
        [left_eye_x - 20, eye_y - 12, left_eye_x + 20, eye_y + 12],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [left_eye_x - 8, eye_y - 8, left_eye_x + 8, eye_y + 8],
        fill=(0, 0, 0, 255),
    )
    # 左眉毛（真剣・下がった形）
    draw.line(
        [left_eye_x - 28, eye_y - 25, left_eye_x + 28, eye_y - 30],
        fill=(50, 50, 50, 255),
        width=4,
    )

    # 右目（やや細め）
    right_eye_x = face_center[0] + eye_spacing
    draw.ellipse(
        [right_eye_x - 20, eye_y - 12, right_eye_x + 20, eye_y + 12],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [right_eye_x - 8, eye_y - 8, right_eye_x + 8, eye_y + 8],
        fill=(0, 0, 0, 255),
    )
    # 右眉毛（真剣・下がった形）
    draw.line(
        [right_eye_x - 28, eye_y - 30, right_eye_x + 28, eye_y - 25],
        fill=(50, 50, 50, 255),
        width=4,
    )

    return img


def create_eyes_surprised(size: int = 512) -> Image.Image:
    """驚いた目パーツを生成（上がった眉毛込み）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目（大きめ）
    left_eye_x = face_center[0] - eye_spacing
    draw.ellipse(
        [left_eye_x - 22, eye_y - 18, left_eye_x + 22, eye_y + 18],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [left_eye_x - 10, eye_y - 10, left_eye_x + 10, eye_y + 10],
        fill=(0, 0, 0, 255),
    )
    # 左眉毛（驚き・高く上がった形）
    draw.arc(
        [left_eye_x - 25, eye_y - 50, left_eye_x + 25, eye_y - 35],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    # 右目（大きめ）
    right_eye_x = face_center[0] + eye_spacing
    draw.ellipse(
        [right_eye_x - 22, eye_y - 18, right_eye_x + 22, eye_y + 18],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [right_eye_x - 10, eye_y - 10, right_eye_x + 10, eye_y + 10],
        fill=(0, 0, 0, 255),
    )
    # 右眉毛（驚き・高く上がった形）
    draw.arc(
        [right_eye_x - 25, eye_y - 50, right_eye_x + 25, eye_y - 35],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    return img


def create_eyes_worried(size: int = 512) -> Image.Image:
    """困った目パーツを生成（困り眉込み）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目（やや細め）
    left_eye_x = face_center[0] - eye_spacing
    draw.ellipse(
        [left_eye_x - 18, eye_y - 13, left_eye_x + 18, eye_y + 13],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [left_eye_x - 7, eye_y - 7, left_eye_x + 7, eye_y + 7],
        fill=(0, 0, 0, 255),
    )
    # 左眉毛（困り・ハの字）
    draw.line(
        [left_eye_x - 25, eye_y - 30, left_eye_x, eye_y - 25],
        fill=(50, 50, 50, 255),
        width=3,
    )
    draw.line(
        [left_eye_x, eye_y - 25, left_eye_x + 25, eye_y - 30],
        fill=(50, 50, 50, 255),
        width=3,
    )

    # 右目（やや細め）
    right_eye_x = face_center[0] + eye_spacing
    draw.ellipse(
        [right_eye_x - 18, eye_y - 13, right_eye_x + 18, eye_y + 13],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [right_eye_x - 7, eye_y - 7, right_eye_x + 7, eye_y + 7],
        fill=(0, 0, 0, 255),
    )
    # 右眉毛（困り・ハの字）
    draw.line(
        [right_eye_x - 25, eye_y - 30, right_eye_x, eye_y - 25],
        fill=(50, 50, 50, 255),
        width=3,
    )
    draw.line(
        [right_eye_x, eye_y - 25, right_eye_x + 25, eye_y - 30],
        fill=(50, 50, 50, 255),
        width=3,
    )

    return img


def create_eyes_angry(size: int = 512) -> Image.Image:
    """怒った目パーツを生成（怒り眉込み）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目（細め、釣り目）
    left_eye_x = face_center[0] - eye_spacing
    draw.ellipse(
        [left_eye_x - 18, eye_y - 10, left_eye_x + 18, eye_y + 10],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [left_eye_x - 7, eye_y - 7, left_eye_x + 7, eye_y + 7],
        fill=(0, 0, 0, 255),
    )
    # 左眉毛（怒り・逆ハの字）
    draw.line(
        [left_eye_x - 28, eye_y - 22, left_eye_x + 28, eye_y - 28],
        fill=(50, 50, 50, 255),
        width=4,
    )

    # 右目（細め、釣り目）
    right_eye_x = face_center[0] + eye_spacing
    draw.ellipse(
        [right_eye_x - 18, eye_y - 10, right_eye_x + 18, eye_y + 10],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [right_eye_x - 7, eye_y - 7, right_eye_x + 7, eye_y + 7],
        fill=(0, 0, 0, 255),
    )
    # 右眉毛（怒り・逆ハの字）
    draw.line(
        [right_eye_x - 28, eye_y - 28, right_eye_x + 28, eye_y - 22],
        fill=(50, 50, 50, 255),
        width=4,
    )

    return img


def create_eyes_wink(size: int = 512) -> Image.Image:
    """ウィンク目パーツを生成（片目閉じ）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目（閉じ）
    left_eye_x = face_center[0] - eye_spacing
    draw.arc(
        [left_eye_x - 20, eye_y - 5, left_eye_x + 20, eye_y + 25],
        start=180,
        end=0,
        fill=(0, 0, 0, 255),
        width=3,
    )
    # 左眉毛（笑顔）
    draw.arc(
        [left_eye_x - 25, eye_y - 40, left_eye_x + 25, eye_y - 25],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    # 右目（開いている）
    right_eye_x = face_center[0] + eye_spacing
    draw.ellipse(
        [right_eye_x - 20, eye_y - 15, right_eye_x + 20, eye_y + 15],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [right_eye_x - 8, eye_y - 8, right_eye_x + 8, eye_y + 8],
        fill=(0, 0, 0, 255),
    )
    # 右眉毛（通常）
    draw.arc(
        [right_eye_x - 25, eye_y - 35, right_eye_x + 25, eye_y - 20],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    return img


def create_eyes_thinking(size: int = 512) -> Image.Image:
    """考え中の目パーツを生成（片眉上げ）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    eye_y = face_center[1] - size // 16
    eye_spacing = size // 8

    # 左目
    left_eye_x = face_center[0] - eye_spacing
    draw.ellipse(
        [left_eye_x - 20, eye_y - 15, left_eye_x + 20, eye_y + 15],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [left_eye_x - 8, eye_y - 8, left_eye_x + 8, eye_y + 8],
        fill=(0, 0, 0, 255),
    )
    # 左眉毛（上がっている）
    draw.arc(
        [left_eye_x - 25, eye_y - 42, left_eye_x + 25, eye_y - 27],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    # 右目
    right_eye_x = face_center[0] + eye_spacing
    draw.ellipse(
        [right_eye_x - 20, eye_y - 15, right_eye_x + 20, eye_y + 15],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )
    draw.ellipse(
        [right_eye_x - 8, eye_y - 8, right_eye_x + 8, eye_y + 8],
        fill=(0, 0, 0, 255),
    )
    # 右眉毛（通常）
    draw.arc(
        [right_eye_x - 25, eye_y - 35, right_eye_x + 25, eye_y - 20],
        start=180,
        end=0,
        fill=(50, 50, 50, 255),
        width=3,
    )

    return img


def create_mouth_closed(size: int = 512) -> Image.Image:
    """閉じた口パーツを生成"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    mouth_y = face_center[1] + size // 8

    # 口(線)
    draw.line(
        [size // 2 - 30, mouth_y, size // 2 + 30, mouth_y],
        fill=(0, 0, 0, 255),
        width=3,
    )

    return img


def create_mouth_open(size: int = 512) -> Image.Image:
    """開いた口パーツを生成"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    mouth_y = face_center[1] + size // 8

    # 口(楕円)
    draw.ellipse(
        [size // 2 - 25, mouth_y - 15, size // 2 + 25, mouth_y + 15],
        fill=(255, 100, 100, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )

    return img


def create_hair(size: int = 512) -> Image.Image:
    """髪パーツを生成"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_center = (size // 2, size // 2 - size // 8)
    face_radius = size // 3

    # 前髪(半円)
    hair_top = face_center[1] - face_radius
    draw.pieslice(
        [
            face_center[0] - face_radius - 10,
            hair_top - 30,
            face_center[0] + face_radius + 10,
            hair_top + face_radius,
        ],
        start=180,
        end=360,
        fill=(50, 50, 150, 255),  # 青い髪
        outline=(0, 0, 0, 255),
    )

    return img


def main():
    """メイン処理"""
    output_dir = os.path.join(os.path.dirname(__file__), "teto")
    os.makedirs(output_dir, exist_ok=True)

    print("簡易キャラクター素材を生成中...")

    # 各パーツを生成
    parts = {
        "base.png": create_base_part(),
        "eyes_open.png": create_eyes_open(),
        "eyes_closed.png": create_eyes_closed(),
        "eyes_smile.png": create_eyes_smile(),
        "eyes_serious.png": create_eyes_serious(),
        "eyes_surprised.png": create_eyes_surprised(),
        "eyes_worried.png": create_eyes_worried(),
        "eyes_angry.png": create_eyes_angry(),
        "eyes_wink.png": create_eyes_wink(),
        "eyes_thinking.png": create_eyes_thinking(),
        "mouth_closed.png": create_mouth_closed(),
        "mouth_open.png": create_mouth_open(),
        "hair.png": create_hair(),
    }

    # 保存
    for filename, image in parts.items():
        filepath = os.path.join(output_dir, filename)
        image.save(filepath)
        print(f"✓ {filename} を生成しました")

    # プレビュー画像も生成
    preview = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    preview.paste(parts["base.png"], (0, 0), parts["base.png"])
    preview.paste(parts["eyes_open.png"], (0, 0), parts["eyes_open.png"])
    preview.paste(parts["mouth_closed.png"], (0, 0), parts["mouth_closed.png"])
    preview.paste(parts["hair.png"], (0, 0), parts["hair.png"])
    preview_path = os.path.join(output_dir, "preview.png")
    preview.save(preview_path)
    print(f"✓ preview.png を生成しました")

    print(f"\n素材の生成が完了しました!")
    print(f"出力先: {output_dir}")
    print(f"\nプレビュー: {preview_path}")


if __name__ == "__main__":
    main()

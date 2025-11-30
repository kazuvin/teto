#!/usr/bin/env python3
"""Builder パターンを使用したサンプルプロジェクト"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core"))

from teto_core.models import ProjectBuilder


def create_youtube_short():
    """YouTube ショート向けの動画プロジェクト"""
    project = (
        ProjectBuilder("youtube_short.mp4")
        .output(width=1080, height=1920, fps=30)  # 縦長フォーマット

        # イントロ動画
        .add_video("assets/intro.mp4")
            .at(0.0)
            .fade_in(0.5)
            .with_volume(0.9)
            .build()

        # メインコンテンツ
        .add_video("assets/main_content.mp4")
            .at(3.0)
            .zoom(start_scale=1.0, end_scale=1.1, duration=10.0)
            .build()

        # アウトロ画像
        .add_image("assets/outro.jpg", 3.0)
            .at(13.0)
            .ken_burns(start_scale=1.0, end_scale=1.2)
            .fade_out(0.5)
            .build()

        # BGM
        .add_audio("assets/background_music.mp3")
            .with_volume(0.15)
            .for_duration(16.0)
            .build()

        # タイトル字幕
        .add_subtitle_layer()
            .add_item("驚きの事実!", 0.5, 2.5)
            .font(size="2xl", google_font="Noto Sans JP", weight="bold")
            .stroke(width=3, color="black")
            .style(position="center", appearance="shadow")
            .build()

        # 本文字幕
        .add_subtitle_layer()
            .add_item("これを知っていましたか?", 3.0, 5.0)
            .add_item("実は...", 5.0, 7.0)
            .add_item("答えはこちら!", 7.0, 9.0)
            .font(size="lg", google_font="Noto Sans JP")
            .style(position="bottom", appearance="background", bg_color="black@0.6")
            .build()

        # ロゴ
        .add_stamp("assets/channel_logo.png", 16.0)
            .position(0.05, 0.05)
            .with_scale(0.15)
            .fade_in(0.3)
            .build()

        .build()
    )

    return project


def create_tutorial_video():
    """チュートリアル動画プロジェクト"""
    builder = ProjectBuilder()

    # 出力設定
    builder.output(
        path="tutorial.mp4",
        width=1920,
        height=1080,
        fps=60
    )

    # イントロ
    (builder
        .add_image("assets/tutorial_cover.jpg", 3.0)
        .ken_burns()
        .build())

    # メインコンテンツ（複数のクリップ）
    clips = [
        ("assets/clip1.mp4", 0),
        ("assets/clip2.mp4", 10),
        ("assets/clip3.mp4", 20),
        ("assets/clip4.mp4", 30),
    ]

    for clip_path, start_time in clips:
        (builder
            .add_video(clip_path)
            .at(3.0 + start_time)
            .fade_in(0.5)
            .build())

    # BGM
    builder.add_audio("assets/tutorial_bgm.mp3").with_volume(0.2).build()

    # 字幕（ステップバイステップ）
    steps = [
        ("ステップ 1: 準備", 3, 8),
        ("ステップ 2: 設定", 13, 18),
        ("ステップ 3: 実行", 23, 28),
        ("ステップ 4: 確認", 33, 38),
    ]

    subtitles = builder.add_subtitle_layer()
    for text, start, end in steps:
        subtitles.add_item(text, start, end)

    (subtitles
        .font(size="xl", google_font="Roboto", weight="bold")
        .stroke(width=2, color="black")
        .style(position="top", appearance="background")
        .build())

    # ウォーターマーク
    (builder
        .add_stamp("assets/watermark.png", 43.0)
        .position(0.92, 0.05)
        .with_scale(0.1)
        .build())

    return builder.build()


def create_promo_video():
    """プロモーション動画プロジェクト"""
    project = (
        ProjectBuilder("promo.mp4")
        .output(width=1920, height=1080, fps=30)

        # 動的なオープニング
        .add_video("assets/promo_intro.mp4")
            .at(0.0)
            .slide_in("left", 1.0)
            .color_grade(
                duration=3.0,
                saturation=1.2,
                contrast=1.1
            )
            .build()

        # 製品画像（複数）
        .add_image("assets/product1.jpg", 3.0)
            .at(5.0)
            .ken_burns(end_scale=1.3)
            .fade_in(0.5)
            .fade_out(0.5)
            .build()

        .add_image("assets/product2.jpg", 3.0)
            .at(8.0)
            .zoom(1.0, 1.2, 3.0)
            .fade_in(0.5)
            .fade_out(0.5)
            .build()

        # クロージング
        .add_video("assets/promo_outro.mp4")
            .at(11.0)
            .fade_in(1.0)
            .build()

        # エネルギッシュな BGM
        .add_audio("assets/promo_music.mp3")
            .with_volume(0.4)
            .build()

        # キャッチコピー
        .add_subtitle_layer()
            .add_item("新登場!", 5.5, 7.5)
            .add_item("今すぐチェック!", 8.5, 10.5)
            .font(size="2xl", weight="bold", color="yellow")
            .stroke(width=4, color="black", outer_width=2, outer_color="red")
            .style(position="center", appearance="shadow")
            .build()

        # ロゴアニメーション
        .add_stamp("assets/company_logo.png", 2.0)
            .at(13.0)
            .position(0.5, 0.5)
            .with_scale(0.3)
            .fade_in(0.5)
            .zoom(0.3, 0.5, 1.5)
            .build()

        .build()
    )

    return project


def main():
    """メイン関数"""
    print("Builder パターンを使用したサンプルプロジェクト\n")

    # YouTube ショート
    print("1. YouTube ショート向けプロジェクトを作成中...")
    youtube_short = create_youtube_short()
    print(f"   ✅ プロジェクト作成完了: {youtube_short.output.path}")
    print(f"      - 動画/画像レイヤー: {len(youtube_short.timeline.video_layers)}")
    print(f"      - 音声レイヤー: {len(youtube_short.timeline.audio_layers)}")
    print(f"      - 字幕レイヤー: {len(youtube_short.timeline.subtitle_layers)}")
    print(f"      - スタンプレイヤー: {len(youtube_short.timeline.stamp_layers)}")
    print()

    # チュートリアル動画
    print("2. チュートリアル動画プロジェクトを作成中...")
    tutorial = create_tutorial_video()
    print(f"   ✅ プロジェクト作成完了: {tutorial.output.path}")
    print(f"      - 動画/画像レイヤー: {len(tutorial.timeline.video_layers)}")
    print(f"      - 音声レイヤー: {len(tutorial.timeline.audio_layers)}")
    print(f"      - 字幕レイヤー: {len(tutorial.timeline.subtitle_layers)}")
    print(f"      - スタンプレイヤー: {len(tutorial.timeline.stamp_layers)}")
    print()

    # プロモーション動画
    print("3. プロモーション動画プロジェクトを作成中...")
    promo = create_promo_video()
    print(f"   ✅ プロジェクト作成完了: {promo.output.path}")
    print(f"      - 動画/画像レイヤー: {len(promo.timeline.video_layers)}")
    print(f"      - 音声レイヤー: {len(promo.timeline.audio_layers)}")
    print(f"      - 字幕レイヤー: {len(promo.timeline.subtitle_layers)}")
    print(f"      - スタンプレイヤー: {len(promo.timeline.stamp_layers)}")
    print()

    # JSON エクスポート
    print("4. JSON ファイルにエクスポート中...")
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    youtube_short.to_json_file(str(output_dir / "youtube_short.json"))
    tutorial.to_json_file(str(output_dir / "tutorial.json"))
    promo.to_json_file(str(output_dir / "promo.json"))

    print(f"   ✅ JSON ファイル保存完了: {output_dir}")
    print()

    print("✨ すべてのサンプルプロジェクトの作成が完了しました!")


if __name__ == "__main__":
    main()

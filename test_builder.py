#!/usr/bin/env python3
"""Builder パターンのテストスクリプト"""

from packages.core.teto_core.models.builders import ProjectBuilder


def test_simple_project():
    """シンプルなプロジェクトの構築テスト"""
    print("=== Simple Project Test ===")

    project = (
        ProjectBuilder("output.mp4")
        .output(width=1920, height=1080, fps=30)
        .add_video("intro.mp4").at(0.0).fade_in(1.0).build()
        .add_video("main.mp4").at(5.0).with_volume(0.8).fade_out(1.0).build()
        .add_audio("bgm.mp3").with_volume(0.3).build()
        .add_subtitle_layer()
            .add_item("Hello", 0.0, 2.0)
            .add_item("World", 2.0, 4.0)
            .font(size="lg", color="white")
            .style(position="bottom", appearance="background")
            .build()
        .build()
    )

    print(f"Project created: {project.output.path}")
    print(f"Video layers: {len(project.timeline.video_layers)}")
    print(f"Audio layers: {len(project.timeline.audio_layers)}")
    print(f"Subtitle layers: {len(project.timeline.subtitle_layers)}")
    print()


def test_complex_project():
    """複雑なプロジェクトの構築テスト"""
    print("=== Complex Project Test ===")

    builder = ProjectBuilder()
    builder.output(path="my_video.mp4", width=1280, height=720, fps=60)

    # 動画レイヤーの追加
    builder.add_video("clip1.mp4").at(0.0).fade_in(0.5).zoom(1.0, 1.2, 3.0).fade_out(0.5).build()
    builder.add_video("clip2.mp4").at(10.0).slide_in("left", 1.0).build()

    # 画像レイヤーの追加
    builder.add_image("cover.jpg", 5.0).ken_burns().build()
    builder.add_image("outro.png", 3.0).at(20.0).fade_in(0.5).build()

    # 音声レイヤーの追加
    builder.add_audio("background_music.mp3").with_volume(0.2).build()
    builder.add_audio("sound_effect.wav").at(5.0).for_duration(2.0).with_volume(0.5).build()

    # 字幕レイヤーの追加
    (builder
        .add_subtitle_layer()
        .add_item("Introduction", 0, 3)
        .add_item("Main content", 3, 10)
        .add_item("Conclusion", 10, 15)
        .font(size="xl", google_font="Noto Sans JP", weight="bold")
        .stroke(width=2, color="black")
        .style(position="bottom", appearance="shadow")
        .build())

    # スタンプレイヤーの追加
    (builder
        .add_stamp("logo.png", 3.0)
        .at(0.0)
        .position(0.9, 0.1)
        .with_scale(0.2)
        .fade_in(0.5)
        .build())

    project = builder.build()

    print(f"Project created: {project.output.path}")
    print(f"Video layers: {len(project.timeline.video_layers)}")
    print(f"Audio layers: {len(project.timeline.audio_layers)}")
    print(f"Subtitle layers: {len(project.timeline.subtitle_layers)}")
    print(f"Stamp layers: {len(project.timeline.stamp_layers)}")

    # 最初の動画レイヤーのエフェクトを確認
    first_video = project.timeline.video_layers[0]
    print(f"\nFirst video layer effects: {len(first_video.effects)}")
    for effect in first_video.effects:
        print(f"  - {effect.type}: duration={effect.duration}s")

    # 字幕の確認
    if project.timeline.subtitle_layers:
        first_subtitle = project.timeline.subtitle_layers[0]
        print(f"\nSubtitle items: {len(first_subtitle.items)}")
        for item in first_subtitle.items:
            print(f"  - '{item.text}': {item.start_time}s - {item.end_time}s")

    print()


def test_json_export():
    """JSON エクスポートのテスト"""
    print("=== JSON Export Test ===")

    project = (
        ProjectBuilder("test_output.mp4")
        .output(width=1920, height=1080)
        .add_video("test.mp4").fade_in(1.0).build()
        .add_subtitle_layer()
            .add_item("Test", 0.0, 5.0)
            .font(size="lg")
            .build()
        .build()
    )

    # JSON にシリアライズ
    json_data = project.model_dump()
    print(f"JSON keys: {list(json_data.keys())}")
    print(f"Output config: {json_data['output']}")
    print()


if __name__ == "__main__":
    try:
        test_simple_project()
        test_complex_project()
        test_json_export()
        print("✅ All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

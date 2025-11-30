#!/usr/bin/env python3
"""Builder パターンの新しいインポート方法のテスト"""

# 新しいインポート方法: teto_core.models から直接インポート
from packages.core.teto_core.models import ProjectBuilder


def test_new_import():
    """新しいインポート方法のテスト"""
    print("=== Testing New Import Method ===")

    project = (
        ProjectBuilder("output.mp4")
        .output(width=1920, height=1080, fps=30)
        .add_video("intro.mp4").at(0.0).fade_in(1.0).build()
        .add_subtitle_layer()
            .add_item("Hello, World!", 0.0, 5.0)
            .font(size="xl", color="white")
            .build()
        .build()
    )

    print(f"✅ Project created successfully: {project.output.path}")
    print(f"   Video layers: {len(project.timeline.video_layers)}")
    print(f"   Subtitle layers: {len(project.timeline.subtitle_layers)}")
    print()


if __name__ == "__main__":
    try:
        test_new_import()
        print("✅ Import test passed!")
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()

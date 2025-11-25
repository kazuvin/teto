import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
import sys

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Teto - 解説系動画生成ツール"""
    pass


@main.command()
def info():
    """Show system information"""
    console.print("[bold green]Teto CLI v0.1.0[/bold green]")
    console.print("解説系動画生成ツール")
    console.print("\n機能:")
    console.print("  • 動画・画像の連結")
    console.print("  • 音声ファイルの追加")
    console.print("  • 字幕の追加（焼き込み/SRT/VTT）")


@main.command()
@click.argument("project_file")
@click.option("--validate-only", is_flag=True, help="プロジェクトファイルの検証のみ")
def generate(project_file, validate_only):
    """
    プロジェクトファイルから動画を生成

    PROJECT_FILE: プロジェクト定義JSONファイル
    """
    try:
        from teto_core import VideoGenerator, Project

        project_path = Path(project_file)
        if not project_path.exists():
            console.print(f"[red]エラー: {project_file} が見つかりません[/red]")
            sys.exit(1)

        # プロジェクトを読み込み
        console.print(f"[cyan]プロジェクトファイルを読み込み中: {project_file}[/cyan]")
        try:
            project = Project.from_json_file(str(project_path))
        except Exception as e:
            console.print(f"[red]エラー: プロジェクトファイルの読み込みに失敗しました[/red]")
            console.print(f"[red]{e}[/red]")
            sys.exit(1)

        # バリデーションのみの場合
        if validate_only:
            console.print("[green]✓ プロジェクトファイルは有効です[/green]")
            console.print(f"\n出力設定:")
            console.print(f"  パス: {project.output.path}")
            console.print(f"  サイズ: {project.output.width}x{project.output.height}")
            console.print(f"  FPS: {project.output.fps}")
            console.print(f"  字幕モード: {project.output.subtitle_mode}")
            return

        # 動画生成
        console.print("\n[bold yellow]動画生成を開始します...[/bold yellow]\n")

        generator = VideoGenerator(project)

        current_status = {"message": ""}

        def progress_callback(message: str):
            current_status["message"] = message
            console.print(f"[cyan]{message}[/cyan]")

        try:
            output_path = generator.generate(progress_callback=progress_callback)
            console.print(f"\n[bold green]✓ 動画生成が完了しました！[/bold green]")
            console.print(f"[green]出力ファイル: {output_path}[/green]")

        except Exception as e:
            console.print(f"\n[red]エラー: 動画生成に失敗しました[/red]")
            console.print(f"[red]{e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            sys.exit(1)

    except ImportError:
        console.print("[red]エラー: teto-core がインストールされていません[/red]")
        console.print("以下のコマンドでインストールしてください:")
        console.print("  uv pip install -e packages/core")
        sys.exit(1)


@main.command()
@click.argument("output_file")
def init(output_file):
    """
    新規プロジェクトファイルを作成

    OUTPUT_FILE: 作成するプロジェクトファイル名
    """
    from teto_core import Project, OutputConfig
    import json

    # サンプルプロジェクトを作成
    project = Project(
        version="1.0",
        output=OutputConfig(
            path="output.mp4",
            width=1920,
            height=1080,
            fps=30,
        ),
    )

    # ファイルに保存
    output_path = Path(output_file)
    if output_path.exists():
        if not click.confirm(f"{output_file} は既に存在します。上書きしますか？"):
            console.print("[yellow]キャンセルしました[/yellow]")
            return

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(project.model_dump(), f, indent=2, ensure_ascii=False)

    console.print(f"[green]✓ プロジェクトファイルを作成しました: {output_file}[/green]")
    console.print("\n次のステップ:")
    console.print("  1. プロジェクトファイルを編集して動画・画像・音声・字幕を追加")
    console.print(f"  2. teto generate {output_file} で動画を生成")


if __name__ == "__main__":
    main()

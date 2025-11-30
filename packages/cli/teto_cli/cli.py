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
    console.print("  • テキスト音声変換（Google Cloud TTS）")


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
        console.print("以下のコマンドで teto CLI を再インストールしてください:")
        console.print("  uv tool install --editable packages/cli --force")
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


@main.command()
@click.argument("text")
@click.option("-o", "--output", required=True, help="出力ファイルパス")
@click.option("-v", "--voice", default="ja-JP-Wavenet-A", help="音声名 (デフォルト: ja-JP-Wavenet-A)")
@click.option("--pitch", type=float, default=0.0, help="ピッチ調整 (-20.0～20.0)")
@click.option("--speed", type=float, default=1.0, help="話す速度 (0.25～4.0)")
@click.option("--volume", type=float, default=0.0, help="音量調整 (dB)")
@click.option("--format", type=click.Choice(["mp3", "wav", "ogg"]), default="mp3", help="出力フォーマット")
@click.option("--ssml", is_flag=True, help="テキストをSSMLとして解釈")
def tts(text, output, voice, pitch, speed, volume, format, ssml):
    """
    テキストから音声を生成 (Google Cloud TTS)

    TEXT: 変換するテキスト (または --text-file でファイルから読み込み)
    """
    try:
        from teto_core.tts.builders import TTSBuilder
        from teto_core.tts.processors import GoogleTTSProcessor

        console.print("[cyan]テキスト音声変換を開始します...[/cyan]\n")

        # リクエストを構築
        builder = TTSBuilder() \
            .text(text) \
            .voice(voice) \
            .pitch(pitch) \
            .speed(speed) \
            .volume(volume) \
            .output_format(format) \
            .output_path(output)

        if ssml:
            builder.ssml(True)

        request = builder.build()

        # 設定を表示
        console.print("[bold]設定:[/bold]")
        console.print(f"  テキスト: {text[:50]}{'...' if len(text) > 50 else ''}")
        console.print(f"  音声: {voice}")
        console.print(f"  ピッチ: {pitch:+.1f}")
        console.print(f"  速度: {speed:.2f}x")
        console.print(f"  音量: {volume:+.1f} dB")
        console.print(f"  フォーマット: {format}")
        console.print(f"  出力: {output}\n")

        # 音声生成
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("音声生成中...", total=None)

            try:
                processor = GoogleTTSProcessor()
                result = processor.execute(request)
                progress.update(task, completed=True)
            except Exception as e:
                console.print(f"\n[red]エラー: 音声生成に失敗しました[/red]")
                console.print(f"[red]{e}[/red]")
                console.print("\n[yellow]ヒント:[/yellow]")
                console.print("  1. Google Cloud の認証情報が設定されているか確認してください")
                console.print("  2. GOOGLE_APPLICATION_CREDENTIALS 環境変数を設定してください")
                console.print("  3. Text-to-Speech API が有効になっているか確認してください")
                sys.exit(1)

        # 結果を表示
        console.print(f"\n[bold green]✓ 音声生成が完了しました！[/bold green]")
        console.print(f"[green]出力ファイル: {result.audio_path}[/green]")
        console.print(f"\n[bold]詳細:[/bold]")
        console.print(f"  音声長: {result.duration_seconds:.2f}秒")
        console.print(f"  文字数: {result.character_count}文字")
        console.print(f"  推定コスト: ${result.estimated_cost_usd:.6f} USD")

    except ImportError as e:
        console.print("[red]エラー: teto-core の TTS 機能がインストールされていません[/red]")
        console.print(f"[red]{e}[/red]")
        console.print("\n必要な依存パッケージ:")
        console.print("  • google-cloud-texttospeech")
        console.print("  • pydub")
        console.print("  • python-dotenv")
        sys.exit(1)


@main.command()
@click.option("--language", default="ja-JP", help="言語コード (デフォルト: ja-JP)")
def tts_voices(language):
    """
    利用可能な音声の一覧を表示

    Google Cloud TTS で利用可能な音声のリストを取得します。
    """
    try:
        from teto_core.tts.google_tts import GoogleTTSClient
        from rich.table import Table

        console.print(f"[cyan]利用可能な音声を取得中... (言語: {language})[/cyan]\n")

        try:
            client = GoogleTTSClient()
            voices = client.list_voices(language_code=language)
        except Exception as e:
            console.print(f"[red]エラー: 音声リストの取得に失敗しました[/red]")
            console.print(f"[red]{e}[/red]")
            console.print("\n[yellow]ヒント:[/yellow]")
            console.print("  1. Google Cloud の認証情報が設定されているか確認してください")
            console.print("  2. GOOGLE_APPLICATION_CREDENTIALS 環境変数を設定してください")
            sys.exit(1)

        # テーブルで表示
        table = Table(title=f"利用可能な音声 ({language})")
        table.add_column("音声名", style="cyan")
        table.add_column("性別", style="magenta")
        table.add_column("サンプルレート", style="green")

        for voice in voices:
            table.add_row(
                voice["name"],
                voice["ssml_gender"],
                f"{voice['natural_sample_rate_hertz']} Hz",
            )

        console.print(table)
        console.print(f"\n合計: {len(voices)} 個の音声")

    except ImportError as e:
        console.print("[red]エラー: teto-core の TTS 機能がインストールされていません[/red]")
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

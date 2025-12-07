import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
import sys
import json

console = Console()


def detect_file_type(file_path: Path) -> str | None:
    """JSONファイルの種類を自動検出する

    Returns:
        "script": Scriptファイル（title + scenes キーがある）
        "project": Projectファイル（output + timeline キーがある）
        None: 判別不能
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Script: title と scenes キーがある
        if "title" in data and "scenes" in data:
            return "script"

        # Project: output と timeline キーがある
        if "output" in data and "timeline" in data:
            return "project"

        return None
    except (json.JSONDecodeError, IOError):
        return None


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
    console.print("  • Script → Project 変換")


@main.command()
@click.argument("input_file")
@click.option("-o", "--output", default=None, help="出力ファイルパス")
@click.option(
    "--type",
    "file_type",
    type=click.Choice(["auto", "script", "project"]),
    default="auto",
    help="ファイルタイプ（auto: 自動検出）",
)
@click.option("--validate-only", is_flag=True, help="ファイルの検証のみ")
@click.option(
    "--output-dir",
    default="./output",
    help="出力ディレクトリ（Script用: ナレーション音声など）",
)
@click.option(
    "--preset",
    type=click.Choice(["default", "bold_subtitle", "minimal", "vertical"]),
    default="default",
    help="プリセット（Script用）",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="TTSを呼び出さずに実行（Script用）",
)
@click.option(
    "--no-generate",
    is_flag=True,
    help="Projectへの変換のみ（Script用: 動画生成はスキップ）",
)
def generate(
    input_file,
    output,
    file_type,
    validate_only,
    output_dir,
    preset,
    dry_run,
    no_generate,
):
    """
    Script/Projectファイルから動画を生成

    INPUT_FILE: ScriptまたはProject定義JSONファイル

    ファイルタイプは自動検出されます。明示的に指定する場合は --type オプションを使用してください。

    \b
    例:
      teto generate my_script.json              # Script（自動検出）
      teto generate my_project.json             # Project（自動検出）
      teto generate file.json --type script     # 明示的にScript
      teto generate my_script.json --dry-run    # TTSなしでテスト
      teto generate my_script.json --preset bold_subtitle
    """
    try:
        input_path = Path(input_file)
        if not input_path.exists():
            console.print(f"[red]エラー: {input_file} が見つかりません[/red]")
            sys.exit(1)

        # ファイルタイプを検出
        if file_type == "auto":
            detected_type = detect_file_type(input_path)
            if detected_type is None:
                console.print(
                    "[red]エラー: ファイルタイプを自動検出できませんでした[/red]"
                )
                console.print("--type オプションで明示的に指定してください")
                sys.exit(1)
            file_type = detected_type
            console.print(f"[cyan]ファイルタイプを自動検出: {file_type}[/cyan]")

        # ファイルタイプに応じて処理を分岐
        if file_type == "script":
            _generate_from_script(
                input_file=input_file,
                output=output or "output.mp4",
                output_dir=output_dir,
                preset=preset,
                validate_only=validate_only,
                dry_run=dry_run,
                no_generate=no_generate,
            )
        else:
            _generate_from_project(
                project_file=input_file,
                validate_only=validate_only,
            )

    except ImportError as e:
        console.print("[red]エラー: teto-core がインストールされていません[/red]")
        console.print(f"[red]{e}[/red]")
        console.print("以下のコマンドで teto CLI を再インストールしてください:")
        console.print("  uv tool install --editable packages/cli --force")
        sys.exit(1)


def _generate_from_project(project_file: str, validate_only: bool) -> None:
    """Projectファイルから動画を生成"""
    from teto_core import VideoGenerator, Project

    project_path = Path(project_file)

    # プロジェクトを読み込み
    console.print(f"[cyan]Projectファイルを読み込み中: {project_file}[/cyan]")
    try:
        project = Project.from_json_file(str(project_path))
    except Exception as e:
        console.print("[red]エラー: Projectファイルの読み込みに失敗しました[/red]")
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    # バリデーションのみの場合
    if validate_only:
        console.print("[green]✓ Projectファイルは有効です[/green]")
        console.print("\n[bold]出力設定:[/bold]")
        console.print(f"  パス: {project.output.path}")
        console.print(f"  サイズ: {project.output.width}x{project.output.height}")
        console.print(f"  FPS: {project.output.fps}")
        console.print(f"  字幕モード: {project.output.subtitle_mode}")
        return

    # 動画生成
    console.print("\n[bold yellow]動画生成を開始します...[/bold yellow]\n")

    generator = VideoGenerator(project)

    def progress_callback(message: str):
        console.print(f"[cyan]{message}[/cyan]")

    try:
        output_path = generator.generate(progress_callback=progress_callback)
        console.print("\n[bold green]✓ 動画生成が完了しました！[/bold green]")
        console.print(f"[green]出力ファイル: {output_path}[/green]")

    except Exception as e:
        console.print("\n[red]エラー: 動画生成に失敗しました[/red]")
        console.print(f"[red]{e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


def _generate_from_script(
    input_file: str,
    output: str,
    output_dir: str,
    preset: str,
    validate_only: bool,
    dry_run: bool,
    no_generate: bool,
) -> None:
    """Scriptファイルから動画を生成"""
    from teto_core.script import Script, ScriptCompiler
    from teto_core.script.providers import (
        GoogleTTSProvider,
        ElevenLabsTTSProvider,
        GeminiTTSProvider,
        MockTTSProvider,
        CompositeAssetResolver,
    )
    from teto_core import VideoGenerator

    script_path = Path(input_file)

    # Scriptを読み込み
    console.print(f"[cyan]Scriptファイルを読み込み中: {input_file}[/cyan]")
    try:
        script_data = Script.from_json_file(str(script_path))
    except Exception as e:
        console.print("[red]エラー: Scriptファイルの読み込みに失敗しました[/red]")
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    # バリデーションのみの場合
    if validate_only:
        console.print("[green]✓ Scriptファイルは有効です[/green]")
        console.print("\n[bold]Script情報:[/bold]")
        console.print(f"  タイトル: {script_data.title}")
        console.print(f"  シーン数: {len(script_data.scenes)}")
        narration_count = sum(len(scene.narrations) for scene in script_data.scenes)
        console.print(f"  ナレーション数: {narration_count}")
        if script_data.bgm:
            console.print(f"  BGM: {script_data.bgm.path}")
        console.print("\n[bold]音声設定:[/bold]")
        console.print(f"  プロバイダー: {script_data.voice.provider}")
        console.print(f"  言語: {script_data.voice.language_code}")
        console.print(f"  話速: {script_data.voice.speed}x")
        return

    # CLIで指定されたプリセットでscriptのdefault_presetを上書き
    if preset != script_data.default_preset:
        console.print(
            f"[cyan]プリセット: {preset} (スクリプトのdefault_preset '{script_data.default_preset}' を上書き)[/cyan]"
        )
        script_data = script_data.model_copy(update={"default_preset": preset})
    else:
        console.print(f"[cyan]プリセット: {preset}[/cyan]")

    # TTSプロバイダーを選択
    if dry_run:
        console.print("[yellow]ドライラン: MockTTSProviderを使用[/yellow]")
        tts_provider = MockTTSProvider()
    else:
        provider_name = script_data.voice.provider
        try:
            if provider_name == "elevenlabs":
                console.print("[cyan]ElevenLabs TTSを使用[/cyan]")
                tts_provider = ElevenLabsTTSProvider()
            elif provider_name == "gemini":
                console.print("[cyan]Gemini TTSを使用[/cyan]")
                tts_provider = GeminiTTSProvider()
            else:
                console.print("[cyan]Google Cloud TTSを使用[/cyan]")
                tts_provider = GoogleTTSProvider()
        except Exception as e:
            console.print(f"[red]エラー: {provider_name} TTSの初期化に失敗[/red]")
            console.print(f"[red]{e}[/red]")
            console.print("\n[yellow]ヒント:[/yellow]")
            console.print("  --dry-run オプションでTTSなしでテストできます")
            sys.exit(1)

    # Compilerを作成（CompositeAssetResolver で AI 画像生成にも対応）
    compiler = ScriptCompiler(
        tts_provider=tts_provider,
        asset_resolver=CompositeAssetResolver(
            default_config=script_data.image_generation,
        ),
        output_dir=output_dir,
    )

    # Script → Project に変換
    console.print("\n[bold yellow]Script → Project 変換を開始します...[/bold yellow]\n")

    # 複数出力の場合は一時ディレクトリ内のoutput_pathを使用
    is_multi_output = isinstance(script_data.output, list)
    if is_multi_output:
        import tempfile

        temp_dir = tempfile.mkdtemp(prefix="teto_")
        compile_output_path = str(Path(temp_dir) / "temp_output.mp4")
    else:
        # 単一出力の場合、output_dir があればそれを使用
        if script_data.output_dir:
            output_filename = Path(output).name
            compile_output_path = str(Path(script_data.output_dir) / output_filename)
        else:
            compile_output_path = output

    try:
        result = compiler.compile(script_data, output_path=compile_output_path)
    except Exception as e:
        console.print("[red]エラー: 変換に失敗しました[/red]")
        console.print(f"[red]{e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)

    # メタデータを表示
    console.print("[green]✓ Script → Project 変換完了[/green]")
    console.print("\n[bold]変換結果:[/bold]")
    console.print(f"  総再生時間: {result.metadata.total_duration:.2f}秒")
    console.print(f"  シーン数: {len(result.metadata.scene_timings)}")
    console.print(f"  生成されたアセット: {len(result.metadata.generated_assets)}件")

    # シーンごとのタイミングを表示
    console.print("\n[bold]シーンタイミング:[/bold]")
    for scene_timing in result.metadata.scene_timings:
        duration = scene_timing.end_time - scene_timing.start_time
        seg_count = len(scene_timing.segments)
        console.print(
            f"  Scene {scene_timing.scene_index + 1}: "
            f"{scene_timing.start_time:.2f}s - {scene_timing.end_time:.2f}s "
            f"({duration:.2f}s, {seg_count} segments)"
        )

    # 変換のみの場合
    if no_generate:
        # Projectファイルを出力
        project_output = Path(output).with_suffix(".project.json")
        result.project.to_json_file(str(project_output))
        console.print(f"\n[green]✓ Projectファイルを出力: {project_output}[/green]")
        console.print("\n次のステップ:")
        console.print(f"  teto generate {project_output}")
        return

    # 動画生成
    console.print("\n[bold yellow]動画生成を開始します...[/bold yellow]\n")

    generator = VideoGenerator(result.project)

    def progress_callback(message: str):
        console.print(f"[cyan]{message}[/cyan]")

    try:
        # output が配列の場合は複数フォーマット出力
        if isinstance(script_data.output, list):
            from teto_core.output_config.models import OutputConfig

            # 出力ディレクトリを決定（優先順位: script.output_dir > CLI の output_dir）
            if script_data.output_dir:
                # Script で output_dir が指定されている場合
                base_dir = Path(script_data.output_dir)
            else:
                # CLI のデフォルト (output_dir / output_base)
                output_base = Path(output).stem
                base_dir = Path(output_dir) / output_base

            base_dir.mkdir(parents=True, exist_ok=True)
            output_dir_path = base_dir

            console.print(
                f"[cyan]複数フォーマットで並列出力します: {len(script_data.output)}個[/cyan]"
            )

            # 出力設定を作成
            output_configs = []
            config_names = []
            for output_settings in script_data.output:
                name = output_settings.name or "output"

                # ファイル名を生成
                output_path_multi = output_dir_path / f"{name}.mp4"

                config = OutputConfig(
                    path=str(output_path_multi),
                    aspect_ratio=output_settings.aspect_ratio,
                    width=output_settings.width,
                    height=output_settings.height,
                    fps=output_settings.fps,
                    codec=output_settings.codec,
                    audio_codec=output_settings.audio_codec,
                    bitrate=output_settings.bitrate,
                    preset=output_settings.preset,
                    subtitle_mode=output_settings.subtitle_mode,
                    object_fit=output_settings.object_fit,
                )
                output_configs.append(config)
                config_names.append(name)

                console.print(
                    f"  • {name}: {config.width}x{config.height} ({output_settings.aspect_ratio or 'custom'})"
                )

            console.print()

            # 並列生成用の進捗表示
            from rich.progress import (
                Progress,
                BarColumn,
                TaskProgressColumn,
                TimeElapsedColumn,
            )

            completed_names = []

            def parallel_progress_callback(message: str):
                # "完了 (n/m): path" 形式のメッセージから完了したファイル名を抽出
                if message.startswith("完了"):
                    for name in config_names:
                        if name in message and name not in completed_names:
                            completed_names.append(name)
                            console.print(f"  [green]✓[/green] {name} 完了")

            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "動画生成中...",
                    total=len(output_configs),
                )

                # 並列生成（verbose=False で MoviePy のログを抑制）
                output_paths = generator.generate_multi_parallel(
                    output_configs,
                    progress_callback=lambda msg: (
                        parallel_progress_callback(msg),
                        progress.update(task, completed=len(completed_names)),
                    ),
                    verbose=False,
                )

                progress.update(task, completed=len(output_configs))

            console.print("\n[bold green]✓ 全ての動画生成が完了しました！[/bold green]")
            console.print(f"[green]出力ディレクトリ: {output_dir_path}[/green]")
            for path in output_paths:
                console.print(f"  • {path}")

            # 一時ディレクトリをクリーンアップ
            if is_multi_output:
                import shutil

                shutil.rmtree(temp_dir, ignore_errors=True)

        else:
            # 単一フォーマット出力
            output_path = generator.generate(progress_callback=progress_callback)
            console.print("\n[bold green]✓ 動画生成が完了しました！[/bold green]")
            console.print(f"[green]出力ファイル: {output_path}[/green]")

    except Exception as e:
        console.print("\n[red]エラー: 動画生成に失敗しました[/red]")
        console.print(f"[red]{e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")

        # エラー時も一時ディレクトリをクリーンアップ
        if is_multi_output:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

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
@click.option(
    "-v",
    "--voice",
    default="ja-JP-Wavenet-A",
    help="音声名 (デフォルト: ja-JP-Wavenet-A)",
)
@click.option("--pitch", type=float, default=0.0, help="ピッチ調整 (-20.0～20.0)")
@click.option("--speed", type=float, default=1.0, help="話す速度 (0.25～4.0)")
@click.option("--volume", type=float, default=0.0, help="音量調整 (dB)")
@click.option(
    "--format",
    type=click.Choice(["mp3", "wav", "ogg"]),
    default="mp3",
    help="出力フォーマット",
)
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
        builder = (
            TTSBuilder()
            .text(text)
            .voice(voice)
            .pitch(pitch)
            .speed(speed)
            .volume(volume)
            .output_format(format)
            .output_path(output)
        )

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
                console.print("\n[red]エラー: 音声生成に失敗しました[/red]")
                console.print(f"[red]{e}[/red]")
                console.print("\n[yellow]ヒント:[/yellow]")
                console.print(
                    "  1. Google Cloud の認証情報が設定されているか確認してください"
                )
                console.print(
                    "  2. GOOGLE_APPLICATION_CREDENTIALS 環境変数を設定してください"
                )
                console.print(
                    "  3. Text-to-Speech API が有効になっているか確認してください"
                )
                sys.exit(1)

        # 結果を表示
        console.print("\n[bold green]✓ 音声生成が完了しました！[/bold green]")
        console.print(f"[green]出力ファイル: {result.audio_path}[/green]")
        console.print("\n[bold]詳細:[/bold]")
        console.print(f"  音声長: {result.duration_seconds:.2f}秒")
        console.print(f"  文字数: {result.character_count}文字")
        console.print(f"  推定コスト: ${result.estimated_cost_usd:.6f} USD")

    except ImportError as e:
        console.print(
            "[red]エラー: teto-core の TTS 機能がインストールされていません[/red]"
        )
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
            console.print("[red]エラー: 音声リストの取得に失敗しました[/red]")
            console.print(f"[red]{e}[/red]")
            console.print("\n[yellow]ヒント:[/yellow]")
            console.print(
                "  1. Google Cloud の認証情報が設定されているか確認してください"
            )
            console.print(
                "  2. GOOGLE_APPLICATION_CREDENTIALS 環境変数を設定してください"
            )
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
        console.print(
            "[red]エラー: teto-core の TTS 機能がインストールされていません[/red]"
        )
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@main.command(hidden=True)
@click.argument("script_file")
@click.option("-o", "--output", default="output.mp4", help="出力ファイルパス")
@click.option(
    "--output-dir",
    default="./output",
    help="出力ディレクトリ（ナレーション音声など）",
)
@click.option(
    "--preset",
    type=click.Choice(["default", "bold_subtitle", "minimal", "vertical"]),
    default="default",
    help="使用するプリセット",
)
@click.option("--validate-only", is_flag=True, help="スクリプトファイルの検証のみ")
@click.option(
    "--dry-run",
    is_flag=True,
    help="TTSを呼び出さずに実行（タイミング計算のみ）",
)
@click.option(
    "--no-generate",
    is_flag=True,
    help="Projectへの変換のみ（動画生成はスキップ）",
)
@click.pass_context
def script(
    ctx, script_file, output, output_dir, preset, validate_only, dry_run, no_generate
):
    """
    [非推奨] Scriptファイルから動画を生成

    このコマンドは非推奨です。代わりに teto generate を使用してください。
    """
    console.print(
        "[yellow]警告: 'teto script' は非推奨です。代わりに 'teto generate' を使用してください。[/yellow]"
    )
    console.print(f"[yellow]例: teto generate {script_file}[/yellow]\n")

    # generateコマンドを呼び出す
    ctx.invoke(
        generate,
        input_file=script_file,
        output=output,
        file_type="script",
        validate_only=validate_only,
        output_dir=output_dir,
        preset=preset,
        dry_run=dry_run,
        no_generate=no_generate,
    )


@main.command()
def script_presets():
    """
    利用可能なScriptプリセットの一覧を表示

    プリセットはシーン毎のエフェクトとトランジションを定義します。
    出力設定と字幕スタイルはScriptファイルで直接指定してください。
    """
    try:
        from teto_core.script.presets import ScenePresetRegistry
        from rich.table import Table

        console.print("[cyan]利用可能なシーンプリセット[/cyan]\n")

        table = Table(title="プリセット一覧")
        table.add_column("名前", style="cyan")
        table.add_column("画像エフェクト", style="green")
        table.add_column("トランジション", style="yellow")
        table.add_column("説明", style="magenta")

        presets_info = {
            "default": ("kenBurns", "crossfade 0.5s", "標準的なプリセット"),
            "bold_subtitle": ("zoom", "crossfade 0.3s", "インパクトのある演出向け"),
            "minimal": ("なし", "なし（カット）", "シンプルな演出向け"),
            "vertical": ("kenBurns", "crossfade 0.3s", "縦型動画向け"),
        }

        for name in ScenePresetRegistry.list_names():
            info = presets_info.get(name, ("", "", ""))
            table.add_row(name, info[0], info[1], info[2])

        console.print(table)

        console.print("\n[bold]使用例:[/bold]")
        console.print("  teto generate my_script.json --preset default")
        console.print("  teto generate my_script.json --preset minimal")
        console.print("\n[bold]シーン毎にプリセットを指定:[/bold]")
        console.print('  各シーンの "preset" フィールドでプリセットを上書きできます')
        console.print("\n[bold]出力設定と字幕スタイル:[/bold]")
        console.print('  Scriptファイルの "output" と "subtitle_style" で設定します')

    except ImportError as e:
        console.print("[red]エラー: teto-core がインストールされていません[/red]")
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@main.command()
@click.argument("output_file")
def script_init(output_file):
    """
    新規Scriptファイルのテンプレートを作成

    OUTPUT_FILE: 作成するScriptファイル名
    """
    import json

    # サンプルScriptを作成
    sample_script = {
        "title": "サンプル動画",
        "description": "Scriptファイルのサンプルです",
        "default_preset": "default",
        "scenes": [
            {
                "narrations": [],
                "visual": {"path": "./assets/title.png"},
                "duration": 3.0,
                "note": "タイトル画面（ナレーションなし）",
                "preset": "minimal",
            },
            {
                "narrations": [
                    {"text": "こんにちは！"},
                    {"text": "今日は素敵な一日ですね。", "pause_after": 0.5},
                ],
                "visual": {"path": "./assets/intro.png"},
            },
            {
                "narrations": [
                    {"text": "それでは、始めましょう。"},
                ],
                "visual": {"type": "video", "path": "./assets/main.mp4"},
            },
        ],
        "voice": {
            "provider": "google",
            "language_code": "ja-JP",
            "speed": 1.0,
            "pitch": 0.0,
        },
        "timing": {
            "default_segment_gap": 0.3,
            "default_scene_gap": 0.5,
            "subtitle_padding": 0.1,
        },
        "output": {
            "width": 1920,
            "height": 1080,
            "fps": 30,
        },
        "subtitle_style": {
            "font_size": "lg",
            "font_color": "white",
            "google_font": "Noto Sans JP",
            "appearance": "background",
            "position": "bottom",
        },
    }

    output_path = Path(output_file)
    if output_path.exists():
        if not click.confirm(f"{output_file} は既に存在します。上書きしますか？"):
            console.print("[yellow]キャンセルしました[/yellow]")
            return

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sample_script, f, indent=2, ensure_ascii=False)

    console.print(f"[green]✓ Scriptファイルを作成しました: {output_file}[/green]")
    console.print("\n次のステップ:")
    console.print("  1. Scriptファイルを編集してシーンとナレーションを追加")
    console.print("  2. アセットファイル（画像・動画）を準備")
    console.print(f"  3. teto generate {output_file} で動画を生成")
    console.print("\n[bold]ヒント:[/bold]")
    console.print("  • --dry-run オプションでTTSなしでテストできます")
    console.print("  • --preset オプションでデフォルトプリセットを変更できます")
    console.print(
        '  • 各シーンに "preset" を指定してシーン毎にプリセットを変更できます'
    )
    console.print("  • teto script-presets で利用可能なプリセットを確認できます")


@main.group()
def cache():
    """アセットキャッシュを管理（TTS、画像、動画）"""
    pass


@cache.command("info")
@click.option(
    "--type",
    "cache_type",
    type=click.Choice(["all", "tts", "image", "video"]),
    default="all",
    help="表示するキャッシュタイプ",
)
def cache_info(cache_type):
    """
    キャッシュ情報を表示

    アセットキャッシュの現在の状態（ファイル数、サイズ）を表示します。
    """
    try:
        from teto_core.cache import get_cache_manager
        from rich.table import Table

        manager = get_cache_manager()
        all_info = manager.get_info()

        if cache_type == "all":
            console.print("[cyan]アセットキャッシュ情報[/cyan]\n")

            table = Table()
            table.add_column("タイプ", style="cyan")
            table.add_column("ファイル数", justify="right")
            table.add_column("サイズ", justify="right")
            table.add_column("ディレクトリ", style="dim")

            table.add_row(
                "TTS",
                str(all_info.tts.total_files),
                f"{all_info.tts.total_size_mb:.2f} MB",
                str(all_info.tts.cache_dir),
            )
            table.add_row(
                "画像",
                str(all_info.image.total_files),
                f"{all_info.image.total_size_mb:.2f} MB",
                str(all_info.image.cache_dir),
            )
            table.add_row(
                "動画",
                str(all_info.video.total_files),
                f"{all_info.video.total_size_mb:.2f} MB",
                str(all_info.video.cache_dir),
            )
            table.add_row(
                "[bold]合計[/bold]",
                f"[bold]{all_info.total_files}[/bold]",
                f"[bold]{all_info.total_size_mb:.2f} MB[/bold]",
                "",
            )

            console.print(table)
        else:
            if cache_type == "tts":
                info = all_info.tts
                type_name = "TTS"
            elif cache_type == "image":
                info = all_info.image
                type_name = "画像"
            else:
                info = all_info.video
                type_name = "動画"

            console.print(f"[cyan]{type_name} キャッシュ情報[/cyan]\n")
            console.print(f"  キャッシュディレクトリ: {info.cache_dir}")
            console.print(f"  ファイル数: {info.total_files}")
            console.print(f"  合計サイズ: {info.total_size_mb:.2f} MB")

    except ImportError as e:
        console.print("[red]エラー: teto-core がインストールされていません[/red]")
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@cache.command("clear")
@click.option("--yes", "-y", is_flag=True, help="確認をスキップ")
@click.option(
    "--type",
    "cache_type",
    type=click.Choice(["all", "tts", "image", "video"]),
    default="all",
    help="クリアするキャッシュタイプ",
)
def cache_clear(yes, cache_type):
    """
    キャッシュをクリア

    アセットキャッシュを削除します。--type で特定のタイプのみ削除できます。
    """
    try:
        from teto_core.cache import get_cache_manager

        manager = get_cache_manager()
        all_info = manager.get_info()

        # 対象のキャッシュ情報を取得
        if cache_type == "all":
            total_files = all_info.total_files
            total_size = all_info.total_size_mb
            type_name = "全アセット"
        elif cache_type == "tts":
            total_files = all_info.tts.total_files
            total_size = all_info.tts.total_size_mb
            type_name = "TTS"
        elif cache_type == "image":
            total_files = all_info.image.total_files
            total_size = all_info.image.total_size_mb
            type_name = "画像"
        else:
            total_files = all_info.video.total_files
            total_size = all_info.video.total_size_mb
            type_name = "動画"

        if total_files == 0:
            console.print(f"[yellow]{type_name} キャッシュは空です[/yellow]")
            return

        console.print(f"[cyan]{type_name} キャッシュ情報[/cyan]\n")
        console.print(f"  ファイル数: {total_files}")
        console.print(f"  合計サイズ: {total_size:.2f} MB")

        if not yes:
            if not click.confirm(f"\n{type_name} キャッシュを削除しますか？"):
                console.print("[yellow]キャンセルしました[/yellow]")
                return

        # キャッシュをクリア
        if cache_type == "all":
            results = manager.clear_all()
            total_deleted = sum(results.values())
            console.print(f"\n[green]✓ {total_deleted} ファイルを削除しました[/green]")
            console.print(f"  TTS: {results['tts']} ファイル")
            console.print(f"  画像: {results['image']} ファイル")
            console.print(f"  動画: {results['video']} ファイル")
        elif cache_type == "tts":
            deleted = manager.clear_tts()
            console.print(
                f"\n[green]✓ TTS キャッシュ {deleted} ファイルを削除しました[/green]"
            )
        elif cache_type == "image":
            deleted = manager.clear_image()
            console.print(
                f"\n[green]✓ 画像キャッシュ {deleted} ファイルを削除しました[/green]"
            )
        else:
            deleted = manager.clear_video()
            console.print(
                f"\n[green]✓ 動画キャッシュ {deleted} ファイルを削除しました[/green]"
            )

    except ImportError as e:
        console.print("[red]エラー: teto-core がインストールされていません[/red]")
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

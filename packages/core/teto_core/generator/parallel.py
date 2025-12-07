"""並列動画生成のワーカー関数"""

from pathlib import Path


def _create_generator_and_run(
    project_dict: dict, output_config_dict: dict, verbose: bool = True
) -> str:
    """VideoGenerator を作成して実行する内部関数

    テスト時にモックしやすいように分離しています。
    """
    from ..project import Project
    from ..output_config.models import OutputConfig
    from ..video_generator import VideoGenerator

    # Project を再構築
    project = Project(**project_dict)

    # OutputConfig を設定
    project.output = OutputConfig(**output_config_dict)

    # VideoGenerator を作成して実行
    generator = VideoGenerator(project)
    return generator.generate(verbose=verbose)


def generate_single_output(
    project_dict: dict,
    output_config_dict: dict,
    verbose: bool = True,
) -> str:
    """単一出力を生成するワーカー関数

    ProcessPoolExecutor で使用するため、シリアライズ可能な dict を引数に取ります。
    各プロセスで VideoGenerator を再構築して実行します。

    Args:
        project_dict: Project をシリアライズした dict
        output_config_dict: OutputConfig をシリアライズした dict
        verbose: MoviePy のログを出力するかどうか

    Returns:
        生成された出力ファイルのパス

    Raises:
        RuntimeError: 動画生成に失敗した場合
    """
    try:
        # 出力ディレクトリを作成
        output_path = output_config_dict["path"]
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        return _create_generator_and_run(project_dict, output_config_dict, verbose)

    except Exception as e:
        output_path = output_config_dict.get("path", "unknown")
        raise RuntimeError(f"Failed to generate {output_path}: {e}") from e

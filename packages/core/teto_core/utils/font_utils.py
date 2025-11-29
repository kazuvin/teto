"""フォント関連のユーティリティ関数"""

import platform
import requests
from pathlib import Path
from PIL import ImageFont
from fontTools import ttLib


def load_font(
    font_path: str | None = None,
    font_size: int = 40,
    font_weight: str = "normal"
) -> ImageFont.FreeTypeFont:
    """フォントを読み込む

    Args:
        font_path: フォントファイルパス
        font_size: フォントサイズ
        font_weight: フォントの太さ（"normal" または "bold"）

    Returns:
        読み込んだフォント
    """
    try:
        # カスタムフォントパスが指定されている場合（最優先）
        if font_path and Path(font_path).exists():
            return ImageFont.truetype(font_path, font_size)

        # システムフォントを検索
        system_font = find_system_font(font_weight)
        if system_font:
            return ImageFont.truetype(system_font, font_size)

        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def find_system_font(font_weight: str = "normal") -> str | None:
    """システムに応じた日本語フォントを探す

    Args:
        font_weight: フォントの太さ（"normal" または "bold"）

    Returns:
        フォントファイルパス（見つからない場合はNone）
    """
    system = platform.system()
    font_paths = []

    if system == "Darwin":  # macOS
        if font_weight == "bold":
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/Library/Fonts/Arial Unicode.ttf",
            ]
        else:
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/Library/Fonts/Arial Unicode.ttf",
            ]
    elif system == "Windows":
        if font_weight == "bold":
            font_paths = [
                "C:/Windows/Fonts/yugothicb.ttf",
                "C:/Windows/Fonts/yugothic.ttf",
                "C:/Windows/Fonts/msgothic.ttc",
            ]
        else:
            font_paths = [
                "C:/Windows/Fonts/yugothic.ttf",
                "C:/Windows/Fonts/msgothic.ttc",
            ]
    else:  # Linux
        if font_weight == "bold":
            font_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]
        else:
            font_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]

    for font_path in font_paths:
        if Path(font_path).exists():
            return font_path

    return None


def get_font_cache_dir() -> Path:
    """フォントキャッシュディレクトリを取得

    Returns:
        フォントキャッシュディレクトリのパス
    """
    cache_dir = Path.home() / ".teto" / "fonts"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def download_google_font(font_name: str, font_weight: str = "normal") -> str | None:
    """Google Fontsからフォントをダウンロード

    woff2形式でダウンロードし、fontToolsでTTF/OTFに変換します。

    Args:
        font_name: フォント名（例: "Noto Sans JP", "Roboto"）
        font_weight: フォントの太さ（"normal" または "bold"）

    Returns:
        ダウンロードしたフォントファイルのパス（失敗時はNone）
    """
    try:
        # キャッシュディレクトリを取得
        cache_dir = get_font_cache_dir()

        # フォント名をファイル名用に変換
        safe_font_name = font_name.replace(" ", "_")
        weight_suffix = "bold" if font_weight == "bold" else "regular"
        font_file = cache_dir / f"{safe_font_name}_{weight_suffix}.ttf"

        # 既にキャッシュが存在する場合は再利用
        if font_file.exists():
            return str(font_file)

        # Google Fonts API v2を使用してwoff2をダウンロード
        # ウェイト値のマッピング
        weight_value = "700" if font_weight == "bold" else "400"

        # API v2のURL（wght パラメータを使用）
        api_url = "https://fonts.googleapis.com/css2"
        params = {
            "family": f"{font_name}:wght@{weight_value}",
            "display": "swap"
        }

        # User-Agentを指定してwoff2を取得
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # CSSからwoff/woff2のURLを抽出
        css_content = response.text
        import re
        # URL内に.woff2や.woffの拡張子がない場合もあるため、より柔軟にマッチング
        url_match = re.search(r'src:\s*url\((https://[^\)]+)\)\s*format\([\'"]woff2?[\'"]\)', css_content)

        if not url_match:
            print(f"Warning: Could not find font URL in CSS for '{font_name}'")
            print(f"CSS content: {css_content[:500]}...")
            return None

        font_url = url_match.group(1)

        # woff2ファイルをダウンロード
        font_response = requests.get(font_url, timeout=30)
        font_response.raise_for_status()

        # 一時的にwoff2ファイルを保存
        woff2_file = cache_dir / f"{safe_font_name}_{weight_suffix}.woff2"
        woff2_file.write_bytes(font_response.content)

        # fontToolsを使ってwoff2からTTF/OTFに変換
        font = ttLib.TTFont(str(woff2_file))

        # TTF/OTFとして保存（フォントの種類に応じて適切な形式で保存）
        font.save(str(font_file))

        # woff2ファイルを削除
        woff2_file.unlink()

        return str(font_file)

    except Exception as e:
        # エラーが発生した場合はNoneを返す
        print(f"Failed to download Google Font '{font_name}': {e}")
        return None

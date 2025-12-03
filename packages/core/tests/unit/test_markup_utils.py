"""markup_utils のユニットテスト"""

from teto_core.utils.markup_utils import (
    TextSpan,
    has_markup,
    parse_styled_text,
    strip_markup,
)


class TestParseStyledText:
    """parse_styled_text のテスト"""

    def test_single_markup(self):
        """単一のマークアップをパースできる"""
        result = parse_styled_text("<A>hello</A>")
        assert result == [TextSpan(text="hello", style_name="A")]

    def test_multiple_markups(self):
        """複数のマークアップをパースできる"""
        result = parse_styled_text("<A>hello</A><B>world</B>")
        assert result == [
            TextSpan(text="hello", style_name="A"),
            TextSpan(text="world", style_name="B"),
        ]

    def test_plain_text_only(self):
        """プレーンテキストのみの場合は単一スパンを返す"""
        result = parse_styled_text("plain text")
        assert result == [TextSpan(text="plain text", style_name=None)]

    def test_mixed_markup_and_plain(self):
        """マークアップとプレーンテキストの混在"""
        result = parse_styled_text("<emphasis>重要:</emphasis> 説明文")
        assert result == [
            TextSpan(text="重要:", style_name="emphasis"),
            TextSpan(text=" 説明文", style_name=None),
        ]

    def test_plain_before_markup(self):
        """マークアップの前にプレーンテキスト"""
        result = parse_styled_text("prefix <A>content</A>")
        assert result == [
            TextSpan(text="prefix ", style_name=None),
            TextSpan(text="content", style_name="A"),
        ]

    def test_plain_between_markups(self):
        """マークアップの間にプレーンテキスト"""
        result = parse_styled_text("<A>first</A> middle <B>second</B>")
        assert result == [
            TextSpan(text="first", style_name="A"),
            TextSpan(text=" middle ", style_name=None),
            TextSpan(text="second", style_name="B"),
        ]

    def test_japanese_text(self):
        """日本語テキストを正しく処理できる"""
        result = parse_styled_text("<A>こんにちは</A><B>世界</B>")
        assert result == [
            TextSpan(text="こんにちは", style_name="A"),
            TextSpan(text="世界", style_name="B"),
        ]

    def test_tag_with_hyphen(self):
        """ハイフンを含むタグ名をパースできる"""
        result = parse_styled_text("<my-style>content</my-style>")
        assert result == [TextSpan(text="content", style_name="my-style")]

    def test_tag_with_underscore(self):
        """アンダースコアを含むタグ名をパースできる"""
        result = parse_styled_text("<my_style>content</my_style>")
        assert result == [TextSpan(text="content", style_name="my_style")]

    def test_tag_with_numbers(self):
        """数字を含むタグ名をパースできる"""
        result = parse_styled_text("<style1>content</style1>")
        assert result == [TextSpan(text="content", style_name="style1")]

    def test_empty_string(self):
        """空文字列の場合"""
        result = parse_styled_text("")
        assert result == [TextSpan(text="", style_name=None)]

    def test_empty_markup_content(self):
        """空のマークアップコンテンツは無視される"""
        result = parse_styled_text("<A></A>text")
        assert result == [TextSpan(text="text", style_name=None)]

    def test_multiline_content(self):
        """複数行のコンテンツを処理できる"""
        result = parse_styled_text("<A>line1\nline2</A>")
        assert result == [TextSpan(text="line1\nline2", style_name="A")]


class TestStripMarkup:
    """strip_markup のテスト"""

    def test_single_markup(self):
        """単一のマークアップを除去できる"""
        result = strip_markup("<A>hello</A>")
        assert result == "hello"

    def test_multiple_markups(self):
        """複数のマークアップを除去できる"""
        result = strip_markup("<A>hello</A><B>world</B>")
        assert result == "helloworld"

    def test_plain_text_only(self):
        """プレーンテキストはそのまま"""
        result = strip_markup("plain text")
        assert result == "plain text"

    def test_mixed_markup_and_plain(self):
        """マークアップとプレーンテキストの混在"""
        result = strip_markup("<emphasis>重要:</emphasis> 説明文")
        assert result == "重要: 説明文"

    def test_japanese_text(self):
        """日本語テキストを正しく処理できる"""
        result = strip_markup("<A>こんにちは</A><B>世界</B>へようこそ")
        assert result == "こんにちは世界へようこそ"

    def test_empty_string(self):
        """空文字列の場合"""
        result = strip_markup("")
        assert result == ""


class TestHasMarkup:
    """has_markup のテスト"""

    def test_with_markup(self):
        """マークアップがある場合はTrue"""
        assert has_markup("<A>hello</A>") is True

    def test_without_markup(self):
        """マークアップがない場合はFalse"""
        assert has_markup("plain text") is False

    def test_incomplete_markup(self):
        """不完全なマークアップはFalse"""
        assert has_markup("<A>hello") is False
        assert has_markup("hello</A>") is False

    def test_mismatched_tags(self):
        """タグが一致しない場合はFalse"""
        assert has_markup("<A>hello</B>") is False

    def test_empty_string(self):
        """空文字列はFalse"""
        assert has_markup("") is False

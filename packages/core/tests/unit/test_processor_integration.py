"""プロセッサーの統合テスト"""

from teto_core.processors import (
    VideoLayerProcessor,
    ImageLayerProcessor,
    AudioLayerProcessor,
    AudioProcessor,
    VideoProcessor,
)
from teto_core.models.layers import VideoLayer, ImageLayer, AudioLayer


class TestVideoLayerProcessor:
    """VideoLayerProcessor のテスト"""

    def test_validate_missing_file(self):
        """存在しないファイルのバリデーションテスト"""
        processor = VideoLayerProcessor()
        layer = VideoLayer(path="/nonexistent/video.mp4", start_time=0)

        # バリデーション失敗
        assert processor.validate(layer) is False

    def test_validate_existing_file(self, tmp_path):
        """存在するファイルのバリデーションテスト（モック）"""
        # 実際のファイル処理は統合テストで行う
        # ここでは、パスのバリデーションのみテスト
        processor = VideoLayerProcessor()

        # 存在しないパスでバリデーション失敗を確認
        layer = VideoLayer(path=str(tmp_path / "video.mp4"), start_time=0)
        assert processor.validate(layer) is False


class TestImageLayerProcessor:
    """ImageLayerProcessor のテスト"""

    def test_validate_missing_file(self):
        """存在しないファイルのバリデーションテスト"""
        processor = ImageLayerProcessor()
        layer = ImageLayer(path="/nonexistent/image.png", start_time=0, duration=5)

        # バリデーション失敗
        assert processor.validate(layer, target_size=(1920, 1080)) is False

    def test_validate_missing_target_size(self, tmp_path):
        """target_size が指定されていない場合のバリデーションテスト"""
        processor = ImageLayerProcessor()

        # 一時ファイルを作成
        image_file = tmp_path / "image.png"
        image_file.touch()

        layer = ImageLayer(path=str(image_file), start_time=0, duration=5)

        # target_size がないとバリデーション失敗
        assert processor.validate(layer) is False


class TestAudioLayerProcessor:
    """AudioLayerProcessor のテスト"""

    def test_validate_missing_file(self):
        """存在しないファイルのバリデーションテスト"""
        processor = AudioLayerProcessor()
        layer = AudioLayer(path="/nonexistent/audio.mp3", start_time=0)

        # バリデーション失敗
        assert processor.validate(layer) is False


class TestAudioProcessor:
    """AudioProcessor のテスト"""

    def test_validate_empty_layers(self):
        """空のレイヤーリストのバリデーションテスト"""
        processor = AudioProcessor()

        # 空のリストでも許可（None を返すため）
        assert processor.validate([]) is True

    def test_validate_with_layers(self):
        """レイヤーがある場合のバリデーションテスト"""
        processor = AudioProcessor()
        layers = [
            AudioLayer(path="/path/to/audio1.mp3", start_time=0),
            AudioLayer(path="/path/to/audio2.mp3", start_time=5),
        ]

        # レイヤーがあっても True
        assert processor.validate(layers) is True


class TestVideoProcessor:
    """VideoProcessor のテスト"""

    def test_validate_empty_layers(self):
        """空のレイヤーリストのバリデーションテスト"""
        processor = VideoProcessor()

        # 空のリストは無効
        assert processor.validate([], output_size=(1920, 1080)) is False

    def test_validate_missing_output_size(self):
        """output_size が指定されていない場合のバリデーションテスト"""
        processor = VideoProcessor()
        layers = [VideoLayer(path="/path/to/video.mp4", start_time=0)]

        # output_size がないとバリデーション失敗
        assert processor.validate(layers) is False

    def test_validate_with_valid_inputs(self):
        """正しい入力でのバリデーションテスト"""
        processor = VideoProcessor()
        layers = [
            VideoLayer(path="/path/to/video.mp4", start_time=0),
            ImageLayer(path="/path/to/image.png", start_time=5, duration=3),
        ]

        # レイヤーと output_size があれば True
        assert processor.validate(layers, output_size=(1920, 1080)) is True


class TestDependencyInjection:
    """依存性注入のテスト"""

    def test_custom_effect_processor_injection(self):
        """カスタム EffectProcessor の注入テスト"""
        from teto_core.processors.effect import EffectProcessor

        custom_effect_processor = EffectProcessor()

        # VideoLayerProcessor にカスタムプロセッサーを注入
        processor = VideoLayerProcessor(effect_processor=custom_effect_processor)

        # 注入されたプロセッサーが使用されることを確認
        assert processor.effect_processor is custom_effect_processor

    def test_custom_audio_processor_injection(self):
        """カスタム AudioLayerProcessor の注入テスト"""
        custom_audio_processor = AudioLayerProcessor()

        # AudioProcessor にカスタムプロセッサーを注入
        processor = AudioProcessor(audio_processor=custom_audio_processor)

        # 注入されたプロセッサーが使用されることを確認
        assert processor.audio_processor is custom_audio_processor

    def test_custom_video_processors_injection(self):
        """カスタム VideoLayerProcessor と ImageLayerProcessor の注入テスト"""
        custom_video_processor = VideoLayerProcessor()
        custom_image_processor = ImageLayerProcessor()

        # VideoProcessor にカスタムプロセッサーを注入
        processor = VideoProcessor(
            video_processor=custom_video_processor,
            image_processor=custom_image_processor,
        )

        # 注入されたプロセッサーが使用されることを確認
        assert processor.video_processor is custom_video_processor
        assert processor.image_processor is custom_image_processor

# Project → Video 生成パイプライン

このドキュメントでは、Project モデルから実際の動画ファイルを生成するレンダリングパイプラインを詳しく説明します。

---

## 目次

1. [生成の概要](#生成の概要)
2. [VideoGenerator アーキテクチャ](#videogenerator-アーキテクチャ)
3. [処理パイプライン](#処理パイプライン)
4. [レイヤープロセッサー](#レイヤープロセッサー)
5. [エフェクトシステム](#エフェクトシステム)
6. [マルチ出力生成](#マルチ出力生成)
7. [拡張ポイント](#拡張ポイント)

---

## 生成の概要

### 目的

Project は実行可能なデータ構造ですが、実際の動画ファイルを生成するには以下の処理が必要です：

1. **映像処理**: VideoLayer/ImageLayer をリサイズ、エフェクト適用、合成
2. **音声処理**: AudioLayer を合成、音量調整
3. **字幕処理**: SubtitleLayer を焼き込みまたは SRT/VTT エクスポート
4. **スタンプ処理**: StampLayer をオーバーレイ
5. **動画出力**: MP4 ファイルとしてエンコード

### 入出力

**入力**: `Project` モデル
```python
Project(
    output=OutputConfig(path="output.mp4", aspect_ratio="16:9"),
    timeline=Timeline(
        video_layers=[...],
        audio_layers=[...],
        subtitle_layers=[...]
    )
)
```

**出力**: MP4 動画ファイル + 字幕ファイル（オプション）
```
output.mp4
output.srt  (subtitle_mode=srt の場合)
```

---

## VideoGenerator アーキテクチャ

**場所**: `packages/core/teto_core/video_generator.py`

### クラス設計

```python
class VideoGenerator:
    """動画生成エンジン"""

    def __init__(self, project: Project):
        self.project = project
        self._pre_hooks: list[Callable] = []
        self._post_hooks: list[Callable] = []
        self._pipeline: ProcessingStep | None = None

    def generate(self, progress_callback: Callable | None = None) -> str:
        """動画を生成"""
        # Pre hooks
        for hook in self._pre_hooks:
            hook(self.project)

        # パイプライン実行
        pipeline = self._pipeline or self._build_default_pipeline()
        context = ProcessingContext(project=self.project)
        final_context = pipeline.process(context)

        # Post hooks
        for hook in self._post_hooks:
            hook(self.project.output.path, self.project)

        return self.project.output.path

    def _build_default_pipeline(self) -> ProcessingStep:
        """デフォルトパイプラインを構築"""
        return (
            VideoLayerProcessingStep()
            .then(AudioLayerProcessingStep())
            .then(AudioMergingStep())
            .then(StampLayerProcessingStep())
            .then(SubtitleProcessingStep())
            .then(VideoOutputStep())
            .then(CleanupStep())
        )
```

### 主な特徴

1. **Pipeline Pattern**: ステップをチェーンして実行
2. **Pre/Post Hooks**: 生成前後に処理を挿入可能
3. **Progress Callback**: 進捗状況を通知
4. **カスタムパイプライン**: デフォルトを置き換え可能

---

## 処理パイプライン

**場所**: `packages/core/teto_core/generator/pipeline.py`, `generator/steps/`

### ProcessingStep 抽象クラス

```python
class ProcessingStep(ABC):
    """処理ステップの基底クラス（Chain of Responsibility）"""

    def __init__(self):
        self._next: ProcessingStep | None = None

    def then(self, next_step: "ProcessingStep") -> "ProcessingStep":
        """次のステップをチェーン"""
        self._next = next_step
        return next_step

    @abstractmethod
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """このステップの処理を実行"""
        ...

    def _process_next(self, context: ProcessingContext) -> ProcessingContext:
        """次のステップに処理を渡す"""
        if self._next:
            return self._next.process(context)
        return context
```

### ProcessingContext

```python
@dataclass
class ProcessingContext:
    """処理パイプラインの共有コンテキスト"""

    project: Project
    video_clip: VideoClip | None = None          # 現在の映像クリップ
    audio_clips: list[AudioClip] = field(default_factory=list)  # 音声クリップ
    video_size: tuple[int, int] | None = None    # 出力サイズ
    progress_callback: Callable | None = None    # 進捗コールバック
```

### デフォルトパイプラインの各ステップ

#### 1. VideoLayerProcessingStep

**役割**: 映像レイヤー（VideoLayer/ImageLayer）を処理して1つの映像クリップに合成

```python
class VideoLayerProcessingStep(ProcessingStep):
    def process(self, context: ProcessingContext) -> ProcessingContext:
        output_config = context.project.output
        video_layers = context.project.timeline.video_layers

        # 出力サイズを計算
        video_size = self._calculate_video_size(output_config)
        context.video_size = video_size

        # レイヤープロセッサーを初期化
        processor = VideoLayerProcessor(
            video_size=video_size,
            object_fit=output_config.object_fit,
        )

        # 各レイヤーを処理
        clips = []
        for layer in video_layers:
            clip = processor.process_layer(layer)
            clips.append(clip)

        # クリップを連結
        context.video_clip = concatenate_videoclips(clips, method="compose")

        return self._process_next(context)
```

**処理内容**:
1. 出力サイズを計算（アスペクト比から）
2. VideoLayerProcessor でレイヤー処理
3. エフェクト適用
4. クリップを連結

#### 2. AudioLayerProcessingStep

**役割**: 音声レイヤー（AudioLayer）を処理して音声クリップのリストを作成

```python
class AudioLayerProcessingStep(ProcessingStep):
    def process(self, context: ProcessingContext) -> ProcessingContext:
        audio_layers = context.project.timeline.audio_layers

        # プロセッサーを初期化
        processor = AudioLayerProcessor()

        # 各レイヤーを処理
        audio_clips = []
        for layer in audio_layers:
            clip = processor.process_layer(layer)
            audio_clips.append(clip)

        context.audio_clips = audio_clips

        return self._process_next(context)
```

#### 3. AudioMergingStep

**役割**: 複数の音声クリップを1つに合成

```python
class AudioMergingStep(ProcessingStep):
    def process(self, context: ProcessingContext) -> ProcessingContext:
        if not context.audio_clips:
            return self._process_next(context)

        # 音声クリップを合成
        merged_audio = CompositeAudioClip(context.audio_clips)

        # 映像クリップに音声を設定
        if context.video_clip:
            context.video_clip = context.video_clip.set_audio(merged_audio)

        return self._process_next(context)
```

#### 4. StampLayerProcessingStep

**役割**: スタンプレイヤー（StampLayer）をオーバーレイ

```python
class StampLayerProcessingStep(ProcessingStep):
    def process(self, context: ProcessingContext) -> ProcessingContext:
        stamp_layers = context.project.timeline.stamp_layers

        if not stamp_layers or not context.video_clip:
            return self._process_next(context)

        # プロセッサーを初期化
        processor = StampLayerProcessor(video_size=context.video_size)

        # 各スタンプを処理してオーバーレイ
        for layer in stamp_layers:
            stamp_clip = processor.process_layer(layer)
            context.video_clip = CompositeVideoClip([
                context.video_clip,
                stamp_clip
            ])

        return self._process_next(context)
```

#### 5. SubtitleProcessingStep

**役割**: 字幕を焼き込みまたはファイルにエクスポート

```python
class SubtitleProcessingStep(ProcessingStep):
    def process(self, context: ProcessingContext) -> ProcessingContext:
        subtitle_layers = context.project.timeline.subtitle_layers
        output_config = context.project.output

        if not subtitle_layers:
            return self._process_next(context)

        processor = SubtitleProcessor(
            video_size=context.video_size,
            mode=output_config.subtitle_mode,
        )

        if output_config.subtitle_mode == SubtitleMode.BURN:
            # 字幕を焼き込み
            context.video_clip = processor.burn_subtitles(
                video_clip=context.video_clip,
                subtitle_layers=subtitle_layers,
            )
        else:
            # SRT/VTT ファイルにエクスポート
            subtitle_path = output_config.path.replace(".mp4", f".{output_config.subtitle_mode}")
            processor.export_subtitles(
                subtitle_layers=subtitle_layers,
                output_path=subtitle_path,
            )

        return self._process_next(context)
```

#### 6. VideoOutputStep

**役割**: 最終的な動画ファイルを出力

```python
class VideoOutputStep(ProcessingStep):
    def process(self, context: ProcessingContext) -> ProcessingContext:
        if not context.video_clip:
            raise ValueError("映像クリップが生成されていません")

        output_config = context.project.output

        # ディレクトリ作成
        Path(output_config.path).parent.mkdir(parents=True, exist_ok=True)

        # 動画を書き出し
        context.video_clip.write_videofile(
            output_config.path,
            fps=output_config.fps,
            codec=output_config.codec,
            preset=output_config.preset,
            audio_codec="aac",
            logger=None if context.progress_callback else "bar",
        )

        return self._process_next(context)
```

#### 7. CleanupStep

**役割**: リソースを解放

```python
class CleanupStep(ProcessingStep):
    def process(self, context: ProcessingContext) -> ProcessingContext:
        # クリップをクローズ
        if context.video_clip:
            context.video_clip.close()

        for audio_clip in context.audio_clips:
            audio_clip.close()

        return context
```

---

## レイヤープロセッサー

**場所**: `packages/core/teto_core/layer/processors/`

### VideoLayerProcessor

**役割**: VideoLayer/ImageLayer を処理

```python
class VideoLayerProcessor:
    def __init__(
        self,
        video_size: tuple[int, int],
        object_fit: ObjectFit = ObjectFit.CONTAIN,
    ):
        self.video_size = video_size
        self.object_fit = object_fit

    def process_layer(self, layer: VideoLayer | ImageLayer) -> VideoClip:
        """レイヤーを処理"""
        # クリップをロード
        if isinstance(layer, VideoLayer):
            clip = VideoFileClip(layer.path)
            if layer.loop:
                clip = clip.loop(duration=layer.duration)
            clip = clip.set_audio(None) if layer.volume == 0 else clip.volumex(layer.volume)
        else:  # ImageLayer
            clip = ImageClip(layer.path, duration=layer.duration)

        # リサイズ（object_fit に応じて）
        clip = self._resize_clip(clip, self.video_size, self.object_fit)

        # エフェクト適用
        for effect in layer.effects:
            clip = self._apply_effect(clip, effect)

        # トランジション（次のクリップとの間に適用、ここでは無視）

        return clip

    def _resize_clip(self, clip, size, object_fit):
        """オブジェクトフィットに応じてリサイズ"""
        if object_fit == ObjectFit.CONTAIN:
            return clip.resize(height=size[1]).on_color(
                size=size, color=(0, 0, 0), pos="center"
            )
        elif object_fit == ObjectFit.COVER:
            return clip.resize(height=size[1]).crop(
                x_center=clip.w / 2, y_center=clip.h / 2, width=size[0], height=size[1]
            )
        elif object_fit == ObjectFit.FILL:
            return clip.resize(size)

    def _apply_effect(self, clip, effect):
        """エフェクトを適用"""
        processor = EffectProcessor()
        return processor.apply_effect(clip, effect, self.video_size)
```

**Object Fit モード**:

| モード | 動作 | 用途 |
|--------|------|------|
| `contain` | アスペクト比維持、黒帯付き | デフォルト、全体表示 |
| `cover` | アスペクト比維持、はみ出し切り取り | 余白なし、一部非表示OK |
| `fill` | 引き伸ばし | アスペクト比を無視 |

### AudioLayerProcessor

**役割**: AudioLayer を処理

```python
class AudioLayerProcessor:
    def process_layer(self, layer: AudioLayer) -> AudioClip:
        """レイヤーを処理"""
        # 音声ファイルをロード
        clip = AudioFileClip(layer.path)

        # 開始時刻を設定
        clip = clip.set_start(layer.start_time)

        # 音量調整
        if layer.volume != 1.0:
            clip = clip.volumex(layer.volume)

        # 再生時間を制限
        if layer.duration:
            clip = clip.set_duration(layer.duration)

        return clip
```

### SubtitleProcessor

**役割**: SubtitleLayer を処理（焼き込みまたはエクスポート）

```python
class SubtitleProcessor:
    def __init__(
        self,
        video_size: tuple[int, int],
        mode: SubtitleMode = SubtitleMode.BURN,
    ):
        self.video_size = video_size
        self.mode = mode

    def burn_subtitles(
        self,
        video_clip: VideoClip,
        subtitle_layers: list[SubtitleLayer],
    ) -> VideoClip:
        """字幕を焼き込み"""
        subtitle_clips = []

        for layer in subtitle_layers:
            for item in layer.items:
                # テキストをパースしてマークアップを処理
                text_elements = self._parse_markup(item.text, layer)

                # テキストクリップを作成
                text_clip = self._create_text_clip(
                    text_elements,
                    layer,
                    start_time=item.start_time,
                    duration=item.end_time - item.start_time,
                )

                subtitle_clips.append(text_clip)

        # 字幕をオーバーレイ
        if subtitle_clips:
            return CompositeVideoClip([video_clip] + subtitle_clips)

        return video_clip

    def export_subtitles(
        self,
        subtitle_layers: list[SubtitleLayer],
        output_path: str,
    ):
        """字幕をSRT/VTTファイルにエクスポート"""
        with open(output_path, "w", encoding="utf-8") as f:
            index = 1
            for layer in subtitle_layers:
                for item in layer.items:
                    # マークアップを除去
                    plain_text = strip_markup(item.text)

                    # SRT形式で書き出し
                    f.write(f"{index}\n")
                    f.write(f"{self._format_time(item.start_time)} --> {self._format_time(item.end_time)}\n")
                    f.write(f"{plain_text}\n\n")
                    index += 1

    def _parse_markup(self, text, layer):
        """マークアップをパースして部分スタイルを適用"""
        # <emphasis>強調</emphasis> のようなマークアップを解析
        # layer.partial_styles からスタイルを取得
        ...

    def _create_text_clip(self, text_elements, layer, start_time, duration):
        """テキストクリップを作成"""
        # Google Fonts をダウンロード
        font_path = self._download_google_font(layer.font_family)

        # TextClip を作成
        text_clip = TextClip(
            txt=text,
            fontsize=layer.font_size,
            color=layer.font_color,
            font=font_path,
            bg_color=layer.background_color,
            method="caption",
            size=(self.video_size[0] - layer.margin_x * 2, None),
        )

        # 配置
        text_clip = text_clip.set_position((layer.margin_x, self._get_y_position(layer)))

        # タイミング
        text_clip = text_clip.set_start(start_time).set_duration(duration)

        return text_clip
```

**マークアップサポート**:
```html
<emphasis>強調</emphasis>
<highlight>ハイライト</highlight>
<note>注釈</note>
```

これらのタグに対して `SubtitleLayer.partial_styles` でスタイルを定義します。

---

## エフェクトシステム

**場所**: `packages/core/teto_core/effect/`

### EffectProcessor

```python
class EffectProcessor:
    """エフェクトプロセッサー（Registry + Strategy）"""

    _effects: dict[str, EffectStrategy] = {}

    @classmethod
    def register_effect(cls, name: str, strategy: EffectStrategy):
        """エフェクトを登録"""
        cls._effects[name] = strategy

    def apply_effect(
        self,
        clip: VideoClip,
        effect: AnimationEffect,
        video_size: tuple[int, int],
    ) -> VideoClip:
        """エフェクトを適用"""
        strategy = self._effects.get(effect.type)
        if not strategy:
            raise ValueError(f"Unknown effect: {effect.type}")

        return strategy.apply(clip, effect, video_size)
```

### EffectStrategy インターフェース

```python
class EffectStrategy(ABC):
    """エフェクト戦略の基底クラス"""

    @abstractmethod
    def apply(
        self,
        clip: VideoClip,
        effect: AnimationEffect,
        video_size: tuple[int, int],
    ) -> VideoClip:
        """エフェクトを適用"""
        ...
```

### エフェクト実装例: Ken Burns

```python
class KenBurnsEffect(EffectStrategy):
    def apply(self, clip, effect, video_size):
        params = effect.params
        start_zoom = params.get("start_zoom", 1.0)
        end_zoom = params.get("end_zoom", 1.2)
        direction = params.get("direction", "right")

        def make_frame(t):
            # 進捗率
            progress = t / clip.duration

            # ズーム係数
            zoom = start_zoom + (end_zoom - start_zoom) * progress

            # 移動方向に応じてパン
            if direction == "right":
                x_offset = -progress * (clip.w * zoom - video_size[0])
            elif direction == "left":
                x_offset = progress * (clip.w * zoom - video_size[0])
            else:
                x_offset = 0

            # フレームを取得してズーム・パン
            frame = clip.get_frame(t)
            frame = zoom_frame(frame, zoom)
            frame = pan_frame(frame, x_offset, 0)

            return frame

        return clip.fl(make_frame)

# 登録
EffectProcessor.register_effect("kenburns", KenBurnsEffect())
```

---

## マルチ出力生成

**場所**: `VideoGenerator.generate_all()`

### 単一出力 vs 複数出力

**単一出力**:
```python
project = Project(
    output=OutputConfig(path="output.mp4", aspect_ratio="16:9"),
    timeline=timeline
)
generator = VideoGenerator(project)
generator.generate()
```

**複数出力**（マルチプラットフォーム）:
```python
# Scriptでの指定
script = Script(
    output=[
        OutputSettings(name="youtube", aspect_ratio="16:9"),
        OutputSettings(name="tiktok", aspect_ratio="9:16"),
        OutputSettings(name="instagram", aspect_ratio="1:1"),
    ],
    ...
)

# ScriptCompilerは3つのProjectを生成
# VideoGenerator.generate_all()で順次生成
```

### マルチ出力の実装

```python
def generate_all(
    projects: list[Project],
    progress_callback: Callable | None = None,
) -> list[str]:
    """複数のプロジェクトを順次生成"""
    output_paths = []

    for i, project in enumerate(projects):
        print(f"生成中 ({i+1}/{len(projects)}): {project.output.path}")

        generator = VideoGenerator(project)
        output_path = generator.generate(progress_callback)
        output_paths.append(output_path)

    return output_paths
```

**並列生成（将来の拡張）**:
```python
from concurrent.futures import ProcessPoolExecutor

def generate_all_parallel(projects: list[Project]) -> list[str]:
    """複数のプロジェクトを並列生成"""
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(generate_one, p) for p in projects]
        return [f.result() for f in futures]
```

---

## 拡張ポイント

### 1. カスタムパイプライン

```python
# カスタムステップを定義
class WatermarkStep(ProcessingStep):
    def process(self, context):
        # ウォーターマークを追加
        watermark = ImageClip("watermark.png", duration=context.video_clip.duration)
        context.video_clip = CompositeVideoClip([context.video_clip, watermark])
        return self._process_next(context)

# カスタムパイプラインを構築
custom_pipeline = (
    VideoLayerProcessingStep()
    .then(AudioLayerProcessingStep())
    .then(AudioMergingStep())
    .then(WatermarkStep())  # カスタムステップ挿入
    .then(SubtitleProcessingStep())
    .then(VideoOutputStep())
    .then(CleanupStep())
)

# 適用
generator = VideoGenerator(project)
generator.set_pipeline(custom_pipeline)
generator.generate()
```

### 2. Pre/Post Hooks

```python
def pre_hook(project: Project):
    print(f"生成開始: {project.output.path}")
    # 事前チェック、ログ記録など

def post_hook(output_path: str, project: Project):
    print(f"生成完了: {output_path}")
    # サムネイル生成、アップロード、通知など

generator = VideoGenerator(project)
generator.register_pre_hook(pre_hook)
generator.register_post_hook(post_hook)
generator.generate()
```

### 3. カスタムエフェクト

```python
class MyCustomEffect(EffectStrategy):
    def apply(self, clip, effect, video_size):
        # カスタムエフェクトロジック
        return clip.fx(my_custom_fx, **effect.params)

# 登録
EffectProcessor.register_effect("my_custom", MyCustomEffect())

# 使用
layer = ImageLayer(
    path="image.jpg",
    effects=[AnimationEffect(type="my_custom", params={...})],
    ...
)
```

### 4. カスタムレイヤープロセッサー

```python
class CustomVideoProcessor(VideoLayerProcessor):
    def _apply_effect(self, clip, effect):
        # カスタムエフェクト適用ロジック
        if effect.type == "my_special_effect":
            return self._apply_special_effect(clip, effect)
        return super()._apply_effect(clip, effect)

# 使用
step = VideoLayerProcessingStep()
step.processor = CustomVideoProcessor(video_size=(1920, 1080))
```

---

## パフォーマンス最適化

### メモリ管理

**クリップのクローズ**:
```python
# 使用後は必ずクローズ
clip.close()

# with 文での自動クローズ
with VideoFileClip("video.mp4") as clip:
    # 処理
    pass
```

### 並列処理

**moviepy の内部並列化**:
```python
clip.write_videofile(
    "output.mp4",
    threads=4,  # スレッド数を指定
    preset="ultrafast",  # エンコード速度優先
)
```

### プログレスコールバック

```python
def progress_callback(current_frame, total_frames):
    progress = current_frame / total_frames * 100
    print(f"進捗: {progress:.1f}%")

generator = VideoGenerator(project)
generator.generate(progress_callback=progress_callback)
```

---

## エラーハンドリング

### よくあるエラー

1. **ファイルが見つからない**:
   ```python
   try:
       generator.generate()
   except FileNotFoundError as e:
       print(f"ファイルが見つかりません: {e}")
   ```

2. **メモリ不足**:
   ```python
   # 長時間動画の場合、チャンク単位で処理
   clip.write_videofile("output.mp4", codec="libx264", preset="ultrafast")
   ```

3. **エンコードエラー**:
   ```python
   # ffmpeg のパスを確認
   import os
   os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/local/bin/ffmpeg"
   ```

---

## まとめ

Project → Video 生成パイプラインの特徴：

- ✅ **Pipeline Pattern**: ステップをチェーンして柔軟に構成
- ✅ **レイヤー処理**: VideoLayer、AudioLayer、SubtitleLayer を統一的に処理
- ✅ **エフェクトシステム**: Strategy パターンで拡張可能
- ✅ **Object Fit**: contain/cover/fill で様々な画面比に対応
- ✅ **マルチ出力**: 複数のアスペクト比を同時生成
- ✅ **拡張性**: カスタムステップ、エフェクト、フックで柔軟にカスタマイズ

このパイプラインにより、Project モデルから高品質な動画ファイルへの変換が実現されています。

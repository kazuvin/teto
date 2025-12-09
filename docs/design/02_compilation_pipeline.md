# Script → Project コンパイルパイプライン

このドキュメントでは、高レベルな Script モデルから実行可能な Project モデルへの変換プロセスを詳しく説明します。

---

## 目次

1. [コンパイルの概要](#コンパイルの概要)
2. [ScriptCompiler アーキテクチャ](#scriptcompiler-アーキテクチャ)
3. [コンパイルステップ詳細](#コンパイルステップ詳細)
4. [音声設定の解決](#音声設定の解決)
5. [タイミング計算](#タイミング計算)
6. [レイヤー構築](#レイヤー構築)
7. [プリセットシステム](#プリセットシステム)

---

## コンパイルの概要

### 目的

Script は AI や人間が記述しやすい抽象的な表現ですが、動画レンダリングには具体的な情報が必要です。コンパイルは以下を実現します：

1. **TTS 生成**: ナレーションテキストから音声ファイルを生成
2. **アセット解決**: ローカルファイルまたは AI 生成画像を取得
3. **タイミング計算**: 各シーン・セグメントの開始・終了時刻を決定
4. **レイヤー構築**: Timeline（VideoLayer、AudioLayer、SubtitleLayer）を作成
5. **プリセット適用**: シーンプリセットからエフェクトを展開

### 入出力

**入力**: `Script` モデル（JSON から生成）
```json
{
  "title": "サンプル動画",
  "scenes": [
    {
      "narrations": [{"text": "こんにちは"}],
      "visual": {"path": "image.jpg"}
    }
  ],
  "voice": {"provider": "google"}
}
```

**出力**: `Project` モデル + メタデータ
```python
Project(
    output=OutputConfig(path="output.mp4", ...),
    timeline=Timeline(
        video_layers=[...],
        audio_layers=[...],
        subtitle_layers=[...]
    )
)
```

---

## ScriptCompiler アーキテクチャ

**場所**: `packages/core/teto_core/script/compiler.py`

### クラス設計

```python
class ScriptCompiler:
    """Script → Project 変換（Template Method + Strategy）"""

    def __init__(
        self,
        tts_provider: TTSProvider,
        asset_resolver: AssetResolver,
        output_dir: str = "./output",
        cache_manager: TTSCacheManager | None = None,
        use_cache: bool = True,
    ):
        self._tts = tts_provider
        self._assets = asset_resolver
        self._output_dir = output_dir
        self._cache = cache_manager or get_cache_manager()
        self._use_cache = use_cache
```

### 依存関係

- **TTSProvider**: TTS 音声生成（Strategy パターン）
- **AssetResolver**: アセット解決（Chain of Responsibility）
- **TTSCacheManager**: TTS キャッシュ管理（Repository パターン）
- **ScenePresetRegistry**: プリセット取得（Registry パターン）

---

## コンパイルステップ詳細

### メインメソッド: `compile()`

**Template Method パターン**による段階的な処理：

```python
def compile(self, script: Script, output_path: str = "output.mp4") -> CompileResult:
    """Script を Project に変換する（Template Method）"""

    # 1. 準備
    self._prepare(script)

    # 2. 全セグメントのナレーション音声を生成
    narrations = self._generate_all_narrations(script)

    # 3. タイムラインを計算（間隔を考慮）
    scene_timings = self._calculate_timings(script, narrations)

    # 4. 各レイヤーを生成
    video_layers = self._build_video_layers(script, scene_timings)
    audio_layers = self._build_audio_layers(script, scene_timings, narrations)
    subtitle_layers = self._build_subtitle_layers(script, scene_timings)

    # 5. Project を組み立て
    project = self._assemble_project(
        script, video_layers, audio_layers, subtitle_layers, output_path
    )

    # 6. メタデータ作成
    metadata = self._create_metadata(scene_timings, narrations)

    return CompileResult(project=project, metadata=metadata)
```

### ステップ 1: 準備 (`_prepare()`)

```python
def _prepare(self, script: Script) -> None:
    """前処理"""
    import os

    os.makedirs(self._output_dir, exist_ok=True)
    os.makedirs(f"{self._output_dir}/narrations", exist_ok=True)
```

**処理内容**:
- 出力ディレクトリ作成
- ナレーション音声保存用ディレクトリ作成

### ステップ 2: TTS 生成 (`_generate_all_narrations()`)

```python
def _generate_all_narrations(self, script: Script) -> list[list[TTSResult]]:
    """全シーン・全セグメントのナレーションを生成"""
    all_narrations: list[list[TTSResult]] = []

    cache_hits = 0
    cache_misses = 0

    for scene_idx, scene in enumerate(script.scenes):
        scene_narrations: list[TTSResult] = []

        # シーン固有のvoice設定を解決
        effective_voice = self._resolve_scene_voice(script, scene)

        # プロバイダーに応じて拡張子を決定
        audio_ext = ".wav" if effective_voice.provider == "gemini" else ".mp3"

        for seg_idx, segment in enumerate(scene.narrations):
            # マークアップを除去したテキストをTTSに渡す
            plain_text = strip_markup(segment.text)

            # キャッシュをチェック
            cached_audio = None
            if self._use_cache:
                cached_audio = self._cache.get(plain_text, effective_voice, audio_ext)

            if cached_audio is not None:
                # キャッシュヒット
                cache_hits += 1
                duration = self._tts.estimate_duration(plain_text, effective_voice)
                result = TTSResult(
                    audio_content=cached_audio,
                    duration=duration,
                    text=plain_text,
                )
            else:
                # キャッシュミス - TTS生成
                cache_misses += 1
                result = self._tts.generate(
                    text=plain_text,
                    config=effective_voice,
                )
                # キャッシュに保存
                if self._use_cache:
                    self._cache.put(
                        plain_text, effective_voice, audio_ext, result.audio_content
                    )

            # 音声ファイルを保存
            output_path = (
                f"{self._output_dir}/narrations/"
                f"scene_{scene_idx:03d}_seg_{seg_idx:03d}{audio_ext}"
            )
            result.save(output_path)
            scene_narrations.append(result)

        all_narrations.append(scene_narrations)

    # キャッシュ統計を表示
    total = cache_hits + cache_misses
    if total > 0:
        print(
            f"  TTS キャッシュ: {cache_hits}/{total} ヒット "
            f"({cache_hits * 100 // total}%)"
        )

    return all_narrations
```

**処理内容**:
1. シーン毎に音声設定を解決（`_resolve_scene_voice()`）
2. 各セグメントのテキストからマークアップを除去
3. キャッシュをチェック
4. キャッシュミスの場合、TTS API を呼び出し
5. 音声ファイルを保存
6. キャッシュヒット率を表示

**最適化**:
- キャッシュによる API コスト削減
- 同じテキスト + 同じ音声設定 = 即座に再利用

### ステップ 3: タイミング計算 (`_calculate_timings()`)

```python
def _calculate_timings(
    self,
    script: Script,
    all_narrations: list[list[TTSResult]],
) -> list[SceneTiming]:
    """タイミングを計算（間隔を考慮）"""
    scene_timings: list[SceneTiming] = []
    current_time = 0.0
    timing_config = script.timing
    padding = timing_config.subtitle_padding

    for scene_idx, scene in enumerate(script.scenes):
        scene_narrations = all_narrations[scene_idx]
        scene_start = current_time
        segment_timings: list[SegmentTiming] = []

        if len(scene.narrations) == 0:
            # ナレーションなしのシーン（タイトル、見出し等）
            assert scene.duration is not None
            scene_end = current_time + scene.duration
            current_time = scene_end
        else:
            # ナレーションありのシーン
            for seg_idx, (segment, narration) in enumerate(
                zip(scene.narrations, scene_narrations)
            ):
                # padding 分遅らせて開始
                seg_start = current_time + padding
                seg_end = seg_start + narration.duration

                segment_timings.append(
                    SegmentTiming(
                        segment_index=seg_idx,
                        start_time=seg_start,
                        end_time=seg_end,
                        narration_path=narration.path or "",
                        text=segment.text,
                    )
                )

                # 次のセグメントへ
                current_time = seg_end + padding + segment.pause_after

                # セグメント間のデフォルト間隔
                if seg_idx < len(scene.narrations) - 1:
                    current_time += timing_config.default_segment_gap

            scene_end = current_time

        # シーン後の間隔
        current_time += scene.pause_after + timing_config.default_scene_gap

        scene_timings.append(
            SceneTiming(
                scene_index=scene_idx,
                start_time=scene_start,
                end_time=scene_end,
                segments=segment_timings,
            )
        )

    return scene_timings
```

**処理内容**:
1. シーンを順番に処理
2. ナレーションありの場合:
   - 各セグメントに `subtitle_padding` を追加
   - セグメント間に `default_segment_gap` を挿入
   - セグメントの `pause_after` を適用
3. ナレーションなしの場合:
   - `scene.duration` を使用
4. シーン間に `default_scene_gap` を挿入
5. `SceneTiming` と `SegmentTiming` を生成

**タイミング図**:
```
|← padding →|← narration →|← padding →|← segment_gap →|← padding →|← narration →|← padding →|← scene_gap →|
             ↑                         ↑                           ↑                         ↑
          seg_start                 seg_end                    seg_start                 seg_end
```

### ステップ 4: レイヤー構築

#### 4.1 映像レイヤー (`_build_video_layers()`)

```python
def _build_video_layers(
    self, script: Script, scene_timings: list[SceneTiming]
) -> list[VideoLayer | ImageLayer]:
    """映像レイヤーを構築"""
    video_layers: list[VideoLayer | ImageLayer] = []

    for scene, timing in zip(script.scenes, scene_timings):
        # アセットを解決（ローカルまたはAI生成）
        asset_path = self._assets.resolve(scene.visual)

        # プリセットを取得
        preset = self._get_preset_for_scene(script, scene)

        # アセットタイプを判定
        if scene.visual.type == AssetType.VIDEO:
            # 動画レイヤー
            video_layers.append(
                VideoLayer(
                    path=asset_path,
                    start_time=timing.start_time,
                    end_time=timing.end_time,
                    duration=timing.end_time - timing.start_time,
                    volume=0.0 if scene.mute_video else 1.0,
                    effects=preset.get_video_effects(),
                    transition=scene.transition,
                )
            )
        else:
            # 画像レイヤー
            video_layers.append(
                ImageLayer(
                    path=asset_path,
                    start_time=timing.start_time,
                    end_time=timing.end_time,
                    duration=timing.end_time - timing.start_time,
                    effects=preset.get_image_effects(),
                    transition=scene.transition,
                )
            )

    return video_layers
```

**処理内容**:
1. シーン毎にアセットを解決
2. プリセットからエフェクトを取得
3. VideoLayer または ImageLayer を作成
4. タイミング情報を設定

#### 4.2 音声レイヤー (`_build_audio_layers()`)

```python
def _build_audio_layers(
    self,
    script: Script,
    scene_timings: list[SceneTiming],
    all_narrations: list[list[TTSResult]],
) -> list[AudioLayer]:
    """音声レイヤーを構築"""
    audio_layers: list[AudioLayer] = []

    # 1. ナレーション音声
    for scene_idx, (scene, timing) in enumerate(zip(script.scenes, scene_timings)):
        for seg_timing in timing.segments:
            audio_layers.append(
                AudioLayer(
                    path=seg_timing.narration_path,
                    start_time=seg_timing.start_time,
                    volume=1.0,
                )
            )

    # 2. 効果音
    for scene, timing in zip(script.scenes, scene_timings):
        for sound_effect in scene.sound_effects:
            audio_layers.append(
                AudioLayer(
                    path=sound_effect.path,
                    start_time=timing.start_time + sound_effect.offset,
                    volume=sound_effect.volume,
                )
            )

    # 3. BGM
    if script.bgm:
        total_duration = scene_timings[-1].end_time if scene_timings else 0.0
        audio_layers.append(
            AudioLayer(
                path=script.bgm.path,
                start_time=0.0,
                volume=script.bgm.volume,
                duration=total_duration,
            )
        )

    return audio_layers
```

**処理内容**:
1. ナレーション音声レイヤーを作成
2. 効果音レイヤーを作成（シーン開始からのオフセット）
3. BGM レイヤーを作成（全体に適用）

#### 4.3 字幕レイヤー (`_build_subtitle_layers()`)

```python
def _build_subtitle_layers(
    self, script: Script, scene_timings: list[SceneTiming]
) -> list[SubtitleLayer]:
    """字幕レイヤーを構築"""
    subtitle_items: list[SubtitleItem] = []

    # 全シーンから字幕アイテムを収集
    for timing in scene_timings:
        for seg_timing in timing.segments:
            subtitle_items.append(
                SubtitleItem(
                    text=seg_timing.text,
                    start_time=seg_timing.start_time,
                    end_time=seg_timing.end_time,
                )
            )

    # 字幕レイヤーを作成
    if subtitle_items:
        subtitle_layer = SubtitleLayer(
            items=subtitle_items,
            font_family=script.subtitle_style.font_family,
            font_size=script.subtitle_style.font_size,
            font_color=script.subtitle_style.font_color,
            background_color=script.subtitle_style.background_color,
            background_opacity=script.subtitle_style.background_opacity,
            position=script.subtitle_style.position,
            partial_styles=script.subtitle_styles,
        )
        return [subtitle_layer]

    return []
```

**処理内容**:
1. 全セグメントから SubtitleItem を生成
2. Script の字幕スタイル設定を適用
3. 部分スタイル（マークアップ用）を設定

### ステップ 5: Project 組み立て (`_assemble_project()`)

```python
def _assemble_project(
    self,
    script: Script,
    video_layers: list[VideoLayer | ImageLayer],
    audio_layers: list[AudioLayer],
    subtitle_layers: list[SubtitleLayer],
    output_path: str,
) -> Project:
    """Project を組み立て"""
    # 出力設定を構築
    output_config = self._build_output_config(script, output_path)

    # Timeline を構築
    timeline = Timeline(
        video_layers=video_layers,
        audio_layers=audio_layers,
        subtitle_layers=subtitle_layers,
        stamp_layers=[],  # Script には stamp 機能なし
    )

    return Project(output=output_config, timeline=timeline)
```

### ステップ 6: メタデータ作成 (`_create_metadata()`)

```python
def _create_metadata(
    self, scene_timings: list[SceneTiming], narrations: list[list[TTSResult]]
) -> CompileMetadata:
    """コンパイルメタデータを作成"""
    total_duration = scene_timings[-1].end_time if scene_timings else 0.0

    # 生成されたアセットのリストを作成
    generated_assets = []
    for scene_narrations in narrations:
        for narration in scene_narrations:
            if narration.path:
                generated_assets.append(narration.path)

    return CompileMetadata(
        total_duration=total_duration,
        scene_timings=scene_timings,
        generated_assets=generated_assets,
    )
```

---

## 音声設定の解決

**場所**: `ScriptCompiler._resolve_scene_voice()`

### 優先順位

シーン毎に異なる音声を使用できる機能（新機能）：

```python
def _resolve_scene_voice(self, script: Script, scene: Scene):
    """シーンに適用する音声設定を解決

    優先順位:
    1. scene.voice（直接指定）
    2. scene.voice_profile（名前付きプロファイル参照）
    3. script.voice（グローバルデフォルト）
    """
    # 1. 直接指定
    if scene.voice is not None:
        return scene.voice

    # 2. プロファイル参照
    if scene.voice_profile is not None:
        if script.voice_profiles is None or scene.voice_profile not in script.voice_profiles:
            raise ValueError(
                f"ボイスプロファイル '{scene.voice_profile}' が見つかりません。"
                f"Script.voice_profiles に定義してください。"
            )
        return script.voice_profiles[scene.voice_profile]

    # 3. グローバルデフォルト
    return script.voice
```

### 使用例

**対談形式の動画**:
```json
{
  "voice_profiles": {
    "host": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"},
    "guest": {"provider": "google", "voice_id": "ja-JP-Wavenet-B"}
  },
  "scenes": [
    {
      "narrations": [{"text": "ホストのセリフ"}],
      "voice_profile": "host"
    },
    {
      "narrations": [{"text": "ゲストのセリフ"}],
      "voice_profile": "guest"
    }
  ]
}
```

---

## タイミング計算

### タイミング構造

```python
@dataclass
class SegmentTiming:
    """セグメントのタイミング情報"""
    segment_index: int
    start_time: float
    end_time: float
    narration_path: str
    text: str

@dataclass
class SceneTiming:
    """シーンのタイミング情報"""
    scene_index: int
    start_time: float
    end_time: float
    segments: list[SegmentTiming]
```

### タイミング計算の詳細

**例**: 2 シーン、各シーンに 2 セグメント

```
設定:
  subtitle_padding: 0.1秒
  default_segment_gap: 0.3秒
  default_scene_gap: 0.5秒

シーン0:
  セグメント0: "こんにちは" (duration=1.0秒)
  セグメント1: "今日は" (duration=0.8秒)

シーン1:
  セグメント0: "良い天気ですね" (duration=1.2秒)

タイムライン:
0.0                                            → 時刻（秒）
├── [0.1秒 padding]
├── [1.0秒 narration] ← セグメント0
├── [0.1秒 padding]
├── [0.3秒 segment_gap]
├── [0.1秒 padding]
├── [0.8秒 narration] ← セグメント1
├── [0.1秒 padding]
├── [0.5秒 scene_gap]
├── [0.1秒 padding]
├── [1.2秒 narration] ← セグメント0 (シーン1)
├── [0.1秒 padding]
└── 5.3秒（終了）

計算:
  シーン0 開始: 0.0秒
  セグメント0: 0.1 〜 1.1秒
  セグメント1: 1.5 〜 2.3秒
  シーン0 終了: 2.4秒

  シーン1 開始: 2.9秒
  セグメント0: 3.0 〜 4.2秒
  シーン1 終了: 4.3秒

  合計: 5.3秒
```

---

## レイヤー構築

### 映像レイヤーの構成

**アセット解決の流れ**:
```
Visual
  └─→ AssetResolver.resolve()
       ├─→ LocalAssetResolver (ローカルファイル)
       └─→ AIImageAssetResolver (AI生成)
            └─→ Stability AI API
```

**プリセット適用**:
```
Scene.preset
  └─→ ScenePresetRegistry.get(preset_name)
       └─→ ScenePreset
            ├─→ get_image_effects()
            └─→ get_video_effects()
```

### 音声レイヤーの構成

**レイヤーの優先順位**（後から追加されたものが上に重なる）:
1. ナレーション（最も重要）
2. 効果音（ナレーションに重ねる）
3. BGM（背景）

**音量バランス**:
- ナレーション: 1.0（フル音量）
- 効果音: 1.0（デフォルト、調整可能）
- BGM: 0.3（デフォルト、ナレーションを邪魔しない）

### 字幕レイヤーの構成

**マークアップ処理**:
```
入力テキスト: "これは<emphasis>重要</emphasis>です"
  ↓
マークアップ除去（TTS用）: "これは重要です"
  ↓
TTS生成
  ↓
字幕表示: マークアップを保持して SubtitleItem に格納
  ↓
レンダリング時: partial_styles を適用して色・太さを変更
```

---

## プリセットシステム

**場所**: `packages/core/teto_core/script/presets/`

### プリセットインターフェース

```python
class ScenePreset(ABC):
    """シーンプリセットの基底クラス"""

    @property
    @abstractmethod
    def name(self) -> str:
        """プリセット名"""
        ...

    @abstractmethod
    def get_image_effects(self) -> list[AnimationEffect]:
        """画像用エフェクト"""
        ...

    @abstractmethod
    def get_video_effects(self) -> list[AnimationEffect]:
        """動画用エフェクト"""
        ...
```

### ビルトインプリセット

| プリセット名 | 画像エフェクト | 動画エフェクト |
|------------|-------------|-------------|
| `default` | Ken Burns (1.0→1.1) | なし |
| `kenburns-left-to-right` | Ken Burns (左→右) | なし |
| `kenburns-zoom-in` | Ken Burns (ズームイン) | なし |
| `dramatic` | Zoom (1.2倍) | Zoom (1.1倍) |
| `minimal` | なし | なし |

### カスタムプリセット登録

```python
from teto_core.script.presets import ScenePreset, ScenePresetRegistry
from teto_core.effect.models import AnimationEffect

class MyCustomPreset(ScenePreset):
    @property
    def name(self):
        return "my_custom"

    def get_image_effects(self):
        return [
            AnimationEffect(type="fadeIn", duration=1.0),
            AnimationEffect(
                type="kenburns",
                params={"start_zoom": 1.0, "end_zoom": 1.3, "direction": "diagonal"}
            ),
        ]

    def get_video_effects(self):
        return []

# 登録
ScenePresetRegistry.register(MyCustomPreset())

# 使用
script = {
  "scenes": [
    {
      "preset": "my_custom",
      "narrations": [...],
      "visual": {...}
    }
  ]
}
```

---

## エラーハンドリング

### バリデーションエラー

**Pydantic によるデータ検証**:
```python
try:
    script = Script(**json_data)
except ValidationError as e:
    print("スクリプトのバリデーションに失敗しました:")
    print(e)
```

### コンパイルエラー

**主なエラーケース**:
1. **音声プロファイルが見つからない**:
   ```
   ValueError: ボイスプロファイル 'nonexistent' が見つかりません
   ```

2. **アセットが見つからない**:
   ```
   FileNotFoundError: 指定された画像ファイルが見つかりません: image.jpg
   ```

3. **TTS API エラー**:
   ```
   TTSError: Google Cloud TTS API が失敗しました: [詳細]
   ```

---

## パフォーマンス最適化

### TTS キャッシュ

**キャッシュヒット率の向上**:
- 同じテキスト + 同じ音声設定 = 即座に再利用
- プロファイル名は関係なく、実際の設定値でキャッシュ
- 異なるプロジェクトでもキャッシュを共有

**例**:
```
プロジェクトA: "こんにちは" + Google TTS (voice_id=A)
  → キャッシュに保存

プロジェクトB: "こんにちは" + Google TTS (voice_id=A)
  → キャッシュヒット（API 呼び出しなし）

プロジェクトC: "こんにちは" + Google TTS (voice_id=B)
  → キャッシュミス（異なる音声設定）
```

### 並列処理

**将来の拡張ポイント**:
- 複数シーンの TTS 生成を並列化
- マルチ出力生成を並列化（現在は順次実行）

---

## まとめ

Script → Project コンパイルパイプラインの特徴：

- ✅ **Template Method パターン**: 明確な処理ステップ
- ✅ **キャッシング**: TTS コストの削減
- ✅ **音声設定の柔軟性**: シーン毎に異なる音声を使用可能
- ✅ **タイミング自動計算**: ナレーション長さから自動決定
- ✅ **プリセットシステム**: エフェクトの再利用
- ✅ **拡張性**: カスタムプリセット、TTS プロバイダー追加可能

このパイプラインにより、AI が生成した抽象的な Script から、レンダリング可能な具体的な Project への変換が実現されています。

# シーン毎の音声変更機能

このドキュメントでは、シーン毎に異なるナレーション音声を使用できる機能について詳しく説明します。

---

## 目次

1. [機能概要](#機能概要)
2. [ユースケース](#ユースケース)
3. [実装詳細](#実装詳細)
4. [使用方法](#使用方法)
5. [キャッシュとの統合](#キャッシュとの統合)
6. [ベストプラクティス](#ベストプラクティス)

---

## 機能概要

### 目的

従来の Teto では、動画全体で1つの音声設定（グローバル設定）のみが使用可能でした。この制限により、以下のようなコンテンツの作成が困難でした：

- 対談形式（2人以上の話者）
- 教育コンテンツ（先生と生徒）
- ラジオ番組（ホストとゲスト）
- ドラマ（複数キャラクター）

**シーン毎の音声変更機能**により、各シーンで異なる音声設定を使用できるようになり、複数の話者が登場するコンテンツの作成が可能になります。

### 主な特徴

- ✅ **シーン毎に音声を指定**: 各シーンで異なる TTS 音声を使用
- ✅ **名前付きプロファイル**: 再利用可能な音声設定
- ✅ **DRY 原則**: 重複を避けてコードを整理
- ✅ **後方互換性**: 既存のスクリプトはそのまま動作
- ✅ **キャッシュ対応**: 自動的に最適化されたキャッシング

---

## ユースケース

### 1. 対談形式の動画

**シナリオ**: 2人のホストが交互に話す対談動画

```json
{
  "title": "対談: AI の未来について",
  "voice_profiles": {
    "host_a": {
      "provider": "google",
      "voice_id": "ja-JP-Wavenet-A",
      "pitch": -2.0
    },
    "host_b": {
      "provider": "google",
      "voice_id": "ja-JP-Wavenet-C",
      "pitch": 0.0
    }
  },
  "scenes": [
    {
      "narrations": [{"text": "今日は AI の未来について話しましょう。"}],
      "visual": {"path": "host_a.jpg"},
      "voice_profile": "host_a"
    },
    {
      "narrations": [{"text": "興味深いテーマですね。"}],
      "visual": {"path": "host_b.jpg"},
      "voice_profile": "host_b"
    },
    {
      "narrations": [{"text": "まず、機械学習の進化から始めましょう。"}],
      "visual": {"path": "host_a.jpg"},
      "voice_profile": "host_a"
    }
  ]
}
```

### 2. 教育コンテンツ（先生と生徒）

**シナリオ**: 先生が説明し、生徒が質問する教育動画

```json
{
  "title": "数学レッスン: 二次方程式",
  "voice_profiles": {
    "teacher": {
      "provider": "google",
      "voice_id": "ja-JP-Neural2-B",
      "speed": 1.0,
      "pitch": -2.0
    },
    "student": {
      "provider": "google",
      "voice_id": "ja-JP-Neural2-D",
      "speed": 1.1,
      "pitch": 5.0
    }
  },
  "scenes": [
    {
      "narrations": [{"text": "今日は二次方程式について学びます。"}],
      "visual": {"path": "teacher.jpg"},
      "voice_profile": "teacher"
    },
    {
      "narrations": [{"text": "二次方程式って何ですか？"}],
      "visual": {"path": "student.jpg"},
      "voice_profile": "student"
    },
    {
      "narrations": [{"text": "良い質問です。x の二乗を含む方程式のことです。"}],
      "visual": {"path": "teacher.jpg"},
      "voice_profile": "teacher"
    }
  ]
}
```

### 3. ラジオ番組形式

**シナリオ**: ホスト1名とゲスト2名のラジオ番組

```json
{
  "title": "Tech Talk Radio - エピソード 10",
  "voice_profiles": {
    "host": {
      "provider": "google",
      "voice_id": "ja-JP-Wavenet-A"
    },
    "guest_1": {
      "provider": "elevenlabs",
      "voice_id": "21m00Tcm4TlvDq8ikWAM"
    },
    "guest_2": {
      "provider": "google",
      "voice_id": "ja-JP-Wavenet-C"
    }
  },
  "scenes": [
    {
      "narrations": [{"text": "今日のゲストは、AI 研究の専門家お二人です。"}],
      "voice_profile": "host"
    },
    {
      "narrations": [{"text": "よろしくお願いします。"}],
      "voice_profile": "guest_1"
    },
    {
      "narrations": [{"text": "こちらこそよろしくお願いします。"}],
      "voice_profile": "guest_2"
    }
  ]
}
```

---

## 実装詳細

### データモデル

#### Scene モデルの拡張

**場所**: `packages/core/teto_core/script/models.py:147-217`

```python
class Scene(BaseModel):
    """シーン（台本の基本単位）"""

    # 既存フィールド
    narrations: list[NarrationSegment]
    visual: Visual
    duration: float | None
    pause_after: float
    transition: TransitionConfig | None
    sound_effects: list[SoundEffect]
    note: str | None
    preset: str | None
    mute_video: bool

    # ✨ 新規追加: 音声設定（シーン固有）
    voice: VoiceConfig | None = Field(
        None,
        description="このシーン専用のナレーション音声設定（指定時はグローバル設定を上書き）",
    )
    voice_profile: str | None = Field(
        None,
        description="使用するボイスプロファイル名（Script.voice_profiles から参照）",
    )

    @model_validator(mode="after")
    def validate_voice_config(self) -> "Scene":
        # voice と voice_profile の両方が指定されている場合はエラー
        if self.voice is not None and self.voice_profile is not None:
            raise ValueError("voice と voice_profile は同時に指定できません")
        return self
```

**フィールド説明**:

| フィールド | 型 | 説明 | 使用例 |
|-----------|-----|------|--------|
| `voice` | `VoiceConfig \| None` | シーン固有の音声設定（直接指定） | 一度だけ使う特殊な音声 |
| `voice_profile` | `str \| None` | 名前付きプロファイル参照 | 複数シーンで再利用する音声 |

**制約**:
- `voice` と `voice_profile` は排他的（同時に指定するとエラー）
- どちらも指定しない場合は `script.voice`（グローバル設定）を使用

#### Script モデルの拡張

**場所**: `packages/core/teto_core/script/models.py:268-279`

```python
class Script(BaseModel):
    """台本（AI生成用の抽象データ構造）"""

    title: str
    scenes: list[Scene]

    # グローバル設定
    voice: VoiceConfig = Field(default_factory=VoiceConfig, description="音声設定")

    # ✨ 新規追加: 名前付きボイスプロファイル
    voice_profiles: dict[str, VoiceConfig] | None = Field(
        None,
        description="名前付きボイスプロファイル（シーンから名前で参照可能）",
    )

    # その他のフィールド...
```

**フィールド説明**:

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `voice` | `VoiceConfig` | グローバルデフォルト音声設定 |
| `voice_profiles` | `dict[str, VoiceConfig] \| None` | 名前付き音声プロファイル辞書 |

### 音声設定の解決ロジック

**場所**: `packages/core/teto_core/script/compiler.py:106-140`

#### 優先順位

```
1. scene.voice（直接指定） ← 最優先
   ↓ なければ
2. scene.voice_profile（プロファイル参照）
   ↓ なければ
3. script.voice（グローバルデフォルト） ← デフォルト
```

#### 実装

```python
def _resolve_scene_voice(self, script: Script, scene: Scene) -> VoiceConfig:
    """シーンに適用する音声設定を解決

    優先順位:
    1. scene.voice（直接指定）
    2. scene.voice_profile（名前付きプロファイル参照）
    3. script.voice（グローバルデフォルト）

    Args:
        script: 台本
        scene: シーン

    Returns:
        VoiceConfig: 適用する音声設定

    Raises:
        ValueError: voice_profile が見つからない場合
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

### TTS 生成への統合

**場所**: `packages/core/teto_core/script/compiler.py:183-247`

```python
def _generate_all_narrations(self, script: Script) -> list[list[TTSResult]]:
    """全シーン・全セグメントのナレーションを生成"""
    all_narrations: list[list[TTSResult]] = []

    cache_hits = 0
    cache_misses = 0

    for scene_idx, scene in enumerate(script.scenes):
        scene_narrations: list[TTSResult] = []

        # ✨ シーン固有のvoice設定を解決
        effective_voice = self._resolve_scene_voice(script, scene)

        # プロバイダーに応じて拡張子を決定
        audio_ext = ".wav" if effective_voice.provider == "gemini" else ".mp3"

        for seg_idx, segment in enumerate(scene.narrations):
            # マークアップを除去したテキストをTTSに渡す
            plain_text = strip_markup(segment.text)

            # ✨ effective_voice でキャッシュをチェック
            cached_audio = None
            if self._use_cache:
                cached_audio = self._cache.get(plain_text, effective_voice, audio_ext)

            if cached_audio is not None:
                # キャッシュヒット
                cache_hits += 1
                duration = self._tts.estimate_duration(plain_text, effective_voice)
                result = TTSResult(...)
            else:
                # キャッシュミス - TTS生成
                cache_misses += 1
                result = self._tts.generate(
                    text=plain_text,
                    config=effective_voice,  # ✨ effective_voice を使用
                )
                # キャッシュに保存
                if self._use_cache:
                    self._cache.put(plain_text, effective_voice, audio_ext, result.audio_content)

            # 音声ファイルを保存
            output_path = f"{self._output_dir}/narrations/scene_{scene_idx:03d}_seg_{seg_idx:03d}{audio_ext}"
            result.save(output_path)
            scene_narrations.append(result)

        all_narrations.append(scene_narrations)

    # キャッシュ統計を表示
    total = cache_hits + cache_misses
    if total > 0:
        print(f"  TTS キャッシュ: {cache_hits}/{total} ヒット ({cache_hits * 100 // total}%)")

    return all_narrations
```

---

## 使用方法

### 方法 1: 直接 voice 指定

各シーンで `voice` フィールドに直接 `VoiceConfig` を指定します。

**適用場面**:
- 一度だけ使う特殊な音声
- プロトタイピング

**例**:

```json
{
  "title": "サンプル動画",
  "scenes": [
    {
      "narrations": [{"text": "こんにちは"}],
      "visual": {"path": "image1.jpg"},
      "voice": {
        "provider": "google",
        "voice_id": "ja-JP-Wavenet-A",
        "speed": 1.0,
        "pitch": -2.0
      }
    },
    {
      "narrations": [{"text": "さようなら"}],
      "visual": {"path": "image2.jpg"},
      "voice": {
        "provider": "google",
        "voice_id": "ja-JP-Wavenet-B",
        "speed": 1.1,
        "pitch": 5.0
      }
    }
  ],
  "voice": {"provider": "google"}
}
```

**デメリット**:
- 同じ設定を複数シーンで使う場合、重複が発生
- 保守性が低い

### 方法 2: 名前付きプロファイル（推奨）

`Script.voice_profiles` でプロファイルを定義し、`Scene.voice_profile` で参照します。

**適用場面**:
- 複数シーンで同じ音声を再利用
- 本番環境
- 保守性重視

**例**:

```json
{
  "title": "先生と生徒の対話",
  "voice_profiles": {
    "teacher": {
      "provider": "google",
      "voice_id": "ja-JP-Neural2-B",
      "speed": 1.0,
      "pitch": -2.0
    },
    "student": {
      "provider": "google",
      "voice_id": "ja-JP-Neural2-D",
      "speed": 1.1,
      "pitch": 5.0
    }
  },
  "scenes": [
    {
      "narrations": [{"text": "今日は数学を学びます。"}],
      "visual": {"path": "teacher.jpg"},
      "voice_profile": "teacher"
    },
    {
      "narrations": [{"text": "よろしくお願いします！"}],
      "visual": {"path": "student.jpg"},
      "voice_profile": "student"
    },
    {
      "narrations": [{"text": "まずは基本から始めましょう。"}],
      "visual": {"path": "teacher.jpg"},
      "voice_profile": "teacher"
    }
  ],
  "voice": {"provider": "google"}
}
```

**メリット**:
- DRY 原則（重複排除）
- 保守性が高い（一箇所変更で全シーンに反映）
- 可読性が高い

### 方法 3: グローバル設定のみ（既存の動作）

`Scene.voice` も `Scene.voice_profile` も指定しない場合、`Script.voice` が使用されます。

**例**:

```json
{
  "title": "シンプルな動画",
  "scenes": [
    {
      "narrations": [{"text": "シーン1"}],
      "visual": {"path": "image1.jpg"}
    },
    {
      "narrations": [{"text": "シーン2"}],
      "visual": {"path": "image2.jpg"}
    }
  ],
  "voice": {
    "provider": "google",
    "voice_id": "ja-JP-Wavenet-A"
  }
}
```

**適用場面**:
- 単一話者の動画
- 既存のスクリプトとの互換性維持

---

## キャッシュとの統合

### キャッシュキーの生成

**重要**: キャッシュキーは**テキスト + 音声設定の全フィールド**から生成されます。

```python
cache_key = SHA256({
    "text": "こんにちは",
    "config": {
        "provider": "google",
        "voice_id": "ja-JP-Wavenet-A",
        "language_code": "ja-JP",
        "speed": 1.0,
        "pitch": -2.0,
        "model_id": "eleven_multilingual_v2",
        "output_format": "mp3_44100_128",
        "voice_name": "Kore",
        "gemini_model_id": "gemini-2.5-flash-preview-tts",
        "style_prompt": None,
    }
})[:16]
```

### プロファイル名はキャッシュに影響しない

**重要なポイント**: プロファイル名は解決後に実際の設定値に変換されるため、キャッシュキーには影響しません。

**例**:

```json
{
  "voice_profiles": {
    "narrator_a": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"},
    "narrator_b": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"}
  },
  "scenes": [
    {
      "narrations": [{"text": "こんにちは"}],
      "voice_profile": "narrator_a"
    },
    {
      "narrations": [{"text": "こんにちは"}],
      "voice_profile": "narrator_b"
    }
  ]
}
```

**動作**:
1. シーン1: `narrator_a` → `VoiceConfig(voice_id="ja-JP-Wavenet-A")` → キャッシュキー `a1b2c3...`
2. シーン2: `narrator_b` → `VoiceConfig(voice_id="ja-JP-Wavenet-A")` → キャッシュキー `a1b2c3...`（同じ）
3. **キャッシュヒット！** （API 呼び出しなし）

### キャッシュ最適化の例

```json
{
  "voice_profiles": {
    "host": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"}
  },
  "scenes": [
    {"narrations": [{"text": "こんにちは"}], "voice_profile": "host"},
    {"narrations": [{"text": "さようなら"}], "voice_profile": "host"},
    {"narrations": [{"text": "こんにちは"}], "voice_profile": "host"}
  ]
}
```

**キャッシュ動作**:
- シーン1: "こんにちは" + host → API 呼び出し、キャッシュに保存
- シーン2: "さようなら" + host → API 呼び出し、キャッシュに保存
- シーン3: "こんにちは" + host → **キャッシュヒット**（API 呼び出しなし）

**結果**: 3 つのナレーションに対し、2 回の API 呼び出しのみ（33% コスト削減）

---

## ベストプラクティス

### 1. 名前付きプロファイルを使用する

❌ **悪い例**: 直接指定で重複が多い

```json
{
  "scenes": [
    {
      "narrations": [{"text": "シーン1"}],
      "voice": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"}
    },
    {
      "narrations": [{"text": "シーン2"}],
      "voice": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"}
    },
    {
      "narrations": [{"text": "シーン3"}],
      "voice": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"}
    }
  ]
}
```

✅ **良い例**: プロファイルで重複排除

```json
{
  "voice_profiles": {
    "narrator": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"}
  },
  "scenes": [
    {"narrations": [{"text": "シーン1"}], "voice_profile": "narrator"},
    {"narrations": [{"text": "シーン2"}], "voice_profile": "narrator"},
    {"narrations": [{"text": "シーン3"}], "voice_profile": "narrator"}
  ]
}
```

### 2. わかりやすいプロファイル名を使用する

❌ **悪い例**: 抽象的な名前

```json
{
  "voice_profiles": {
    "voice1": {...},
    "voice2": {...}
  }
}
```

✅ **良い例**: 役割が明確な名前

```json
{
  "voice_profiles": {
    "host": {...},
    "guest": {...},
    "narrator": {...}
  }
}
```

### 3. グローバル設定をフォールバックとして利用

```json
{
  "voice": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"},
  "voice_profiles": {
    "special_voice": {"provider": "elevenlabs", "voice_id": "custom_voice"}
  },
  "scenes": [
    {"narrations": [{"text": "通常のシーン"}]},  // グローバル設定を使用
    {"narrations": [{"text": "特別なシーン"}], "voice_profile": "special_voice"},
    {"narrations": [{"text": "また通常のシーン"}]}  // グローバル設定を使用
  ]
}
```

### 4. キャッシュヒット率を最大化する

✅ **同じテキスト + 同じ音声設定を再利用**:

```json
{
  "voice_profiles": {
    "host": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"}
  },
  "scenes": [
    {"narrations": [{"text": "こんにちは"}], "voice_profile": "host"},
    {"narrations": [{"text": "別のセリフ"}], "voice_profile": "host"},
    {"narrations": [{"text": "こんにちは"}], "voice_profile": "host"}  // キャッシュヒット
  ]
}
```

---

## トラブルシューティング

### エラー: "voice と voice_profile は同時に指定できません"

**原因**: Scene に `voice` と `voice_profile` の両方を指定した

```json
{
  "narrations": [{"text": "..."}],
  "voice": {...},
  "voice_profile": "narrator"  // ❌ エラー
}
```

**解決策**: どちらか一方のみを指定

```json
{
  "narrations": [{"text": "..."}],
  "voice_profile": "narrator"  // ✅ OK
}
```

### エラー: "ボイスプロファイル 'xxx' が見つかりません"

**原因**: 定義されていないプロファイル名を参照

```json
{
  "voice_profiles": {
    "host": {...}
  },
  "scenes": [
    {"narrations": [{"text": "..."}], "voice_profile": "guest"}  // ❌ 未定義
  ]
}
```

**解決策**: プロファイルを定義するか、正しい名前を使用

```json
{
  "voice_profiles": {
    "host": {...},
    "guest": {...}  // ✅ 追加
  }
}
```

### キャッシュヒット率が低い

**原因**: 音声設定が微妙に異なる

**解決策**: プロファイルを使用して設定を統一

---

## まとめ

シーン毎の音声変更機能の特徴：

- ✅ **柔軟性**: シーン毎に異なる音声を使用可能
- ✅ **DRY 原則**: プロファイルで重複を排除
- ✅ **後方互換性**: 既存スクリプトはそのまま動作
- ✅ **キャッシュ最適化**: 自動的に最適化されたキャッシング
- ✅ **エラーハンドリング**: 明確なバリデーションとエラーメッセージ
- ✅ **ユースケース対応**: 対談、教育、ラジオなど多様なコンテンツに対応

この機能により、Teto は複数の話者が登場する高度な動画コンテンツの作成が可能になりました。

from pydantic import BaseModel, Field
from typing import Literal


class TransitionConfig(BaseModel):
    """トランジション設定"""

    type: Literal["crossfade"] = Field("crossfade", description="トランジションタイプ")
    duration: float = Field(0.5, description="トランジション時間（秒）", gt=0)


class AnimationEffect(BaseModel):
    """アニメーション効果の定義"""

    type: Literal[
        "fadein",
        "fadeout",
        "slideIn",
        "slideOut",
        "zoom",
        "kenBurns",
        "blur",
        "colorGrade",
        "vignette",
        "glitch",
        "parallax",
        "bounce",
        "rotate",
    ] = Field(..., description="アニメーションタイプ")
    duration: float = Field(1.0, description="アニメーション時間（秒）", gt=0)
    direction: Literal["left", "right", "top", "bottom"] | None = Field(
        None, description="スライド方向（slideIn/slideOut用）"
    )
    start_scale: float | None = Field(None, description="開始スケール（zoom用）", gt=0)
    end_scale: float | None = Field(None, description="終了スケール（zoom用）", gt=0)

    # Ken Burns用
    pan_start: tuple[float, float] | None = Field(None, description="開始位置（kenBurns用）")
    pan_end: tuple[float, float] | None = Field(None, description="終了位置（kenBurns用）")

    # ブラー用
    blur_amount: float | None = Field(None, description="ブラー量（blur用）", ge=0)

    # カラーグレーディング用
    color_temp: float | None = Field(None, description="色温度（colorGrade用）", ge=-1, le=1)
    saturation: float | None = Field(None, description="彩度（colorGrade用）", ge=0, le=2)
    contrast: float | None = Field(None, description="コントラスト（colorGrade用）", ge=0, le=2)
    brightness: float | None = Field(None, description="明度（colorGrade用）", ge=0, le=2)

    # ビネット用
    vignette_amount: float | None = Field(None, description="ビネット強度（vignette用）", ge=0, le=1)

    # グリッチ用
    glitch_intensity: float | None = Field(None, description="グリッチ強度（glitch用）", ge=0, le=1)

    # 回転用
    rotation_angle: float | None = Field(None, description="回転角度（rotate用、度）")

    # イージング
    easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] | None = Field(
        "easeInOut", description="イージング関数"
    )

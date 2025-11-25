from pydantic import BaseModel, Field
from typing import Literal


class AnimationEffect(BaseModel):
    """アニメーション効果の定義"""

    type: Literal["fadein", "fadeout", "slideIn", "slideOut", "zoom"] = Field(
        ..., description="アニメーションタイプ"
    )
    duration: float = Field(1.0, description="アニメーション時間（秒）", gt=0)
    direction: Literal["left", "right", "top", "bottom"] | None = Field(
        None, description="スライド方向（slideIn/slideOut用）"
    )
    start_scale: float | None = Field(None, description="開始スケール（zoom用）", gt=0)
    end_scale: float | None = Field(None, description="終了スケール（zoom用）", gt=0)

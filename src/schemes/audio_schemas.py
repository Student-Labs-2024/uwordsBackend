from datetime import datetime

from pydantic import BaseModel, Field


class Audio(BaseModel):
    filename: str = Field(examples=["audio_2024-05-21_23-48-47.ogg"])
    extension: str = Field(examples=[".ogg"])
    filepath: str = Field(
        examples=[
            "audio_transfer/audio_6515bf33-e63c-4493-b29d-55f2b70a892d_converted.wav"
        ]
    )
    uploaded_at: datetime = Field(examples=["2024-05-26T10:10:21.520492"])


class YoutubeLink(BaseModel):
    link: str = Field(
        examples=["https://www.youtube.com/shorts/of3729gHjNs?feature=share"]
    )

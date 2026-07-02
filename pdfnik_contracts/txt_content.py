from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TargetKind = Literal["storage_key", "url", "url_batch"]
SourceType = Literal["voice", "audio", "video", "youtube"]
DeliveryMode = Literal["text", "document"]


class TxtTarget(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: TargetKind
    value: str = Field(min_length=1)


class TxtReply(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_id: int
    reply_to_message_id: int | None = None


class TxtDelivery(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_type: SourceType
    mode: DeliveryMode


class TxtCfgOverrides(BaseModel):
    model_config = ConfigDict(frozen=True)

    model: str | None = None
    device: str | None = None
    compute_type: str | None = None
    threads: int | None = Field(default=None, ge=1)
    workers: int | None = Field(default=None, ge=1)
    beam_size: int | None = Field(default=None, ge=1)
    patience: float | None = Field(default=None, ge=0.0)
    vad: bool | None = None
    lang: str | None = None


class YouTubeMetadata(BaseModel):
    """
    YouTube video metadata obtained via yt-dlp --dump-json.
    All fields are optional: yt-dlp may return incomplete JSON
    (private videos, live streams, regional locks).
    """

    url: str
    title: str | None = None
    channel: str | None = None
    uploader: str | None = None  # Channel or uploader name
    upload_date: str | None = None  # "YYYYMMDD"
    duration_sec: float | None = None
    view_count: int | None = None
    description: str | None = None
    thumbnail_url: str | None = None

    @property
    def duration_str(self) -> str:
        """Human-readable duration: '1:23:45' or '3:21'."""
        if not self.duration_sec:
            return "unknown"
        total = int(self.duration_sec)
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    @property
    def upload_date_str(self) -> str:
        """'20240315' -> '15.03.2024'."""
        d = self.upload_date
        if not d or len(d) != 8:
            return ""
        return f"{d[6:8]}.{d[4:6]}.{d[:4]}"


class TxtTranscribeJob(BaseModel):
    """
    Canonical payload for the txt.transcribe queue.

    Published by the Telegram bot:
    {
      "job_id": "...",
      "target": {"kind": "storage_key" | "url" | "url_batch", "value": "..."},
      "reply": {"chat_id": 123, "reply_to_message_id": 456},
      "delivery": {"source_type": "voice", "mode": "text"},
      "extract_mode": "summary" | "learn" | "commands" | "pipeline" | "tips" | "none" | null,
      "cfg": {}
    }

    normalize_legacy_payload also accepts the old flat message format
    (chat_id, storage_key, input_url, source_type, mode at the top level)
    and reshapes it into the nested format above.
    """

    job_id: str = Field(min_length=1)
    target: TxtTarget
    reply: TxtReply | None = None
    delivery: TxtDelivery | None = None
    cfg: TxtCfgOverrides | None = None
    extract_mode: str | None = None
    attempt: int = 1
    max_attempts: int = 3

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        payload = dict(data)

        if payload.get("target") is None:
            storage_key = payload.get("storage_key")
            input_url = payload.get("input_url")

            if storage_key:
                payload["target"] = {"kind": "storage_key", "value": storage_key}
            elif input_url:
                payload["target"] = {"kind": "url", "value": input_url}

        if payload.get("reply") is None:
            chat_id = payload.get("chat_id")
            reply_to_message_id = payload.get("reply_to_message_id")

            if chat_id is not None:
                payload["reply"] = {
                    "chat_id": chat_id,
                    "reply_to_message_id": reply_to_message_id,
                }

        if payload.get("delivery") is None:
            source_type = payload.get("source_type")
            mode = payload.get("mode")

            if source_type is not None or mode is not None:
                payload["delivery"] = {"source_type": source_type, "mode": mode}

        return payload


class TxtDoneResult(BaseModel):
    """
    Canonical payload for the txt.done queue. Discriminated by `status`.
    """

    job_id: str = Field(min_length=1)
    status: Literal["ok", "error"]
    txt_storage_key: str | None = None
    reply: TxtReply | None = None
    delivery: TxtDelivery | None = None
    cached: bool | None = None
    error: str | None = None
    error_code: str | None = None
    # Populated only for YouTube jobs (source_type="youtube").
    youtube_metadata: YouTubeMetadata | None = None
    # LLM-generated extraction; None when provider is disabled or call failed.
    summary: str | None = None
    # Mode used for extraction (summary/learn/commands/pipeline/tips/none).
    extract_mode: str | None = None

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    max_video_size_mb: int = int(os.getenv("MAX_VIDEO_SIZE_MB", "50"))
    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/fileconverter.db"))
    temp_directory: Path = Path(os.getenv("TEMP_DIRECTORY", "temp"))
    conversion_timeout: int = int(os.getenv("CONVERSION_TIMEOUT_SECONDS", "300"))
    ffmpeg_timeout: int = int(os.getenv("FFMPEG_TIMEOUT_SECONDS", "300"))
    port: int = int(os.getenv("PORT", "10000"))
    render_external_url: str = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    webhook_base_url: str = os.getenv("WEBHOOK_BASE_URL", "").rstrip("/")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "fileconverter-webhook-secret")

    @property
    def max_file_size(self): return self.max_file_size_mb * 1024 * 1024
    @property
    def max_video_size(self): return self.max_video_size_mb * 1024 * 1024
    @property
    def public_url(self): return self.webhook_base_url or self.render_external_url

config = Config()

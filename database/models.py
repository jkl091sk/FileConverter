from dataclasses import dataclass

@dataclass
class UserSettings:
    user_id: int
    language: str = "en"
    image_quality: int = 90
    audio_quality: str = "medium"
    preserve_filenames: bool = True
    preserve_metadata: bool = True

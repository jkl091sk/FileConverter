# FileConverter

> Logo placeholder: `assets/logo.png`

A privacy-minded Telegram bot that converts files directly in Telegram. It uses aiogram 3, FFmpeg, Pillow, PyMuPDF/pypdf, LibreOffice headless, SQLite, and isolated temporary work directories.

## Features
- Images: PNG, JPG/JPEG, WEBP, BMP, TIFF, GIF; image → PDF
- Audio: MP3, WAV, OGG, FLAC, AAC, M4A
- Video: MP4, WEBM, MOV, MKV, AVI, GIF; video → MP3/WAV
- Documents: DOCX, PDF, TXT, ODT, RTF, HTML via LibreOffice
- PDF: text extraction, images ZIP, compression, split, selected pages
- Archives: ZIP, 7Z, TAR, TAR.GZ listing/extraction with traversal checks
- Per-user settings, history metadata and statistics
- English, Ukrainian and Russian settings/localization foundation
- Per-conversion temporary directories and automatic cleanup

## Screenshots
Add screenshots here after deploying the bot.

## Requirements
Python 3.12+, FFmpeg, LibreOffice, libmagic.

Ubuntu:
```bash
sudo apt update
sudo apt install python3 python3-venv ffmpeg libreoffice libmagic1
```

Arch Linux:
```bash
sudo pacman -S python ffmpeg libreoffice-fresh file
```

## Installation
```bash
unzip FileConverter.zip
cd FileConverter
cp .env.example .env
nano .env
chmod +x install.sh run.sh
./install.sh
./run.sh
```

## Configuration
`.env`:
```env
BOT_TOKEN=
MAX_FILE_SIZE_MB=50
MAX_VIDEO_SIZE_MB=100
DATABASE_PATH=data/fileconverter.db
TEMP_DIRECTORY=temp
CONVERSION_TIMEOUT_SECONDS=300
FFMPEG_TIMEOUT_SECONDS=300
```

## Commands
`/start`, `/help`, `/formats`, `/settings`, `/history`, `/stats`, `/about`, `/cancel`.

## Project structure
`handlers/` Telegram flows; `converters/` conversion engines; `services/` detection, i18n, cleanup and orchestration; `database/` SQLite; `utils/` security/helpers; `locales/` translations.

## Security & privacy
Files are not permanently stored. Every upload is placed in a unique temporary directory and removed after success/error/cancel. User input is never interpolated into shell commands: external programs are started with argument arrays and `shell=False` behavior. Filenames are sanitized, MIME/type is validated, conversions have limits/timeouts, archive paths are checked, archive file counts and expanded size are bounded, and uploaded executables are never executed.

For public deployment, also set Telegram-side upload expectations appropriately and run the bot as an unprivileged OS user, ideally inside a container/systemd sandbox with resource limits.

## Notes
Some document conversions depend on the exact LibreOffice build and installed fonts/codecs. The bot only advertises document targets implemented through LibreOffice. Corrupt/incompatible input is handled as a conversion failure rather than crashing the bot.

## License
MIT.

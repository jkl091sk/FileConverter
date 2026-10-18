# FileConverter on Render

This edition runs as an HTTP webhook service instead of Telegram long polling.

## Deploy
1. Create a GitHub repository and upload the contents of the `FileConverter` folder.
2. In Render choose **New → Blueprint** (or create a Docker Web Service).
3. Connect the GitHub repository.
4. Render reads `render.yaml`.
5. Set the secret environment variable `BOT_TOKEN` to the token from BotFather.
6. Deploy.
7. Open `/health` on the Render service URL. It should return JSON with `"status":"ok"`.
8. Send `/start` to the Telegram bot.

`RENDER_EXTERNAL_URL` is used automatically as the Telegram webhook base URL. `WEBHOOK_BASE_URL` is only needed if you use a custom public URL.

## Important free-tier note
SQLite lives on the service filesystem. On ephemeral hosting, conversion history/settings may reset after redeploy/restart. Uploaded and converted files are intentionally temporary and are deleted after processing.

For durable user settings/history, move SQLite to a persistent database/service later.

## Included system software
The Docker image installs FFmpeg and LibreOffice Writer, plus common fonts.

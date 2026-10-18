import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import config
from database.database import init_db
from handlers import start, files, callbacks, settings, history
from services.cleanup import cleanup_stale_temp
from utils.logger import setup_logging

WEBHOOK_PATH = "/telegram/webhook"

async def health(_):
    return web.json_response({"status":"ok","service":"FileConverter"})

async def on_startup(bot: Bot):
    if not config.public_url:
        raise RuntimeError("No public URL. On Render, RENDER_EXTERNAL_URL should be set automatically.")
    url = config.public_url + WEBHOOK_PATH
    await bot.set_webhook(
        url=url,
        secret_token=config.webhook_secret,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=False,
    )
    logging.info("Webhook configured: %s", url)

async def on_shutdown(bot: Bot):
    logging.info("FileConverter shutting down")

setup_logging()
if not config.bot_token:
    raise RuntimeError("BOT_TOKEN is empty.")

config.temp_directory.mkdir(parents=True, exist_ok=True)
config.database_path.parent.mkdir(parents=True, exist_ok=True)

bot = Bot(config.bot_token)
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(start.router, settings.router, history.router, files.router, callbacks.router)
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

async def prepare():
    await init_db()
    await cleanup_stale_temp()

asyncio.run(prepare())

app = web.Application(client_max_size=(config.max_file_size_mb + 5) * 1024 * 1024)
app.router.add_get("/", health)
app.router.add_get("/health", health)

SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
    secret_token=config.webhook_secret,
).register(app, path=WEBHOOK_PATH)

setup_application(app, dp, bot=bot)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=config.port)

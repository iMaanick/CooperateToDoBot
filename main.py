import asyncio
import os
import asyncpg
from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import (
    DialogManager, setup_dialogs, StartMode, )
from dotenv import load_dotenv
from create_to_do.create_to_do import create_task_dialog, CreateTask
from DbMiddleware import DbMiddleware
from Profile.profile import Profile, profile_dialog


async def start(message: Message, dialog_manager: DialogManager, pool: asyncpg.pool.Pool):
    await pool.execute(f"insert into users (user_id, name, username) select {message.from_user.id}, "
                       f"'{message.from_user.first_name}', '{message.from_user.username}'"
                       f" where not exists (select null from users where (user_id) = ({message.from_user.id}))")
    await dialog_manager.start(CreateTask.start_create_task, mode=StartMode.RESET_STACK)


async def profile(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(Profile.start_profile, mode=StartMode.RESET_STACK)


async def main():
    load_dotenv()
    print("Starting bot")
    pool_connect = await asyncpg.create_pool(
        host=os.environ.get("HOST"),
        user=os.environ.get("USER"),
        password=os.environ.get("PASSWORD"),
        database=os.environ.get("DATABASE"))
    # res = await connection.fetch("""SELECT * FROM users;""")
    # for result in res:
    #     print("user_id: ", result["user_id"], "name: ", result["name"])
    storage = MemoryStorage()
    bot = Bot(token=os.environ.get("BOT_TOKEN"))
    dp = Dispatcher(storage=storage)
    dp.update.middleware.register(DbMiddleware(pool_connect))
    dp.message.register(start, F.text == "/start")
    dp.message.register(profile, F.text == "/profile")
    dialog_router = Router()
    dialog_router.include_routers(
        create_task_dialog, profile_dialog
    )
    dp.include_router(dialog_router)
    setup_dialogs(dp)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())

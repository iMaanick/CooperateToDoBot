import operator
from datetime import date
from typing import Any

from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Calendar, ManagedCalendarAdapter,
)
from aiogram_dialog.widgets.kbd import Group, Select, Button
from aiogram_dialog.widgets.kbd import (
    Multiselect, ScrollingGroup, SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
import pprint
from aiogram_dialog.widgets.input import TextInput


class Profile(StatesGroup):
    start_profile = State()
    update_options = State()
    update_name = State()


async def set_name(message: Message, text_input: TextInput, manager: DialogManager, text: str):
    manager.current_context().dialog_data["update_name"] = text
    await manager.switch_to(Profile.update_name)


async def update_name(c: CallbackQuery, button: Button, manager: DialogManager):
    data = await manager.middleware_data["pool"]. \
        fetchrow(f"update users set name = '{manager.current_context().dialog_data['update_name']}' "
                 f"where user_id = {c.from_user.id}")
    manager.current_context().dialog_data.pop("update_name", None)
    await  manager.switch_to(Profile.start_profile)

async def getter_profile_data(dialog_manager: DialogManager, event_from_user, **kwargs):
    data = await dialog_manager.middleware_data["pool"]. \
        fetchrow(f"SELECT * FROM users where user_id = {event_from_user.id}")
    data = dict(data)
    dialog_manager.current_context().dialog_data["name"] = data["name"]
    dialog_manager.current_context().dialog_data["user_id"] = data["user_id"]
    dialog_manager.current_context().dialog_data["username"] = data["username"]
    pprint.pprint(dialog_manager.current_context().dialog_data)

    return {}


profile_dialog = Dialog(
    Window(
        Format("Ваши данные:"),
        Format("Name: {dialog_data[name]}", F["dialog_data"].func(lambda dialog_data: "name" in dialog_data)),
        Format("User_id: {dialog_data[user_id]}", F["dialog_data"].func(lambda dialog_data: "user_id" in dialog_data)),
        Format("Username: {dialog_data[username]}",
               F["dialog_data"].func(lambda dialog_data: "username" in dialog_data)),

        SwitchTo(Const("Обновить данные"), id="start_profile_update", state=Profile.update_options),
        getter=getter_profile_data,
        state=Profile.start_profile
    ),
    Window(
        Format("Ваши данные:"),
        Format("Name: {dialog_data[name]}", F["dialog_data"].func(lambda dialog_data: "name" in dialog_data)),
        Format("User_id: {dialog_data[user_id]}", F["dialog_data"].func(lambda dialog_data: "user_id" in dialog_data)),
        Format("Username: {dialog_data[username]}",
               F["dialog_data"].func(lambda dialog_data: "username" in dialog_data)),
        SwitchTo(Const("Назад"), id="update_options_back", state=Profile.start_profile),
        SwitchTo(Const("Name"), id="update_options_name", state=Profile.update_name),
        # SwitchTo(Const("Username"), id="update_options_username", state=Profile.start_profile),
        state=Profile.update_options
    ),
    Window(
        Format("Ваши данные:"),
        Format("Name: {dialog_data[name]}", F["dialog_data"].func(lambda dialog_data: "name" in dialog_data)),
        Format("Вы хотите изменить name на: {dialog_data[update_name]}", F["dialog_data"].
               func(lambda dialog_data: "update_name" in dialog_data)),
        TextInput(id="input_name", on_success=set_name),
        SwitchTo(Const("Назад"), id="update_options_back", state=Profile.start_profile),
        Button(Const("Обновить"), id="update_name_set", on_click=update_name),
        state=Profile.update_name
    ),
)

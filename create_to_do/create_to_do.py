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

from TimePager import TimePager


async def set_name(message: Message, text_input: TextInput, manager: DialogManager, text: str):
    manager.current_context().dialog_data["name"] = text


async def set_description(message: Message, text_input: TextInput, manager: DialogManager, text: str):
    manager.current_context().dialog_data["description"] = text


async def add_own_tag(message: Message, text_input: TextInput, manager: DialogManager, text: str):
    if "own_tags" in manager.current_context().dialog_data:
        manager.current_context().dialog_data["own_tags"].append((text, text))
    else:
        manager.current_context().dialog_data["own_tags"] = [(text, text)]


class CreateTask(StatesGroup):
    start_create_task = State()
    set_name = State()
    set_description = State()
    set_tags = State()
    add_own_tags = State()
    set_to_do_date = State()
    set_to_do_time = State()
    save_to_do = State()


tags = [
    ("Работа", "Работа"),
    ("Личное", "Личное"),
    ("Покупки", "Покупки"),
    ("Фитнес", "Фитнес"),
    ("Учеба", "Учеба"),
    ("Дом", "Дом"),
    ("Социальный", "Социальный"),
    ("Путешествие", "Путешествие"),
    ("Здоровье", "Здоровье"),
    ("Семья", "Семья")
]


async def get_text(dialog_manager: DialogManager, **kwargs):
    if "tags" in dialog_manager.current_context().widget_data:
        output_str = ""
        for tag in dialog_manager.current_context().widget_data["tags"]:
            output_str += f"•{tag}\n"
        return {"tags": output_str
                }
    return {"no_tags": "---"
            }


async def get_user_tags(dialog_manager: DialogManager, **kwargs):
    if "own_tags" in dialog_manager.current_context().dialog_data:
        dialog_manager.current_context().dialog_data["own_tags"] = list(set(dialog_manager.current_context().
                                                                            dialog_data["own_tags"]))
        output_buttons = []
        user_tags_str = ""
        for tag in dialog_manager.current_context().dialog_data["own_tags"]:
            output_buttons.append(tag)
            user_tags_str += f"•{tag[0]}\n"
        print(user_tags_str)
        return {"user_tags": output_buttons,
                "user_tags_str": user_tags_str}
    return {"no_user_tags": "---"
            }


async def set_tags_back(c: CallbackQuery, button: Button, manager: DialogManager):
    # manager.current_context().widget_data
    manager.current_context().dialog_data["tags"] = list(set(manager.current_context().widget_data["tags"]))
    await manager.switch_to(CreateTask.start_create_task)


async def on_date_selected(callback: CallbackQuery, widget: ManagedCalendarAdapter, manager: DialogManager,
                           selected_date: date):
    manager.current_context().dialog_data["date"] = selected_date
    await manager.switch_to(CreateTask.set_to_do_time)


async def on_time_selected(callback: CallbackQuery, widget: Any, manager: DialogManager,
                           selected_time: str):
    manager.current_context().dialog_data["time"] = selected_time
    await manager.switch_to(CreateTask.start_create_task)


ID_SCROLL_NO_PAGER = "scroll_no_pager"


async def button_time_getter(**kwargs):
    output = []
    buttons_time = []
    for i in ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15",
              "16", "17", "18", "19", "20", "21", "22", "23"]:
        buttons_time.append((str(i), str(i)))
        for j in ["00", "15", "30", "45"]:
            output.append((str(i) + ":" + j, str(i) + ":" + j))
    return {
        "time": output,
        "buttons_time": buttons_time
    }


create_task_dialog = Dialog(
    Window(
        Const("Выберете поля, которые вы хотите заполнить"),
        Group(
            SwitchTo(Const("Название"), id="start_create_task_set_name", state=CreateTask.set_name),
            SwitchTo(Const("Описание"), id="start_create_task_set_description", state=CreateTask.set_description),
            SwitchTo(Const("Дата"), id="start_create_task_set_notification",
                     state=CreateTask.set_to_do_date),
            SwitchTo(Const("Тэги"), id="start_create_task_set_tags", state=CreateTask.set_tags),
            SwitchTo(Const("Сохранить"), id="start_create_task_save", state=CreateTask.save_to_do),

            width=2
        ),
        state=CreateTask.start_create_task,
    ),
    Window(
        Format("Вы ввели {dialog_data[name]}.\nЕсли хотите изменить название, то введите новое:",
               F["dialog_data"].func(lambda dialog_data: "name" in dialog_data)),
        Format("Введите название toDo", F["dialog_data"].func(lambda dialog_data: "name" not in dialog_data)),
        TextInput(id="set_name_text_input", on_success=set_name),
        Group(
            SwitchTo(Const("Назад"), id="set_name_back", state=CreateTask.start_create_task),
            width=2
        ),
        state=CreateTask.set_name,
    ),
    Window(
        Format("Вы ввели {dialog_data[description]}.\nЕсли хотите изменить описание то введите новое:",
               F["dialog_data"].func(lambda dialog_data: "description" in dialog_data)),
        Format("Введите описание toDo", F["dialog_data"].func(lambda dialog_data: "description" not in dialog_data)),
        TextInput(id="set_description_text_input", on_success=set_description),
        Group(
            SwitchTo(Const("Назад"), id="set_description_back", state=CreateTask.start_create_task),
            width=2
        ),
        state=CreateTask.set_description,
    ),
    Window(
        Format("Вы выбрали: \n\n{tags}",
               F.func(lambda widget_data: "tags" in widget_data)),
        Format("Выберете тэги к toDo ", F.func(lambda widget_data: "tags" not in widget_data)),
        Group(
            Multiselect(
                Format("🟢 {item[0]}"),
                Format("{item[0]}"),
                id="tags",
                item_id_getter=operator.itemgetter(1),
                items=tags,
            ),
            width=2,
        ),
        Group(
            Button(Const("Назад"), id="set_tags_back", on_click=set_tags_back),
            SwitchTo(Const("Добавить свои тэги"), id="set_tags_to_add_own_tags", state=CreateTask.add_own_tags),

            width=2
        ),
        getter=get_text,
        state=CreateTask.set_tags,
    ),
    Window(
        Format("Вы ввели: \n{user_tags_str} Выберите, которые хотите добавить", F["dialog_data"]["own_tags"]),
        Format("Введите свои тэги", F.is_not(F["dialog_data"]["own_tags"])),
        TextInput(id="add_own_tag", on_success=add_own_tag),
        Group(
            Multiselect(
                Format("🟢 {item[0]}"),
                Format("{item[0]}"),
                id="tags",
                item_id_getter=operator.itemgetter(1),
                items="user_tags",
            ),
            width=2,
            when=F["dialog_data"]["own_tags"]
        ),
        Group(
            SwitchTo(Const("Назад"), id="add_own_tags_back", state=CreateTask.set_tags),
            width=2
        ),
        getter=get_user_tags,
        state=CreateTask.add_own_tags,
    ),
    Window(
        Const("Введите дату"),
        Calendar(
            id="calendar",
            on_click=on_date_selected,
        ),
        state=CreateTask.set_to_do_date,
    ),
    Window(
        Format("Вы выбрали {dialog_data[date]}\n"
               "Теперь выберете время:"),
        ScrollingGroup(
            TimePager(
                scroll=ID_SCROLL_NO_PAGER,
                page_text=Format("{target_page}"),
                current_page_text=Format("{current_page}"),
            ),
            height=1,
            width=8,
            id="to_do_time",
        ),
        ScrollingGroup(
            Select(
                # Format("✓ {item[0]}"),
                Format("{item[0]}"),
                id="exact_time",
                items="time",
                item_id_getter=operator.itemgetter(1),
                on_click=on_time_selected,
            ),
            width=1,
            height=4,
            hide_pager=True,
            id=ID_SCROLL_NO_PAGER,
        ),
        SwitchTo(Const("Назад"), id="set_to_do_time_back", state=CreateTask.start_create_task),
        getter=button_time_getter,
        state=CreateTask.set_to_do_time),
    Window(
        Format("Название: {dialog_data[name]}", F["dialog_data"].func(lambda dialog_data: "name" in dialog_data)),
        Format("Название: не введено", F["dialog_data"].func(lambda dialog_data: "name" not in dialog_data)),
        Format("Описание: {dialog_data[description]}",
               F["dialog_data"].func(lambda dialog_data: "description" in dialog_data)),
        Format("Описание: не введено", F["dialog_data"].func(lambda dialog_data: "description" not in dialog_data)),
        Format("Тэги: {dialog_data[tags]}", F["dialog_data"].func(lambda dialog_data: "tags" in dialog_data)),
        Format("Тэги: не введены", F["dialog_data"].func(lambda dialog_data: "tags" not in dialog_data)),
        Format("Дата: {dialog_data[date]} {dialog_data[time]}", F["dialog_data"].
               func(lambda dialog_data: "time" in dialog_data)),
        Format("Дата: не введена", F["dialog_data"].func(lambda dialog_data: "time" not in dialog_data)),
        Group(
            SwitchTo(Const("Назад"), id="set_to_do_time_back", state=CreateTask.start_create_task),
            width=2
        ),
        state=CreateTask.save_to_do,
    ),
)
from typing import List, Dict

from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram_dialog import DialogManager, DialogProtocol
from aiogram_dialog.widgets.kbd import SwitchInlineQuery
from aiogram_dialog.widgets.kbd import Counter
from aiogram_dialog.widgets.text import Const


class SwitchInlineQueryCurrentChat(SwitchInlineQuery):
    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    switch_inline_query_current_chat=await self.switch_inline.render_text(
                        data, manager,
                    ),
                ),
            ],
        ]


class CustomMoneyCounter(Counter):
    def __init__(self, custom_value_minus=Const("-10"), custom_value_plus=Const("+10"), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_value_minus = custom_value_minus
        self.custom_value_plus = custom_value_plus

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:

        kbd = await super()._render_keyboard(data, manager)

        new_row = []

        if self.custom_value_minus:
            minus = await self.custom_value_minus.render_text(data, manager)
            new_row.append(
                InlineKeyboardButton(
                    text=minus,
                    callback_data=self._item_callback_data("-10"),
                ),
            )

        if self.custom_value_plus:
            plus = await self.custom_value_plus.render_text(data, manager)
            new_row.append(
                InlineKeyboardButton(
                    text=plus,
                    callback_data=self._item_callback_data("+10"),
                ),
            )
        kbd.extend([new_row])
        return kbd

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        await self.on_click.process_event(
            callback, self.managed(manager), manager,
        )

        value = self.get_value(manager)
        if data == "+":
            value += self.increment
            if value > self.max and self.cycle:
                value = self.min
            await self.set_value(manager, value)
        elif data == "-":
            value -= self.increment
            if value < self.min and self.cycle:
                value = self.max
            await self.set_value(manager, value)
        elif data == "":
            await self.on_text_click.process_event(
                callback, self.managed(manager), manager,
            )
        elif data == "+10":
            value += 10
            if value > self.max and self.cycle:
                value = self.min

            await self.set_value(manager, value)
        elif data == "-10":
            value -= 10
            if value < self.min and self.cycle:
                value = self.max

            await self.set_value(manager, value)

        return True

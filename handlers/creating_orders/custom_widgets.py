from typing import Dict, List
from datetime import timedelta, date

from aiogram.types import InlineKeyboardButton
from aiogram_dialog.widgets.common import WhenCondition
from babel.dates import format_date

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import (
    Calendar, CalendarScope, CalendarUserConfig,
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView, CalendarMonthView, CalendarScopeView, CalendarYearsView, empty_button,
    next_month_begin, get_today,
)
from aiogram_dialog.widgets.text import Text


class DateText(Text):

    def __init__(self, dt_format: str, when: WhenCondition = None):
        super().__init__(when=when)
        self.dt_format = dt_format

    async def _render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        dt = data.get("date")
        formatted_date = format_date(dt, self.dt_format, locale="ukr_UA")

        char_ind = len(formatted_date)

        for ind, char in enumerate(formatted_date):
            if char.isalpha():
                char_ind = ind
                break

        return formatted_date[:char_ind] + formatted_date[char_ind:].capitalize()


class CustomCalendarDaysView(CalendarDaysView):

    async def _render_days(
            self,
            config: CalendarUserConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        keyboard = []
        # align beginning
        start_date = offset.replace(day=1)  # month beginning
        min_date = max(self.config.min_date, start_date)
        days_since_week_start = start_date.weekday() - config.firstweekday
        if days_since_week_start < 0:
            days_since_week_start += 7
        start_date -= timedelta(days=days_since_week_start)
        end_date = next_month_begin(offset) - timedelta(days=1)
        # align ending
        max_date = min(self.config.max_date, end_date)
        days_since_week_start = end_date.weekday() - config.firstweekday
        days_till_week_end = (6 - days_since_week_start) % 7
        end_date += timedelta(days=days_till_week_end)
        # add days
        today = get_today(config.timezone)
        for offset in range(0, (end_date - start_date).days, 7):
            row = []
            for row_offset in range(7):
                days_offset = timedelta(days=(offset + row_offset))
                current_date = start_date + days_offset
                if min_date <= current_date <= max_date and current_date >= date.today():
                    row.append(await self._render_date_button(
                        current_date, today, data, manager,
                    ))
                else:
                    row.append(empty_button())
            keyboard.append(row)
        return keyboard


class CustomCalendar(Calendar):

    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CustomCalendarDaysView(
                self._item_callback_data, self.config,
                header_text=DateText("LLLL Y"),
                prev_month_text=DateText("<< LLLL Y"),
                next_month_text=DateText("LLLL Y >>"),
                weekday_text=DateText("EE"),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data, self.config,
                month_text=DateText("LLLL"),
                this_month_text=DateText("[ LLLL ]"),
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data, self.config,
            ),
        }

    async def _get_user_config(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> CalendarUserConfig:
        return CalendarUserConfig(
            firstweekday=7,
        )

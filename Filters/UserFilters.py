from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class Has_One_Chan_Filter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return True if callback.data.split("_")[0] == "one" or callback.data.split("_")[0] == "chan" else False

class Get_Buy_Message_Filter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return True if callback.data.isdigit() and int(callback.data) < 7 else False

class Redact_Card_Filter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return True if callback.data.isdigit() and int(callback.data.split("_")[0]) >= 15 else False

class Show_All_Cards_Filter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return True if "choose_" in callback.data or "redact_" in callback.data or "destroy_" in callback.data else False


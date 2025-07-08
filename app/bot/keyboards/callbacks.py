from aiogram.filters.callback_data import CallbackData

class ServiceCallback(CallbackData, prefix="service"):
    action: str
    service_id: int

class PaginationCallback(CallbackData, prefix="pag"):
    action: str
    page: int
    category_name: str
import reflex as rx
from app.state import AppState
from app.components.sidebar import sidebar
from app.components.header import header
from app.components.stats_cards import stats_cards
from app.components.transaction_list import transaction_list
from app.components.transaction_form import transaction_form


def dashboard() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                stats_cards(),
                transaction_list(),
                class_name="p-4 md:p-6 flex-1 flex flex-col gap-6",
            ),
            class_name="flex flex-col flex-1 overflow-hidden",
        ),
        transaction_form(),
        class_name="flex min-h-screen w-full bg-gray-50 font-['Inter']",
    )
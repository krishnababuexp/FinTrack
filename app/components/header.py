import reflex as rx
from app.state import AppState


def header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.h1(
                rx.match(
                    AppState.router.page.path,
                    ("/", "Dashboard"),
                    ("/budgets", "Budgets"),
                    ("/analytics", "Analytics"),
                    ("/insights", "Insights"),
                    "Dashboard",
                ),
                class_name="font-semibold text-lg md:text-2xl text-gray-800",
            )
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("circle_plus", class_name="mr-2 h-4 w-4"),
                "Add Transaction",
                on_click=AppState.toggle_transaction_dialog,
                class_name="flex items-center text-sm font-medium bg-blue-600 text-white px-4 py-2 rounded-lg shadow-sm hover:bg-blue-700 transition-colors",
            ),
            rx.el.div(
                rx.el.button(
                    rx.image(
                        src=f"https://api.dicebear.com/9.x/initials/svg?seed=User",
                        class_name="h-8 w-8 rounded-full border-2 border-white",
                    ),
                    class_name="rounded-full",
                ),
                class_name="relative ml-4",
            ),
        ),
        class_name="flex items-center justify-between h-16 border-b bg-white px-4 md:px-6 sticky top-0 z-30",
    )
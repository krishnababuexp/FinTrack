import reflex as rx
from app.state import AppState


def stat_card(
    icon: str, title: str, value: rx.Var[float], color_class: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(title, class_name="text-sm font-medium text-gray-500"),
            rx.icon(icon, class_name="h-4 w-4 text-gray-400"),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.el.p(
                f"${value.to_string()}", class_name=f"text-2xl font-bold {color_class}"
            ),
            rx.el.p("+20.1% from last month", class_name="text-xs text-gray-500"),
            class_name="mt-2",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow",
    )


def stats_cards() -> rx.Component:
    return rx.el.div(
        stat_card("arrow_up", "Total Income", AppState.total_income, "text-green-600"),
        stat_card(
            "arrow_down", "Total Expenses", AppState.total_expenses, "text-red-600"
        ),
        stat_card(
            "banknote", "Current Balance", AppState.current_balance, "text-blue-600"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h3("Pending", class_name="text-sm font-medium text-gray-500"),
                rx.icon("badge_alert", class_name="h-4 w-4 text-gray-400"),
                class_name="flex items-center justify-between",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p("Payables", class_name="text-xs text-gray-500"),
                    rx.el.p(
                        f"${AppState.pending_payables.to_string()}",
                        class_name="font-bold text-orange-500",
                    ),
                ),
                rx.el.div(
                    rx.el.p("Receivables", class_name="text-xs text-gray-500"),
                    rx.el.p(
                        f"${AppState.pending_receivables.to_string()}",
                        class_name="font-bold text-teal-500",
                    ),
                ),
                class_name="mt-2 flex justify-between items-center",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow",
        ),
        class_name="grid gap-4 md:grid-cols-2 lg:grid-cols-4",
    )
import reflex as rx
from app.state import AppState
from app.components.sidebar import sidebar
from app.components.header import header
from app.components.transaction_form import transaction_form

TOOLTIP_PROPS = {
    "content_style": {
        "background": "white",
        "border_color": "#E8E8E8",
        "border_radius": "0.75rem",
        "font_family": "sans-serif",
        "font_size": "0.875rem",
    },
    "separator": " : ",
}


def income_expense_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Income vs. Expenses (Last 6 Months)",
            class_name="font-semibold text-gray-800",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-25"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.x_axis(data_key="month"),
            rx.recharts.y_axis(),
            rx.recharts.line(data_key="income", type_="monotone", stroke="#10b981"),
            rx.recharts.line(data_key="expense", type_="monotone", stroke="#ef4444"),
            data=AppState.income_vs_expense_data,
            height=300,
            class_name="[&_.recharts-tooltip-cursor]:stroke-gray-300",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def category_pie_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Expense by Category (Current Month)",
            class_name="font-semibold text-gray-800",
        ),
        rx.recharts.pie_chart(
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.pie(
                data=AppState.expense_by_category_data,
                data_key="value",
                name_key="name",
                cx="50%",
                cy="50%",
                outer_radius=80,
                fill="#8884d8",
                label=True,
                stroke="#fff",
                stroke_width=2,
            ),
            height=300,
            class_name="[&_.recharts-tooltip-cursor]:stroke-gray-300",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col items-center",
    )


def cash_flow_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Cash Flow Over Time", class_name="font-semibold text-gray-800"),
        rx.recharts.area_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-25"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.x_axis(data_key="date"),
            rx.recharts.y_axis(),
            rx.recharts.area(
                data_key="balance",
                type_="monotone",
                stroke="#3b82f6",
                fill="#3b82f6",
                fill_opacity=0.3,
            ),
            data=AppState.cash_flow_data,
            height=300,
            class_name="[&_.recharts-tooltip-cursor]:stroke-gray-300",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def analytics_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                rx.el.div(
                    rx.el.h1(
                        "Financial Analytics",
                        class_name="text-2xl font-bold text-gray-800",
                    ),
                    class_name="flex justify-between items-center mb-6",
                ),
                rx.el.div(
                    income_expense_chart(),
                    category_pie_chart(),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-6",
                ),
                rx.el.div(cash_flow_chart(), class_name="mt-6"),
                class_name="p-4 md:p-6 flex-1 flex flex-col gap-6",
            ),
            class_name=rx.cond(
                AppState.sidebar_collapsed,
                "flex flex-col flex-1 transition-all duration-300 ease-in-out ml-20",
                "flex flex-col flex-1 transition-all duration-300 ease-in-out ml-64",
            ),
        ),
        transaction_form(),
        class_name="flex min-h-screen w-full bg-gray-50 font-['Inter']",
    )
import reflex as rx
from app.state import AppState
from app.components.sidebar import sidebar
from app.components.header import header
from app.components.transaction_form import transaction_form


def insight_card(
    title: str, description: str, on_click: rx.event.EventType
) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.h3(title, class_name="font-semibold text-gray-800 text-left"),
            rx.el.p(description, class_name="text-sm text-gray-500 text-left"),
            class_name="flex flex-col gap-1",
        ),
        rx.icon("arrow-right", class_name="h-5 w-5 text-gray-400"),
        on_click=on_click,
        class_name="flex items-center justify-between w-full p-4 bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow",
    )


def investment_card(rec: dict) -> rx.Component:
    color_map = {
        "Conservative": "bg-blue-100 text-blue-800",
        "Moderate": "bg-yellow-100 text-yellow-800",
        "Aggressive": "bg-red-100 text-red-800",
    }
    return rx.el.div(
        rx.el.div(
            rx.el.h3(rec["title"], class_name="font-semibold text-gray-900"),
            rx.el.span(
                rec["risk_level"],
                class_name=f"px-2 py-1 text-xs font-medium rounded-full {color_map.get(rec['risk_level'], 'bg-gray-100 text-gray-800')}",
            ),
            class_name="flex justify-between items-center",
        ),
        rx.el.p(rec["description"], class_name="text-sm text-gray-600 mt-2"),
        rx.el.p(
            f"Suggested Allocation: ${rec['allocation'].to_string()}",
            class_name="text-sm font-bold text-gray-800 mt-3",
        ),
        class_name="bg-white p-4 rounded-lg border border-gray-200 shadow-sm",
    )


def alert_card(alert: dict) -> rx.Component:
    icon_map = {
        "warning": ("alert-triangle", "text-yellow-600"),
        "error": ("alert-circle", "text-red-600"),
        "info": ("info", "text-blue-600"),
    }
    icon, color = icon_map.get(alert.get("type", "info"), ("info", "text-blue-600"))
    return rx.el.div(
        rx.icon(icon, class_name=f"h-6 w-6 {color}"),
        rx.el.div(
            rx.el.h3(alert["title"], class_name="font-semibold text-gray-800"),
            rx.el.p(alert["message"], class_name="text-sm text-gray-600"),
            class_name="flex-1",
        ),
        class_name="flex items-start gap-4 p-4 bg-white rounded-lg border border-gray-200 shadow-sm",
    )


def insights_dialog() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black bg-opacity-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.el.h2(
                        AppState.current_insight.get("title", "Insight"),
                        class_name="text-xl font-bold text-gray-900",
                    ),
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            class_name="p-1 rounded-full hover:bg-gray-100",
                            aria_label="Close",
                        )
                    ),
                    class_name="flex items-center justify-between pb-4 border-b",
                ),
                rx.el.p(
                    AppState.current_insight.get("description", ""),
                    class_name="mt-4 text-gray-600",
                ),
                rx.cond(
                    AppState.current_insight.contains("potential_savings"),
                    rx.el.div(
                        rx.el.p("Potential Monthly Savings:", class_name="font-medium"),
                        rx.el.p(
                            f"${AppState.current_insight.get('potential_savings', 0).to_string()}",
                            class_name="text-2xl font-bold text-green-600",
                        ),
                        class_name="mt-4 p-4 bg-green-50 rounded-lg text-center",
                    ),
                    None,
                ),
                class_name="bg-white p-6 rounded-2xl shadow-xl w-full max-w-md",
            ),
        ),
        open=AppState.show_insights_dialog,
        on_open_change=AppState.close_insights_dialog,
    )


def insights_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                rx.el.div(
                    rx.el.h1(
                        "AI-Powered Insights",
                        class_name="text-2xl font-bold text-gray-800",
                    ),
                    class_name="mb-6",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Smart Alerts",
                            class_name="text-lg font-semibold text-gray-800 mb-4",
                        ),
                        rx.cond(
                            AppState.smart_alerts.length() > 0,
                            rx.el.div(
                                rx.foreach(AppState.smart_alerts, alert_card),
                                class_name="flex flex-col gap-4",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "All clear! No alerts at the moment.",
                                    class_name="text-gray-500",
                                ),
                                class_name="p-8 text-center border-2 border-dashed rounded-lg",
                            ),
                        ),
                    ),
                    rx.el.div(
                        rx.el.h2(
                            "Savings Suggestions",
                            class_name="text-lg font-semibold text-gray-800 mb-4",
                        ),
                        rx.cond(
                            AppState.savings_suggestions.length() > 0,
                            rx.el.div(
                                rx.foreach(
                                    AppState.savings_suggestions,
                                    lambda s: insight_card(
                                        s["title"],
                                        s["description"],
                                        lambda: AppState.show_insight_details(s),
                                    ),
                                ),
                                class_name="flex flex-col gap-4",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "You're doing great! No specific savings suggestions right now.",
                                    class_name="text-gray-500",
                                ),
                                class_name="p-8 text-center border-2 border-dashed rounded-lg",
                            ),
                        ),
                    ),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-6",
                ),
                rx.el.div(
                    rx.el.h2(
                        "Investment Recommendations",
                        class_name="text-lg font-semibold text-gray-800 mb-4",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Based on your average monthly surplus of",
                            class_name="text-gray-600",
                        ),
                        rx.el.p(
                            f"${AppState.monthly_surplus.to_string()}",
                            class_name="text-3xl font-bold text-blue-600",
                        ),
                        class_name="mb-6 p-6 bg-blue-50 rounded-lg text-center",
                    ),
                    rx.cond(
                        AppState.investment_recommendations.length() > 0,
                        rx.el.div(
                            rx.foreach(
                                AppState.investment_recommendations, investment_card
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-3 gap-6",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Start earning to get investment recommendations.",
                                class_name="text-gray-500",
                            ),
                            class_name="p-8 text-center border-2 border-dashed rounded-lg",
                        ),
                    ),
                    class_name="mt-6",
                ),
                class_name="p-4 md:p-6 flex-1 flex flex-col gap-6",
            ),
            class_name=rx.cond(
                AppState.sidebar_collapsed,
                "flex flex-col flex-1 transition-all duration-300 ease-in-out ml-20",
                "flex flex-col flex-1 transition-all duration-300 ease-in-out ml-64",
            ),
        ),
        transaction_form(),
        insights_dialog(),
        class_name="flex min-h-screen w-full bg-gray-50 font-['Inter']",
    )
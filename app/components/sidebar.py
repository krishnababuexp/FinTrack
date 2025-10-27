import reflex as rx
from app.state import AppState


def nav_item(text: str, icon: str, href: str, is_active: bool) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, class_name="h-5 w-5 shrink-0"),
        rx.cond(
            ~AppState.sidebar_collapsed, rx.el.span(text, class_name="truncate"), None
        ),
        href=href,
        class_name=rx.cond(
            AppState.router.page.path == href,
            "flex items-center gap-3 rounded-lg bg-blue-100 px-3 py-2 text-blue-600 transition-all hover:text-blue-700",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
        ),
    )


def sidebar() -> rx.Component:
    nav_items = [
        {"text": "Dashboard", "icon": "layout-grid", "href": "/"},
        {"text": "Budgets", "icon": "piggy-bank", "href": "/budgets"},
        {"text": "Analytics", "icon": "bar-chart-3", "href": "/analytics"},
        {"text": "Insights", "icon": "lightbulb", "href": "/insights"},
    ]
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("wallet-cards", class_name="h-8 w-8 text-blue-600"),
                    rx.cond(
                        ~AppState.sidebar_collapsed,
                        rx.el.span("Financly", class_name="sr-only"),
                        None,
                    ),
                    href="#",
                    class_name="flex items-center gap-2",
                ),
                rx.el.button(
                    rx.icon("panel-left-close", class_name="h-5 w-5"),
                    on_click=AppState.toggle_sidebar,
                    class_name="rounded-lg p-2 hover:bg-gray-100",
                    aria_label="Toggle sidebar",
                ),
                class_name="flex h-16 shrink-0 items-center justify-between border-b px-4 lg:px-6",
            ),
            rx.el.nav(
                rx.foreach(
                    nav_items,
                    lambda item: nav_item(
                        item["text"],
                        item["icon"],
                        item["href"],
                        item["href"] == AppState.router.page.path,
                    ),
                ),
                class_name="flex-1 overflow-auto py-2 flex flex-col gap-1 px-2 text-sm font-medium",
            ),
        ),
        rx.el.div(
            rx.cond(
                ~AppState.sidebar_collapsed,
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "Upgrade to Pro", class_name="font-semibold text-gray-800"
                        ),
                        rx.el.p(
                            "Get AI insights, predictions, and more.",
                            class_name="text-xs text-gray-500",
                        ),
                        class_name="mb-2",
                    ),
                    rx.el.button(
                        "Upgrade",
                        class_name="w-full bg-gray-900 text-white text-xs py-1.5 rounded-md hover:bg-gray-800",
                    ),
                    class_name="p-4 rounded-lg bg-gray-100 border",
                ),
                None,
            ),
            class_name="mt-auto p-4",
        ),
        class_name=rx.cond(
            AppState.sidebar_collapsed,
            "hidden border-r bg-white md:flex flex-col w-20 transition-all duration-300 ease-in-out",
            "hidden border-r bg-white md:flex flex-col w-64 transition-all duration-300 ease-in-out",
        ),
    )
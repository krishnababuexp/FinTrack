import reflex as rx
from app.state import AppState, Budget
from app.components.sidebar import sidebar
from app.components.header import header
from app.components.transaction_form import transaction_form


def budget_form() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black bg-opacity-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.el.h2(
                        "Create New Budget",
                        class_name="text-2xl font-bold text-gray-900",
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
                rx.el.form(
                    rx.el.div(
                        rx.el.label(
                            "Category",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.select(
                            rx.el.option(
                                "Select a category...", value="", disabled=True
                            ),
                            rx.foreach(
                                AppState.budget_categories,
                                lambda category: rx.el.option(category, value=category),
                            ),
                            name="category",
                            required=True,
                            class_name="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                        ),
                        class_name="flex-1",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Monthly Limit",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.div(
                            rx.el.span(
                                "$",
                                class_name="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500",
                            ),
                            rx.el.input(
                                name="limit",
                                placeholder="500.00",
                                type="number",
                                step="0.01",
                                required=True,
                                class_name="pl-7 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                            ),
                            class_name="relative mt-1",
                        ),
                        class_name="flex-1",
                    ),
                    rx.cond(
                        AppState.form_error != "",
                        rx.el.div(
                            rx.icon("flag_triangle_right", class_name="h-4 w-4 mr-2"),
                            rx.el.p(AppState.form_error),
                            class_name="flex items-center text-sm text-red-600 bg-red-50 p-3 rounded-lg",
                        ),
                        None,
                    ),
                    rx.el.div(
                        rx.radix.primitives.dialog.close(
                            rx.el.button(
                                "Cancel",
                                class_name="w-full justify-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50",
                                type="button",
                            )
                        ),
                        rx.el.button(
                            "Create Budget",
                            type="submit",
                            class_name="w-full justify-center rounded-lg border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700",
                        ),
                        class_name="mt-6 flex gap-4",
                    ),
                    class_name="flex flex-col gap-4 mt-4",
                    on_submit=AppState.add_budget,
                    reset_on_submit=True,
                ),
                class_name="bg-white p-6 rounded-2xl shadow-xl w-full max-w-md",
            ),
        ),
        open=AppState.show_budget_dialog,
        on_open_change=AppState.toggle_budget_dialog,
    )


def budget_item(budget: Budget) -> rx.Component:
    progress_color = rx.cond(
        budget.progress > 100,
        "bg-red-500",
        rx.cond(budget.progress > 80, "bg-yellow-500", "bg-green-500"),
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(budget.category, class_name="font-semibold text-gray-800"),
                rx.el.p(
                    f"Limit: ${budget.limit.to_string()}",
                    class_name="text-sm text-gray-500",
                ),
                class_name="flex-1",
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: AppState.delete_budget(budget.id),
                class_name="text-gray-400 hover:text-red-600",
                variant="ghost",
            ),
            class_name="flex justify-between items-start",
        ),
        rx.el.div(
            rx.el.div(
                class_name="h-2 rounded-full",
                style={"width": budget.progress.to_string() + "%"},
                bg=progress_color,
            ),
            class_name="w-full bg-gray-200 rounded-full h-2 mt-2",
        ),
        rx.el.div(
            rx.el.p(
                f"Spent: ${budget.spent.to_string()}",
                class_name="text-sm font-medium text-gray-600",
            ),
            rx.el.p(
                f"Remaining: ${budget.remaining.to_string()}",
                class_name="text-sm font-medium text-green-600",
            ),
            class_name="flex justify-between mt-1",
        ),
        class_name="bg-white p-4 rounded-lg border border-gray-200 shadow-sm",
    )


def budgets_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                rx.el.div(
                    rx.el.h1(
                        "Budget Management",
                        class_name="text-2xl font-bold text-gray-800",
                    ),
                    rx.el.button(
                        "Add Budget",
                        on_click=AppState.toggle_budget_dialog,
                        class_name="flex items-center text-sm font-medium bg-blue-600 text-white px-4 py-2 rounded-lg shadow-sm hover:bg-blue-700 transition-colors",
                    ),
                    class_name="flex justify-between items-center mb-6",
                ),
                rx.cond(
                    AppState.budgets.length() > 0,
                    rx.el.div(
                        rx.foreach(AppState.budgets_with_progress, budget_item),
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                    ),
                    rx.el.div(
                        rx.icon("piggy-bank", class_name="h-12 w-12 text-gray-400"),
                        rx.el.h3(
                            "No Budgets Created",
                            class_name="mt-4 text-lg font-semibold text-gray-800",
                        ),
                        rx.el.p(
                            "Create your first budget to start tracking your spending.",
                            class_name="mt-1 text-sm text-gray-500",
                        ),
                        rx.el.button(
                            "Create Budget",
                            on_click=AppState.toggle_budget_dialog,
                            class_name="mt-4 text-sm font-medium bg-blue-600 text-white px-4 py-2 rounded-lg shadow-sm hover:bg-blue-700 transition-colors",
                        ),
                        class_name="flex flex-col items-center justify-center text-center p-16 border-2 border-dashed rounded-lg mt-4",
                    ),
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
        budget_form(),
        class_name="flex min-h-screen w-full bg-gray-50 font-['Inter']",
    )
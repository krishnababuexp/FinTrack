import reflex as rx
from app.state import AppState, TransactionType


def transaction_form() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black bg-opacity-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.el.h2(
                        "New Transaction", class_name="text-2xl font-bold text-gray-900"
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
                            "Transaction Type",
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.div(
                            rx.foreach(
                                AppState.transaction_types,
                                lambda type: rx.el.button(
                                    type,
                                    on_click=lambda: AppState.set_transaction_type(
                                        type
                                    ),
                                    class_name=rx.cond(
                                        AppState.current_transaction_type == type,
                                        "px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-700 border border-blue-200",
                                        "px-3 py-1 text-xs font-medium rounded-full bg-white text-gray-600 border hover:bg-gray-50",
                                    ),
                                    type="button",
                                ),
                            ),
                            class_name="flex flex-wrap gap-2 mt-2",
                        ),
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Amount",
                                class_name="block text-sm font-medium text-gray-700",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "$",
                                    class_name="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500",
                                ),
                                rx.el.input(
                                    name="amount",
                                    placeholder="0.00",
                                    type="number",
                                    step="0.01",
                                    required=True,
                                    class_name="pl-7 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                                ),
                                class_name="relative mt-1",
                            ),
                            class_name="flex-1",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Date",
                                class_name="block text-sm font-medium text-gray-700",
                            ),
                            rx.el.input(
                                name="date",
                                type="date",
                                required=True,
                                default_value=rx.Var.create(
                                    "new Date().toISOString().slice(0, 10)"
                                ),
                                class_name="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                            ),
                            class_name="flex-1",
                        ),
                        class_name="flex gap-4",
                    ),
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
                                AppState.categories_for_type,
                                lambda category: rx.el.option(category, value=category),
                            ),
                            name="category",
                            required=True,
                            class_name="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Description",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            name="description",
                            placeholder="e.g., Coffee with a friend",
                            class_name="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                        ),
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
                            "Add Transaction",
                            type="submit",
                            class_name="w-full justify-center rounded-lg border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700",
                        ),
                        class_name="mt-6 flex gap-4",
                    ),
                    class_name="flex flex-col gap-4 mt-4",
                    on_submit=AppState.add_transaction,
                    reset_on_submit=True,
                ),
                class_name="bg-white p-6 rounded-2xl shadow-xl w-full max-w-lg z-50 fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2",
            ),
        ),
        open=AppState.show_transaction_dialog,
        on_open_change=AppState.set_show_transaction_dialog,
    )
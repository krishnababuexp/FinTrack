import reflex as rx
from app.state import AppState
from app.components.transaction_list import status_badge


def detail_row(label: str, value: rx.Var, icon: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-4 w-4 text-gray-500"),
        rx.el.span(label, class_name="font-medium text-gray-600"),
        rx.el.span(value, class_name="text-gray-800 text-right truncate"),
        class_name="grid grid-cols-3 items-center gap-2 text-sm",
    )


def transaction_detail_dialog() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black bg-opacity-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Transaction Details",
                            class_name="text-2xl font-bold text-gray-900",
                        ),
                        rx.el.p(
                            f"ID: {AppState.selected_transaction.get('id', '')}",
                            class_name="text-xs text-gray-400 mt-1",
                        ),
                    ),
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            class_name="p-1 rounded-full hover:bg-gray-100",
                            aria_label="Close",
                        )
                    ),
                    class_name="flex items-start justify-between pb-4 border-b",
                ),
                rx.el.div(
                    detail_row(
                        "Amount",
                        f"${AppState.selected_transaction.get('amount', 0).to_string()}",
                        "dollar-sign",
                    ),
                    detail_row(
                        "Date",
                        AppState.selected_transaction.get("date", ""),
                        "calendar",
                    ),
                    detail_row(
                        "Type", AppState.selected_transaction.get("type", ""), "tag"
                    ),
                    detail_row(
                        "Category",
                        AppState.selected_transaction.get("category", "N/A"),
                        "layout-grid",
                    ),
                    rx.cond(
                        AppState.selected_transaction.get("party", "") != "",
                        detail_row(
                            "Party",
                            AppState.selected_transaction.get("party", "N/A"),
                            "user",
                        ),
                        None,
                    ),
                    detail_row(
                        "Description",
                        AppState.selected_transaction.get("description", "N/A"),
                        "file-text",
                    ),
                    rx.el.div(
                        rx.icon("badge-check", class_name="h-4 w-4 text-gray-500"),
                        rx.el.span("Status", class_name="font-medium text-gray-600"),
                        rx.el.div(
                            status_badge(
                                AppState.selected_transaction.get("status", "")
                            ),
                            class_name="flex justify-end",
                        ),
                        class_name="grid grid-cols-3 items-center gap-2 text-sm",
                    ),
                    rx.cond(
                        AppState.selected_transaction.contains("linked_transaction_id"),
                        detail_row(
                            "Linked To",
                            AppState.selected_transaction.get(
                                "linked_transaction_id", ""
                            ),
                            "link-2",
                        ),
                        None,
                    ),
                    class_name="flex flex-col gap-3 mt-4",
                ),
                rx.cond(
                    AppState.selected_transaction.contains("loan_details"),
                    rx.el.div(
                        rx.el.h3(
                            "Loan Information",
                            class_name="text-lg font-semibold text-gray-800 mt-6 mb-3 border-t pt-4",
                        ),
                        detail_row(
                            "Loan Type",
                            AppState.selected_transaction["loan_details"]
                            .to(dict)["type"]
                            .to(str),
                            "landmark",
                        ),
                        detail_row(
                            "Principal",
                            f"${AppState.selected_transaction['loan_details'].to(dict)['principal'].to(str)}",
                            "banknote",
                        ),
                        detail_row(
                            "Interest Rate",
                            f"{AppState.selected_transaction['loan_details'].to(dict)['interest_rate'].to(str)}%",
                            "percent",
                        ),
                        detail_row(
                            "Status",
                            AppState.selected_transaction["loan_details"]
                            .to(dict)["status"]
                            .to(str),
                            "shield-check",
                        ),
                        detail_row(
                            "Remaining Balance",
                            f"${AppState.selected_transaction['loan_details'].to(dict)['outstanding_balance'].to(str)}",
                            "wallet",
                        ),
                    ),
                    None,
                ),
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        "Close",
                        class_name="w-full justify-center mt-6 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50",
                        type="button",
                    )
                ),
                class_name="bg-white p-6 rounded-2xl shadow-xl w-full max-w-lg z-50 fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2",
            ),
        ),
        open=AppState.show_transaction_detail_dialog,
        on_open_change=AppState.close_transaction_detail_dialog,
    )
import reflex as rx
from app.state import AppState, Transaction


def transaction_item(t: Transaction) -> rx.Component:
    icon_map = {
        "Income": ("trending-up", "bg-green-100 text-green-700"),
        "Expense": ("trending-down", "bg-red-100 text-red-700"),
        "Loan Payment": ("landmark", "bg-orange-100 text-orange-700"),
        "Interest Payment": ("percent", "bg-orange-100 text-orange-700"),
        "EMI": ("receipt", "bg-yellow-100 text-yellow-700"),
        "Insurance": ("shield", "bg-indigo-100 text-indigo-700"),
        "Bill Payment": ("file-text", "bg-purple-100 text-purple-700"),
        "Payables": ("arrow-up-right", "bg-pink-100 text-pink-700"),
        "Receivables": ("arrow-down-left", "bg-teal-100 text-teal-700"),
    }
    icon, style = icon_map.get(t.type, ("dollar-sign", "bg-gray-100 text-gray-700"))
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.div(
                    rx.icon(icon, class_name="h-5 w-5"),
                    class_name=f"p-2 rounded-full {style}",
                ),
                rx.el.div(
                    rx.el.p(t.category, class_name="font-medium text-gray-900"),
                    rx.el.p(
                        t.description,
                        class_name="text-xs text-gray-500 truncate max-w-xs",
                    ),
                ),
                class_name="flex items-center gap-3",
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.el.p(
                f"${t.amount.to_string()}",
                class_name=rx.cond(
                    t.type == "Income",
                    "font-medium text-green-600",
                    "font-medium text-gray-800",
                ),
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.el.span(
                t.type,
                class_name="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600",
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(t.date, class_name="px-6 py-4 text-gray-600"),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: AppState.delete_transaction(t.id),
                class_name="text-gray-400 hover:text-red-600",
            ),
            class_name="px-6 py-4",
        ),
        class_name="hover:bg-gray-50",
    )


def transaction_list() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Transaction History", class_name="text-xl font-bold text-gray-800"
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.input(
                    placeholder="Search transactions...",
                    on_change=AppState.set_search_query.debounce(300),
                    default_value=AppState.search_query,
                    class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                ),
                class_name="flex-grow",
            ),
            rx.el.select(
                rx.el.option("All Types", value=""),
                rx.foreach(
                    AppState.transaction_types,
                    lambda type: rx.el.option(type, value=type),
                ),
                on_change=AppState.set_filter_type,
                value=AppState.filter_type,
                class_name="rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
            ),
            rx.el.select(
                rx.el.option("All Categories", value=""),
                rx.foreach(
                    AppState.all_categories, lambda cat: rx.el.option(cat, value=cat)
                ),
                on_change=AppState.set_filter_category,
                value=AppState.filter_category,
                class_name="rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
            ),
            rx.el.button(
                "Clear",
                on_click=AppState.clear_filters,
                class_name="text-sm text-gray-600 hover:text-gray-900",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4 items-center",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Description", class_name="text-left"),
                        rx.el.th("Amount", class_name="text-left"),
                        rx.el.th("Type", class_name="text-left"),
                        rx.el.th("Date", class_name="text-left"),
                        rx.el.th("Actions", class_name="text-left"),
                        class_name="text-xs text-gray-500 uppercase bg-gray-50",
                        style={"textAlign": "left", "padding": "1rem 1.5rem"},
                    )
                ),
                rx.el.tbody(
                    rx.foreach(AppState.filtered_transactions, transaction_item),
                    class_name="bg-white divide-y divide-gray-200",
                ),
                class_name="min-w-full",
            ),
            rx.cond(
                AppState.filtered_transactions.length() == 0,
                rx.el.div(
                    rx.icon("folder-search", class_name="h-12 w-12 text-gray-400"),
                    rx.el.h3(
                        "No Transactions Found",
                        class_name="mt-4 text-lg font-semibold text-gray-800",
                    ),
                    rx.el.p(
                        "Add a new transaction or adjust your filters.",
                        class_name="mt-1 text-sm text-gray-500",
                    ),
                    class_name="flex flex-col items-center justify-center text-center p-16 border-2 border-dashed rounded-lg mt-4",
                ),
                None,
            ),
            class_name="overflow-hidden border border-gray-200 rounded-xl",
        ),
        class_name="bg-white p-6 rounded-xl shadow-sm",
    )
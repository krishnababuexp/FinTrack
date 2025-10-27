import reflex as rx
from app.state import AppState
from app.pages.dashboard import dashboard
from app.pages.budgets import budgets_page
from app.pages.analytics import analytics_page
from app.pages.insights import insights_page
from app.components.transaction_form import transaction_form

app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(dashboard, route="/")
app.add_page(budgets_page, route="/budgets")
app.add_page(analytics_page, route="/analytics")
app.add_page(insights_page, route="/insights")
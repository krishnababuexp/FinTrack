import reflex as rx
from typing import Literal, TypedDict, cast, Optional
import datetime
import json
from pydantic import BaseModel
import logging
from collections import defaultdict

TransactionType = Literal[
    "Income",
    "Expense",
    "Loan Payment",
    "Interest Payment",
    "EMI",
    "Insurance",
    "Bill Payment",
    "Payables",
    "Receivables",
    "Loan Taken",
    "Loan Given",
]
TransactionStatus = Literal["pending", "paid", "received", "settled", "active"]
LoanType = Literal["Taken", "Given"]
LoanStatus = Literal["Active", "Paid Off"]


class Transaction(BaseModel):
    id: str
    type: TransactionType
    amount: float
    category: str
    date: str
    description: str
    status: TransactionStatus = "active"
    linked_transaction_id: Optional[str] = None
    loan_id: Optional[str] = None
    party: Optional[str] = None


class Loan(BaseModel):
    id: str
    type: LoanType
    principal: float
    interest_rate: float
    party: str
    start_date: str
    status: LoanStatus = "Active"

    @property
    def outstanding_balance(self) -> float:
        return self.principal


class Budget(BaseModel):
    id: str
    category: str
    limit: float
    spent: float = 0.0
    remaining: float = 0.0
    progress: float = 0.0


class AppState(rx.State):
    """The main state for the application."""

    sidebar_collapsed: bool = False
    transactions_json: str = rx.LocalStorage("[]", name="transactions_v2")
    budgets_json: str = rx.LocalStorage("[]", name="budgets_v1")
    loans_json: str = rx.LocalStorage("[]", name="loans_v1")
    show_transaction_dialog: bool = False
    current_transaction_type: TransactionType = "Expense"
    form_error: str = ""
    search_query: str = ""
    filter_type: str = ""
    filter_category: str = ""
    filter_start_date: str = ""
    filter_end_date: str = ""
    sort_by: str = "date_desc"
    show_budget_dialog: bool = False
    show_insights_dialog: bool = False
    current_insight: dict = {}

    @rx.event
    def show_insight_details(self, insight: dict):
        self.current_insight = insight
        self.show_insights_dialog = True

    @rx.event
    def close_insights_dialog(self):
        self.show_insights_dialog = False
        self.current_insight = {}

    @rx.event
    def toggle_sidebar(self):
        """Toggles the sidebar's collapsed state."""
        self.sidebar_collapsed = not self.sidebar_collapsed

    @rx.event
    def toggle_transaction_dialog(self):
        """Toggles the visibility of the transaction form dialog."""
        self.show_transaction_dialog = not self.show_transaction_dialog
        self.form_error = ""
        self.current_transaction_type = "Expense"

    @rx.event
    def set_show_transaction_dialog(self, value: bool):
        self.show_transaction_dialog = value

    @rx.event
    def toggle_budget_dialog(self):
        self.show_budget_dialog = not self.show_budget_dialog
        self.form_error = ""

    @rx.event
    def set_transaction_type(self, type: TransactionType):
        """Sets the current transaction type in the form."""
        self.current_transaction_type = type

    @rx.event
    def add_transaction(self, form_data: dict):
        """Adds a new transaction, validates it, and saves to local storage."""
        self.form_error = ""
        try:
            amount = float(form_data.get("amount", 0))
            if amount <= 0:
                self.form_error = "Amount must be greater than zero."
                return
            if not form_data.get("date"):
                self.form_error = "Date is required."
                return
            tx_type = self.current_transaction_type
            party = form_data.get("party")
            loan_id = form_data.get("loan_id")
            interest_rate = form_data.get("interest_rate")
            category = form_data.get("category")
            if tx_type in ["Payables", "Receivables", "Loan Taken", "Loan Given"] and (
                not party
            ):
                self.form_error = "Party name is required for this transaction type."
                return
            if tx_type in ["Loan Taken", "Loan Given"] and (not interest_rate):
                self.form_error = "Interest rate is required for new loans."
                return
            if tx_type in ["Loan Payment", "Interest Payment"] and (not loan_id):
                self.form_error = "A loan must be selected for this payment."
                return
            if tx_type not in [
                "Loan Taken",
                "Loan Given",
                "Loan Payment",
                "Interest Payment",
            ] and (not category):
                self.form_error = "Category is required."
                return
        except (ValueError, TypeError) as e:
            logging.exception(f"Error parsing form data: {e}")
            self.form_error = "Invalid data provided. Check amount and interest rate."
            return
        transactions = self.transactions
        loans = self.loans
        transaction_id = datetime.datetime.now().isoformat()
        transaction_data = {
            "id": transaction_id,
            "type": tx_type,
            "amount": amount,
            "date": form_data["date"],
            "description": form_data.get("description", ""),
            "party": party,
            "loan_id": loan_id,
            "category": category,
        }
        if tx_type in ["Payables", "Receivables"]:
            transaction_data["status"] = "pending"
        if tx_type in ["Loan Taken", "Loan Given"]:
            new_loan = Loan(
                id=transaction_id,
                type="Taken" if tx_type == "Loan Taken" else "Given",
                principal=amount,
                interest_rate=float(interest_rate),
                party=party,
                start_date=form_data["date"],
            )
            loans.append(new_loan)
            self._save_loans(loans)
            transaction_data["loan_id"] = new_loan.id
            transaction_data["category"] = f"Loan with {party}"
        elif tx_type in ["Loan Payment", "Interest Payment"]:
            loan = next((l for l in loans if l.id == loan_id), None)
            if loan:
                transaction_data["category"] = (
                    f"{tx_type.split(' ')[0]} to {loan.party}"
                )
        new_transaction = Transaction(**transaction_data)
        transactions.insert(0, new_transaction)
        self._save_transactions(transactions)
        yield AppState.toggle_transaction_dialog
        yield rx.toast.success("Transaction added successfully!")

    @rx.event
    def delete_transaction(self, transaction_id: str):
        """Deletes a transaction from the list and saves."""
        transactions = [t for t in self.transactions if t.id != transaction_id]
        self._save_transactions(transactions)
        yield rx.toast.error("Transaction deleted.")

    def _save_transactions(self, transactions: list[Transaction]):
        """Helper to serialize and save transactions to local storage."""
        self.transactions_json = json.dumps([t.model_dump() for t in transactions])

    @rx.event
    def add_budget(self, form_data: dict):
        self.form_error = ""
        try:
            limit = float(form_data.get("limit", 0))
            category = form_data.get("category")
            if not category:
                self.form_error = "Category is required."
                return
            if limit <= 0:
                self.form_error = "Limit must be a positive number."
                return
            if any((b.category == category for b in self.budgets)):
                self.form_error = f"A budget for '{category}' already exists."
                return
        except (ValueError, TypeError) as e:
            logging.exception(f"Error parsing budget limit: {e}")
            self.form_error = "Invalid limit amount."
            return
        budgets = self.budgets
        new_budget = Budget(
            id=datetime.datetime.now().isoformat(), category=category, limit=limit
        )
        budgets.append(new_budget)
        self._save_budgets(budgets)
        yield AppState.toggle_budget_dialog
        yield rx.toast.success(f"Budget for '{category}' created!")

    @rx.event
    def delete_budget(self, budget_id: str):
        budgets = [b for b in self.budgets if b.id != budget_id]
        self._save_budgets(budgets)
        yield rx.toast.error("Budget deleted.")

    def _save_budgets(self, budgets: list[Budget]):
        self.budgets_json = json.dumps([b.model_dump() for b in budgets])

    def _save_loans(self, loans: list[Loan]):
        self.loans_json = json.dumps([l.model_dump() for l in loans])

    @rx.event
    def settle_payable(self, transaction_id: str):
        transactions = self.transactions
        original_tx = next((t for t in transactions if t.id == transaction_id), None)
        if (
            not original_tx
            or original_tx.type != "Payables"
            or original_tx.status != "pending"
        ):
            return rx.toast.error("Invalid action.")
        settlement_tx = Transaction(
            id=datetime.datetime.now().isoformat(),
            type="Expense",
            amount=original_tx.amount,
            category="Settlement",
            date=datetime.date.today().isoformat(),
            description=f"Paid off: {original_tx.description}",
            status="settled",
            linked_transaction_id=original_tx.id,
            party=original_tx.party,
        )
        original_tx.status = "settled"
        transactions.insert(0, settlement_tx)
        self._save_transactions(transactions)
        yield rx.toast.success("Payable marked as paid!")

    @rx.event
    def settle_receivable(self, transaction_id: str):
        transactions = self.transactions
        original_tx = next((t for t in transactions if t.id == transaction_id), None)
        if (
            not original_tx
            or original_tx.type != "Receivables"
            or original_tx.status != "pending"
        ):
            return rx.toast.error("Invalid action.")
        settlement_tx = Transaction(
            id=datetime.datetime.now().isoformat(),
            type="Income",
            amount=original_tx.amount,
            category="Settlement",
            date=datetime.date.today().isoformat(),
            description=f"Received payment for: {original_tx.description}",
            status="received",
            linked_transaction_id=original_tx.id,
            party=original_tx.party,
        )
        original_tx.status = "settled"
        transactions.insert(0, settlement_tx)
        self._save_transactions(transactions)
        yield rx.toast.success("Receivable marked as received!")

    @rx.event
    def clear_filters(self):
        """Resets all filter and search fields."""
        self.search_query = ""
        self.filter_type = ""
        self.filter_category = ""
        self.filter_start_date = ""
        self.filter_end_date = ""

    @rx.var
    def transactions(self) -> list[Transaction]:
        """Parses the JSON string from local storage into a list of Transaction models."""
        try:
            raw_data = json.loads(self.transactions_json)
            return [Transaction.model_validate(item) for item in raw_data]
        except (json.JSONDecodeError, TypeError) as e:
            logging.exception(f"Failed to parse transactions JSON: {e}")
            return []

    @rx.var
    def budgets(self) -> list[Budget]:
        try:
            raw_data = json.loads(self.budgets_json)
            return [Budget.model_validate(item) for item in raw_data]
        except (json.JSONDecodeError, TypeError) as e:
            logging.exception(f"Failed to parse budgets JSON: {e}")
            return []

    @rx.var
    def loans(self) -> list[Loan]:
        try:
            raw_data = json.loads(self.loans_json)
            return [Loan.model_validate(item) for item in raw_data]
        except (json.JSONDecodeError, TypeError) as e:
            logging.exception(f"Failed to parse loans JSON: {e}")
            return []

    @rx.var
    def active_loans(self) -> list[Loan]:
        return [loan for loan in self.loans if loan.status == "Active"]

    @rx.var
    def budgets_with_progress(self) -> list[Budget]:
        expense_by_cat = defaultdict(float)
        current_month = datetime.date.today().strftime("%Y-%m")
        for t in self.transactions:
            if t.type == "Expense" and t.date.startswith(current_month):
                expense_by_cat[t.category] += t.amount
        updated_budgets = []
        for budget in self.budgets:
            spent = expense_by_cat[budget.category]
            remaining = budget.limit - spent
            progress = spent / budget.limit * 100 if budget.limit > 0 else 0
            budget.spent = spent
            budget.remaining = remaining
            budget.progress = progress
            updated_budgets.append(budget)
        return updated_budgets

    @rx.var
    def filtered_transactions(self) -> list[Transaction]:
        """Applies all filters and sorting to the transaction list."""
        items = self.transactions
        if self.search_query:
            query = self.search_query.lower()
            items = [
                t
                for t in items
                if query in t.description.lower() or query in t.category.lower()
            ]
        if self.filter_type:
            items = [t for t in items if t.type == self.filter_type]
        if self.filter_category:
            items = [t for t in items if t.category == self.filter_category]
        if self.filter_start_date:
            items = [t for t in items if t.date >= self.filter_start_date]
        if self.filter_end_date:
            items = [t for t in items if t.date <= self.filter_end_date]
        if self.sort_by == "date_asc":
            items.sort(key=lambda t: t.date)
        elif self.sort_by == "date_desc":
            items.sort(key=lambda t: t.date, reverse=True)
        elif self.sort_by == "amount_asc":
            items.sort(key=lambda t: t.amount)
        elif self.sort_by == "amount_desc":
            items.sort(key=lambda t: t.amount, reverse=True)
        return items

    @rx.var
    def transaction_types(self) -> list[TransactionType]:
        """Returns a list of all available transaction types."""
        return [
            "Income",
            "Expense",
            "Loan Payment",
            "Interest Payment",
            "EMI",
            "Insurance",
            "Bill Payment",
            "Payables",
            "Receivables",
            "Loan Taken",
            "Loan Given",
        ]

    @rx.var
    def categories_for_type(self) -> list[str]:
        """Returns a list of categories based on the currently selected transaction type."""
        return self.categories_for_type_map.get(self.current_transaction_type, [])

    @rx.var
    def all_categories(self) -> list[str]:
        """Returns a unique, sorted list of all categories across all transactions."""
        categories = {t.category for t in self.transactions}
        return sorted(list(categories))

    @rx.var
    def budget_categories(self) -> list[str]:
        """Returns a list of all expense categories."""
        return sorted(self.categories_for_type_map.get("Expense", []))

    @rx.var
    def monthly_surplus(self) -> float:
        """Calculates the average monthly surplus."""
        income = 0
        expenses = 0
        num_months = len(self.income_vs_expense_data)
        if num_months == 0:
            return 0.0
        for month_data in self.income_vs_expense_data:
            income += month_data["income"]
            expenses += month_data["expense"]
        avg_monthly_income = income / num_months if num_months > 0 else 0
        avg_monthly_expenses = expenses / num_months if num_months > 0 else 0
        return avg_monthly_income - avg_monthly_expenses

    @rx.var
    def savings_suggestions(self) -> list[dict]:
        """Generates personalized savings suggestions."""
        suggestions = []
        total_expense = self.total_expenses
        if total_expense == 0:
            return []
        category_totals = defaultdict(float)
        for t in self.transactions:
            if t.type == "Expense":
                category_totals[t.category] += t.amount
        for category, spent in category_totals.items():
            if spent > total_expense * 0.2:
                suggestions.append(
                    {
                        "title": f"Review Spending in {category}",
                        "description": f"You've spent ${spent:.2f} in this category, which is a significant portion of your total expenses. Look for ways to reduce this.",
                        "potential_savings": round(spent * 0.1, 2),
                    }
                )
        return suggestions

    @rx.var
    def investment_recommendations(self) -> list[dict]:
        """Generates investment recommendations based on surplus."""
        surplus = self.monthly_surplus
        if surplus <= 50:
            return [
                {
                    "risk_level": "Low",
                    "title": "Build Emergency Fund",
                    "description": "Focus on building an emergency fund in a high-yield savings account before investing.",
                    "allocation": surplus,
                }
            ]
        return [
            {
                "risk_level": "Conservative",
                "title": "Low-Risk Bonds",
                "description": "Consider government or corporate bonds for steady, low-risk returns.",
                "allocation": round(surplus * 0.5, 2),
            },
            {
                "risk_level": "Moderate",
                "title": "Index Funds (S&P 500)",
                "description": "Invest in a broad market index fund for diversified growth.",
                "allocation": round(surplus * 0.3, 2),
            },
            {
                "risk_level": "Aggressive",
                "title": "Growth Stocks",
                "description": "Allocate a smaller portion to individual growth stocks or sector ETFs for higher potential returns.",
                "allocation": round(surplus * 0.2, 2),
            },
        ]

    @rx.var
    def smart_alerts(self) -> list[dict]:
        """Generates smart alerts based on spending and budgets."""
        alerts = []
        for budget in self.budgets_with_progress:
            if 80 < budget.progress <= 100:
                alerts.append(
                    {
                        "type": "warning",
                        "title": f"Approaching Budget Limit for {budget.category}",
                        "message": f"You have spent ${budget.spent:.2f} of your ${budget.limit:.2f} budget ({budget.progress:.0f}% used).",
                    }
                )
            elif budget.progress > 100:
                alerts.append(
                    {
                        "type": "error",
                        "title": f"Budget Exceeded for {budget.category}",
                        "message": f"You have overspent by ${abs(budget.remaining):.2f} in {budget.category}.",
                    }
                )
        avg_expense_amount = (
            self.total_expenses
            / len([t for t in self.transactions if "Expense" in t.type])
            if len([t for t in self.transactions if "Expense" in t.type]) > 0
            else 0
        )
        if avg_expense_amount > 0:
            for t in self.transactions:
                if t.type == "Expense" and t.amount > avg_expense_amount * 3:
                    alerts.append(
                        {
                            "type": "info",
                            "title": "Unusual Transaction Detected",
                            "message": f"A transaction of ${t.amount:.2f} for '{t.category}' is significantly higher than your average.",
                        }
                    )
                    break
        return alerts

    @rx.var
    def income_vs_expense_data(self) -> list[dict]:
        monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
        today = datetime.date.today()
        for i in range(6):
            month = (today - datetime.timedelta(days=i * 30)).strftime("%b %Y")
            monthly_data[month]
        for t in self.transactions:
            try:
                t_date = datetime.datetime.strptime(t.date, "%Y-%m-%d").date()
                month_key = t_date.strftime("%b %Y")
                if month_key in monthly_data:
                    if t.type == "Income":
                        monthly_data[month_key]["income"] += t.amount
                    elif t.type == "Expense":
                        monthly_data[month_key]["expense"] += t.amount
            except ValueError as e:
                logging.exception(f"Error parsing transaction date for chart: {e}")
                continue
        return sorted(
            [{"month": k, **v} for k, v in monthly_data.items()],
            key=lambda x: datetime.datetime.strptime(x["month"], "%b %Y"),
        )

    @rx.var
    def expense_by_category_data(self) -> list[dict]:
        category_totals = defaultdict(float)
        current_month = datetime.date.today().strftime("%Y-%m")
        for t in self.transactions:
            if t.type == "Expense" and t.date.startswith(current_month):
                category_totals[t.category] += t.amount
        return [
            {"name": cat, "value": round(val)} for cat, val in category_totals.items()
        ]

    @rx.var
    def cash_flow_data(self) -> list[dict]:
        sorted_transactions = sorted(self.transactions, key=lambda t: t.date)
        balance = self.initial_balance
        data = []
        for t in sorted_transactions:
            if t.type == "Income":
                balance += t.amount
            elif t.type in {
                "Expense",
                "Loan Payment",
                "Interest Payment",
                "EMI",
                "Insurance",
                "Bill Payment",
            }:
                balance -= t.amount
            data.append({"date": t.date, "balance": round(balance, 2)})
        return data

    @rx.var
    def initial_balance(self) -> float:
        """Calculate balance from transactions before the chart's date range."""
        return 0.0

    @rx.var
    def categories_for_type_map(self) -> dict:
        return {
            "Income": ["Salary", "Freelance", "Investment", "Gift", "Other"],
            "Expense": [
                "Food",
                "Groceries",
                "Transport",
                "Shopping",
                "Entertainment",
                "Utilities",
                "Other",
            ],
            "Loan Payment": ["Personal Loan", "Home Loan", "Car Loan", "Student Loan"],
            "Interest Payment": ["Credit Card", "Loan Interest"],
            "EMI": ["Electronics", "Vehicle", "Home Appliance"],
            "Insurance": ["Health", "Life", "Vehicle", "Home"],
            "Bill Payment": ["Electricity", "Water", "Internet", "Phone", "Gas"],
            "Payables": ["Friend", "Vendor", "Credit"],
            "Receivables": ["Friend", "Client", "Refund"],
            "Loan Taken": ["Personal", "Business"],
            "Loan Given": ["Personal", "Business"],
        }

    @rx.var
    def total_income(self) -> float:
        """Calculates the total income."""
        return sum((t.amount for t in self.transactions if t.type == "Income"))

    @rx.var
    def total_expenses(self) -> float:
        """Calculates total expenses, including various payment types."""
        expense_types = {
            "Expense",
            "Loan Payment",
            "Interest Payment",
            "EMI",
            "Insurance",
            "Bill Payment",
        }
        return sum((t.amount for t in self.transactions if t.type in expense_types))

    @rx.var
    def current_balance(self) -> float:
        """Calculates the current balance (income - expenses)."""
        return self.total_income - self.total_expenses

    @rx.var
    def pending_payables(self) -> float:
        """Calculates the total amount of pending payables."""
        return sum(
            (
                t.amount
                for t in self.transactions
                if t.type == "Payables" and t.status == "pending"
            )
        )

    @rx.var
    def pending_receivables(self) -> float:
        """Calculates the total amount of pending receivables."""
        return sum(
            (
                t.amount
                for t in self.transactions
                if t.type == "Receivables" and t.status == "pending"
            )
        )
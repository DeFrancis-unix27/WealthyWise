import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class ContextAssembler:
    def __init__(self, user):
        self.user = user
        self._profile = None
        self._accounts = None
        self._transactions = None
        self._budgets = None
        self._goals = None
        self._businesses = None
        self._learning_profile = None

    @property
    def profile(self):
        if self._profile is None:
            self._profile = getattr(self.user, "profile", None)
        return self._profile

    @property
    def accounts(self):
        if self._accounts is None:
            self._accounts = list(self.user.accounts.all())
        return self._accounts

    @property
    def transactions(self):
        if self._transactions is None:
            three_months_ago = timezone.now().date() - relativedelta(months=3)
            self._transactions = list(
                self.user.transactions.filter(date__gte=three_months_ago).order_by("-date")[:50]
            )
        return self._transactions

    @property
    def budgets(self):
        if self._budgets is None:
            this_month = timezone.now().date().replace(day=1)
            self._budgets = list(self.user.budget_set.filter(month=this_month))
        return self._budgets

    @property
    def goals(self):
        if self._goals is None:
            try:
                self._goals = list(self.user.financial_goals.filter(status="active"))
            except AttributeError:
                self._goals = []
        return self._goals

    @property
    def businesses(self):
        if self._businesses is None:
            try:
                self._businesses = list(self.user.businesses.filter(is_active=True))
            except AttributeError:
                self._businesses = []
        return self._businesses

    @property
    def learning_profile(self):
        if self._learning_profile is None:
            try:
                self._learning_profile = getattr(self.user, "learning_profile", None)
            except AttributeError:
                self._learning_profile = None
        return self._learning_profile

    def _summarize_transactions(self) -> dict:
        txns = self.transactions
        income = sum(t.amount for t in txns if t.transaction_type == "income")
        expenses = sum(t.amount for t in txns if t.transaction_type == "expense")
        categories = {}
        for t in txns:
            if t.transaction_type == "expense":
                categories[t.category] = categories.get(t.category, 0) + t.amount
        top_categories = sorted(categories.items(), key=lambda x: -x[1])[:5]

        return {
            "total_income_3mo": income,
            "total_expenses_3mo": expenses,
            "transaction_count": len(txns),
            "top_spending_categories": [
                {"category": cat, "amount": amt} for cat, amt in top_categories
            ],
        }

    def _summarize_budgets(self) -> dict:
        budgets = self.budgets
        budget_data = []
        for b in budgets:
            spent = b.spent_amount()
            budget_data.append({
                "category": b.category,
                "budgeted": b.amount,
                "spent": spent,
                "remaining": b.remaining_amount(),
                "percentage": b.percentage_used(),
            })
        return {"budgets": budget_data}

    def _summarize_accounts(self) -> dict:
        accts = self.accounts
        total_balance = sum(a.balance for a in accts)
        return {
            "total_accounts": len(accts),
            "total_balance": total_balance,
            "accounts": [
                {"name": a.name, "type": a.account_type, "balance": a.balance, "currency": a.currency}
                for a in accts
            ],
        }

    def _summarize_goals(self) -> dict:
        return {
            "goals": [
                {
                    "title": g.title,
                    "category": g.category,
                    "target": g.target_amount,
                    "current": g.current_amount,
                    "progress_pct": float(g.current_amount) / float(g.target_amount) * 100
                    if g.target_amount else 0,
                    "currency": g.currency,
                }
                for g in self.goals
            ]
        }

    def _user_profile_summary(self) -> dict:
        p = self.profile
        return {
            "account_type": p.account_type if p else "standard",
            "member_since": str(self.user.date_joined.date()) if self.user.date_joined else None,
            "name": self.user.get_full_name() or self.user.username,
        }

    def build_system_prompt(self) -> str:
        profile = self._user_profile_summary()
        accounts = self._summarize_accounts()
        transactions = self._summarize_transactions()
        budgets = self._summarize_budgets()
        goals = self._summarize_goals()

        return f"""You are WealthyWise AI, a personal financial assistant. You help users understand their finances, set goals, improve financial literacy, and make better money decisions.

## User Profile
- Name: {profile['name']}
- Account Type: {profile['account_type']}
- Member Since: {profile['member_since']}

## Financial Overview
- Total Balance: {accounts['total_balance']} across {accounts['total_accounts']} accounts
- Income (last 3 months): {transactions['total_income_3mo']}
- Expenses (last 3 months): {transactions['total_expenses_3mo']}
- Transaction count (last 3 months): {transactions['transaction_count']}

## Top Spending Categories (last 3 months)
{chr(10).join(f"- {c['category']}: {c['amount']}" for c in transactions['top_spending_categories'])}

## Active Budgets (this month)
{chr(10).join(f"- {b['category']}: {b['spent']}/{b['budgeted']} ({b['percentage']}%)" for b in budgets['budgets']) if budgets['budgets'] else "No budgets set for this month."}

## Financial Goals
{chr(10).join(f"- {g['title']}: {g['current']}/{g['target']} ({g['progress_pct']:.0f}%)" for g in goals['goals']) if goals['goals'] else "No active financial goals."}

## Accounts
{chr(10).join(f"- {a['name']} ({a['type']}): {a['balance']} {a['currency']}" for a in accounts['accounts'])}

## Guidelines
1. Give personalized advice based on the user's actual financial data above.
2. Suggest financial literacy concepts, projects, or courses that would help them.
3. If they ask about budgeting, reference their actual budgets and spending.
4. Be concise but informative.
5. If they're spending too much in a category, suggest practical ways to reduce it.
6. Recommend relevant goals based on their spending patterns.
7. For entrepreneurial users, suggest business-relevant content.
8. Keep responses under 500 words. Use plain text, no markdown formatting."""

    def build_personalized_message(self, user_message: str) -> str:
        context = self.build_system_prompt()
        return f"{context}\n\n## User Question\n{user_message}"

    def get_context_json(self) -> str:
        return json.dumps({
            "profile": self._user_profile_summary(),
            "accounts": self._summarize_accounts(),
            "transactions": self._summarize_transactions(),
            "budgets": self._summarize_budgets(),
            "goals": self._summarize_goals(),
        }, default=str)


def get_gemini_response(user_message: str, user=None) -> str:
    from google import genai

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    if user and user.is_authenticated:
        assembler = ContextAssembler(user)
        prompt = assembler.build_personalized_message(user_message)
    else:
        prompt = f"""You are WealthyWise AI, a personal financial assistant. Help users understand personal finance, investing, budgeting, and building wealth. Be concise and practical.

User question: {user_message}"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text

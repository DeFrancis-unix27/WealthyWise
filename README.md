# WealthyWise

AI-powered financial intelligence platform. Track spending, learn financial concepts, set goals, and grow your business — all in one place.

## Features

- **AI Financial Assistant** — Gemini-powered chat with context from your real transactions, budgets, and goals
- **Bank Sync** — Connect bank accounts via Mono (Nigeria), Plaid (US/CA), or Truelayer (UK/EU)
- **Financial Education** — 15+ concepts, 6 hands-on projects, 4 courses (24 lessons), live workshops, webinars
- **Goal Tracking** — Set financial goals (emergency fund, debt payoff, investments) with progress tracking
- **Literacy Assessment** — Measure your knowledge across budgeting, saving, investing, debt, and retirement
- **Entrepreneur Tools** — Businesses, side hustles, revenue tracking, and guided entrepreneurship paths
- **Marketplace** — Curated financial products, templates, tools, and affiliate partner directory
- **Subscription Billing** — Free / Premium / Business tiers with Stripe & Paystack
- **Real Market Data** — Live S&P 500 chart via TradingView widget with RSI + MACD
- **Marketing Landing Page** — Three.js particle network, 3D CSS cards, market ticker, 12 curated resources

## Tech Stack

- **Backend**: Django 5, Python 3, Celery, Redis
- **Database**: PostgreSQL (production) / SQLite (local dev)
- **Frontend**: Django templates, Bootstrap 5, Three.js, TradingView widgets
- **Static Files**: WhiteNoise
- **Auth**: django-two-factor-auth, WebAuthn, Google OAuth
- **Deployment**: Docker, Render

## Quick Start

```bash
git clone https://github.com/DeFrancis-unix27/WealthyWise.git
cd WealthyWise

cp .env.example .env
# Edit .env with your secrets

# Option A: Docker
docker compose up -d

# Option B: Local
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_content
python manage.py runserver
```

## Environment Variables

See `.env.example` for the full list. Key ones:

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key |
| `DATABASE_URL` | For production | PostgreSQL connection string |
| `GOOGLE_API_KEY` | For AI chat | Gemini API key |
| `STRIPE_SECRET_KEY` | For billing | Stripe secret key |
| `MONO_SECRET_KEY` | For bank sync | Mono API key (Nigeria) |
| `PLAID_SECRET` | For bank sync | Plaid API key (US/CA) |
| `TRUELAYER_CLIENT_ID` | For bank sync | Truelayer client ID (UK/EU) |
| `SENTRY_DSN` | Optional | Error tracking |

## Project Structure

```
WealthyWise/
├── finance/              # Django project config
│   ├── settings.py
│   └── urls.py
├── financeapp/           # Core app (auth, dashboard, transactions)
├── ai/                   # AI chat, insights, recommendations
├── banking/              # Bank connectors (Mono, Plaid, Truelayer)
├── billing/              # Subscriptions, plans, invoices
├── education/            # Concepts, projects, courses, workshops
├── entrepreneur/         # Businesses, side hustles, paths
├── goals/                # Financial goals, literacy assessment
├── marketplace/          # Products, affiliates, orders
├── static/               # CSS, JS
│   ├── css/layout.css    # Theme variables (dark/light)
│   ├── css/features.css  # 70+ reusable component classes
│   └── css/dashboard.css # Dashboard widgets
└── templates/            # Shared templates
```

## Deployment

```bash
# Build and deploy with Docker
docker compose up -d --build

# Or deploy on Render:
# 1. Connect GitHub repo
# 2. Add PostgreSQL add-on
# 3. Set env vars from .env.example
# 4. Deploy (build command: pip install -r requirements.txt)
#    (start command: gunicorn finance.wsgi:application --bind 0.0.0.0:$PORT)
```

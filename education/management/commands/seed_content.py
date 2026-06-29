from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from education.models import Instructor, Concept, Project, ProjectStep, Course, Lesson, Workshop, Webinar, LearningPath
from marketplace.models import ProductCategory, Product, CuratedCollection, AffiliatePartner
from entrepreneur.models import EntrepreneurshipPath

User = get_user_model()

CONCEPTS = [
    {"title": "Budgeting Foundations", "difficulty": "beginner", "estimated_minutes": 15, "icon": "📊",
     "content": """Budgeting is the cornerstone of personal finance. A budget is simply a plan for your money — it tells every dollar where to go instead of wondering where it went.

The 50/30/20 Rule is the most popular budgeting framework:
- **50% for Needs**: Rent/mortgage, utilities, groceries, insurance, minimum debt payments
- **30% for Wants**: Dining out, entertainment, shopping, vacations
- **20% for Savings & Debt**: Emergency fund, retirement, extra debt payments, investments

To start budgeting, track your income and expenses for one month. Categorize everything. Then compare against the 50/30/20 guideline and adjust.

Remember: A budget isn't restrictive — it's empowering. It ensures your spending aligns with your values and goals."""},
    {"title": "Understanding Credit Scores", "difficulty": "beginner", "estimated_minutes": 12, "icon": "💳",
     "content": """Your credit score is a three-digit number that represents your creditworthiness. In most countries, scores range from 300 to 850. The higher your score, the more likely lenders are to approve you for loans and credit cards at favorable rates.

**What affects your score:**
- Payment history (35%): Paying bills on time is the biggest factor
- Credit utilization (30%): How much of your available credit you're using
- Length of credit history (15%): Longer is generally better
- Credit mix (10%): Having different types of credit helps
- New credit inquiries (10%): Too many hard inquiries in a short time hurts

**To improve your score:**
1. Always pay bills on time
2. Keep credit utilization below 30%
3. Don't close old credit cards (they help your history length)
4. Only apply for new credit when necessary"""},
    {"title": "Emergency Funds: Your Safety Net", "difficulty": "beginner", "estimated_minutes": 10, "icon": "🛡️",
     "content": """An emergency fund is money set aside for unexpected expenses — medical emergencies, car repairs, job loss, or urgent home repairs. It's your financial safety net that prevents you from going into debt when life happens.

**How much should you save?**
- **Beginner level**: $1,000 or one month of essential expenses
- **Standard recommendation**: 3-6 months of essential expenses
- **Conservative**: 6-12 months for irregular income or high-risk industries

**Where to keep it:**
- High-yield savings account (HYSA) — earns interest but is easily accessible
- Money market account
- NOT in the stock market (too volatile for emergency funds)

**Pro tip**: Set up automatic monthly transfers to your emergency fund. Treat it like a non-negotiable bill."""},
    {"title": "Introduction to Investing", "difficulty": "beginner", "estimated_minutes": 20, "icon": "📈",
     "content": """Investing means putting money into assets with the expectation that they'll grow in value over time. Unlike saving (which preserves capital), investing takes on risk in exchange for potentially higher returns.

**Key investment vehicles:**
- **Stocks**: Ownership shares in companies. Higher risk, higher potential return.
- **Bonds**: Loans to governments or companies. Lower risk, lower return.
- **Mutual Funds**: Pooled money invested in many assets. Good diversification.
- **ETFs**: Like mutual funds but trade like stocks. Low fees.
- **Real Estate**: Property investments. Can provide rental income and appreciation.

**Core principles:**
1. **Start early**: The power of compound interest is strongest over long periods
2. **Diversify**: Don't put all your eggs in one basket — spread across asset types
3. **Stay consistent**: Dollar-cost averaging (investing regularly) beats timing the market
4. **Think long-term**: Markets go up and down, but historically the trend is upward over decades

**Rule of 72**: Divide 72 by your annual return rate to estimate how many years it takes your money to double. At 10% returns, money doubles every 7.2 years."""},
    {"title": "Compound Interest Explained", "difficulty": "beginner", "estimated_minutes": 8, "icon": "🔮",
     "content": """Albert Einstein reportedly called compound interest "the eighth wonder of the world." Compound interest is interest earned on interest — your money earning money on the money your money already earned.

**Simple vs. Compound Interest:**
- Simple: Interest earned only on the principal (original amount)
- Compound: Interest earned on principal + accumulated interest

**Example**: If you invest $10,000 at 10% annual return:
- **Year 1**: $10,000 + $1,000 = $11,000
- **Year 2**: $11,000 + $1,100 = $12,100
- **Year 10**: $25,937
- **Year 20**: $67,275
- **Year 30**: $174,494

The later years show the true power of compounding. The first 10 years grew by $15,937. The last 10 years grew by over $107,000 — all from the same initial $10,000 investment.

**Key takeaways**:
1. Start investing as early as possible
2. Time in the market beats timing the market
3. Reinvest your dividends and returns"""},
    {"title": "Debt Management Strategies", "difficulty": "intermediate", "estimated_minutes": 15, "icon": "⛓️",
     "content": """Not all debt is bad. A mortgage can build equity. Student loans can increase earning potential. But high-interest debt (credit cards, payday loans) can destroy wealth.

**The Debt Avalanche Method**:
- List all debts by interest rate (highest first)
- Pay minimums on everything
- Put all extra money toward the highest-interest debt
- Once paid off, roll that payment to the next highest
- Mathematically optimal — you pay the least interest overall

**The Debt Snowball Method**:
- List all debts by balance (smallest first)
- Pay minimums on everything
- Put all extra money toward the smallest debt
- Once paid off, roll that payment to the next smallest
- Psychologically motivating — you get quick wins

**Good Debt vs Bad Debt**:
- **Good**: Mortgage, student loans, business loans (assets that appreciate or increase income)
- **Bad**: Credit card debt, payday loans, auto loans for depreciating assets

**The 28/36 Rule**: No more than 28% of gross monthly income on housing, and no more than 36% on total debt."""},
    {"title": "Retirement Planning 101", "difficulty": "intermediate", "estimated_minutes": 18, "icon": "🏖️",
     "content": """Retirement planning ensures you can maintain your lifestyle when you stop working. The earlier you start, the less you need to save each month thanks to compound interest.

**Retirement Accounts by Country**:
- **USA**: 401(k), IRA, Roth IRA, SEP IRA
- **UK**: Pension (State, Workplace, Personal), SIPP, ISA
- **Nigeria**: RSA (Retirement Savings Account), voluntary contributions
- **Canada**: RRSP, TFSA

**How much do you need?** A common rule is the **4% Rule**: In retirement, you can safely withdraw 4% of your portfolio annually without running out of money for 30 years.
- Calculate: Annual expenses in retirement / 0.04 = Target nest egg
- If you need $40,000/year: $40,000 / 0.04 = $1,000,000 needed

**Employer matching**: If your employer offers a 401(k) match, contribute at least enough to get the full match — it's free money and an instant 100% return."""},
    {"title": "Tax-Efficient Investing", "difficulty": "intermediate", "estimated_minutes": 12, "icon": "🧾",
     "content": """Tax-efficient investing means structuring your investments to minimize the taxes you pay on gains and income. Over decades, taxes can significantly erode your returns.

**Key strategies:**
1. **Use tax-advantaged accounts first**: Max out 401(k), IRA, Roth IRA before investing in taxable accounts
2. **Asset location**: Place tax-inefficient investments (bonds, REITs, actively managed funds) in tax-advantaged accounts. Place tax-efficient investments (index ETFs, municipal bonds) in taxable accounts
3. **Hold for the long term**: Short-term capital gains (assets held less than a year) are taxed at higher ordinary income rates. Long-term gains get preferential rates
4. **Tax-loss harvesting**: Sell investments at a loss to offset gains elsewhere

**Important**: Tax laws vary by country. Consult a tax professional for personalized advice."""},
    {"title": "Real Estate Investing", "difficulty": "intermediate", "estimated_minutes": 20, "icon": "🏠",
     "content": """Real estate can be a powerful wealth-building tool. It provides rental income, appreciation, tax benefits, and leverage (using borrowed money to control assets).

**Types of real estate investing:**
- **Rental properties**: Buy and hold for monthly cash flow + long-term appreciation
- **REITs**: Real Estate Investment Trusts — trade like stocks, pay dividends
- **House hacking**: Buy a multi-unit property, live in one unit, rent the others
- **Fix and flip**: Buy distressed properties, renovate, sell for profit
- **Real estate crowdfunding**: Pool money with other investors for development projects

**Key metrics to evaluate:**
- **Cap Rate**: Net operating income / Property value (target: 8%+)
- **Cash-on-Cash Return**: Annual pre-tax cash flow / Total cash invested (target: 10%+)
- **1% Rule**: Monthly rent should be at least 1% of purchase price

**Warning**: Real estate is not passive. It requires work, capital, and carries risks (vacancies, repairs, market downturns)."""},
    {"title": "Understanding Financial Statements", "difficulty": "intermediate", "estimated_minutes": 15, "icon": "📋",
     "content": """Financial statements tell the story of a company's financial health. Every investor should understand the basics of reading them.

**Three core statements:**

1. **Balance Sheet** (snapshot at a point in time):
   - Assets = Liabilities + Shareholders' Equity
   - Shows what a company owns and owes

2. **Income Statement** (performance over time):
   - Revenue - Expenses = Net Income
   - Shows profitability

3. **Cash Flow Statement** (actual cash movements):
   - Operating activities (core business)
   - Investing activities (buying/selling assets)
   - Financing activities (debt, equity, dividends)

**Key ratios to calculate:**
- **P/E Ratio**: Price / Earnings per share — how much you're paying for $1 of earnings
- **Debt-to-Equity**: Total liabilities / Shareholders' equity — measures leverage
- **ROE**: Net Income / Shareholders' equity — return on shareholders' investment
- **Current Ratio**: Current assets / Current liabilities — ability to pay short-term obligations"""},
    {"title": "Options Trading Basics", "difficulty": "advanced", "estimated_minutes": 25, "icon": "🎯",
     "content": """Options are contracts that give you the right, but not the obligation, to buy or sell an asset at a specific price (strike price) on or before a specific date (expiration date).

**Two types:**
- **Call option**: Right to BUY an asset — you profit if the price goes UP
- **Put option**: Right to SELL an asset — you profit if the price goes DOWN

**Key terms:**
- **Premium**: The price you pay to buy an option
- **Strike price**: The price at which you can buy/sell the asset
- **Expiration date**: When the option contract expires
- **In the money (ITM)**: Option has intrinsic value
- **Out of the money (OTM)**: Option has no intrinsic value

**⚠️ WARNING**: Options are complex and risky. Most options expire worthless. Never trade options with money you can't afford to lose. Start with paper trading to learn."""},
    {"title": "Behavioral Finance", "difficulty": "advanced", "estimated_minutes": 18, "icon": "🧠",
     "content": """Behavioral finance studies how psychological biases affect financial decisions. Understanding these biases can help you make better investment choices.

**Common biases:**

1. **Loss Aversion**: People feel losses twice as much as equivalent gains. This leads to selling winners too early and holding losers too long.

2. **Confirmation Bias**: Seeking information that confirms existing beliefs while ignoring contradictory evidence. Always look for the counterargument.

3. **Herd Mentality**: Following the crowd into hot stocks or selling during panics. When everyone is buying, be cautious. When everyone is selling, look for opportunities.

4. **Overconfidence**: Overestimating your knowledge and abilities. Studies show most investors believe they're above average (mathematically impossible).

5. **Anchoring**: Fixating on a specific price (e.g., what you paid for a stock) rather than objective valuation. The market doesn't care what you paid.

**Solution**: Create an investment policy statement, automate your investing, and rebalance periodically. Remove emotions from the equation."""},
    {"title": "Portfolio Diversification", "difficulty": "advanced", "estimated_minutes": 15, "icon": "🎯",
     "content": """Diversification is the only free lunch in investing. It means spreading your investments across different asset classes, sectors, geographies, and strategies to reduce risk.

**The benefit**:
When one investment is down, another may be up. A diversified portfolio has lower volatility than any single investment, without sacrificing returns.

**How to diversify across:**
1. **Asset Classes**: Stocks, bonds, real estate, commodities, cash
2. **Geographies**: Domestic, developed international, emerging markets
3. **Sectors**: Tech, healthcare, finance, energy, consumer goods
4. **Company Size**: Large-cap, mid-cap, small-cap stocks
5. **Investment Style**: Growth, value, dividend

**Simple approach**: A three-fund portfolio (total US stock market, total international stock market, total bond market) provides instant diversification. Adjust the bond percentage based on your age and risk tolerance.

**Rebalancing**: Once or twice a year, sell some winners and buy some losers to maintain your target allocation. This forces you to "buy low, sell high" systematically."""},
    {"title": "Entrepreneurial Finance", "difficulty": "advanced", "estimated_minutes": 20, "icon": "🚀",
     "content": """Starting and running a business requires a different financial mindset than personal finance. Here's what every entrepreneur needs to know:

**Funding Stages:**
1. **Bootstrapping**: Self-funding from personal savings and revenue
2. **Friends & Family**: Early capital from people who believe in you
3. **Angel Investors**: High-net-worth individuals investing early
4. **Venture Capital**: Institutional money for high-growth startups
5. **Debt Financing**: Bank loans, lines of credit, SBA loans

**Key Financial Metrics for Business:**
- **Burn Rate**: How much cash you're spending monthly
- **Runway**: How many months until you run out of cash (Cash / Burn Rate)
- **Unit Economics**: Revenue per customer minus cost per customer
- **LTV**: Customer Lifetime Value
- **CAC**: Customer Acquisition Cost
- **LTV/CAC Ratio**: Target 3:1 or higher

**Financial Management Tips:**
1. Separate personal and business finances immediately
2. Use accounting software from day one
3. Understand your tax obligations (self-employment tax, VAT, etc.)
4. Build a cash reserve for slow periods
5. Reinvest profits wisely"""},
    {"title": "Crypto & Blockchain Fundamentals", "difficulty": "intermediate", "estimated_minutes": 20, "icon": "₿",
     "content": """Cryptocurrency is digital money that uses cryptography for security and operates on decentralized networks called blockchains. Bitcoin, created in 2009, was the first cryptocurrency.

**Key concepts:**
- **Blockchain**: A distributed ledger that records all transactions across a network of computers
- **Mining/Validation**: The process of confirming transactions and adding them to the blockchain
- **Wallets**: Software or hardware that stores your private keys (access to your crypto)
- **DeFi**: Decentralized Finance — financial services built on blockchain without intermediaries

**Major cryptocurrencies:**
- **Bitcoin (BTC)**: Digital gold, store of value
- **Ethereum (ETH)**: Smart contract platform, powers DeFi and NFTs
- **Stablecoins**: Pegged to fiat currency (USDT, USDC) for price stability

**⚠️ RISK WARNING**: Cryptocurrency is highly volatile and speculative. Never invest more than you can afford to lose. Be aware of scams, rug pulls, and security risks. Only use reputable exchanges and secure wallets."""},
]

PROJECTS = [
    {
        "title": "Build Your Personal Budget",
        "description": "Create a comprehensive personal budget using the 50/30/20 rule. Track your actual income and expenses, categorize spending, and identify areas for improvement.",
        "learning_objectives": "Understand the 50/30/20 framework, categorize expenses accurately, identify spending leaks, set realistic savings targets.",
        "difficulty": "beginner",
        "estimated_minutes": 30,
        "steps": [
            {"title": "Track Your Income", "description": "List all sources of income (salary, freelance, side hustles, investments) and calculate your total monthly take-home pay.", "step_type": "input"},
            {"title": "Categorize Your Expenses", "description": "Review your last 3 months of bank statements and categorize every expense into: Needs, Wants, or Savings/Debt.", "step_type": "input"},
            {"title": "Calculate Your Current Allocation", "description": "Calculate what percentage of your income goes to Needs, Wants, and Savings. Compare against the 50/30/20 benchmark.", "step_type": "calculation"},
            {"title": "Set Target Amounts", "description": "Based on the 50/30/20 rule, calculate target amounts for each category. Adjust based on your personal situation and goals.", "step_type": "calculation"},
            {"title": "Create Your Action Plan", "description": "Identify 3 specific changes you'll make this month to align your spending with your targets.", "step_type": "reflection"},
        ],
    },
    {
        "title": "Investment Portfolio Simulator",
        "description": "Design a diversified investment portfolio based on your risk tolerance, time horizon, and financial goals. Simulate different allocation strategies.",
        "learning_objectives": "Understand asset allocation, calculate expected returns, assess risk tolerance, build a diversified portfolio.",
        "difficulty": "intermediate",
        "estimated_minutes": 45,
        "steps": [
            {"title": "Assess Your Risk Tolerance", "description": "Take a risk tolerance questionnaire. Consider: age, income stability, financial goals, and how you'd react to a 30% market drop.", "step_type": "quiz"},
            {"title": "Choose Your Asset Allocation", "description": "Based on your risk tolerance, select percentages for: Stocks (domestic/international), Bonds, Real Estate, Cash.", "step_type": "input"},
            {"title": "Select Specific Investments", "description": "For each asset class, choose specific ETFs or index funds. Include ticker symbols and expense ratios.", "step_type": "input"},
            {"title": "Calculate Expected Returns", "description": "Using historical average returns (stocks ~7-10%, bonds ~3-5%, real estate ~6-8%), calculate your portfolio's expected annual return.", "step_type": "calculation"},
            {"title": "Rebalancing Plan", "description": "Define your rebalancing strategy: time-based (annually) or threshold-based (when allocation drifts by 5%+). Write your rebalancing rules.", "step_type": "reflection"},
        ],
    },
    {
        "title": "Startup Financial Model",
        "description": "Build a financial model for a startup or side hustle. Project revenue, expenses, and cash flow for the first 12 months.",
        "learning_objectives": "Understand unit economics, project cash flow, calculate burn rate and runway, build a simple P&L.",
        "difficulty": "advanced",
        "estimated_minutes": 60,
        "steps": [
            {"title": "Define Your Business Model", "description": "Describe your business: what you sell, who you sell to, how you charge, and your key assumptions about customer volume.", "step_type": "input"},
            {"title": "Project Monthly Revenue", "description": "Estimate customers per month, average transaction value, and growth rate. Create a 12-month revenue projection.", "step_type": "calculation"},
            {"title": "List All Expenses", "description": "Categorize expenses into: fixed (rent, salaries, software) and variable (COGS, marketing, transaction fees). Estimate monthly amounts.", "step_type": "input"},
            {"title": "Calculate Unit Economics", "description": "Calculate LTV (average revenue per customer) and CAC (cost to acquire a customer). Target LTV/CAC ratio of 3:1 or higher.", "step_type": "calculation"},
            {"title": "Cash Flow & Runway", "description": "Calculate monthly burn rate, cash runway, and determine when you'll reach breakeven. Identify the amount of funding needed.", "step_type": "reflection"},
        ],
    },
    {
        "title": "Debt Freedom Plan",
        "description": "Create a personalized debt payoff strategy. Choose between avalanche and snowball methods, calculate timelines, and commit to your plan.",
        "learning_objectives": "Calculate total debt burden, compare payoff strategies, create a realistic timeline, track progress.",
        "difficulty": "beginner",
        "estimated_minutes": 25,
        "steps": [
            {"title": "List All Debts", "description": "List every debt: creditor, balance, interest rate, minimum payment. Include credit cards, student loans, car loans, personal loans.", "step_type": "input"},
            {"title": "Choose Your Strategy", "description": "Compare the Avalanche (highest interest first) vs Snowball (smallest balance first) methods. Which fits your personality?", "step_type": "quiz"},
            {"title": "Calculate Payoff Timeline", "description": "Using your chosen method and available extra monthly payment, calculate how long until each debt is paid off.", "step_type": "calculation"},
            {"title": "Create Your Payment Schedule", "description": "Map out the monthly payments for each debt in order. Show the projected payoff date for each debt.", "step_type": "input"},
            {"title": "Commitment & Tracking", "description": "Write down your motivation for becoming debt-free. Define how you'll track progress and celebrate milestones.", "step_type": "reflection"},
        ],
    },
    {
        "title": "Financial Goal Visualization",
        "description": "Use data visualization principles to create a compelling visual dashboard of your financial goals and progress.",
        "learning_objectives": "Translate financial targets into visual formats, track progress effectively, build sustainable motivation systems.",
        "difficulty": "intermediate",
        "estimated_minutes": 35,
        "steps": [
            {"title": "Define SMART Goals", "description": "Write 3 financial goals that are Specific, Measurable, Achievable, Relevant, and Time-bound.", "step_type": "input"},
            {"title": "Design Progress Metrics", "description": "For each goal, define: starting point, target, current progress, and how you'll measure success (%, milestones, dates).", "step_type": "input"},
            {"title": "Visual Progress Tracker", "description": "Design a visual tracker for each goal: progress bars, thermometers, milestone maps, or countdown timers.", "step_type": "reflection"},
            {"title": "Create Accountability System", "description": "Define how you'll review progress (weekly/monthly check-ins). Who will hold you accountable? What's the consequence for falling behind?", "step_type": "reflection"},
        ],
    },
    {
        "title": "Side Hustle Profitability Analysis",
        "description": "Evaluate a side hustle idea by analyzing startup costs, ongoing expenses, pricing, and profit potential before investing time and money.",
        "learning_objectives": "Evaluate business viability, calculate true costs, determine break-even pricing, assess time vs. return.",
        "difficulty": "intermediate",
        "estimated_minutes": 40,
        "steps": [
            {"title": "Describe Your Side Hustle", "description": "What service or product will you offer? Who is your target customer? What makes you different from competitors?", "step_type": "input"},
            {"title": "Calculate Startup Costs", "description": "List all one-time costs to launch: equipment, software, licensing, marketing materials, website, initial inventory.", "step_type": "calculation"},
            {"title": "Determine Pricing", "description": "Calculate your hourly rate or product price. Consider: material costs, time, market rates, desired profit margin.", "step_type": "calculation"},
            {"title": "Profitability Projection", "description": "Project monthly revenue, expenses, and profit for months 1, 3, 6, and 12. When do you break even on startup costs?", "step_type": "calculation"},
            {"title": "Go/No-Go Decision", "description": "Based on your analysis, decide whether to launch. What would need to change for a 'no' to become a 'yes'?", "step_type": "reflection"},
        ],
    },
]

COURSES = [
    {
        "title": "Personal Finance Foundations",
        "description": "A complete beginner-friendly course covering budgeting, saving, credit, debt, and investing basics. No prior knowledge required.",
        "difficulty": "beginner",
        "estimated_hours": 4,
        "is_published": True,
        "lessons": [
            {"title": "Why Personal Finance Matters", "content": "Personal finance is 80% behavior and 20% knowledge. In this lesson, we'll explore why financial literacy is the most important skill you can develop. You'll learn about the wealth gap, the cost of financial illiteracy, and how small changes compound into massive results over time.", "duration_minutes": 12, "is_preview": True},
            {"title": "The 50/30/20 Budget Framework", "content": "Dive deep into the 50/30/20 rule. We'll walk through real examples of Needs vs Wants, how to handle irregular expenses, and how to adjust the framework for different income levels and life situations.", "duration_minutes": 18, "is_preview": True},
            {"title": "Building Your Emergency Fund", "content": "Learn why an emergency fund is your first financial priority. We'll cover how much to save, where to keep it, and strategies to build it quickly even on a tight budget.", "duration_minutes": 15},
            {"title": "Understanding Credit & Loans", "content": "How credit scores work, how to build credit from scratch, and when it makes sense to use debt. We'll compare good debt vs bad debt with real-world examples.", "duration_minutes": 20},
            {"title": "Introduction to Investing", "content": "Stocks, bonds, ETFs, mutual funds — demystified. Learn the difference between saving and investing, how to start with small amounts, and why time in the market beats timing the market.", "duration_minutes": 25},
            {"title": "Creating Your Financial Action Plan", "content": "Bring everything together into a personalized action plan. Set your first financial goals, create your budget, and commit to your first investment.", "duration_minutes": 15},
        ],
    },
    {
        "title": "Wealth Building & Investing",
        "description": "Intermediate course on building long-term wealth through strategic investing, portfolio management, and tax optimization.",
        "difficulty": "intermediate",
        "estimated_hours": 6,
        "is_published": True,
        "lessons": [
            {"title": "Asset Allocation Strategies", "content": "Learn how to divide your portfolio across asset classes based on your age, risk tolerance, and goals. We'll cover the classic 60/40 portfolio, target-date funds, and the all-weather portfolio.", "duration_minutes": 22},
            {"title": "Index Fund Investing", "content": "Why Warren Buffett recommends index funds for most investors. Compare S&P 500 index funds, total market funds, and international funds. Learn about expense ratios and their impact.", "duration_minutes": 18},
            {"title": "Real Estate Investing Fundamentals", "content": "Rental properties, REITs, and real estate crowdfunding. Calculate cap rates, cash-on-cash returns, and evaluate potential deals like a pro.", "duration_minutes": 25},
            {"title": "Tax-Efficient Investing", "content": "Strategies to minimize taxes on your investments. 401(k) vs Roth IRA vs taxable accounts. Tax-loss harvesting, asset location, and managing capital gains.", "duration_minutes": 20},
            {"title": "Portfolio Rebalancing", "content": "When and how to rebalance your portfolio. Time-based vs threshold-based rebalancing. How rebalancing forces you to buy low and sell high automatically.", "duration_minutes": 15},
            {"title": "Building Your Investment Policy Statement", "content": "Create a written IPS that governs all your investment decisions. This prevents emotional decisions during market volatility.", "duration_minutes": 20},
        ],
    },
    {
        "title": "Entrepreneurial Finance & Business Growth",
        "description": "For founders, freelancers, and business owners: manage cash flow, raise capital, and scale your business financially.",
        "difficulty": "advanced",
        "estimated_hours": 8,
        "is_published": True,
        "lessons": [
            {"title": "Business Financial Statements", "content": "Master the three core financial statements: P&L, Balance Sheet, and Cash Flow Statement. Learn how they connect and what they reveal about your business health.", "duration_minutes": 25},
            {"title": "Cash Flow Management", "content": "Why cash is king. Forecasting cash flow, managing receivables and payables, building a cash reserve, and avoiding the most common cash flow mistakes that kill businesses.", "duration_minutes": 22},
            {"title": "Fundraising & Valuation", "content": "From bootstrapping to VC funding. Understand term sheets, valuation methods, dilution, and how to choose the right funding path for your business.", "duration_minutes": 30},
            {"title": "Unit Economics Mastery", "content": "Calculate and optimize LTV, CAC, gross margin, and contribution margin. Learn how to improve unit economics before scaling.", "duration_minutes": 20},
            {"title": "Financial Modeling for Startups", "content": "Build a financial model from scratch: revenue projections, expense budgets, headcount planning, and scenario analysis.", "duration_minutes": 35},
            {"title": "Exit Strategies & Wealth Planning", "content": "Understanding acquisition, IPO, and other exit paths. How to plan for a liquidity event and manage your newfound wealth.", "duration_minutes": 25},
        ],
    },
    {
        "title": "Advanced Market Analysis",
        "description": "Learn technical and fundamental analysis, options strategies, and behavioral finance to become a sophisticated investor.",
        "difficulty": "advanced",
        "estimated_hours": 10,
        "is_published": True,
        "lessons": [
            {"title": "Fundamental Analysis Deep Dive", "content": "Analyze company financials: revenue trends, profit margins, competitive advantages, management quality, and intrinsic value calculation.", "duration_minutes": 30},
            {"title": "Technical Analysis Basics", "content": "Support and resistance, moving averages, RSI, MACD, and chart patterns. Learn when technical analysis works and its limitations.", "duration_minutes": 25},
            {"title": "Options Strategies for Income", "content": "Covered calls, cash-secured puts, credit spreads. Generate income from existing holdings or enter positions at desired prices.", "duration_minutes": 30},
            {"title": "Behavioral Finance & Psychology", "content": "Master your own psychology. Cognitive biases, emotional discipline, and the mental models used by the world's best investors.", "duration_minutes": 22},
            {"title": "Macroeconomic Analysis", "content": "How interest rates, inflation, GDP, and central bank policy affect your investments. Build a framework for top-down investing.", "duration_minutes": 25},
            {"title": "Building Your Investment Thesis", "content": "Synthesize everything into a clear investment thesis. Define your edge, your process, and how you'll evaluate your performance.", "duration_minutes": 20},
        ],
    },
]

WORKSHOPS = [
    {
        "title": "Live Budgeting Workshop",
        "description": "Build your personal budget in real-time with guidance from financial experts. Bring your bank statements and leave with a complete budget.",
        "duration_minutes": 90,
        "status": "scheduled",
    },
    {
        "title": "Stock Market Basics for Beginners",
        "description": "An interactive workshop on how the stock market works, how to read stock quotes, and how to make your first trade.",
        "duration_minutes": 60,
        "status": "scheduled",
    },
    {
        "title": "Side Hustle Launchpad",
        "description": "A hands-on workshop to validate, launch, and grow a profitable side hustle in 30 days.",
        "duration_minutes": 120,
        "status": "scheduled",
    },
    {
        "title": "Real Estate Investing 101",
        "description": "Learn how to evaluate rental properties, calculate returns, and finance your first investment property.",
        "duration_minutes": 90,
        "status": "scheduled",
    },
    {
        "title": "Cryptocurrency & Blockchain Workshop",
        "description": "Understanding blockchain technology, evaluating crypto projects securely, and building a crypto portfolio.",
        "duration_minutes": 75,
        "status": "scheduled",
    },
]

ENTREPRENEURSHIP_PATHS = [
    {"title": "Freelancer to Agency", "description": "A step-by-step journey from solo freelancer to running a full-service agency with employees and recurring revenue.", "is_published": True},
    {"title": "E-Commerce Empire", "description": "Build and scale an e-commerce business from product sourcing to customer acquisition to fulfillment.", "is_published": True},
    {"title": "SaaS Founder Track", "description": "From idea to MVP to paying customers. Learn product development, pricing, and growth for software businesses.", "is_published": True},
    {"title": "Content Creator Economy", "description": "Monetize your knowledge and creativity through courses, memberships, sponsorships, and digital products.", "is_published": True},
    {"title": "Social Impact Entrepreneur", "description": "Build a business that makes money and makes a difference. Impact measurement, B Corps, and mission-driven growth.", "is_published": True},
]

PRODUCT_CATEGORIES = [
    {"name": "Budgeting Templates", "slug": "budgeting-templates", "icon": "📊", "description": "Spreadsheet and app templates for personal and business budgeting"},
    {"name": "Investment Guides", "slug": "investment-guides", "icon": "📈", "description": "In-depth guides on stocks, bonds, real estate, and crypto investing"},
    {"name": "Business Tools", "slug": "business-tools", "icon": "💼", "description": "Tools and templates for entrepreneurs and small business owners"},
    {"name": "Financial Planning", "slug": "financial-planning", "icon": "📋", "description": "Retirement planning, tax optimization, and wealth management resources"},
    {"name": "Educational Content", "slug": "educational-content", "icon": "📚", "description": "E-books, courses, and learning materials for financial literacy"},
]

PRODUCTS = [
    {"title": "Ultimate Budgeting Spreadsheet", "slug": "ultimate-budgeting-spreadsheet", "description": "A comprehensive Google Sheets budget template with auto-categorization, charts, and monthly rollover. Includes 50/30/20 and zero-based budget versions.", "product_type": "template", "price": 19.99, "currency": "USD", "is_active": True, "category": "budgeting-templates"},
    {"title": "Small Business P&L Template", "slug": "small-business-pnl-template", "description": "Professional profit & loss statement template for small businesses. Includes expense tracking, revenue analysis, and margin calculations.", "product_type": "template", "price": 24.99, "currency": "USD", "is_active": True, "category": "business-tools"},
    {"title": "The Complete Guide to Index Investing", "slug": "complete-guide-index-investing", "description": "A 50-page e-book covering everything about index fund investing: selection criteria, portfolio construction, rebalancing strategies, and tax optimization.", "product_type": "ebook", "price": 14.99, "currency": "USD", "is_active": True, "category": "investment-guides"},
    {"title": "Retirement Calculator Pro", "slug": "retirement-calculator-pro", "description": "An advanced retirement calculator with Monte Carlo simulation, tax scenario modeling, and withdrawal strategy optimization.", "product_type": "tool", "price": 9.99, "currency": "USD", "is_active": True, "category": "financial-planning"},
    {"title": "Startup Financial Model Template", "slug": "startup-financial-model", "description": "Investor-ready financial model template for startups. Includes revenue projections, expense budgeting, cash flow analysis, and valuation estimates.", "product_type": "template", "price": 49.99, "currency": "USD", "is_active": True, "category": "business-tools"},
    {"title": "Crypto Portfolio Tracker", "slug": "crypto-portfolio-tracker", "description": "Track your cryptocurrency portfolio across exchanges. Real-time prices, profit/loss calculations, and tax reporting ready.", "product_type": "tool", "price": 12.99, "currency": "USD", "is_active": True, "category": "investment-guides"},
    {"title": "Financial Independence Workbook", "slug": "financial-independence-workbook", "description": "A step-by-step workbook to plan your journey to financial independence. Calculate your FI number, design your withdrawal strategy, and track progress.", "product_type": "ebook", "price": 19.99, "currency": "USD", "is_active": True, "category": "educational-content"},
    {"title": "Free Budgeting Starter Kit", "slug": "free-budgeting-starter-kit", "description": "Get started with budgeting for free. Includes a simple expense tracker, savings goal planner, and debt payoff calculator.", "product_type": "other", "price": 0, "currency": "USD", "is_active": True, "featured": True, "category": "budgeting-templates"},
]

COLLECTIONS = [
    {"title": "Getting Started", "slug": "getting-started", "description": "Essential resources for financial beginners", "products": ["free-budgeting-starter-kit", "ultimate-budgeting-spreadsheet", "complete-guide-index-investing"]},
    {"title": "Entrepreneur's Toolkit", "slug": "entrepreneurs-toolkit", "description": "Everything you need to launch and grow your business", "products": ["small-business-pnl-template", "startup-financial-model", "financial-independence-workbook"]},
]

AFFILIATE_PARTNERS = [
    {"name": "TradingView", "slug": "tradingview", "description": "Professional charting platform with real-time data across global markets. Used by millions of traders worldwide.", "commission_type": "percentage", "commission_value": 20, "website": "https://www.tradingview.com/", "is_service_provider": True},
    {"name": "Coinbase", "slug": "coinbase", "description": "The most trusted cryptocurrency exchange in the US. Buy, sell, and store 200+ cryptocurrencies securely.", "commission_type": "fixed", "commission_value": 10, "commission_currency": "USD", "website": "https://www.coinbase.com/", "is_service_provider": True},
    {"name": "QuickBooks", "slug": "quickbooks", "description": "Industry-leading accounting software for small businesses. Track income, expenses, payroll, and taxes.", "commission_type": "percentage", "commission_value": 25, "website": "https://quickbooks.intuit.com/", "is_service_provider": True},
    {"name": "Betterment", "slug": "betterment", "description": "Automated investing and savings app. Robo-advisor with tax-loss harvesting and personalized portfolio management.", "commission_type": "fixed", "commission_value": 20, "commission_currency": "USD", "website": "https://www.betterment.com/", "is_service_provider": True},
    {"name": "YNAB", "slug": "ynab", "description": "You Need A Budget — the gold standard budgeting app. Proactive budgeting methodology that helps users save thousands.", "commission_type": "percentage", "commission_value": 30, "website": "https://www.ynab.com/", "is_service_provider": True},
]


class Command(BaseCommand):
    help = "Seeds the database with educational content, marketplace products, and affiliate partners"

    def handle(self, *args, **options):
        now = __import__("django").utils.timezone.now()

        self.stdout.write("Seeding instructors...")
        admin = User.objects.filter(is_superuser=True).first()
        if admin:
            Instructor.objects.get_or_create(user=admin, defaults={
                "bio": "Financial educator and investment analyst with 15+ years of experience",
                "credentials": "CFA Charterholder, MBA Finance",
                "expertise_areas": "Investing, Portfolio Management, Financial Analysis",
                "is_verified": True,
            })

        self.stdout.write("Seeding concepts...")
        for c in CONCEPTS:
            Concept.objects.get_or_create(
                slug=slugify(c["title"]),
                defaults={**c, "is_published": True},
            )

        self.stdout.write("Seeding projects...")
        for p in PROJECTS:
            proj, _ = Project.objects.get_or_create(
                slug=slugify(p["title"]),
                defaults={
                    "title": p["title"],
                    "description": p["description"],
                    "learning_objectives": p["learning_objectives"],
                    "difficulty": p["difficulty"],
                    "estimated_minutes": p["estimated_minutes"],
                    "status": "published",
                },
            )
            for i, step_data in enumerate(p["steps"]):
                ProjectStep.objects.get_or_create(
                    project=proj,
                    sort_order=i + 1,
                    defaults={
                        "title": step_data["title"],
                        "description": step_data["description"],
                        "step_type": step_data["step_type"],
                    },
                )

        self.stdout.write("Seeding courses...")
        for c in COURSES:
            course, _ = Course.objects.get_or_create(
                slug=slugify(c["title"]),
                defaults={
                    "title": c["title"],
                    "description": c["description"],
                    "difficulty": c["difficulty"],
                    "estimated_hours": c["estimated_hours"],
                    "is_published": c["is_published"],
                },
            )
            for i, lesson_data in enumerate(c["lessons"]):
                Lesson.objects.get_or_create(
                    course=course,
                    sort_order=i + 1,
                    defaults={
                        "title": lesson_data["title"],
                        "content": lesson_data["content"],
                        "duration_minutes": lesson_data["duration_minutes"],
                        "is_preview": lesson_data.get("is_preview", False),
                    },
                )

        self.stdout.write("Seeding workshops...")
        for w in WORKSHOPS:
            Workshop.objects.get_or_create(
                title=w["title"],
                defaults={
                    "description": w.get("description", ""),
                    "duration_minutes": w["duration_minutes"],
                    "status": w["status"],
                    "scheduled_at": now + __import__("datetime").timedelta(days=14),
                },
            )

        self.stdout.write("Seeding entrepreneurship paths...")
        for ep in ENTREPRENEURSHIP_PATHS:
            EntrepreneurshipPath.objects.get_or_create(
                slug=slugify(ep["title"]),
                defaults=ep,
            )

        self.stdout.write("Seeding product categories...")
        for cat in PRODUCT_CATEGORIES:
            ProductCategory.objects.get_or_create(
                slug=cat["slug"],
                defaults=cat,
            )

        self.stdout.write("Seeding products...")
        created_products = {}
        for p in PRODUCTS:
            cat = ProductCategory.objects.filter(slug=p["category"]).first()
            prod, _ = Product.objects.get_or_create(
                slug=p["slug"],
                defaults={
                    "title": p["title"],
                    "description": p["description"],
                    "product_type": p["product_type"],
                    "price": p["price"],
                    "currency": p["currency"],
                    "is_active": p["is_active"],
                    "featured": p.get("featured", False),
                    "category": cat,
                },
            )
            created_products[p["slug"]] = prod

        self.stdout.write("Seeding curated collections...")
        for col in COLLECTIONS:
            collection, _ = CuratedCollection.objects.get_or_create(
                slug=col["slug"],
                defaults={"title": col["title"], "description": col["description"]},
            )
            for prod_slug in col["products"]:
                if prod_slug in created_products:
                    collection.products.add(created_products[prod_slug])

        self.stdout.write("Seeding affiliate partners...")
        for ap in AFFILIATE_PARTNERS:
            AffiliatePartner.objects.get_or_create(
                slug=ap["slug"],
                defaults={
                    "name": ap["name"],
                    "description": ap["description"],
                    "commission_type": ap["commission_type"],
                    "commission_value": ap["commission_value"],
                    "commission_currency": ap.get("commission_currency", "USD"),
                    "website": ap.get("website", ""),
                    "is_service_provider": ap.get("is_service_provider", False),
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded: {len(CONCEPTS)} concepts, {len(PROJECTS)} projects, {len(COURSES)} courses, {len(WORKSHOPS)} workshops, {len(PRODUCTS)} products, {len(AFFILIATE_PARTNERS)} affiliate partners"))

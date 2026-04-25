# निर्णय — Nirnay Decision Intelligence Platform

AI-powered risk decisioning for Indian enterprises.
Python + Streamlit · scikit-learn · XGBoost · Docker-ready.

---

## Quickstart — 3 ways to run

### Option 1: Docker (Recommended for deployment)

    # Build and run in one command
    docker compose up --build

    # Or with plain Docker
    docker build -t nirnay .
    docker run -p 8501:8501 nirnay

Opens at http://localhost:8501

---

### Option 2: Local Python (Development)

    python -m venv venv
    source venv/bin/activate        # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run app.py

---

### Option 3: Streamlit Cloud (Free hosting)

1. Push this folder to a GitHub repository
2. Go to share.streamlit.io
3. Set app.py as the entry point
4. Click Deploy — live in ~2 minutes

---

## Docker Commands Reference

    # Build the image
    docker build -t nirnay:latest .

    # Run (detached, auto-restart)
    docker run -d -p 8501:8501 --restart unless-stopped --name nirnay_app nirnay:latest

    # Run with Docker Compose
    docker compose up --build          # foreground
    docker compose up -d --build       # detached (background)
    docker compose down                # stop

    # View logs
    docker logs nirnay_app -f

    # Health check
    curl http://localhost:8501/_stcore/health

    # Rebuild after code changes
    docker compose up --build

---

## Deploy to Production (Render / Railway / Fly.io)

All three platforms support Docker deployments directly:

**Render:**
1. Connect your GitHub repo
2. Choose "Docker" as the runtime
3. Set port to 8501
4. Deploy

**Railway:**
1. railway init
2. railway up

**Fly.io:**
    fly launch
    fly deploy

---

## 10 Indian Business Datasets

| Dataset | Sector | Records |
|---------|--------|---------|
| Airtel / Jio — Customer Churn | Telecom | 847 |
| HDFC / SBI — Loan Default | Banking | 1,243 |
| Flipkart / Meesho — Fraud Detection | E-Commerce | 2,156 |
| LIC / ICICI Lombard — Claim Prediction | Insurance | 934 |
| Indian Startup — Failure Risk | VC / Startup | 456 |
| NABARD — Kisan Loan Default | Agriculture | 1,567 |
| Apollo / Fortis — Patient Readmission | Healthcare | 789 |
| MagicBricks — Property Price Drop | Real Estate | 623 |
| CSR / NGO — Impact Scoring | Social Impact | 312 |
| Delhivery — Shipment Delay | Logistics | 1,834 |

Total: 10,761 records across 10 sectors.

---

## ML Models (trained per dataset on startup)

- Logistic Regression — fast baseline, interpretable
- Random Forest — ensemble, provides feature importance
- XGBoost — gradient boosted, highest accuracy

All three trained with 5-fold cross-validation. Results shown in Reports page.

---

## Pages

| Page | What it does |
|------|-------------|
| Overview | Portfolio summary across all 10 datasets |
| Risk Monitor | Filterable, sortable risk table + CSV export |
| Decision Engine | Per-record action ranking with ROI and reasoning |
| Simulation Studio | Budget/strategy simulator with allocation plan |
| What-If Analysis | Scenario comparison with 6-month trend projection |
| Analytics | Segment charts, trends, top critical cases |
| Rule Engine | Toggle business constraints and parameter sliders |
| Human Review | Approve / reject AI recommendations with notes |
| Reports | Model metrics, action plan, full CSV export |

---

## Project Structure

    nirnay/
    ├── Dockerfile              ← Production Docker image
    ├── docker-compose.yml      ← Local dev + production compose
    ├── .dockerignore
    ├── Procfile                ← For Render / Railway
    ├── requirements.txt
    ├── app.py                  ← Entry point, sidebar, routing
    ├── .streamlit/
    │   └── config.toml         ← Dark theme pre-configured
    ├── utils/
    │   └── data_engine.py      ← All 10 datasets + 3 ML models + scorer
    └── pages/
        ├── overview.py
        ├── risk_monitor.py
        ├── decision_engine.py
        ├── simulation.py
        ├── whatif.py
        ├── analytics.py
        ├── rule_engine.py
        ├── human_review.py
        └── reports.py

---

## Resume Line

Built a full-stack Decision Intelligence Platform (Streamlit + scikit-learn + XGBoost + Docker)
that combines ML risk scoring, action simulation, what-if analysis, and human-in-the-loop review
across 10 Indian business sectors with 10,000+ records. Containerised with Docker and deployable
to any cloud platform in one command.

# निर्णय · Nirnay

Indian businesses make hundreds of risk decisions every day — which loan to approve, which customer is about to leave, which shipment will be delayed. Most of those decisions are still made on gut feel or outdated spreadsheets.

Nirnay changes that. It's a platform that looks at your data, scores every case by risk, and tells your team exactly what to do next — with a human always in the loop before anything is acted on.

**Built with:** Python · Streamlit · scikit-learn · XGBoost · Docker

---

## Get it running

**Easiest — Docker**
```bash
docker compose up --build
```
Open `http://localhost:8501`. That's it.

**Without Docker**
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**Host it free** — push to GitHub, go to [share.streamlit.io](https://share.streamlit.io), pick `app.py`. Live in 2 minutes.

---

## What it covers

Ten real Indian business problems, out of the box:

| Sector | Question it answers |
|---|---|
| Telecom | Which Airtel / Jio customers are about to churn? |
| Banking | Which HDFC / SBI loan applicants are likely to default? |
| E-Commerce | Which Flipkart / Meesho orders are probably fraud? |
| Insurance | Which LIC / ICICI claims are likely to be filed? |
| Startups | Which startups in the portfolio are at failure risk? |
| Agriculture | Which NABARD Kisan loans are at default risk? |
| Healthcare | Which Apollo / Fortis patients will be readmitted? |
| Real Estate | Which MagicBricks listings will see a price drop? |
| Social Impact | How do you score NGO / CSR programme effectiveness? |
| Logistics | Which Delhivery shipments will arrive late? |

Over 10,000 records across all ten. Everything loads automatically when you start the app.

---

## How the scoring works

Nirnay runs three different models on each dataset and shows you all three results. You don't have to pick one — you can see where they agree and where they don't.

- One model is fast and easy to explain to a manager
- One ranks which factors matter most for each decision
- One is the most accurate overall

All three are tested rigorously before their results are shown. Detailed accuracy numbers are in the Reports page.

---

## What you can do with it

| Page | What it's for |
|---|---|
| Overview | See the health of your entire portfolio at a glance |
| Risk Monitor | Browse, filter, and export every case by risk level |
| Decision Engine | Get a recommended action for each case, with reasoning |
| Simulation Studio | Test "what if we intervene on the top 100 cases?" before committing budget |
| What-If Analysis | Change one variable and see how risk scores shift |
| Analytics | Spot patterns — which segments are highest risk, which are trending worse |
| Rule Engine | Add your own business rules on top of the AI (e.g. never flag loans under ₹10k) |
| Human Review | Your team approves or rejects every AI recommendation before it becomes an action |
| Reports | Export everything — scores, decisions, model accuracy — as CSV |

---

## Deploying it properly

Works on Render, Railway, and Fly.io. All three support Docker. Point them at this repo, set the port to `8501`, and deploy.

```bash
# Railway
railway init && railway up

# Fly.io
fly launch && fly deploy
```

---

## How the code is organised

```
nirnay/
├── app.py                  # start here — controls the whole app
├── utils/data_engine.py    # all the data and scoring logic lives here
├── pages/                  # one file per page in the platform
├── Dockerfile
└── docker-compose.yml
```

If you want to add a new dataset or tweak how scoring works, `data_engine.py` is the only file you need to touch.

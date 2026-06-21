# Motilal Oswal Mutual Funds - RAG FAQ Assistant

A facts-only, compliant Retrieval-Augmented Generation (RAG) wealth chatbot assistant for 7 Motilal Oswal mutual fund schemes, inspired by Groww's design patterns and compliance safety guards.

---

### 🌐 Live Demo Chat Link
You can open and test the live chatbot execution directly over the internet here:
👉 **[https://b483cfa3ee4bcf.lhr.life](https://b483cfa3ee4bcf.lhr.life)**

*(Note: Logs into the Groww workspace automatically with secure biometric simulated authentication or pre-filled mock credentials: `a.mercer@groww.io` / `password123`)*

---

## Key Features

1. **Compliant Facts-Only Retrieval**: Answers queries regarding NAV, expense ratios, exit loads, benchmark indexes, and fund managers. Response lengths are strictly bounded to $\le 3$ sentences, exactly 1 markdown citation link, and a source updated timestamp.
2. **Advisory Query Refusal**: Automatically blocks and declines advice-seeking, comparative, or suitability questions (e.g. *"Should I invest in Contra Fund?"*), redirecting the user to official [AMFI Investor Education](https://www.amfiindia.com/investor-corner/education) or [SEBI Investor Education](https://investor.sebi.gov.in/) portals.
3. **PII Security Filter**: Instantly rejects and masks input queries containing PAN cards, Aadhaar cards, email addresses, phone numbers, or bank account details locally before sending anything to external APIs or logging pipelines.
4. **Groww-themed UI Design (SPA)**: Exposes a single-page app containing a mock login screen, active query sidebar, factual database schemes explorer, and a compliance profile workspace showing masked records.

---

## Project Architecture & Docs

* **Problem Statement & Scope**: See [docs/problemStatement.md](docs/problemStatement.md)
* **Architecture Design & Guardrails**: See [docs/architecture.md](docs/architecture.md)
* **Streamlit Cloud Deployment Guide**: See [docs/deployment_plan.md](docs/deployment_plan.md)

---

## Quick Start (Run Locally)

### 1. Setup Virtual Environment & Dependencies
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment variables
Create a `.env` file at the root and set:
```env
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Start the FastAPI API & UI Web Server
Exposes the web app interface locally:
```bash
python server.py
```
Open a browser and navigate to `http://127.0.0.1:8000/`.

### 4. Or Run via Streamlit
Exposes the python-native Streamlit dashboard:
```bash
streamlit run streamlit_app.py
```

### 5. Run Compliance Verification Tests
Executes the automated verification test suite:
```bash
python test_bot.py
```

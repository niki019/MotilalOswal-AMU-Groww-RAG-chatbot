# Deployment Plan: Groww AI FAQ Assistant on Streamlit

This document outlines the step-by-step procedure to deploy the Groww AI Mutual Fund FAQ Assistant on **Streamlit Community Cloud** for public hosting.

---

## Deployment Architecture Overview
To simplify hosting, we bypass the FastAPI server + custom HTML frontend stack, deploying a native Python Streamlit wrapper ([streamlit_app.py](file:///d:/new-project/streamlit_app.py)). This app connects directly to the core [FAQChatbot](file:///d:/new-project/chatbot.py) class, which loads pre-computed local chunks (`data/chunks.json`) and runs search and LLM operations instantly.

---

## Prerequisites
1. **GitHub Account**: A repository hosting the project codebase.
2. **Streamlit Community Cloud Account**: Log in at [share.streamlit.io](https://share.streamlit.io/) (linked to your GitHub account).
3. **Groq API Key**: A valid key to handle LLM classification and facts-only response generation.
4. **Gemini API Key** (Optional): A key to compute vector embeddings during semantic retrieval (defaults to local TF-IDF if omitted).

---

## Configuration Files

### 1. Main App Script
The main entry point for the Streamlit cloud instance is [streamlit_app.py](file:///d:/new-project/streamlit_app.py) located at the project root.

### 2. Dependency List
The cloud environment reads [requirements.txt](file:///d:/new-project/requirements.txt) during build to install Python packages. Ensure the following dependencies are included:
```text
fastapi==0.111.0
uvicorn==0.30.1
requests==2.32.3
beautifulsoup4==4.12.3
google-generativeai==0.7.0
numpy==1.26.4
scikit-learn==1.5.0
groq
streamlit
```

---

## Step-by-Step Deployment Procedure

### Step 1: Push Project Code to GitHub
1. Initialize a git repository and commit your files:
   ```bash
   git init
   git add .
   git commit -m "feat: Add Streamlit app for cloud deployment"
   ```
2. Create a public repository on GitHub (e.g. `groww-mf-faq-assistant`).
3. Add the remote origin and push the main branch:
   ```bash
   git remote add origin https://github.com/<your-username>/groww-mf-faq-assistant.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Set up Streamlit Community Cloud
1. Navigate to [Streamlit Share](https://share.streamlit.io/) and log in with your GitHub account.
2. On the dashboard workspace, click the **"New app"** button.

### Step 3: Configure Deployment Fields
In the "Deploy an app" interface, fill in the following:
* **Repository**: Select your repository (e.g., `<your-username>/groww-mf-faq-assistant`).
* **Branch**: Select `main`.
* **Main file path**: Type `streamlit_app.py`.
* **App URL** (Optional): Custom subdomain suffix if desired.

### Step 4: Configure API Key Secrets
1. Before deploying, click the **"Advanced settings..."** link at the bottom of the form.
2. Under the **Secrets** text box, add your Groq and Gemini API keys using TOML format:
   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   GEMINI_API_KEY = "your-gemini-api-key"
   ```
   *Note: If you do not have a Gemini API key, the chatbot will automatically fall back to local TF-IDF search mode.*
3. Click **"Save"**.

### Step 5: Trigger App Build & Deploy
1. Click **"Deploy!"**.
2. Streamlit will launch the build process: cloning the repository, downloading python dependencies from `requirements.txt`, and launching the server.
3. Once completed, your wealth assistant will be online at a public `*.streamlit.app` URL.

---

## Verifying Post-Deployment Compliance
Once live, verify that the following guardrails function properly in the cloud:
1. **PII Blockers**: Enter a test query containing a PAN card or phone number (e.g., `My phone is 9876543210. What is NAV?`). Ensure it prints the **"Privacy Safeguard"** warning message immediately.
2. **Advisory Check**: Ask `"Should I buy Contra Fund?"`. Ensure the bot politely refuses the advisory query and redirects you to AMFI/SEBI educational resource portals.
3. **Factual Formatting**: Ask `"What is the exit load of Motilal Oswal Contra Fund?"`. Check that the answer is at most 3 sentences, contains exactly one markdown hyperlink source reference, and has a static update footer.

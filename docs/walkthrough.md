# Walkthrough: Mutual Fund FAQ Assistant (Phase 7 Ingestion Scheduler)

This walkthrough documents the final implementation and verification of the daily automated ingestion scheduler (Phase 7).

---

## Completed Scheduler Implementation (Phase 7)

### 1. Working Directory & Path Safeguards
We updated the daily runner script [cron_job.py](file:///d:/new-project/cron_job.py) to resolve absolute paths at execution start:
- Uses `os.path.dirname(os.path.abspath(__file__))` to detect the script's root directory (`D:\new-project`).
- Executes `os.chdir()` to set the current working directory to the project root.
- Appends the directory to `sys.path` to ensure absolute import security.

This guarantees that logs are created inside `logs/ingestion.log` and imports function perfectly regardless of the shell execution origin.

### 2. Task Scheduler Registration Script
We created a PowerShell automation script [setup_scheduler.ps1](file:///d:/new-project/setup_scheduler.ps1) to register the pipeline in Windows Task Scheduler:
- Dynamically resolves absolute paths to the python interpreter (`.venv\Scripts\python.exe`) and the wrapper (`cron_job.py`).
- Registers a daily task named `GrowwFAQIngestion` set to start at `09:45` AM local time (IST) daily.

---

## Verification Results

### 1. Task Registration Checks
We executed `setup_scheduler.ps1` and successfully registered the task:
```text
Registering scheduled task 'GrowwFAQIngestion' to run at 09:45 daily...
Command: schtasks.exe /create /tn GrowwFAQIngestion /tr "D:\new-project\.venv\Scripts\python.exe" "D:\new-project\cron_job.py" /sc DAILY /st 09:45 /f
SUCCESS: The scheduled task "GrowwFAQIngestion" has successfully been created.
Task 'GrowwFAQIngestion' registered successfully.
```

We verified the task parameters in the Task Scheduler registry:
```text
Folder: \
HostName:      DESKTOP-D1DL6Q0
TaskName:      \GrowwFAQIngestion
Next Run Time: 06-06-2026 09:45:00
Status:        Ready
Logon Mode:    Interactive only
```

### 2. Manual On-demand Execution Test
We triggered the scheduled task manually using:
```powershell
schtasks /run /tn "GrowwFAQIngestion"
```
The query returned `Running` during processing, and returned to `Ready` upon successful completion. We inspected [ingestion.log](file:///d:/new-project/logs/ingestion.log) and confirmed the execution logged the ingestion run without errors:
```text
--- Ingestion Run Started at 2026-06-05 18:07:27 ---
Starting ingestion script with Heading-Aware Chunking...
Scraping https://groww.in/mutual-funds/motilal-oswal-large-and-midcap-fund-direct-growth...
Successfully ingested & chunked https://groww.in/mutual-funds/motilal-oswal-large-and-midcap-fund-direct-growth into 19 chunks.
...
Ingestion completed. Total 155 chunks saved to data\chunks.json.
Run completed successfully.
```
This confirms that the task works perfectly.

---

## Instructions to Manage the Scheduler

- **Verify scheduler configuration**:
  ```powershell
  schtasks /query /tn "GrowwFAQIngestion" /fo list
  ```
- **Trigger on-demand run manually**:
  ```powershell
  schtasks /run /tn "GrowwFAQIngestion"
  ```
- **Delete task**:
  ```powershell
  schtasks /delete /tn "GrowwFAQIngestion" /f
```

---

## Git & Demo Link Integration (Phase 8)

### 1. Git Repository Push
We staged and pushed the project files to the remote repository:
- **GitHub Repository**: [niki019/MotilalOswal-AMU-Groww-RAG-chatbot](https://github.com/niki019/MotilalOswal-AMU-Groww-RAG-chatbot.git)
- **Branch**: `main`

### 2. Live Demo Link Update & Premium HTML UI Integration
We updated the root [README.md](file:///d:/new-project/README.md) file to point directly to the premium HTML/CSS/JS Groww-themed frontend served by the FastAPI application:
- **Public URL**: [https://b483cfa3ee4bcf.lhr.life](https://b483cfa3ee4bcf.lhr.life)
- **Deployment Details**: Routed the localhost.run tunnel directly to port `8000` (`ssh -R 80:127.0.0.1:8000 nokey@localhost.run`). This serves the custom SPA built locally (featuring the secure login page, interactive chat history, schema explorer grid, and masked privacy panels).
- Verified that the public link returns 200 OK and renders the exact premium Groww workspace environment.
- **Logo Icon Redesign**: Replaced the generic box-plus logo icon on both the login page and the sidebar header with a premium, financial growth-themed SVG (composed of four rounded, semi-transparent rising growth bars overlaid with a bold, upward-pointing trendline arrow), enhancing the visual appeal.
- **Top 15 Funds Ingestion**: Crawled the Motilal Oswal AMC main page on Groww to identify the top 15 mutual fund schemes, added their URLs to [ingestion.py](file:///d:/new-project/ingestion.py), and expanded the keyword mappings in [rag_engine.py](file:///d:/new-project/rag_engine.py). Re-ran the ingestion pipeline to build a 378-chunk index covering all 15 schemes.

---

## LLM Integration & Local Environment Configuration (Phase 9)

### 1. Root .env Configuration
We created a local [root .env](file:///d:/new-project/.env) file containing the valid Groq API key to handle LLM classification and facts-only response generation. The `.env` file is excluded from remote tracking by `.gitignore` to maintain security.

### 2. Auto-dotenv Loader Implementation
We implemented a custom, pure Python `load_dotenv` parser in [chatbot.py](file:///d:/new-project/chatbot.py) and [rag_engine.py](file:///d:/new-project/rag_engine.py) to load environment variables from the `.env` file automatically during startup.

### 3. Server Re-launch & Compliance Verification
We restarted the background Streamlit and FastAPI instances, enabling online LLM query processing.
- Executed `test_bot.py` and verified that **100% of the compliance checks pass successfully** (refusals, PII triggers, exit loads, expense ratios, and fund managers).
- General questions like `"give me the expense ratio"` now successfully call Llama 3 to summarize the top retrieved context chunk, extracting the exact percentage (e.g., `2.37%`) instead of returning raw metadata.

---

## Deliverables & Documentation (Phase 10)
- **Sample Q&A Generation**: Created the file [docs/qa_samples.md](file:///d:/new-project/docs/qa_samples.md) which contains 8 representative test cases (including factual outputs, advisory refusals with educational links, and PII masking blocks) matching the chatbot's live API outputs.
- **Git Push**: Pushed all deliverables, database schemas, and documentation files to the GitHub repository.

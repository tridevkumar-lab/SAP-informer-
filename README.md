# SAP & Yard Assistant (Python starter)

A local-first starter for an internal SAP process instructor and error explanation chatbot. It includes local document indexing/search, a local Ollama model connector, a small web UI, and an optional read-only SAP OData stock adapter.

## What is included

- FastAPI backend and browser chat page.
- Local SQLite FTS5 search over SOPs, transaction guides, error references and yard procedures.
- Local model calls through the Ollama Python library. No hosted AI API is used.
- Optional SAP stock lookup over an approved OData service. The connector is disabled until configured.
- Local ingestion for TXT, Markdown, CSV, LOG, PDF, DOCX and XLSX documents.
- A basic test for indexing and retrieval.

## Run locally

1. Install Python 3.11 or newer and install Ollama on the same computer or an internal server.
2. Pull a model supported by your machine, for example `ollama pull qwen2.5:7b`. Model memory needs depend on the model and quantization.
3. Create an environment and install dependencies:

   ```bash
   python -m venv .venv
   # Windows PowerShell: .venv\Scripts\Activate.ps1
   # Linux/macOS: source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and adjust the model name if needed. Load `.env` variables into your process (or set them in your IDE/OS).
5. Add approved, non-secret procedures to `data/knowledge/`.
6. Start Ollama, then run the app:

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

7. Open `http://127.0.0.1:8000`, click **Index local procedures**, then ask a question. API docs are at `/docs`.

Run tests with `pytest`.

## Configure SAP stock access

Do this with your SAP Basis/ABAP team. They must provide an approved, read-only OData service that accepts `Material`, `Plant`, and optional `StorageLocation`, and returns the stock fields permitted for the chatbot. Configure its URL and dedicated technical-user credentials in environment variables. Do not put passwords in source control. Keep TLS verification enabled. The service's actual parameter names and response format may need adjustment in `app/sap_connector.py` to match your SAP implementation.

The connector uses HTTP GET only. It does not post goods movements, update inventory, or access the SAP database directly. If you prefer RFC, replace the adapter with a narrowly scoped PyRFC call to an approved read-only ABAP function module; do not expose generic arbitrary RFC execution.

## Current starter limitations

- Search is local keyword full-text search (SQLite FTS5), not semantic vector search.
- The first release does not authenticate users. Keep it bound to localhost until company authentication and role checks are added before a shared deployment.
- OData endpoint and field mapping are environment/configuration dependent and must be tested against your SAP service.
- It is a starter implementation, not a production SAP integration. Validate answers against approved procedures and SAP results before operational use.

## Important data handling

Do not commit SAP passwords, access tokens, internal host details, production exports, customer/vendor information or confidential SOPs. `.env`, local databases and files under `data/knowledge/` are excluded from Git by default. Keep the local model server and application within your organization's approved network boundary.

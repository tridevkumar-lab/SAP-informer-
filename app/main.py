from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from .assistant import answer
from .config import settings
from .knowledge import all_sources, ingest_folder
from .sap_connector import SAPNotConfigured, SAPReadError, get_stock
from .schemas import ChatRequest, ChatResponse, Source

app = FastAPI(title=settings.app_name, version="0.1.0")
KNOWLEDGE_DIR = "data/knowledge"


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/", response_class=HTMLResponse)
def home():
    return Path("app/static/index.html").read_text(encoding="utf-8")


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    intent = "LIVE_STOCK" if any(w in request.message.lower() for w in ("stock", "inventory", "quantity")) else None
    if intent:
        if not request.material or not request.plant:
            return ChatResponse(
                intent="LIVE_STOCK",
                answer="For a live stock lookup, provide the material number and plant. Add storage location if you want a location-specific result.",
            )
        try:
            payload, as_of = get_stock(request.material, request.plant, request.storage_location)
        except SAPNotConfigured:
            return ChatResponse(
                intent="LIVE_STOCK",
                answer="Live SAP stock access is not configured yet. Ask your SAP Basis/ABAP team for an approved read-only OData stock service, then configure SAP_STOCK_ODATA_URL.",
            )
        except (SAPReadError, ValueError) as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        evidence = [{"source": "Live SAP OData stock response", "content": str(payload)}]
        prompt = (f"Explain this live SAP stock result for material {request.material}, "
                  f"plant {request.plant}, storage location {request.storage_location or 'all'}: {payload}")
        try:
            from .assistant import answer_with_local_model
            response_text = answer_with_local_model(prompt, evidence)
        except Exception:
            response_text = f"SAP returned: {payload}"
        return ChatResponse(
            intent="LIVE_STOCK", answer=response_text,
            sources=[Source(name=evidence[0]["source"], excerpt=str(payload)[:500])],
            data_as_of=as_of,
        )

    detected_intent, response_text, evidence = answer(request.message, settings.database_path)
    return ChatResponse(
        intent=detected_intent,
        answer=response_text,
        sources=[Source(name=item["source"], excerpt=item["content"][:500]) for item in evidence],
    )


@app.post("/api/admin/ingest")
def ingest():
    # Local admin convenience for a trusted, on-premise installation.
    try:
        results = ingest_folder(settings.database_path, KNOWLEDGE_DIR)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {type(exc).__name__}") from exc
    return {"indexed_documents": results, "documents": len(results)}


@app.get("/api/admin/sources")
def sources():
    return {"sources": all_sources(settings.database_path)}

from ollama import Client
from .config import settings
from .knowledge import search

ERROR_WORDS = ("error", "message", "failed", "failure", "exception", "not allowed", "cannot", "can't")
STOCK_WORDS = ("stock", "inventory", "available quantity", "storage location", "yard stock")


def classify(message: str) -> str:
    text = message.lower()
    if any(word in text for word in ERROR_WORDS):
        return "ERROR_EXPLANATION"
    if any(word in text for word in STOCK_WORDS):
        return "LIVE_STOCK"
    if any(word in text for word in ("how do i", "process", "procedure", "steps", "transaction", "t-code")):
        return "PROCESS_HELP"
    return "GENERAL"


def answer_with_local_model(message: str, evidence: list[dict[str, str]]) -> str:
    if not evidence:
        return ("I could not find a matching approved procedure in the local knowledge base. "
                "Please provide the transaction, exact error text, or the relevant SOP.")
    context = "\n\n".join(
        f"SOURCE: {item['source']}\nCONTENT: {item['content']}" for item in evidence
    )
    client = Client(host=settings.ollama_host)
    response = client.chat(
        model=settings.ollama_model,
        messages=[
            {"role": "system", "content": (
                "You are an internal SAP, inventory, and yard-process instructor. "
                "Use only the evidence below. Explain steps plainly. Do not invent SAP "
                "transactions, configuration, error causes, or stock values. If evidence "
                "is insufficient, say so and ask for the missing detail. Never instruct "
                "the user to bypass authorization or post a stock change. Cite source names."
            )},
            {"role": "user", "content": f"Question: {message}\n\nEvidence:\n{context}"},
        ],
        options={"temperature": 0.1},
    )
    return response.message.content.strip()


def answer(message: str, db_path: str) -> tuple[str, str, list[dict[str, str]]]:
    intent = classify(message)
    evidence = search(db_path, message)
    try:
        result = answer_with_local_model(message, evidence)
    except Exception as exc:
        # Avoid returning connection strings, environment variables, or SDK internals.
        result = ("The local model is unavailable. Start Ollama, confirm the configured "
                  "model is installed, and retry. Retrieved sources: " +
                  (", ".join(item["source"] for item in evidence) or "none"))
    return intent, result, evidence

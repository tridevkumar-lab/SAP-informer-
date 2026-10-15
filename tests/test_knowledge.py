from app.knowledge import search, upsert_document


def test_document_can_be_indexed_and_searched(tmp_path):
    db = str(tmp_path / "test.db")
    upsert_document(db, "goods_receipt.md", "For a goods receipt, verify the purchase order and material before posting.")
    results = search(db, "goods receipt purchase order")
    assert results
    assert results[0]["source"] == "goods_receipt.md"

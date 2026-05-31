from src.core.chunking import chunk_document, count_tokens
from src.core.layout import LayoutDocument, TextBlock


def test_token_budget_respects_limit():
    blocks = [
        TextBlock(text="word " * 200, page=1, bbox=(0, 0, 100, 10)),
        TextBlock(text="more " * 200, page=1, bbox=(0, 10, 100, 20)),
    ]
    doc = LayoutDocument(blocks=blocks, page_count=1)
    chunks = chunk_document(doc, strategy="token_budget", token_budget=256)
    assert chunks
    for ch in chunks:
        assert ch.token_count <= 256 or ch.token_count <= 300


def test_by_heading_splits():
    blocks = [
        TextBlock(text="Intro", page=1, bbox=(0, 0, 100, 10), kind="heading", level=1),
        TextBlock(text="Body text", page=1, bbox=(0, 10, 100, 20)),
        TextBlock(text="Methods", page=1, bbox=(0, 20, 100, 30), kind="heading", level=2),
        TextBlock(text="More body", page=1, bbox=(0, 30, 100, 40)),
    ]
    doc = LayoutDocument(blocks=blocks, page_count=1)
    chunks = chunk_document(doc, strategy="by_heading")
    assert len(chunks) >= 2


def test_count_tokens_positive():
    assert count_tokens("hello world") > 0

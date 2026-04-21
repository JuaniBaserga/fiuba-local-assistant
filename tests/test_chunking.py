from fiuba_local.config import ChunkConfig
from fiuba_local.textops import chunk_text


def test_chunk_text_produces_multiple_chunks_for_long_input():
    raw = "palabra " * 1200
    chunks = chunk_text(raw, ChunkConfig(max_chars=500, overlap_chars=50))
    assert len(chunks) > 1
    assert chunks[0].index == 0

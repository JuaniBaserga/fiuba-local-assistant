from pathlib import Path

from fiuba_local.semantic import index_semantic_pilot, search_semantic, semantic_stats


class FakeEmbedder:
    model_id = "fake-local"

    def __init__(self):
        self.calls = 0

    def encode(self, texts: list[str]) -> list[list[float]]:
        self.calls += len(texts)
        vectors = []
        for text in texts:
            lower = text.lower()
            vectors.append(
                [
                    float(lower.count("flotacion") + lower.count("flotación")),
                    float(lower.count("trituracion") + lower.count("trituración")),
                    float(len(lower) % 7),
                ]
            )
        return vectors


def test_semantic_index_reuses_embeddings_for_unchanged_text(tmp_path: Path):
    root = tmp_path / "Facultad"
    materia = root / "Ind Extractivas"
    materia.mkdir(parents=True)
    (materia / "apunte.txt").write_text("flotacion por espuma y burbujas", encoding="utf-8")

    db_path = tmp_path / "semantic.db"
    first = FakeEmbedder()
    stats = index_semantic_pilot(db_path=db_path, root=root, area="Ind Extractivas", embedder=first)

    assert stats.updated == 1
    assert stats.embeddings_created == 1
    assert first.calls == 1

    second = FakeEmbedder()
    stats = index_semantic_pilot(db_path=db_path, root=root, area="Ind Extractivas", embedder=second)

    assert stats.skipped_unchanged == 1
    assert stats.embeddings_created == 0
    assert second.calls == 0
    assert semantic_stats(db_path)["embeddings"] == 1


def test_semantic_search_returns_best_neighbor(tmp_path: Path):
    root = tmp_path / "Facultad"
    materia = root / "Ind Extractivas"
    materia.mkdir(parents=True)
    (materia / "flotacion.txt").write_text("flotacion por espuma y burbujas", encoding="utf-8")
    (materia / "trituracion.txt").write_text("trituracion molienda chancado", encoding="utf-8")

    db_path = tmp_path / "semantic.db"
    embedder = FakeEmbedder()
    index_semantic_pilot(db_path=db_path, root=root, area="Ind Extractivas", embedder=embedder, limit_files=10)

    hits = search_semantic(db_path=db_path, query="separacion por flotacion", embedder=embedder, limit=2)

    assert len(hits) == 2
    assert hits[0].path.endswith("flotacion.txt")
    assert hits[0].page_start == 1

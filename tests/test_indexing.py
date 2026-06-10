import unittest

import numpy as np

from app.indexing.vector_store import SimpleVectorStore


class SimpleVectorStoreTests(unittest.TestCase):
    def test_search_returns_most_similar_chunk_first(self) -> None:
        store = SimpleVectorStore()
        store.add_documents(
            ["profil data science", "experience marketing"],
            np.array([[1.0, 0.0], [0.0, 1.0]]),
        )

        results = store.search(np.array([0.9, 0.1]), top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].text, "profil data science")

    def test_top_k_limits_results(self) -> None:
        store = SimpleVectorStore()
        store.add_documents(
            ["a", "b", "c"],
            np.array([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]),
        )

        self.assertEqual(len(store.search(np.array([1.0, 0.0]), top_k=2)), 2)

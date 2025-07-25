import numpy as np
class VectorStore:
    def __init__(self):
        self.vectorStore = []

    def add(self, data: dict):
        self.vectorStore.append(data)

    def search(self, embedding: list[float], topK: int = 3 ):
        scored = []
        for item in self.vectorStore:
            score = self.cosine_similarity(embedding, item['embedding'])
            scored.append({
                "score": score,
                "document": item['document']
            })
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:topK]

    def cosine_similarity(self, v1: list[float], v2: list[float]):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        
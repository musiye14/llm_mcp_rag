from VectorStore import VectorStore
import requests
import os
from dotenv import load_dotenv
import asyncio

load_dotenv(verbose=True)

class EmbeddingRetrivers:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.vectorStore = VectorStore()

    async def embedQuery(self, query: str):
        embed = await self.embed(query)
        return embed

    async def embedDocument(self, document: str):
        embed = await self.embed(document)
        self.vectorStore.add({
            "embedding": embed,
            "document": document,
        })
        return embed

    async def embed(self, doucument: str):
        key = os.getenv("EMBEDDING_KEY")
        url = os.getenv("EMBEDDING_BASE_URL") + "/embeddings"
        payload = {
            "model": self.model_name,
            "input": doucument
        }
        headers = {
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json"
        }

        response_obj = await asyncio.to_thread(requests.request, "POST", url, json=payload, headers=headers)
        response = response_obj.json()
        print(response['data'][0]['embedding'])
        return response['data'][0]['embedding']
    
    async def retrieve(self, query: str, topK: int = 3):
        embed = await self.embedQuery(query)
        return self.vectorStore.search(embed, topK)
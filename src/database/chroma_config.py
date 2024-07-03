import os

import chromadb

path = os.getcwd()
chroma_client = chromadb.PersistentClient(path=path)

topic_collection = chroma_client.get_or_create_collection(name="topics")
subtopic_collection = chroma_client.get_or_create_collection(name="subtopics")

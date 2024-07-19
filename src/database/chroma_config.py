import os
import chromadb


path = os.getcwd() + "/chroma_db"
chroma_client = chromadb.PersistentClient(path=path)

subtopic_collection = chroma_client.get_or_create_collection(name="subtopics")

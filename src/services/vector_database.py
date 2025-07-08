import chromadb

class VectorDatabase:
    def __init__(self, persist_directory="./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)

"""ChromaDB manager for long-term memory storage."""

from chromadb import Client, Settings
from chromadb.config import Settings as ChromaSettings

class ChromaManager:
    """Manages ChromaDB operations for long-term memory."""
    
    def __init__(self, host: str, port: int):
        """Initialize ChromaDB client and collection.
        
        Args:
            host: ChromaDB server host
            port: ChromaDB server port
        """
        self.client = Client(Settings(
            chroma_api_impl="rest",
            chroma_server_host=host,
            chroma_server_http_port=port
        ))
        self.collection = self.client.get_or_create_collection("geometra_memory") 
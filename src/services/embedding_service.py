from enum import Enum
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from typing import List, Tuple, Union, Dict

class EmbeddingModelS(Enum): 
    MINI_LM_L6_V2 = "all-MiniLM-L6-v2"
    PARAPHRASE_MPNET_BASE_V2 = "paraphrase-mpnet-base-v2"
    DISTILBERT_BASE_NLI_STSB = "distilbert-base-nli-stsb-mean-tokens"
    ALL_DISTILROBERTA_V1 = "all-distilroberta-v1"
    ALL_MPNET_BASE_V2 = "all-mpnet-base-v2"

class EmbeddingService:
    def __init__(self, model_name=EmbeddingModelS.MINI_LM_L6_V2):
        self.model = self._initialize_model(model_name)

    def _initialize_model(self, model_name: EmbeddingModelS) -> SentenceTransformer:
        """
        Initialize and load the sentence transformer model.
        
        Args:
            model_name: EmbeddingModelS enum value specifying which model to load
            
        Returns:
            SentenceTransformer: Loaded sentence transformer model
            
        Raises:
            ValueError: If model_name is not an instance of EmbeddingModelS Enum
        """
        if not isinstance(model_name, EmbeddingModelS):
            raise ValueError(f"Invalid model name: {model_name}. Must be an instance of EmbeddingModelS Enum.")
        
        self.model = SentenceTransformer(model_name.value)
        return self.model

    def generate_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for input text(s).
        
        Args:
            text: A single string or a list of strings to encode
            
        Returns:
            np.ndarray: Embedding vector(s) for the input text(s).
                       Shape is (embedding_dim,) for single string input,
                       or (n, embedding_dim) for list of n strings.
            
        Example:
            >>> service = EmbeddingService()
            >>> # Single text
            >>> emb = service.generate_embedding("Hello world")
            >>> # Multiple texts
            >>> embs = service.generate_embedding(["Hello world", "Hi there"])
        """
        if isinstance(text, str):
            text = [text]
        return self.model.encode(text)

    def clear_model(self):
        """Free model from memory"""
        if self.model:
            del self.model
            self.model = None
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

    def cosine_similarity(
        self, 
        embedding1: Union[List[float], np.ndarray, torch.Tensor],
        embedding2: Union[List[float], np.ndarray, torch.Tensor]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            float: Cosine similarity score between -1 and 1
            
        Example:
            >>> service = EmbeddingService()
            >>> emb1 = service.generate_embedding(["Hello world"])
            >>> emb2 = service.generate_embedding(["Hi there"])
            >>> similarity = service.cosine_similarity(emb1[0], emb2[0])
        """
        # Convert to tensors if needed
        if isinstance(embedding1, list):
            embedding1 = torch.tensor(embedding1)
        if isinstance(embedding2, list):
            embedding2 = torch.tensor(embedding2)
            
        return util.cos_sim(embedding1, embedding2).item()

    def similarity_matrix(
        self,
        embeddings1: Union[List[List[float]], np.ndarray, torch.Tensor],
        embeddings2: Union[List[List[float]], np.ndarray, torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Compute similarity matrix between two sets of embeddings.
        If only embeddings1 is provided, computes pairwise similarities.
        
        Args:
            embeddings1: First set of embeddings (n x d)
            embeddings2: Optional second set of embeddings (m x d)
            
        Returns:
            torch.Tensor: Similarity matrix of shape (n x m) or (n x n)
            
        Example:
            >>> service = EmbeddingService()
            >>> embs = service.generate_embedding(["text1", "text2", "text3"])
            >>> sim_matrix = service.similarity_matrix(embs)
        """
        # Convert to tensors if needed
        if isinstance(embeddings1, list):
            embeddings1 = torch.tensor(embeddings1)
        if embeddings2 is not None and isinstance(embeddings2, list):
            embeddings2 = torch.tensor(embeddings2)
            
        if embeddings2 is None:
            embeddings2 = embeddings1
            
        return util.cos_sim(embeddings1, embeddings2)

    def find_most_similar(
        self,
        query_embedding: Union[List[float], np.ndarray, torch.Tensor],
        candidate_embeddings: Union[List[List[float]], np.ndarray, torch.Tensor],
        top_k: int = 5,
        threshold: float = None
    ) -> List[Tuple[int, float]]:
        """
        Find the most similar embeddings to a query embedding.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embeddings to compare against
            top_k: Number of top results to return
            threshold: Optional minimum similarity threshold
            
        Returns:
            List of tuples (index, similarity_score) sorted by similarity (highest first)
            
        Example:
            >>> service = EmbeddingService()
            >>> query = service.generate_embedding(["How do I learn Python?"])[0]
            >>> docs = service.generate_embedding(["Python tutorial", "Java guide", "Python basics"])
            >>> results = service.find_most_similar(query, docs, top_k=2)
        """
        # Convert to tensors if needed
        if isinstance(query_embedding, list):
            query_embedding = torch.tensor(query_embedding)
        if isinstance(candidate_embeddings, list):
            candidate_embeddings = torch.tensor(candidate_embeddings)
            
        # Compute similarities
        similarities = util.cos_sim(query_embedding, candidate_embeddings)[0]
        
        # Apply threshold if provided
        if threshold is not None:
            mask = similarities >= threshold
            similarities = similarities[mask]
            indices = torch.where(mask)[0]
        else:
            indices = torch.arange(len(similarities))
        
        # Get top k results
        top_k = min(top_k, len(similarities))
        top_results = torch.topk(similarities, k=top_k)
        
        # Return list of (index, score) tuples
        results = [
            (indices[idx].item(), score.item()) 
            for idx, score in zip(top_results.indices, top_results.values)
        ]
        
        return results

    def semantic_search(
        self,
        query_text: str,
        corpus_embeddings: Union[List[List[float]], np.ndarray, torch.Tensor],
        top_k: int = 5,
        threshold: float = None
    ) -> List[Tuple[int, float]]:
        """
        Perform semantic search: encode query text and find most similar corpus embeddings.
        
        Args:
            query_text: Text query to search for
            corpus_embeddings: Pre-computed embeddings of the corpus
            top_k: Number of top results to return
            threshold: Optional minimum similarity threshold
            
        Returns:
            List of tuples (index, similarity_score) sorted by similarity
            
        Example:
            >>> service = EmbeddingService()
            >>> corpus = ["Python is a programming language", "Java is also a language", "Dogs are pets"]
            >>> corpus_embs = service.generate_embedding(corpus)
            >>> results = service.semantic_search("coding in Python", corpus_embs, top_k=2)
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding([query_text])[0]
        
        # Find most similar
        return self.find_most_similar(query_embedding, corpus_embeddings, top_k, threshold)

    def batch_semantic_search(
        self,
        query_texts: List[str],
        corpus_embeddings: Union[List[List[float]], np.ndarray, torch.Tensor],
        top_k: int = 5,
        threshold: float = None
    ) -> List[List[Tuple[int, float]]]:
        """
        Perform semantic search for multiple queries at once.
        
        Args:
            query_texts: List of text queries
            corpus_embeddings: Pre-computed embeddings of the corpus
            top_k: Number of top results to return per query
            threshold: Optional minimum similarity threshold
            
        Returns:
            List of results, one per query. Each result is a list of (index, score) tuples
            
        Example:
            >>> service = EmbeddingService()
            >>> corpus_embs = service.generate_embedding(["doc1", "doc2", "doc3"])
            >>> queries = ["query1", "query2"]
            >>> results = service.batch_semantic_search(queries, corpus_embs, top_k=2)
        """
        # Generate embeddings for all queries
        query_embeddings = self.generate_embedding(query_texts)
        
        # Convert to tensor if needed
        if isinstance(corpus_embeddings, list):
            corpus_embeddings = torch.tensor(corpus_embeddings)
        if isinstance(query_embeddings, list):
            query_embeddings = torch.tensor(query_embeddings)
        
        results = []
        for query_emb in query_embeddings:
            result = self.find_most_similar(query_emb, corpus_embeddings, top_k, threshold)
            results.append(result)
            
        return results

    def find_duplicates(
        self,
        embeddings: Union[List[List[float]], np.ndarray, torch.Tensor],
        threshold: float = 0.95
    ) -> List[Tuple[int, int, float]]:
        """
        Find duplicate or near-duplicate embeddings based on similarity threshold.
        
        Args:
            embeddings: List of embeddings to check for duplicates
            threshold: Similarity threshold above which items are considered duplicates
            
        Returns:
            List of tuples (index1, index2, similarity) for all pairs above threshold
            
        Example:
            >>> service = EmbeddingService()
            >>> texts = ["Hello world", "Hello world!", "Goodbye world"]
            >>> embs = service.generate_embedding(texts)
            >>> duplicates = service.find_duplicates(embs, threshold=0.95)
        """
        # Convert to tensor if needed
        if isinstance(embeddings, list):
            embeddings = torch.tensor(embeddings)
            
        # Compute similarity matrix
        sim_matrix = util.cos_sim(embeddings, embeddings)
        
        duplicates = []
        n = len(embeddings)
        
        # Check upper triangle of matrix (avoid checking same pair twice)
        for i in range(n):
            for j in range(i + 1, n):
                similarity = sim_matrix[i][j].item()
                if similarity >= threshold:
                    duplicates.append((i, j, similarity))
        
        # Sort by similarity (highest first)
        duplicates.sort(key=lambda x: x[2], reverse=True)
        
        return duplicates

    def cluster_embeddings(
        self,
        embeddings: Union[List[List[float]], np.ndarray, torch.Tensor],
        threshold: float = 0.75,
        min_cluster_size: int = 2
    ) -> Dict[int, List[int]]:
        """
        Cluster embeddings based on similarity threshold using community detection.
        
        Args:
            embeddings: List of embeddings to cluster
            threshold: Minimum similarity for items to be in the same cluster
            min_cluster_size: Minimum number of items in a cluster
            
        Returns:
            Dictionary mapping cluster_id to list of embedding indices
            
        Example:
            >>> service = EmbeddingService()
            >>> texts = ["Python tutorial", "Python guide", "Java basics", "Java intro"]
            >>> embs = service.generate_embedding(texts)
            >>> clusters = service.cluster_embeddings(embs, threshold=0.7)
        """
        # Convert to tensor if needed
        if isinstance(embeddings, list):
            embeddings = torch.tensor(embeddings)
        
        # Use sentence-transformers community detection
        clusters = util.community_detection(embeddings, min_community_size=min_cluster_size, threshold=threshold)
        
        # Convert to dictionary format
        cluster_dict = {}
        for cluster_id, cluster_indices in enumerate(clusters):
            cluster_dict[cluster_id] = [idx.item() if isinstance(idx, torch.Tensor) else idx for idx in cluster_indices]
            
        return cluster_dict


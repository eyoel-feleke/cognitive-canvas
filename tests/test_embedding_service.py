import pytest
import torch
import numpy as np
from src.services.embedding_service import EmbeddingService, EmbeddingModelS


@pytest.fixture
def embedding_service():
    """Fixture for creating an EmbeddingService instance."""
    return EmbeddingService(EmbeddingModelS.MINI_LM_L6_V2)


@pytest.fixture
def sample_texts():
    """Fixture for sample texts."""
    return [
        "Python is a programming language",
        "Java is also a programming language",
        "Dogs are pets",
        "Cats are pets too"
    ]


@pytest.fixture
def sample_embeddings(embedding_service, sample_texts):
    """Fixture for sample embeddings."""
    return embedding_service.generate_embedding(sample_texts)


class TestEmbeddingServiceInitialization:
    """Test initialization and model loading."""
    
    def test_initialization_with_default_model(self):
        """Test that service initializes with default model."""
        service = EmbeddingService()
        assert service.model is not None
        
    def test_initialization_with_specific_model(self):
        """Test initialization with a specific model."""
        service = EmbeddingService(EmbeddingModelS.ALL_DISTILROBERTA_V1)
        assert service.model is not None
        
    def test_initialization_with_invalid_model(self):
        """Test that invalid model raises ValueError."""
        with pytest.raises(ValueError):
            service = EmbeddingService("invalid-model")


class TestEmbeddingGeneration:
    """Test embedding generation functionality."""
    
    def test_generate_single_embedding(self, embedding_service):
        """Test generating embedding for a single text."""
        text = ["Hello world"]
        embedding = embedding_service.generate_embedding(text)
        
        assert embedding is not None
        assert len(embedding) == 1
        assert len(embedding[0]) > 0  # Should have dimensions
        
    def test_generate_multiple_embeddings(self, embedding_service, sample_texts):
        """Test generating embeddings for multiple texts."""
        embeddings = embedding_service.generate_embedding(sample_texts)
        
        assert len(embeddings) == len(sample_texts)
        # All embeddings should have the same dimension
        assert all(len(emb) == len(embeddings[0]) for emb in embeddings)
        
    def test_embedding_consistency(self, embedding_service):
        """Test that same text produces same embedding."""
        text = ["Consistent text"]
        emb1 = embedding_service.generate_embedding(text)
        emb2 = embedding_service.generate_embedding(text)
        
        # Should be identical or very close
        similarity = embedding_service.cosine_similarity(emb1[0], emb2[0])
        assert similarity > 0.99


class TestCosineSimilarity:
    """Test cosine similarity calculations."""
    
    def test_cosine_similarity_identical_texts(self, embedding_service):
        """Test that identical texts have similarity of 1.0."""
        text = ["Hello world"]
        emb = embedding_service.generate_embedding(text)
        similarity = embedding_service.cosine_similarity(emb[0], emb[0])
        
        assert abs(similarity - 1.0) < 0.001
        
    def test_cosine_similarity_similar_texts(self, embedding_service):
        """Test that similar texts have high similarity."""
        text1 = ["I love Python programming"]
        text2 = ["Python is my favorite programming language"]
        
        emb1 = embedding_service.generate_embedding(text1)[0]
        emb2 = embedding_service.generate_embedding(text2)[0]
        similarity = embedding_service.cosine_similarity(emb1, emb2)
        
        assert similarity > 0.5  # Should be fairly similar
        
    def test_cosine_similarity_different_texts(self, embedding_service):
        """Test that different texts have lower similarity."""
        text1 = ["Python programming"]
        text2 = ["The weather is nice today"]
        
        emb1 = embedding_service.generate_embedding(text1)[0]
        emb2 = embedding_service.generate_embedding(text2)[0]
        similarity = embedding_service.cosine_similarity(emb1, emb2)
        
        assert similarity < 0.3  # Should be dissimilar
        
    def test_cosine_similarity_with_lists(self, embedding_service):
        """Test cosine similarity with list inputs."""
        emb1 = [0.1, 0.2, 0.3, 0.4]
        emb2 = [0.1, 0.2, 0.3, 0.4]
        similarity = embedding_service.cosine_similarity(emb1, emb2)
        
        assert abs(similarity - 1.0) < 0.001


class TestSimilarityMatrix:
    """Test similarity matrix computation."""
    
    def test_similarity_matrix_square(self, embedding_service, sample_embeddings):
        """Test computing similarity matrix for single set."""
        sim_matrix = embedding_service.similarity_matrix(sample_embeddings)
        
        assert sim_matrix.shape[0] == len(sample_embeddings)
        assert sim_matrix.shape[1] == len(sample_embeddings)
        
        # Diagonal should be 1.0 (identical to self)
        for i in range(len(sample_embeddings)):
            assert abs(sim_matrix[i][i].item() - 1.0) < 0.001
            
    def test_similarity_matrix_rectangular(self, embedding_service):
        """Test computing similarity matrix between two different sets."""
        texts1 = ["Python", "Java"]
        texts2 = ["Programming", "Language", "Code"]
        
        emb1 = embedding_service.generate_embedding(texts1)
        emb2 = embedding_service.generate_embedding(texts2)
        
        sim_matrix = embedding_service.similarity_matrix(emb1, emb2)
        
        assert sim_matrix.shape[0] == len(texts1)
        assert sim_matrix.shape[1] == len(texts2)
        
    def test_similarity_matrix_symmetry(self, embedding_service, sample_embeddings):
        """Test that similarity matrix is symmetric."""
        sim_matrix = embedding_service.similarity_matrix(sample_embeddings)
        
        n = sim_matrix.shape[0]
        for i in range(n):
            for j in range(i + 1, n):
                assert abs(sim_matrix[i][j] - sim_matrix[j][i]) < 0.001


class TestFindMostSimilar:
    """Test finding most similar embeddings."""
    
    def test_find_most_similar_basic(self, embedding_service, sample_texts):
        """Test finding most similar texts."""
        corpus_embeddings = embedding_service.generate_embedding(sample_texts)
        query_embedding = embedding_service.generate_embedding(["Python programming"])[0]
        
        results = embedding_service.find_most_similar(query_embedding, corpus_embeddings, top_k=2)
        
        assert len(results) == 2
        # First result should be about Python
        assert results[0][0] == 0
        # Scores should be in descending order
        assert results[0][1] >= results[1][1]
        
    def test_find_most_similar_with_threshold(self, embedding_service, sample_texts):
        """Test finding similar texts with threshold."""
        corpus_embeddings = embedding_service.generate_embedding(sample_texts)
        query_embedding = embedding_service.generate_embedding(["Pets"])[0]
        
        results = embedding_service.find_most_similar(
            query_embedding, 
            corpus_embeddings, 
            top_k=10,
            threshold=0.4
        )
        
        # All results should be above threshold
        for _, score in results:
            assert score >= 0.4
            
    def test_find_most_similar_returns_correct_count(self, embedding_service):
        """Test that top_k parameter works correctly."""
        texts = ["text1", "text2", "text3", "text4", "text5"]
        embeddings = embedding_service.generate_embedding(texts)
        query_emb = embeddings[0]
        
        for k in [1, 3, 5]:
            results = embedding_service.find_most_similar(query_emb, embeddings, top_k=k)
            assert len(results) == k


class TestSemanticSearch:
    """Test semantic search functionality."""
    
    def test_semantic_search_basic(self, embedding_service, sample_texts):
        """Test basic semantic search."""
        corpus_embeddings = embedding_service.generate_embedding(sample_texts)
        
        results = embedding_service.semantic_search(
            "programming languages",
            corpus_embeddings,
            top_k=2
        )
        
        assert len(results) == 2
        # Top results should be about programming languages
        assert results[0][0] in [0, 1]
        
    def test_semantic_search_with_threshold(self, embedding_service, sample_texts):
        """Test semantic search with minimum threshold."""
        corpus_embeddings = embedding_service.generate_embedding(sample_texts)
        
        results = embedding_service.semantic_search(
            "animals",
            corpus_embeddings,
            top_k=10,
            threshold=0.3
        )
        
        # All results should meet threshold
        for _, score in results:
            assert score >= 0.3


class TestBatchSemanticSearch:
    """Test batch semantic search functionality."""
    
    def test_batch_semantic_search(self, embedding_service, sample_texts):
        """Test searching with multiple queries."""
        corpus_embeddings = embedding_service.generate_embedding(sample_texts)
        
        queries = ["programming", "animals"]
        results = embedding_service.batch_semantic_search(
            queries,
            corpus_embeddings,
            top_k=2
        )
        
        assert len(results) == len(queries)
        # Each query should have 2 results
        for query_results in results:
            assert len(query_results) == 2
            
    def test_batch_semantic_search_empty_queries(self, embedding_service, sample_embeddings):
        """Test batch search with empty query list."""
        results = embedding_service.batch_semantic_search(
            [],
            sample_embeddings,
            top_k=2
        )
        
        assert len(results) == 0


class TestFindDuplicates:
    """Test duplicate detection functionality."""
    
    def test_find_duplicates_exact(self, embedding_service):
        """Test finding exact duplicates."""
        texts = ["Hello", "Hello", "World"]
        embeddings = embedding_service.generate_embedding(texts)
        
        duplicates = embedding_service.find_duplicates(embeddings, threshold=0.99)
        
        # Should find the exact duplicate
        assert len(duplicates) >= 1
        # First duplicate should be indices 0 and 1
        assert (0, 1) == (duplicates[0][0], duplicates[0][1])
        
    def test_find_duplicates_near_duplicates(self, embedding_service):
        """Test finding near-duplicates."""
        texts = [
            "Hello world",
            "Hello world!",
            "Goodbye world",
            "Farewell planet"
        ]
        embeddings = embedding_service.generate_embedding(texts)
        
        duplicates = embedding_service.find_duplicates(embeddings, threshold=0.85)
        
        # Should find Hello world and Hello world! as near-duplicates
        assert len(duplicates) >= 1
        
    def test_find_duplicates_no_duplicates(self, embedding_service):
        """Test when there are no duplicates."""
        texts = ["Python", "Java", "Pets", "Weather"]
        embeddings = embedding_service.generate_embedding(texts)
        
        duplicates = embedding_service.find_duplicates(embeddings, threshold=0.95)
        
        # Might be 0 or very few
        assert len(duplicates) < len(texts)
        
    def test_find_duplicates_sorted_by_similarity(self, embedding_service):
        """Test that results are sorted by similarity."""
        texts = ["A", "A", "B", "B", "C"]
        embeddings = embedding_service.generate_embedding(texts)
        
        duplicates = embedding_service.find_duplicates(embeddings, threshold=0.5)
        
        # Check that scores are in descending order
        scores = [dup[2] for dup in duplicates]
        assert scores == sorted(scores, reverse=True)


class TestClusterEmbeddings:
    """Test embedding clustering functionality."""
    
    def test_cluster_embeddings_basic(self, embedding_service):
        """Test basic clustering."""
        texts = [
            "Python programming",
            "Java programming",
            "Dog training",
            "Cat behavior",
            "JavaScript coding",
            "Pet care"
        ]
        embeddings = embedding_service.generate_embedding(texts)
        
        clusters = embedding_service.cluster_embeddings(
            embeddings,
            threshold=0.5,
            min_cluster_size=2
        )
        
        # Should find some clusters
        assert len(clusters) > 0
        
        # All items should be in some cluster
        all_indices = set()
        for indices in clusters.values():
            all_indices.update(indices)
        assert len(all_indices) > 0
        
    def test_cluster_embeddings_min_size(self, embedding_service):
        """Test that clusters respect minimum size."""
        texts = ["A", "B", "C", "D", "E"]
        embeddings = embedding_service.generate_embedding(texts)
        
        min_size = 2
        clusters = embedding_service.cluster_embeddings(
            embeddings,
            threshold=0.5,
            min_cluster_size=min_size
        )
        
        # All clusters should have at least min_size items
        for indices in clusters.values():
            assert len(indices) >= min_size
            
    def test_cluster_embeddings_high_threshold(self, embedding_service, sample_texts):
        """Test clustering with high threshold (strict)."""
        embeddings = embedding_service.generate_embedding(sample_texts)
        
        # With very high threshold, should get fewer/smaller clusters
        clusters_strict = embedding_service.cluster_embeddings(
            embeddings,
            threshold=0.9,
            min_cluster_size=2
        )
        
        # With low threshold, should get more/larger clusters
        clusters_loose = embedding_service.cluster_embeddings(
            embeddings,
            threshold=0.3,
            min_cluster_size=2
        )
        
        # Loose clustering should have same or more clusters
        assert len(clusters_loose) >= len(clusters_strict)


class TestModelManagement:
    """Test model management functionality."""
    
    def test_clear_model(self, embedding_service):
        """Test clearing model from memory."""
        # Model should be loaded
        assert embedding_service.model is not None
        
        # Clear the model
        embedding_service.clear_model()
        
        # Model should be None
        assert embedding_service.model is None
        
    def test_model_caching(self):
        """Test that model is cached and reused."""
        service = EmbeddingService(EmbeddingModelS.MINI_LM_L6_V2)
        
        # Get reference to model
        model1 = service.model
        
        # Generate embeddings (should use same model)
        service.generate_embedding(["test"])
        
        # Model should be the same object
        assert service.model is model1


class TestInputFormats:
    """Test different input format handling."""
    
    def test_similarity_with_numpy_arrays(self, embedding_service):
        """Test similarity computation with numpy arrays."""
        emb1 = np.array([0.1, 0.2, 0.3])
        emb2 = np.array([0.1, 0.2, 0.3])
        
        similarity = embedding_service.cosine_similarity(emb1, emb2)
        assert abs(similarity - 1.0) < 0.001
        
    def test_similarity_with_torch_tensors(self, embedding_service):
        """Test similarity computation with torch tensors."""
        emb1 = torch.tensor([0.1, 0.2, 0.3])
        emb2 = torch.tensor([0.1, 0.2, 0.3])
        
        similarity = embedding_service.cosine_similarity(emb1, emb2)
        assert abs(similarity - 1.0) < 0.001
        
    def test_find_most_similar_with_lists(self, embedding_service):
        """Test find_most_similar with list inputs."""
        query_emb = [0.5, 0.5, 0.0]
        corpus_embs = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.5, 0.5, 0.0]
        ]
        
        results = embedding_service.find_most_similar(query_emb, corpus_embs, top_k=2)
        
        assert len(results) == 2
        # Last embedding should be most similar
        assert results[0][0] == 2

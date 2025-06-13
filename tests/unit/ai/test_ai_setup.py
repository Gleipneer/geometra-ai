"""Tests for AI setup."""

import pytest
from pathlib import Path
import json
import yaml
from unittest.mock import Mock, patch

@pytest.fixture
def mock_openai():
    """Mock OpenAI API."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        }
        yield mock_create

def test_ai_structure():
    """Test AI directory structure."""
    ai_dir = Path("src/ai")
    assert ai_dir.exists(), "Missing AI directory"
    
    required_dirs = [
        "models",
        "prompts",
        "utils",
        "evaluation",
        "training"
    ]
    
    for dir_name in required_dirs:
        assert (ai_dir / dir_name).exists(), f"Missing AI directory: {dir_name}"

def test_ai_models():
    """Test AI models."""
    models_dir = Path("src/ai/models")
    assert models_dir.exists(), "Missing models directory"
    
    required_models = [
        "gpt.py",
        "embeddings.py",
        "classifier.py"
    ]
    
    for model in required_models:
        assert (models_dir / model).exists(), f"Missing model: {model}"

def test_ai_prompts():
    """Test AI prompts."""
    prompts_dir = Path("src/ai/prompts")
    assert prompts_dir.exists(), "Missing prompts directory"
    
    required_prompts = [
        "system.txt",
        "user.txt",
        "assistant.txt"
    ]
    
    for prompt in required_prompts:
        assert (prompts_dir / prompt).exists(), f"Missing prompt: {prompt}"

def test_ai_utils():
    """Test AI utilities."""
    utils_dir = Path("src/ai/utils")
    assert utils_dir.exists(), "Missing utils directory"
    
    required_utils = [
        "tokenizer.py",
        "preprocessor.py",
        "postprocessor.py"
    ]
    
    for util in required_utils:
        assert (utils_dir / util).exists(), f"Missing utility: {util}"

def test_ai_evaluation():
    """Test AI evaluation."""
    evaluation_dir = Path("src/ai/evaluation")
    assert evaluation_dir.exists(), "Missing evaluation directory"
    
    required_evaluation = [
        "metrics.py",
        "evaluator.py",
        "reports.py"
    ]
    
    for file in required_evaluation:
        assert (evaluation_dir / file).exists(), f"Missing evaluation file: {file}"

def test_ai_training():
    """Test AI training."""
    training_dir = Path("src/ai/training")
    assert training_dir.exists(), "Missing training directory"
    
    required_training = [
        "trainer.py",
        "dataset.py",
        "config.py"
    ]
    
    for file in required_training:
        assert (training_dir / file).exists(), f"Missing training file: {file}"

def test_ai_configuration():
    """Test AI configuration."""
    config_file = Path("src/ai/config.yaml")
    assert config_file.exists(), "Missing AI configuration"
    
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    required_config = [
        "model",
        "temperature",
        "max_tokens",
        "top_p",
        "frequency_penalty",
        "presence_penalty"
    ]
    
    for key in required_config:
        assert key in config, f"Missing configuration key: {key}"

def test_ai_model_integration(mock_openai):
    """Test AI model integration."""
    from src.ai.models.gpt import GPTModel
    
    model = GPTModel()
    response = model.generate("Test prompt")
    
    assert response == "Test response"
    mock_openai.assert_called_once()

def test_ai_embeddings():
    """Test AI embeddings."""
    from src.ai.models.embeddings import EmbeddingModel
    
    model = EmbeddingModel()
    embedding = model.get_embedding("Test text")
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0

def test_ai_classifier():
    """Test AI classifier."""
    from src.ai.models.classifier import ClassifierModel
    
    model = ClassifierModel()
    prediction = model.classify("Test text")
    
    assert isinstance(prediction, dict)
    assert "label" in prediction
    assert "confidence" in prediction

def test_ai_evaluation_metrics():
    """Test AI evaluation metrics."""
    from src.ai.evaluation.metrics import calculate_metrics
    
    predictions = ["A", "B", "A", "C"]
    ground_truth = ["A", "B", "B", "C"]
    
    metrics = calculate_metrics(predictions, ground_truth)
    
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics

def test_ai_training_process():
    """Test AI training process."""
    from src.ai.training.trainer import Trainer
    
    trainer = Trainer()
    model = trainer.train("test_dataset")
    
    assert model is not None
    assert hasattr(model, "predict") 
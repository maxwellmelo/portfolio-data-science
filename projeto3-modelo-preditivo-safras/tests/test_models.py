"""
Testes para o módulo de modelos.
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import make_regression

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.trainer import ModelTrainer
from src.models.evaluator import ModelEvaluator


@pytest.fixture
def sample_data():
    """Gera dados de exemplo para testes."""
    X, y = make_regression(
        n_samples=500,
        n_features=10,
        noise=10,
        random_state=42
    )
    X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(10)])
    y = pd.Series(y, name="target")
    return X, y


@pytest.fixture
def train_test_split_data(sample_data):
    """Divide dados em treino e teste."""
    from sklearn.model_selection import train_test_split
    X, y = sample_data
    return train_test_split(X, y, test_size=0.2, random_state=42)


class TestModelTrainer:
    """Testes para ModelTrainer."""

    def test_initialization(self):
        """Testa inicialização do trainer."""
        trainer = ModelTrainer(random_state=42)
        assert trainer.random_state == 42
        assert len(trainer.trained_models) == 0

    def test_get_model(self):
        """Testa obtenção de modelo."""
        trainer = ModelTrainer()
        model = trainer.get_model("linear_regression")
        assert model is not None

    def test_get_model_invalid(self):
        """Testa erro com modelo inválido."""
        trainer = ModelTrainer()
        with pytest.raises(ValueError):
            trainer.get_model("modelo_inexistente")

    def test_train_model(self, train_test_split_data):
        """Testa treinamento de modelo."""
        X_train, X_test, y_train, y_test = train_test_split_data
        trainer = ModelTrainer()

        model = trainer.train_model(X_train, y_train, "linear_regression")

        assert model is not None
        assert "linear_regression" in trainer.trained_models

    def test_train_multiple_models(self, train_test_split_data):
        """Testa treinamento de múltiplos modelos."""
        X_train, X_test, y_train, y_test = train_test_split_data
        trainer = ModelTrainer()

        models = ["linear_regression", "ridge"]
        trainer.train_multiple_models(X_train, y_train, models)

        assert len(trainer.trained_models) == 2

    def test_evaluate(self, train_test_split_data):
        """Testa avaliação de modelo."""
        X_train, X_test, y_train, y_test = train_test_split_data
        trainer = ModelTrainer()

        model = trainer.train_model(X_train, y_train, "linear_regression")
        metrics = trainer.evaluate(model, X_test, y_test, "linear_regression")

        assert "rmse" in metrics
        assert "mae" in metrics
        assert "r2" in metrics
        assert metrics["rmse"] >= 0
        assert metrics["mae"] >= 0

    def test_evaluate_all(self, train_test_split_data):
        """Testa avaliação de todos os modelos."""
        X_train, X_test, y_train, y_test = train_test_split_data
        trainer = ModelTrainer()

        trainer.train_multiple_models(
            X_train, y_train,
            ["linear_regression", "ridge"]
        )
        results = trainer.evaluate_all(X_test, y_test)

        assert isinstance(results, pd.DataFrame)
        assert len(results) == 2
        assert trainer.best_model is not None

    def test_cross_validate(self, sample_data):
        """Testa validação cruzada."""
        X, y = sample_data
        trainer = ModelTrainer()

        results = trainer.cross_validate(X, y, "ridge", cv=3)

        assert "mean_score" in results
        assert "std_score" in results
        assert results["cv_folds"] == 3


class TestModelEvaluator:
    """Testes para ModelEvaluator."""

    def test_calculate_metrics(self):
        """Testa cálculo de métricas."""
        evaluator = ModelEvaluator()

        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 2.2, 2.8, 4.1, 4.9])

        metrics = evaluator.calculate_metrics(y_true, y_pred)

        assert "rmse" in metrics
        assert "mae" in metrics
        assert "r2" in metrics
        assert "mape" in metrics
        assert metrics["rmse"] < 1  # Predições próximas

    def test_r2_perfect_predictions(self):
        """Testa R² com predições perfeitas."""
        evaluator = ModelEvaluator()

        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = y_true.copy()

        metrics = evaluator.calculate_metrics(y_true, y_pred)

        assert metrics["r2"] == pytest.approx(1.0)
        assert metrics["rmse"] == pytest.approx(0.0)


class TestFeatureImportance:
    """Testes para feature importance."""

    def test_feature_importance_random_forest(self, train_test_split_data):
        """Testa extração de feature importance."""
        X_train, X_test, y_train, y_test = train_test_split_data
        trainer = ModelTrainer()

        trainer.train_model(X_train, y_train, "random_forest")
        importance = trainer.get_feature_importance(
            "random_forest",
            feature_names=X_train.columns.tolist()
        )

        assert importance is not None
        assert "feature" in importance.columns
        assert "importance" in importance.columns
        assert len(importance) == X_train.shape[1]

    def test_feature_importance_linear(self, train_test_split_data):
        """Testa coeficientes de modelo linear."""
        X_train, X_test, y_train, y_test = train_test_split_data
        trainer = ModelTrainer()

        trainer.train_model(X_train, y_train, "ridge")
        importance = trainer.get_feature_importance(
            "ridge",
            feature_names=X_train.columns.tolist()
        )

        # Ridge tem coef_, então deve funcionar
        assert importance is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

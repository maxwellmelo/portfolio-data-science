"""
Treinador de Modelos de Machine Learning para Predição de Safras.
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import pickle
import json
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor
)
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error
)

from loguru import logger

# Importações condicionais para bibliotecas opcionais
try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost não disponível")

try:
    from lightgbm import LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logger.warning("LightGBM não disponível")

try:
    from catboost import CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    logger.warning("CatBoost não disponível")

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings


class ModelTrainer:
    """
    Treinador de modelos para predição de rendimento de safras.

    Suporta múltiplos algoritmos:
    - Regressão Linear (Linear, Ridge, Lasso, ElasticNet)
    - Ensemble (Random Forest, Gradient Boosting, AdaBoost)
    - Boosting (XGBoost, LightGBM, CatBoost)
    - Outros (SVR, KNN)
    """

    MODELS = {
        "linear_regression": LinearRegression,
        "ridge": Ridge,
        "lasso": Lasso,
        "elastic_net": ElasticNet,
        "random_forest": RandomForestRegressor,
        "gradient_boosting": GradientBoostingRegressor,
        "adaboost": AdaBoostRegressor,
        "svr": SVR,
        "knn": KNeighborsRegressor
    }

    # Adicionar modelos opcionais se disponíveis
    if XGBOOST_AVAILABLE:
        MODELS["xgboost"] = XGBRegressor

    if LIGHTGBM_AVAILABLE:
        MODELS["lightgbm"] = LGBMRegressor

    if CATBOOST_AVAILABLE:
        MODELS["catboost"] = CatBoostRegressor

    # Hiperparâmetros padrão para GridSearch
    DEFAULT_PARAMS = {
        "ridge": {"alpha": [0.1, 1.0, 10.0, 100.0]},
        "lasso": {"alpha": [0.001, 0.01, 0.1, 1.0]},
        "elastic_net": {
            "alpha": [0.1, 1.0, 10.0],
            "l1_ratio": [0.2, 0.5, 0.8]
        },
        "random_forest": {
            "n_estimators": [50, 100, 200],
            "max_depth": [5, 10, 20, None],
            "min_samples_split": [2, 5, 10]
        },
        "gradient_boosting": {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.1, 0.2]
        },
        "xgboost": {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.1, 0.2]
        },
        "lightgbm": {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.1, 0.2]
        }
    }

    def __init__(self, random_state: int = 42):
        """
        Inicializa o treinador.

        Args:
            random_state: Semente para reprodutibilidade
        """
        self.random_state = random_state
        self.trained_models: Dict[str, Any] = {}
        self.results: Dict[str, Dict] = {}
        self.best_model_name: Optional[str] = None
        self.best_model: Optional[Any] = None

    def get_model(self, name: str, **kwargs) -> Any:
        """
        Retorna instância do modelo.

        Args:
            name: Nome do modelo
            **kwargs: Parâmetros adicionais

        Returns:
            Instância do modelo
        """
        if name not in self.MODELS:
            raise ValueError(f"Modelo '{name}' não disponível. Opções: {list(self.MODELS.keys())}")

        model_class = self.MODELS[name]

        # Adicionar random_state se o modelo suportar
        if "random_state" in model_class().get_params():
            kwargs.setdefault("random_state", self.random_state)

        # Configurações específicas
        if name == "xgboost":
            kwargs.setdefault("verbosity", 0)
        elif name == "lightgbm":
            kwargs.setdefault("verbose", -1)
        elif name == "catboost":
            kwargs.setdefault("verbose", False)

        return model_class(**kwargs)

    def train_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        model_name: str,
        **kwargs
    ) -> Any:
        """
        Treina um modelo específico.

        Args:
            X_train: Features de treino
            y_train: Target de treino
            model_name: Nome do modelo
            **kwargs: Parâmetros do modelo

        Returns:
            Modelo treinado
        """
        logger.info(f"Treinando modelo: {model_name}")

        model = self.get_model(model_name, **kwargs)
        model.fit(X_train, y_train)

        self.trained_models[model_name] = model

        logger.info(f"Modelo {model_name} treinado com sucesso")

        return model

    def train_multiple_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Treina múltiplos modelos.

        Args:
            X_train: Features de treino
            y_train: Target de treino
            models: Lista de modelos a treinar (None = todos)

        Returns:
            Dicionário de modelos treinados
        """
        if models is None:
            models = list(self.MODELS.keys())

        logger.info(f"Treinando {len(models)} modelos...")

        for model_name in models:
            try:
                self.train_model(X_train, y_train, model_name)
            except Exception as e:
                logger.warning(f"Erro ao treinar {model_name}: {str(e)}")
                continue

        return self.trained_models

    def cross_validate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        model_name: str,
        cv: int = 5,
        scoring: str = "neg_mean_squared_error"
    ) -> Dict[str, float]:
        """
        Realiza validação cruzada.

        Args:
            X: Features
            y: Target
            model_name: Nome do modelo
            cv: Número de folds
            scoring: Métrica de scoring

        Returns:
            Dicionário com resultados da CV
        """
        model = self.get_model(model_name)

        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)

        results = {
            "model": model_name,
            "cv_folds": cv,
            "scoring": scoring,
            "mean_score": -scores.mean() if "neg" in scoring else scores.mean(),
            "std_score": scores.std(),
            "scores": scores.tolist()
        }

        logger.info(
            f"CV {model_name}: {results['mean_score']:.4f} "
            f"(+/- {results['std_score']:.4f})"
        )

        return results

    def grid_search(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        model_name: str,
        param_grid: Optional[Dict] = None,
        cv: int = 5
    ) -> Tuple[Any, Dict]:
        """
        Realiza busca de hiperparâmetros com GridSearch.

        Args:
            X_train: Features de treino
            y_train: Target de treino
            model_name: Nome do modelo
            param_grid: Grade de parâmetros (None = usar padrão)
            cv: Número de folds

        Returns:
            Tuple (melhor_modelo, melhores_parâmetros)
        """
        logger.info(f"Grid Search para {model_name}...")

        model = self.get_model(model_name)
        params = param_grid or self.DEFAULT_PARAMS.get(model_name, {})

        if not params:
            logger.warning(f"Sem parâmetros para Grid Search de {model_name}")
            model.fit(X_train, y_train)
            return model, {}

        grid = GridSearchCV(
            model,
            params,
            cv=cv,
            scoring="neg_mean_squared_error",
            n_jobs=-1,
            verbose=0
        )

        grid.fit(X_train, y_train)

        logger.info(f"Melhores parâmetros: {grid.best_params_}")
        logger.info(f"Melhor score CV: {-grid.best_score_:.4f}")

        self.trained_models[f"{model_name}_tuned"] = grid.best_estimator_

        return grid.best_estimator_, grid.best_params_

    def evaluate(
        self,
        model: Any,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        model_name: str = "model"
    ) -> Dict[str, float]:
        """
        Avalia um modelo no conjunto de teste.

        Args:
            model: Modelo treinado
            X_test: Features de teste
            y_test: Target de teste
            model_name: Nome do modelo

        Returns:
            Dicionário com métricas
        """
        y_pred = model.predict(X_test)

        metrics = {
            "model": model_name,
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "mae": mean_absolute_error(y_test, y_pred),
            "r2": r2_score(y_test, y_pred),
            "mape": mean_absolute_percentage_error(y_test, y_pred) * 100
        }

        self.results[model_name] = metrics

        logger.info(
            f"{model_name} | RMSE: {metrics['rmse']:.2f} | "
            f"MAE: {metrics['mae']:.2f} | R²: {metrics['r2']:.4f} | "
            f"MAPE: {metrics['mape']:.2f}%"
        )

        return metrics

    def evaluate_all(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> pd.DataFrame:
        """
        Avalia todos os modelos treinados.

        Args:
            X_test: Features de teste
            y_test: Target de teste

        Returns:
            DataFrame com métricas de todos os modelos
        """
        results = []

        for name, model in self.trained_models.items():
            metrics = self.evaluate(model, X_test, y_test, name)
            results.append(metrics)

        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values("rmse")

        # Definir melhor modelo
        self.best_model_name = df_results.iloc[0]["model"]
        self.best_model = self.trained_models[self.best_model_name]

        logger.info(f"Melhor modelo: {self.best_model_name}")

        return df_results

    def get_feature_importance(
        self,
        model_name: Optional[str] = None,
        feature_names: Optional[List[str]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Retorna importância das features.

        Args:
            model_name: Nome do modelo (None = melhor modelo)
            feature_names: Nomes das features

        Returns:
            DataFrame com importância das features
        """
        model_name = model_name or self.best_model_name
        model = self.trained_models.get(model_name)

        if model is None:
            return None

        # Verificar se o modelo tem feature_importances_
        if not hasattr(model, "feature_importances_"):
            # Tentar coef_ para modelos lineares
            if hasattr(model, "coef_"):
                importance = np.abs(model.coef_)
            else:
                logger.warning(f"Modelo {model_name} não suporta feature importance")
                return None
        else:
            importance = model.feature_importances_

        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(importance))]

        df_importance = pd.DataFrame({
            "feature": feature_names[:len(importance)],
            "importance": importance
        })

        df_importance = df_importance.sort_values("importance", ascending=False)

        return df_importance

    def save_model(
        self,
        model_name: Optional[str] = None,
        filepath: Optional[str] = None
    ) -> str:
        """
        Salva modelo em arquivo.

        Args:
            model_name: Nome do modelo (None = melhor)
            filepath: Caminho do arquivo (None = gerar automático)

        Returns:
            Caminho do arquivo salvo
        """
        model_name = model_name or self.best_model_name
        model = self.trained_models.get(model_name)

        if model is None:
            raise ValueError(f"Modelo '{model_name}' não encontrado")

        if filepath is None:
            models_dir = Path(settings.data.models_dir)
            models_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = models_dir / f"{model_name}_{timestamp}.pkl"

        filepath = Path(filepath)

        with open(filepath, "wb") as f:
            pickle.dump(model, f)

        # Salvar metadados
        metadata = {
            "model_name": model_name,
            "saved_at": datetime.now().isoformat(),
            "metrics": self.results.get(model_name, {})
        }

        meta_path = filepath.with_suffix(".json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Modelo salvo: {filepath}")

        return str(filepath)

    def load_model(self, filepath: str) -> Any:
        """
        Carrega modelo de arquivo.

        Args:
            filepath: Caminho do arquivo

        Returns:
            Modelo carregado
        """
        with open(filepath, "rb") as f:
            model = pickle.load(f)

        logger.info(f"Modelo carregado: {filepath}")

        return model


# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo
    from sklearn.datasets import make_regression

    X, y = make_regression(n_samples=1000, n_features=20, noise=0.1, random_state=42)
    X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(20)])
    y = pd.Series(y)

    # Split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Treinar e avaliar
    trainer = ModelTrainer()
    trainer.train_multiple_models(X_train, y_train, ["linear_regression", "ridge", "random_forest"])
    results = trainer.evaluate_all(X_test, y_test)
    print(results)

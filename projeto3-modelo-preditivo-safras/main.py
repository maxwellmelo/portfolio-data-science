"""
Pipeline Principal - Modelo Preditivo de Safras Agrícolas.

Este script orquestra todo o processo de ML:
1. Carregamento de dados da PAM/IBGE
2. Engenharia de features
3. Treinamento de múltiplos modelos
4. Avaliação e seleção do melhor modelo
5. Geração de relatórios e visualizações

Uso:
    python main.py --help
    python main.py --train
    python main.py --evaluate
    python main.py --predict --model random_forest
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
import pandas as pd
import numpy as np

from config.settings import settings
from src.data import DataLoader
from src.features import FeatureEngineer
from src.models import ModelTrainer, ModelEvaluator
from src.visualization import AgricultureVisualizer


def setup_logging(level: str = "INFO") -> None:
    """Configura logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level=level
    )
    logger.add(
        "logs/pipeline_{time}.log",
        rotation="10 MB",
        level="DEBUG"
    )


def run_eda(df: pd.DataFrame) -> None:
    """
    Executa análise exploratória dos dados.

    Args:
        df: DataFrame com dados
    """
    logger.info("=" * 60)
    logger.info("ANÁLISE EXPLORATÓRIA DOS DADOS")
    logger.info("=" * 60)

    print(f"\n[SHAPE] {df.shape}")
    print(f"[PERIODO] {df['ano'].min()} - {df['ano'].max()}")
    print(f"[CULTURAS] {df['cultura'].nunique()}")
    print(f"[ESTADOS] {df['estado'].nunique()}")

    print("\n[ESTATISTICAS]")
    print(df.describe().round(2))

    print("\n[VALORES NULOS]")
    nulls = df.isnull().sum()
    print(nulls[nulls > 0])

    # Criar visualizações
    viz = AgricultureVisualizer()
    output_dir = Path("outputs/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Gerar gráficos principais
    fig = viz.plot_evolucao_culturas(
        df,
        culturas=["Soja (em grão)", "Milho (em grão)", "Arroz (em casca)"],
        metric="rendimento_kg_ha"
    )
    fig.write_html(output_dir / "evolucao_culturas.html")

    fig = viz.plot_correlacao(df)
    fig.write_html(output_dir / "correlacao.html")

    logger.info(f"Visualizações salvas em: {output_dir}")


def run_training(
    df: pd.DataFrame,
    models_to_train: list = None
) -> dict:
    """
    Executa pipeline de treinamento.

    Args:
        df: DataFrame com dados
        models_to_train: Lista de modelos a treinar

    Returns:
        Dicionário com resultados
    """
    logger.info("=" * 60)
    logger.info("PIPELINE DE TREINAMENTO")
    logger.info("=" * 60)

    # Feature Engineering
    logger.info("Aplicando engenharia de features...")
    fe = FeatureEngineer(target="rendimento_kg_ha")
    X, y = fe.fit_transform(df)

    # Remover linhas com NaN no target
    mask = ~y.isna()
    X = X[mask]
    y = y[mask]

    # Preparar dados
    loader = DataLoader()
    X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
        pd.concat([X, y.rename("rendimento_kg_ha")], axis=1),
        target="rendimento_kg_ha"
    )

    # Treinar modelos
    logger.info("Treinando modelos...")
    trainer = ModelTrainer(random_state=settings.model.random_state)

    if models_to_train is None:
        models_to_train = ["linear_regression", "ridge", "random_forest", "gradient_boosting"]

    trainer.train_multiple_models(X_train, y_train, models_to_train)

    # Avaliar modelos
    logger.info("Avaliando modelos...")
    results_df = trainer.evaluate_all(X_test, y_test)

    print("\n[RESULTADOS] Modelos:")
    print(results_df.to_string(index=False))

    # Feature Importance
    importance = trainer.get_feature_importance(feature_names=X_train.columns.tolist())
    if importance is not None:
        print("\n[TOP 10] Features Mais Importantes:")
        print(importance.head(10).to_string(index=False))

    # Salvar melhor modelo
    model_path = trainer.save_model()
    logger.info(f"Melhor modelo salvo: {model_path}")

    # Gerar visualizações
    evaluator = ModelEvaluator()
    y_pred = trainer.best_model.predict(X_test)

    evaluator.plot_predictions_vs_actual(y_test.values, y_pred)
    evaluator.plot_residuals(y_test.values, y_pred)
    evaluator.plot_model_comparison(results_df)

    if importance is not None:
        evaluator.plot_feature_importance(importance)

    # Gerar relatório
    report = evaluator.generate_report(
        y_test.values,
        y_pred,
        trainer.best_model_name,
        importance
    )

    return {
        "results": results_df,
        "best_model": trainer.best_model_name,
        "importance": importance,
        "model_path": model_path
    }


def run_prediction(
    model_path: str,
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Executa predições com modelo treinado.

    Args:
        model_path: Caminho do modelo
        df: DataFrame com dados para predição

    Returns:
        DataFrame com predições
    """
    logger.info("=" * 60)
    logger.info("PIPELINE DE PREDIÇÃO")
    logger.info("=" * 60)

    trainer = ModelTrainer()
    model = trainer.load_model(model_path)

    # Preparar dados
    fe = FeatureEngineer()
    X, _ = fe.fit_transform(df)

    # Predizer
    predictions = model.predict(X)

    df_result = df.copy()
    df_result["predicao_rendimento"] = predictions

    logger.info(f"Predições realizadas: {len(predictions)}")

    return df_result


def main():
    """Função principal do CLI."""
    parser = argparse.ArgumentParser(
        description="Pipeline de ML para Predição de Safras Agrícolas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py --eda                    # Análise exploratória
  python main.py --train                  # Treinar modelos
  python main.py --train --models ridge random_forest
  python main.py --evaluate               # Avaliar modelos
  python main.py --predict --model-path data/models/model.pkl
        """
    )

    parser.add_argument(
        "--eda",
        action="store_true",
        help="Executar análise exploratória"
    )

    parser.add_argument(
        "--train",
        action="store_true",
        help="Treinar modelos"
    )

    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Avaliar modelos treinados"
    )

    parser.add_argument(
        "--predict",
        action="store_true",
        help="Fazer predições"
    )

    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Modelos a treinar (ex: ridge random_forest xgboost)"
    )

    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Caminho do modelo para predição"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Nível de log"
    )

    parser.add_argument(
        "--synthetic",
        action="store_true",
        default=True,
        help="Usar dados sintéticos (padrão: True)"
    )

    args = parser.parse_args()

    # Configurar logging
    setup_logging(args.log_level)

    logger.info("=" * 60)
    logger.info("MODELO PREDITIVO DE SAFRAS AGRÍCOLAS")
    logger.info(f"Versão: {settings.version}")
    logger.info("=" * 60)

    # Carregar dados
    logger.info("Carregando dados...")
    loader = DataLoader()
    df = loader.load_data(use_synthetic=args.synthetic)
    logger.info(f"Dados carregados: {len(df)} registros")

    # Executar ação solicitada
    if args.eda:
        run_eda(df)

    if args.train:
        results = run_training(df, args.models)
        print(f"\n[OK] Treinamento concluido! Melhor modelo: {results['best_model']}")

    if args.predict:
        if not args.model_path:
            logger.error("Especifique o caminho do modelo com --model-path")
            return 1

        df_pred = run_prediction(args.model_path, df)
        output_path = Path("outputs/predictions.csv")
        df_pred.to_csv(output_path, index=False)
        print(f"\n[OK] Predicoes salvas em: {output_path}")

    # Se nenhuma ação especificada, executar pipeline completo
    if not any([args.eda, args.train, args.predict]):
        logger.info("Executando pipeline completo...")
        run_eda(df)
        results = run_training(df, args.models)
        print("\n" + "=" * 60)
        print("PIPELINE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"Melhor modelo: {results['best_model']}")
        print(f"Modelo salvo em: {results['model_path']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

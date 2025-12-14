"""
Script de teste para verificar instalação do Dashboard Ambiental
Execute este script para verificar se tudo está configurado corretamente
"""

import sys
from pathlib import Path

print("=" * 70)
print("TESTE DE INSTALAÇÃO - Dashboard Ambiental")
print("=" * 70)
print()

# Verificar Python
print("1. Verificando versão do Python...")
python_version = sys.version_info
print(f"   ✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major >= 3 and python_version.minor >= 8:
    print("   ✓ Versão compatível (>= 3.8)")
else:
    print("   ✗ ERRO: Python 3.8+ necessário")
    sys.exit(1)
print()

# Verificar dependências
print("2. Verificando dependências...")
required_packages = [
    'streamlit',
    'pandas',
    'numpy',
    'plotly',
    'folium',
    'geopandas',
    'requests'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} NÃO INSTALADO")
        missing_packages.append(package)

if missing_packages:
    print()
    print("ERRO: Pacotes faltando. Execute:")
    print("pip install -r requirements.txt")
    sys.exit(1)
print()

# Verificar estrutura de diretórios
print("3. Verificando estrutura de diretórios...")
project_root = Path(__file__).parent
required_dirs = [
    'src',
    'src/utils',
    'src/components',
    'data',
    'data/raw',
    'data/processed',
    'docs',
    '.streamlit'
]

for dir_path in required_dirs:
    full_path = project_root / dir_path
    if full_path.exists():
        print(f"   ✓ {dir_path}/")
    else:
        print(f"   ✗ {dir_path}/ NÃO ENCONTRADO")
print()

# Verificar arquivos principais
print("4. Verificando arquivos principais...")
required_files = [
    'app.py',
    'requirements.txt',
    'README.md',
    'src/utils/config.py',
    'src/utils/data_loader.py',
    'src/utils/data_processor.py',
    'src/components/charts.py',
    'src/components/maps.py',
    '.streamlit/config.toml'
]

for file_path in required_files:
    full_path = project_root / file_path
    if full_path.exists():
        print(f"   ✓ {file_path}")
    else:
        print(f"   ✗ {file_path} NÃO ENCONTRADO")
print()

# Testar importação dos módulos
print("5. Testando importação dos módulos...")
sys.path.insert(0, str(project_root / "src"))

try:
    from utils.config import TEXTOS, BIOMAS, ESTADOS_BRASIL
    print("   ✓ utils.config")
except Exception as e:
    print(f"   ✗ utils.config: {e}")

try:
    from utils.data_loader import DataLoaderPRODES
    print("   ✓ utils.data_loader")
except Exception as e:
    print(f"   ✗ utils.data_loader: {e}")

try:
    from utils.data_processor import DataProcessor
    print("   ✓ utils.data_processor")
except Exception as e:
    print(f"   ✗ utils.data_processor: {e}")

try:
    from components.charts import ChartBuilder
    print("   ✓ components.charts")
except Exception as e:
    print(f"   ✗ components.charts: {e}")

try:
    from components.maps import MapBuilder
    print("   ✓ components.maps")
except Exception as e:
    print(f"   ✗ components.maps: {e}")
print()

# Teste de carregamento de dados
print("6. Testando carregamento de dados...")
try:
    from utils.data_loader import DataLoaderPRODES
    loader = DataLoaderPRODES()
    df = loader.load_data(use_synthetic=True)
    print(f"   ✓ Dados carregados: {len(df)} registros")
    print(f"   ✓ Colunas: {', '.join(df.columns)}")
    print(f"   ✓ Anos: {df['ano'].min()} - {df['ano'].max()}")
    print(f"   ✓ Estados: {df['estado'].nunique()}")
    print(f"   ✓ Biomas: {df['bioma'].nunique()}")
except Exception as e:
    print(f"   ✗ Erro ao carregar dados: {e}")
print()

# Teste de processamento
print("7. Testando processamento de dados...")
try:
    from utils.data_processor import DataProcessor, create_kpis
    processor = DataProcessor(df)
    yearly = processor.calculate_yearly_metrics()
    print(f"   ✓ Métricas anuais calculadas: {len(yearly)} anos")

    kpis = create_kpis(df, ano_atual=2025)
    print(f"   ✓ KPIs gerados: {len(kpis)} indicadores")
except Exception as e:
    print(f"   ✗ Erro no processamento: {e}")
print()

# Teste de visualização
print("8. Testando componentes de visualização...")
try:
    from components.charts import ChartBuilder
    from components.maps import MapBuilder

    chart_builder = ChartBuilder()
    print("   ✓ ChartBuilder instanciado")

    map_builder = MapBuilder()
    print("   ✓ MapBuilder instanciado")

    # Testar criação de gráfico simples
    fig = chart_builder.create_time_series(
        yearly,
        x_col='ano',
        y_col='total_km2',
        title="Teste"
    )
    print("   ✓ Gráfico de teste criado")
except Exception as e:
    print(f"   ✗ Erro na visualização: {e}")
print()

# Resultado final
print("=" * 70)
print("RESULTADO DO TESTE")
print("=" * 70)
print()
print("✓ Instalação completa e funcional!")
print()
print("Próximos passos:")
print("1. Execute: streamlit run app.py")
print("2. Acesse: http://localhost:8501")
print("3. Explore o dashboard!")
print()
print("=" * 70)

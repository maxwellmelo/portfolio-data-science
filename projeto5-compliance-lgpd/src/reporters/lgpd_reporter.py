"""
Gerador de Relatórios de Conformidade LGPD.

Gera relatórios estruturados com:
- Inventário de dados pessoais
- Análise de riscos
- Recomendações de adequação
- Evidências de conformidade
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
from jinja2 import Template
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings, DADOS_SENSIVEIS_LGPD, BASES_LEGAIS_LGPD, DIREITOS_TITULARES
from src.scanners import ScanResult


class LGPDReporter:
    """
    Gerador de relatórios de conformidade LGPD.

    Tipos de relatório:
    - Inventário de Dados Pessoais
    - Relatório de Impacto à Proteção de Dados (RIPD)
    - Relatório de Auditoria
    - Dicionário de Dados com classificação LGPD
    """

    def __init__(self, output_dir: str = None):
        """
        Inicializa o gerador.

        Args:
            output_dir: Diretório de saída dos relatórios
        """
        self.output_dir = Path(output_dir or settings.report.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"LGPDReporter inicializado | output_dir={self.output_dir}")

    def generate_audit_report(
        self,
        scan_results: List[ScanResult],
        company_name: str = None,
        dpo_name: str = None
    ) -> str:
        """
        Gera relatório de auditoria LGPD.

        Args:
            scan_results: Lista de resultados de scan
            company_name: Nome da organização
            dpo_name: Nome do DPO

        Returns:
            Caminho do arquivo gerado
        """
        company = company_name or settings.report.company_name
        dpo = dpo_name or settings.report.dpo_name

        report_data = {
            "title": "Relatório de Auditoria de Dados Pessoais",
            "company_name": company,
            "dpo_name": dpo,
            "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "scans": [],
            "summary": {
                "total_sources": len(scan_results),
                "total_pii_columns": 0,
                "risk_critico": 0,
                "risk_alto": 0,
                "risk_medio": 0,
                "risk_baixo": 0
            },
            "recommendations": [],
            "legal_bases": BASES_LEGAIS_LGPD,
            "data_subject_rights": DIREITOS_TITULARES
        }

        # Processar cada scan
        all_recommendations = set()
        for result in scan_results:
            scan_data = {
                "source_name": result.source_name,
                "scan_date": result.timestamp.strftime("%d/%m/%Y %H:%M"),
                "total_rows": f"{result.total_rows:,}",
                "columns_scanned": result.columns_scanned,
                "pii_found": len(result.pii_found),
                "risk_summary": result.risk_summary,
                "findings": [
                    {
                        "column": m.column,
                        "type": m.pii_type.value,
                        "count": f"{m.count:,}",
                        "percentage": f"{m.percentage:.1f}%",
                        "risk": m.risk_level.value,
                        "method": m.detection_method
                    }
                    for m in result.pii_found
                ]
            }
            report_data["scans"].append(scan_data)

            # Atualizar resumo
            report_data["summary"]["total_pii_columns"] += len(result.pii_found)
            report_data["summary"]["risk_critico"] += result.risk_summary.get("critico", 0)
            report_data["summary"]["risk_alto"] += result.risk_summary.get("alto", 0)
            report_data["summary"]["risk_medio"] += result.risk_summary.get("medio", 0)
            report_data["summary"]["risk_baixo"] += result.risk_summary.get("baixo", 0)

            # Coletar recomendações
            all_recommendations.update(result.recommendations)

        report_data["recommendations"] = list(all_recommendations)

        # Gerar HTML
        html = self._render_audit_html(report_data)

        # Salvar
        filename = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"Relatório de auditoria gerado: {filepath}")

        return str(filepath)

    def _render_audit_html(self, data: dict) -> str:
        """Renderiza relatório de auditoria em HTML."""
        template = Template('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - {{ company_name }}</title>
    <style>
        :root {
            --primary: #2563eb;
            --danger: #dc2626;
            --warning: #f59e0b;
            --success: #10b981;
            --gray: #6b7280;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f9fafb;
        }
        .header {
            background: linear-gradient(135deg, #1e3a8a, #3b82f6);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 { margin: 0 0 10px 0; }
        .header .meta { opacity: 0.9; font-size: 0.9em; }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: var(--primary);
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .summary-item {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            background: #f3f4f6;
        }
        .summary-item .number {
            font-size: 2.5em;
            font-weight: bold;
        }
        .summary-item .label { color: var(--gray); }
        .risk-critico .number { color: var(--danger); }
        .risk-alto .number { color: #ea580c; }
        .risk-medio .number { color: var(--warning); }
        .risk-baixo .number { color: var(--success); }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th { background: #f9fafb; font-weight: 600; }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .badge-critico { background: #fef2f2; color: var(--danger); }
        .badge-alto { background: #fff7ed; color: #ea580c; }
        .badge-medio { background: #fffbeb; color: var(--warning); }
        .badge-baixo { background: #ecfdf5; color: var(--success); }
        .recommendation {
            padding: 15px;
            background: #eff6ff;
            border-left: 4px solid var(--primary);
            margin: 10px 0;
            border-radius: 0 8px 8px 0;
        }
        .footer {
            text-align: center;
            color: var(--gray);
            padding: 20px;
            font-size: 0.9em;
        }
        ul { padding-left: 20px; }
        li { margin: 8px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <div class="meta">
            <strong>Organização:</strong> {{ company_name }} |
            <strong>DPO:</strong> {{ dpo_name }} |
            <strong>Data:</strong> {{ generated_at }}
        </div>
    </div>

    <div class="card">
        <h2>Resumo Executivo</h2>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="number">{{ summary.total_sources }}</div>
                <div class="label">Fontes Analisadas</div>
            </div>
            <div class="summary-item">
                <div class="number">{{ summary.total_pii_columns }}</div>
                <div class="label">Colunas com PII</div>
            </div>
            <div class="summary-item risk-critico">
                <div class="number">{{ summary.risk_critico }}</div>
                <div class="label">Risco Crítico</div>
            </div>
            <div class="summary-item risk-alto">
                <div class="number">{{ summary.risk_alto }}</div>
                <div class="label">Risco Alto</div>
            </div>
            <div class="summary-item risk-medio">
                <div class="number">{{ summary.risk_medio }}</div>
                <div class="label">Risco Médio</div>
            </div>
            <div class="summary-item risk-baixo">
                <div class="number">{{ summary.risk_baixo }}</div>
                <div class="label">Risco Baixo</div>
            </div>
        </div>
    </div>

    {% for scan in scans %}
    <div class="card">
        <h2>{{ scan.source_name }}</h2>
        <p><strong>Data do Scan:</strong> {{ scan.scan_date }} |
           <strong>Registros:</strong> {{ scan.total_rows }} |
           <strong>Colunas:</strong> {{ scan.columns_scanned }}</p>

        {% if scan.findings %}
        <table>
            <thead>
                <tr>
                    <th>Coluna</th>
                    <th>Tipo de Dado</th>
                    <th>Ocorrências</th>
                    <th>Percentual</th>
                    <th>Risco</th>
                    <th>Detecção</th>
                </tr>
            </thead>
            <tbody>
                {% for f in scan.findings %}
                <tr>
                    <td><code>{{ f.column }}</code></td>
                    <td>{{ f.type }}</td>
                    <td>{{ f.count }}</td>
                    <td>{{ f.percentage }}</td>
                    <td><span class="badge badge-{{ f.risk }}">{{ f.risk|upper }}</span></td>
                    <td>{{ f.method }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>Nenhum dado pessoal identificado nesta fonte.</p>
        {% endif %}
    </div>
    {% endfor %}

    <div class="card">
        <h2>Recomendações</h2>
        {% for rec in recommendations %}
        <div class="recommendation">{{ rec }}</div>
        {% endfor %}
    </div>

    <div class="card">
        <h2>Bases Legais para Tratamento (Art. 7º LGPD)</h2>
        <ul>
        {% for key, value in legal_bases.items() %}
            <li><strong>{{ key|replace('_', ' ')|title }}:</strong> {{ value }}</li>
        {% endfor %}
        </ul>
    </div>

    <div class="card">
        <h2>Direitos dos Titulares (Art. 18º LGPD)</h2>
        <ul>
        {% for right in data_subject_rights %}
            <li>{{ right }}</li>
        {% endfor %}
        </ul>
    </div>

    <div class="footer">
        <p>Relatório gerado automaticamente pelo Sistema de Compliance LGPD</p>
        <p>Este documento é confidencial e destinado exclusivamente para fins de conformidade.</p>
    </div>
</body>
</html>
        ''')

        return template.render(**data)

    def generate_data_dictionary(
        self,
        scan_result: ScanResult,
        output_format: str = "html"
    ) -> str:
        """
        Gera dicionário de dados com classificação LGPD.

        Args:
            scan_result: Resultado do scan
            output_format: Formato de saída (html, json, csv)

        Returns:
            Caminho do arquivo gerado
        """
        entries = []

        for finding in scan_result.pii_found:
            # Determinar categoria LGPD
            lgpd_category = self._get_lgpd_category(finding.pii_type.value)

            entries.append({
                "coluna": finding.column,
                "tipo_dado": finding.pii_type.value,
                "categoria_lgpd": lgpd_category["categoria"],
                "base_legal_sugerida": lgpd_category["base_legal"],
                "nivel_risco": finding.risk_level.value,
                "total_registros": finding.count,
                "requer_consentimento": lgpd_category["requer_consentimento"],
                "acao_recomendada": lgpd_category["acao"]
            })

        # Salvar no formato solicitado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if output_format == "json":
            filename = f"data_dictionary_{timestamp}.json"
            filepath = self.output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)

        elif output_format == "csv":
            import pandas as pd
            filename = f"data_dictionary_{timestamp}.csv"
            filepath = self.output_dir / filename
            pd.DataFrame(entries).to_csv(filepath, index=False, encoding="utf-8-sig")

        else:  # html
            filename = f"data_dictionary_{timestamp}.html"
            filepath = self.output_dir / filename
            html = self._render_dictionary_html(scan_result.source_name, entries)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

        logger.info(f"Dicionário de dados gerado: {filepath}")
        return str(filepath)

    def _get_lgpd_category(self, pii_type: str) -> dict:
        """Retorna informações de categoria LGPD para um tipo de PII."""
        categories = {
            "cpf": {
                "categoria": "Dado Pessoal - Identificação",
                "base_legal": "Execução de contrato ou obrigação legal",
                "requer_consentimento": "Não necessariamente",
                "acao": "Pseudonimização recomendada"
            },
            "email": {
                "categoria": "Dado Pessoal - Contato",
                "base_legal": "Consentimento ou interesse legítimo",
                "requer_consentimento": "Depende da finalidade",
                "acao": "Mascaramento para logs"
            },
            "dados_saude": {
                "categoria": "Dado Pessoal Sensível - Saúde",
                "base_legal": "Art. 11 - Requer base legal específica",
                "requer_consentimento": "Sim, explícito",
                "acao": "URGENTE: Verificar base legal"
            },
            "nome": {
                "categoria": "Dado Pessoal - Identificação",
                "base_legal": "Variável conforme finalidade",
                "requer_consentimento": "Depende da finalidade",
                "acao": "Avaliar necessidade"
            }
        }

        return categories.get(pii_type, {
            "categoria": "Dado Pessoal",
            "base_legal": "A definir",
            "requer_consentimento": "A avaliar",
            "acao": "Classificar manualmente"
        })

    def _render_dictionary_html(self, source: str, entries: list) -> str:
        """Renderiza dicionário em HTML."""
        # Simplificado para o exemplo
        html = f"""
        <!DOCTYPE html>
        <html><head><title>Dicionário de Dados - {source}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #f4f4f4; }}
        </style></head>
        <body>
        <h1>Dicionário de Dados LGPD</h1>
        <p><strong>Fonte:</strong> {source}</p>
        <table>
        <tr><th>Coluna</th><th>Tipo</th><th>Categoria LGPD</th><th>Base Legal</th><th>Risco</th><th>Ação</th></tr>
        """

        for e in entries:
            html += f"""
            <tr>
                <td>{e['coluna']}</td>
                <td>{e['tipo_dado']}</td>
                <td>{e['categoria_lgpd']}</td>
                <td>{e['base_legal_sugerida']}</td>
                <td>{e['nivel_risco']}</td>
                <td>{e['acao_recomendada']}</td>
            </tr>
            """

        html += "</table></body></html>"
        return html

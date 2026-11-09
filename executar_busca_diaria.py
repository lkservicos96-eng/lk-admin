"""
Script para execução automática da busca diária
Este será chamado pela scheduled task
"""

import json
import os
from datetime import datetime
from cnpj_searcher import BuscadorIntegrado

def carregar_configuracao(arquivo='config_busca.json'):
    """Carrega configuração da busca"""
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo de configuração não encontrado: {arquivo}")
        return None

    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def executar_busca_automatica():
    """Executa a busca conforme configuração"""
    print("\n" + "="*70)
    print("🤖 BUSCA AUTOMÁTICA DE EMPRESAS COM PROCESSOS")
    print("="*70 + "\n")

    # Carrega configuração
    config = carregar_configuracao()
    if not config:
        return

    buscador = BuscadorIntegrado()
    todos_resultados = []

    # Para cada CNAE configurado
    for cnae_info in config['busca']['cnaes']:
        cnae = cnae_info['codigo']
        descricao = cnae_info['descricao']

        print(f"\n{'─'*70}")
        print(f"📋 Buscando CNAE: {cnae} - {descricao}")
        print(f"{'─'*70}\n")

        # Executa busca
        resultados = buscador.executar_busca_completa(
            cnae=cnae,
            estados=config['busca']['estados'],
            buscar_processos=True,
            apenas_com_processos=config['busca']['filtros']['apenas_com_processos']
        )

        # Adiciona metadados
        for resultado in resultados:
            resultado['cnae_buscado'] = cnae
            resultado['cnae_descricao'] = descricao

        todos_resultados.extend(resultados)

        print(f"\n✅ {len(resultados)} empresas encontradas para este CNAE")

    # Salva resultados consolidados
    if config['notificacao']['salvar_arquivo']:
        pasta_saida = config['notificacao'].get('pasta_saida', './resultados/')
        os.makedirs(pasta_saida, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = os.path.join(pasta_saida, f"busca_automatica_{timestamp}.json")

        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(todos_resultados, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*70}")
        print(f"💾 RESULTADOS SALVOS")
        print(f"📁 Arquivo: {nome_arquivo}")
        print(f"📊 Total de empresas: {len(todos_resultados)}")
        print(f"{'='*70}\n")

        # Gera relatório resumido
        gerar_relatorio_resumido(todos_resultados, pasta_saida, timestamp)

def gerar_relatorio_resumido(resultados, pasta, timestamp):
    """Gera um relatório em texto simples para visualização rápida"""
    nome_relatorio = os.path.join(pasta, f"relatorio_{timestamp}.txt")

    with open(nome_relatorio, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RELATÓRIO DE BUSCA - EMPRESAS COM PROCESSOS JUDICIAIS\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")

        f.write(f"Total de empresas encontradas: {len(resultados)}\n\n")

        # Agrupa por estado
        por_estado = {}
        for r in resultados:
            estado = r.get('estado', 'N/A')
            if estado not in por_estado:
                por_estado[estado] = []
            por_estado[estado].append(r)

        f.write("DISTRIBUIÇÃO POR ESTADO:\n")
        f.write("-" * 40 + "\n")
        for estado, empresas in sorted(por_estado.items()):
            f.write(f"{estado}: {len(empresas)} empresa(s)\n")

        f.write("\n" + "="*80 + "\n")
        f.write("DETALHAMENTO DAS EMPRESAS\n")
        f.write("="*80 + "\n\n")

        # Lista cada empresa
        for idx, empresa in enumerate(resultados, 1):
            f.write(f"\n{idx}. {empresa.get('razao_social', 'N/A')}\n")
            f.write(f"   CNPJ: {empresa.get('cnpj', 'N/A')}\n")
            f.write(f"   CNAE: {empresa.get('cnae_buscado', 'N/A')} - {empresa.get('cnae_descricao', 'N/A')}\n")
            f.write(f"   Cidade: {empresa.get('cidade', 'N/A')}/{empresa.get('estado', 'N/A')}\n")
            f.write(f"   Situação: {empresa.get('situacao', 'N/A')}\n")

            processos_info = empresa.get('processos', {})
            total_processos = processos_info.get('total_processos', 0)
            f.write(f"   ⚖️  Processos: {total_processos}\n")

            if total_processos > 0:
                tribunais = processos_info.get('tribunais_consultados', [])
                f.write(f"   Tribunais: {', '.join(tribunais)}\n")

            f.write("-" * 80 + "\n")

    print(f"📄 Relatório resumido: {nome_relatorio}")

if __name__ == "__main__":
    executar_busca_automatica()

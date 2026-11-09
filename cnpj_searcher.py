"""
Sistema de Busca de Empresas com Processos Judiciais
Busca empresas por CNAE/região e verifica processos públicos
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import time

class CNPJSearcher:
    """Módulo para buscar empresas por filtros"""

    def __init__(self):
        # APIs disponíveis (você escolhe qual usar depois)
        self.apis = {
            'cnpja': 'https://api.cnpja.com',
            'opencnpj': 'https://api.opencnpj.com/v1',
            'receitaws': 'https://www.receitaws.com.br/v1'
        }

    def buscar_por_cnae_regiao(self,
                               cnae: str,
                               estado: str = None,
                               cidade: str = None,
                               limite: int = 50) -> List[Dict]:
        """
        Busca empresas por CNAE e região

        Args:
            cnae: Código CNAE (ex: '6201-5/00' para desenvolvimento de software)
            estado: Sigla do estado (ex: 'SP', 'RJ', 'MG')
            cidade: Nome da cidade
            limite: Número máximo de resultados
        """
        empresas = []

        print(f"🔍 Buscando empresas - CNAE: {cnae}, Estado: {estado}, Cidade: {cidade}")

        # Estratégia 1: CNPJA (tem filtro)
        try:
            empresas = self._buscar_cnpja(cnae, estado, cidade, limite)
        except Exception as e:
            print(f"⚠️  Erro na busca CNPJA: {e}")

        return empresas

    def _buscar_cnpja(self, cnae: str, estado: str, cidade: str, limite: int) -> List[Dict]:
        """Busca usando CNPJA API"""
        # Nota: A versão gratuita pode ter limitações
        # Vamos adaptar conforme os testes
        resultados = []

        # Aqui vamos implementar após testar a API real
        print("📋 Preparando consulta CNPJA...")

        return resultados

    def consultar_cnpj_individual(self, cnpj: str) -> Optional[Dict]:
        """
        Consulta dados detalhados de um CNPJ específico
        """
        cnpj_limpo = cnpj.replace('.', '').replace('/', '').replace('-', '')

        # Tenta múltiplas APIs (fallback)
        apis_para_testar = [
            f"https://api.cnpja.com/office/{cnpj_limpo}",
            f"https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}",
        ]

        for api_url in apis_para_testar:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return self._normalizar_dados_cnpj(data)
            except Exception as e:
                continue

        return None

    def _normalizar_dados_cnpj(self, data: Dict) -> Dict:
        """Padroniza formato dos dados de diferentes APIs"""
        # Vamos ajustar conforme a estrutura real das respostas
        return {
            'cnpj': data.get('cnpj') or data.get('tax_id'),
            'razao_social': data.get('razao_social') or data.get('name'),
            'nome_fantasia': data.get('nome_fantasia') or data.get('alias'),
            'situacao': data.get('situacao') or data.get('status'),
            'cnae_principal': data.get('cnae_fiscal') or data.get('primary_activity'),
            'porte': data.get('porte'),
            'estado': data.get('uf'),
            'cidade': data.get('municipio') or data.get('city'),
            'data_abertura': data.get('data_inicio_atividade') or data.get('founded'),
        }


class ProcessSearcher:
    """Módulo para buscar processos judiciais"""

    def __init__(self):
        self.datajud_base = "https://api-publica.datajud.cnj.jus.br"

    def buscar_processos_empresa(self,
                                 cnpj: str,
                                 razao_social: str) -> Dict:
        """
        Busca processos relacionados a uma empresa

        Como DataJud não aceita busca por CNPJ diretamente,
        vamos usar o nome da empresa como critério
        """
        cnpj_limpo = cnpj.replace('.', '').replace('/', '').replace('-', '')

        resultados = {
            'cnpj': cnpj,
            'razao_social': razao_social,
            'total_processos': 0,
            'processos': [],
            'tribunais_consultados': []
        }

        # Principais tribunais para PMEs
        tribunais = [
            'tjsp',  # SP
            'tjrj',  # RJ
            'tjmg',  # MG
            'trf1',  # Federal 1ª região
            'trt2',  # Trabalhista SP
        ]

        for tribunal in tribunais:
            try:
                processos = self._consultar_tribunal(tribunal, razao_social, cnpj_limpo)
                resultados['processos'].extend(processos)
                resultados['tribunais_consultados'].append(tribunal)
            except Exception as e:
                print(f"⚠️  Erro ao consultar {tribunal}: {e}")

        resultados['total_processos'] = len(resultados['processos'])
        return resultados

    def _consultar_tribunal(self, tribunal: str, nome_empresa: str, cnpj: str) -> List[Dict]:
        """Consulta processos em um tribunal específico"""
        processos = []

        # Endpoint DataJud
        url = f"{self.datajud_base}/api_publica_{tribunal}/_search"

        # Query Elasticsearch para buscar pelo nome da empresa
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"nomePartes": nome_empresa}},
                        {"match": {"nomePartes": cnpj}}
                    ]
                }
            },
            "size": 100
        }

        try:
            # Nota: Vamos testar e ajustar a query conforme necessário
            response = requests.post(url, json=query, timeout=30)
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', {}).get('hits', [])

                for hit in hits:
                    processo = self._extrair_info_processo(hit['_source'])
                    processos.append(processo)

        except Exception as e:
            raise e

        return processos

    def _extrair_info_processo(self, processo_data: Dict) -> Dict:
        """Extrai informações relevantes do processo"""
        return {
            'numero_cnj': processo_data.get('numeroProcesso'),
            'classe': processo_data.get('classe'),
            'assunto': processo_data.get('assunto'),
            'data_ajuizamento': processo_data.get('dataAjuizamento'),
            'tribunal': processo_data.get('tribunal'),
            'grau': processo_data.get('grau'),
            'movimento_recente': processo_data.get('movimento', [{}])[-1] if processo_data.get('movimento') else None
        }


class BuscadorIntegrado:
    """Orquestra a busca completa: empresas + processos"""

    def __init__(self):
        self.cnpj_searcher = CNPJSearcher()
        self.process_searcher = ProcessSearcher()

    def executar_busca_completa(self,
                                cnae: str,
                                estados: List[str] = None,
                                buscar_processos: bool = True,
                                apenas_com_processos: bool = True) -> List[Dict]:
        """
        Execução completa: busca empresas e cruza com processos

        Args:
            cnae: Código CNAE do ramo
            estados: Lista de estados (ex: ['SP', 'RJ', 'MG'])
            buscar_processos: Se deve buscar processos
            apenas_com_processos: Se deve retornar apenas empresas com processos
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO BUSCA - {timestamp}")
        print(f"{'='*60}\n")

        resultados_finais = []

        # Busca empresas por CNAE e região
        for estado in (estados or ['SP']):
            print(f"\n📍 Processando: {estado}")

            empresas = self.cnpj_searcher.buscar_por_cnae_regiao(
                cnae=cnae,
                estado=estado,
                limite=50
            )

            print(f"✅ Encontradas {len(empresas)} empresas em {estado}")

            # Para cada empresa, busca processos
            for empresa in empresas:
                print(f"\n🔎 Analisando: {empresa.get('razao_social', 'N/A')[:50]}")

                resultado_empresa = {
                    **empresa,
                    'processos': {},
                    'tem_processos': False,
                    'data_consulta': timestamp
                }

                if buscar_processos:
                    processos_info = self.process_searcher.buscar_processos_empresa(
                        cnpj=empresa['cnpj'],
                        razao_social=empresa['razao_social']
                    )

                    resultado_empresa['processos'] = processos_info
                    resultado_empresa['tem_processos'] = processos_info['total_processos'] > 0

                    if processos_info['total_processos'] > 0:
                        print(f"   ⚖️  {processos_info['total_processos']} processo(s) encontrado(s)")
                    else:
                        print(f"   ✓ Sem processos públicos")

                # Filtra conforme critério
                if apenas_com_processos:
                    if resultado_empresa['tem_processos']:
                        resultados_finais.append(resultado_empresa)
                else:
                    resultados_finais.append(resultado_empresa)

                # Rate limiting
                time.sleep(1)

        return resultados_finais

    def salvar_resultados(self, resultados: List[Dict], nome_arquivo: str = None):
        """Salva resultados em JSON"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"empresas_processos_{timestamp}.json"

        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Resultados salvos em: {nome_arquivo}")
        return nome_arquivo


# === EXEMPLO DE USO ===
if __name__ == "__main__":
    # Configuração da busca
    buscador = BuscadorIntegrado()

    # Exemplo: Empresas de TI (CNAE 6201-5/00) em SP e RJ com processos
    resultados = buscador.executar_busca_completa(
        cnae="6201-5/00",  # Desenvolvimento de software
        estados=["SP", "RJ"],
        buscar_processos=True,
        apenas_com_processos=True
    )

    # Salva resultados
    arquivo = buscador.salvar_resultados(resultados)

    print(f"\n{'='*60}")
    print(f"✅ BUSCA CONCLUÍDA")
    print(f"📊 Total de empresas com processos: {len(resultados)}")
    print(f"{'='*60}\n")

"""
Módulo de busca de empresas usando API CNPJA Comercial
Busca empresas ME/EPP por ramo de atividade, estado e cidade
"""

import requests
import os
from typing import List, Dict, Optional
import time

class BuscadorCNPJA:
    """Cliente para API CNPJA comercial"""

    def __init__(self):
        self.api_key = os.environ.get('CNPJA_API_KEY', '')
        self.base_url = 'https://api.cnpja.com'
        self.headers = {
            'Authorization': self.api_key
        }

    def buscar_empresas(self,
                       ramo: str,
                       estados: List[str],
                       cidades: List[str],
                       portes: List[str] = ['ME', 'EPP'],
                       limite_por_cidade: int = 50) -> List[Dict]:
        """
        Busca empresas usando a API CNPJA

        Args:
            ramo: Termo de busca livre (ex: "restaurante", "tecnologia")
            estados: Lista de UFs (ex: ['SP', 'RJ'])
            cidades: Lista de nomes de cidade
            portes: Códigos de porte (01=ME, 03=EPP, 05=Demais)
            limite_por_cidade: Máximo de empresas por cidade

        Returns:
            Lista de empresas encontradas
        """

        if not self.api_key:
            print("⚠️  CNPJA_API_KEY não configurada - retornando lista vazia")
            return []

        empresas_encontradas = []

        # Mapeia códigos de porte
        codigo_porte = {
            'ME': '01',   # Microempresa
            'EPP': '03',  # Empresa de Pequeno Porte
        }

        codigos_busca = [codigo_porte.get(p) for p in portes if p in codigo_porte]

        for estado in estados:
            for cidade in cidades:
                print(f"🔍 Buscando em {cidade}/{estado}...")

                try:
                    # Endpoint de busca por filtros
                    # Docs: https://api.cnpja.com/docs
                    params = {
                        'uf': estado,
                        'city': cidade,
                        'company_size': ','.join(codigos_busca) if codigos_busca else None,
                        'status': 'ATIVA',  # Apenas empresas ativas
                        'query': ramo,  # Busca no nome/atividade
                        'limit': min(limite_por_cidade, 100),  # API tem limite
                    }

                    # Remove params vazios
                    params = {k: v for k, v in params.items() if v}

                    response = requests.get(
                        f'{self.base_url}/companies',
                        headers=self.headers,
                        params=params,
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()
                        empresas = data.get('companies', [])

                        print(f"✅ Encontradas {len(empresas)} empresas")

                        for emp in empresas:
                            empresas_encontradas.append(self._normalizar_empresa(emp, estado, cidade, ramo))

                    elif response.status_code == 401:
                        print("❌ Chave de API inválida")
                        return []
                    elif response.status_code == 429:
                        print("⚠️  Limite de requisições atingido - aguardando...")
                        time.sleep(2)
                    else:
                        print(f"⚠️  Erro {response.status_code}: {response.text[:200]}")

                except Exception as e:
                    print(f"❌ Erro ao buscar em {cidade}/{estado}: {e}")

                # Rate limiting básico
                time.sleep(0.5)

        return empresas_encontradas

    def consultar_cnpj(self, cnpj: str) -> Optional[Dict]:
        """
        Consulta dados detalhados de um CNPJ específico
        """
        if not self.api_key:
            return None

        cnpj_limpo = cnpj.replace('.', '').replace('/', '').replace('-', '')

        try:
            response = requests.get(
                f'{self.base_url}/office/{cnpj_limpo}',
                headers=self.headers,
                timeout=15
            )

            if response.status_code == 200:
                return self._normalizar_empresa(response.json(), '', '', '')
            else:
                print(f"⚠️  Erro ao consultar {cnpj}: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Erro ao consultar CNPJ {cnpj}: {e}")
            return None

    def _normalizar_empresa(self, data: Dict, estado: str, cidade: str, ramo_buscado: str) -> Dict:
        """Converte dados da API para formato padrão do sistema"""

        # API CNPJA retorna estrutura como:
        # {
        #   "tax_id": "00000000000191",
        #   "name": "EMPRESA EXEMPLO LTDA",
        #   "alias": "Exemplo",
        #   "founded": "2010-01-15",
        #   "status": {"text": "ATIVA"},
        #   "company": {"size": {"text": "ME"}},
        #   "address": {"state": "SP", "city": "São Paulo"},
        #   "primary_activity": [{"text": "Desenvolvimento de software"}]
        # }

        cnpj_formatado = self._formatar_cnpj(data.get('tax_id', ''))

        return {
            'cnpj': cnpj_formatado,
            'razao_social': data.get('name', 'N/A'),
            'nome_fantasia': data.get('alias', ''),
            'situacao': data.get('status', {}).get('text', 'ATIVA'),
            'cnae_principal': data.get('primary_activity', [{}])[0].get('id', '') if data.get('primary_activity') else '',
            'cnae_buscado': ramo_buscado,
            'porte': data.get('company', {}).get('size', {}).get('id', ''),
            'estado': data.get('address', {}).get('state', estado),
            'cidade': data.get('address', {}).get('city', cidade),
            'data_abertura': data.get('founded', ''),
            'fonte': 'CNPJA API',
        }

    def _formatar_cnpj(self, cnpj: str) -> str:
        """Formata CNPJ: 00000000000191 -> 00.000.000/0001-91"""
        cnpj = cnpj.zfill(14)
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

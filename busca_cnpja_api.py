"""
Módulo de busca de empresas usando API CNPJA Comercial
Endpoint correto: GET /office (pesquisa avançada por filtros)
Docs: https://cnpja.com/api/reference
"""

import requests
import os
from typing import List, Dict, Optional
import time

class BuscadorCNPJA:
    """Cliente para API CNPJA Comercial"""

    def __init__(self):
        self.api_key = os.environ.get('CNPJA_API_KEY', '')
        self.base_url = 'https://api.cnpja.com'
        self.headers = {
            'Authorization': self.api_key
        }

    def buscar_por_filtros(self,
                           cnae_ids: List[str] = None,
                           uf: str = None,
                           cidades: List[str] = None,
                           portes: List[str] = None,
                           limite: int = 100,
                           paginas: int = 1) -> List[Dict]:
        """
        Pesquisa estabelecimentos via GET /office com filtros estruturados
        Docs: https://cnpja.com/api/reference

        Args:
            cnae_ids: Códigos CNAE numéricos (ex: ['5611201', '5611203'])
            uf: Sigla do estado (ex: 'SP')
            cidades: Nomes de cidades (ex: ['São Paulo', 'Campinas'])
            portes: ['ME', 'EPP'] -> company.size.id.in=1,3
            limite: Registros por página (max 1000)
            paginas: Quantas páginas buscar (cada página custa créditos!)

        Returns:
            Lista de estabelecimentos no formato cru da API
        """
        if not self.api_key:
            print("⚠️  CNPJA_API_KEY não configurada")
            return []

        registros = []
        token = None

        for pagina in range(paginas):
            params = {'limit': limite}

            # Filtros conforme documentação oficial (campo.operador=valor)
            if cnae_ids:
                params['mainActivity.id.in'] = ','.join(cnae_ids)
            if uf:
                params['address.state.in'] = uf
            if cidades:
                params['address.city.in'] = ','.join(cidades)
            if portes:
                # company.size.id: 1=ME, 3=EPP, 5=Demais
                mapa = {'ME': '1', 'EPP': '3'}
                ids = [mapa.get(p) for p in portes if p in mapa]
                if ids:
                    params['company.size.id.in'] = ','.join(ids)
            # Apenas ativas (status.id 2 = Ativa)
            params['status.id.in'] = '2'

            if token:
                params = {'token': token, 'limit': limite}

            try:
                resp = requests.get(
                    f'{self.base_url}/office',
                    headers=self.headers,
                    params=params,
                    timeout=30
                )

                if resp.status_code != 200:
                    print(f"⚠️  Erro {resp.status_code}: {resp.text[:300]}")
                    break

                data = resp.json()
                lote = data.get('records', [])
                registros.extend(lote)
                print(f"   Página {pagina+1}: {len(lote)} registros (total disponível: {data.get('count', '?')})")

                token = data.get('next')
                if not token:
                    break  # não há mais páginas

                time.sleep(0.3)

            except Exception as e:
                print(f"❌ Erro na pesquisa: {e}")
                break

        return registros

    def consultar_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Consulta detalhada de um CNPJ (GET /office/:taxId)"""
        if not self.api_key:
            return None

        cnpj_limpo = ''.join(ch for ch in cnpj if ch.isdigit())

        try:
            resp = requests.get(
                f'{self.base_url}/office/{cnpj_limpo}',
                headers=self.headers,
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json()
            print(f"⚠️  Erro ao consultar {cnpj}: {resp.status_code}")
            return None
        except Exception as e:
            print(f"❌ Erro ao consultar CNPJ: {e}")
            return None

    def normalizar_empresa(self, data: Dict, ramo_buscado: str = '') -> Dict:
        """
        Converte registro da pesquisa (/office) para o formato do sistema.
        Estrutura esperada (docs CNPJA):
        {
          "taxId": "00000000000191",
          "alias": "Nome Fantasia",
          "founded": "2020-06-05",
          "status": {"id": 2, "text": "Ativa"},
          "company": {"name": "RAZAO LTDA", "size": {"id": 1, "acronym": "ME"}},
          "address": {"city": "São Paulo", "state": "SP", ...},
          "mainActivity": {"id": 5611201, "text": "Restaurantes..."}
        }
        """
        company = data.get('company', {}) or {}
        address = data.get('address', {}) or {}
        status = data.get('status', {}) or {}
        size = company.get('size', {}) or {}
        activity = data.get('mainActivity', {}) or {}

        tax_id = data.get('taxId', '')

        return {
            'cnpj': self._formatar_cnpj(tax_id),
            'razao_social': company.get('name') or data.get('name') or 'N/A',
            'nome_fantasia': data.get('alias') or '',
            'situacao': status.get('text', 'N/A'),
            'cnae_principal': f"{activity.get('id', '')} - {activity.get('text', '')}" if activity else '',
            'cnae_buscado': ramo_buscado,
            'porte': size.get('acronym', ''),
            'estado': address.get('state', ''),
            'cidade': address.get('city', ''),
            'data_abertura': data.get('founded', ''),
            'fonte': 'CNPJA API',
        }

    def _formatar_cnpj(self, cnpj: str) -> str:
        """00000000000191 -> 00.000.000/0001-91"""
        cnpj = (cnpj or '').zfill(14)
        if len(cnpj) > 14:
            cnpj = cnpj[:14]
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

"""
Módulo de busca de empresas usando API CNPJA Comercial
Endpoint: GET /office (pesquisa avançada por filtros)
Docs: https://cnpja.com/api/reference

Blindagem contra erro 400: se a API rejeitar algum filtro
(mensagem "property X should not exist"), o cliente remove o campo
rejeitado e refaz a busca automaticamente — até 3 tentativas.
Requisições rejeitadas por validação não retornam dados (não consomem créditos).
"""

import requests
import os
import re
import time
from typing import List, Dict, Optional


class BuscadorCNPJA:
    """Cliente para API CNPJA Comercial"""

    def __init__(self):
        self.api_key = os.environ.get('CNPJA_API_KEY', '')
        self.base_url = 'https://api.cnpja.com'
        self.headers = {
            'Authorization': self.api_key
        }

    def montar_filtros(self,
                       cnae_ids: List[str] = None,
                       uf: str = None,
                       cidades: List[str] = None,
                       portes: List[str] = None,
                       limite: int = 100) -> Dict:
        """Monta o dicionário de filtros do GET /office (formato campo.operador=valor)"""
        filtros = {'limit': str(limite)}

        # CNAEs do ramo (códigos numéricos, ex: '5611201')
        if cnae_ids:
            filtros['mainActivity.id.in'] = ','.join(cnae_ids)

        # Estado (ex: 'SP')
        if uf:
            filtros['address.state.in'] = uf

        # Cidades (ex: ['Americana', 'Limeira'])
        if cidades:
            filtros['address.city.in'] = ','.join(cidades)

        # Porte: company.size.id -> 1=ME, 3=EPP
        if portes:
            mapa = {'ME': '1', 'EPP': '3'}
            ids = [mapa.get(p) for p in portes if p in mapa]
            if ids:
                filtros['company.size.id.in'] = ','.join(ids)

        # Apenas empresas ativas (status.id 2 = Ativa)
        filtros['status.id.in'] = '2'

        return filtros

    def _consultar_com_fallback(self, params: Dict) -> Optional[Dict]:
        """
        Faz GET /office. Se a API rejeitar algum campo (erro 400 de validação),
        remove os campos rejeitados e tenta de novo (máx. 3 tentativas).
        Retorna o JSON da resposta ou None.
        """
        for tentativa in range(3):
            try:
                resp = requests.get(
                    f'{self.base_url}/office',
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
            except Exception as e:
                print(f"❌ Erro de rede na consulta: {e}")
                return None

            if resp.status_code == 200:
                return resp.json()

            # Erro 400 de validação: extrai campos rejeitados da mensagem
            if resp.status_code == 400:
                campos = re.findall(r'property (\S+) should not exist', resp.text)
                if campos:
                    removidos = []
                    for campo in campos:
                        # A chave de params pode ser exatamente 'campo' (ex: 'names')
                        # ou algo como 'address.city.in' quando o erro aponta 'city.in'
                        chave_alvo = None
                        for chave in list(params):
                            if chave == campo or chave.endswith('.' + campo):
                                chave_alvo = chave
                                break
                        if chave_alvo and chave_alvo != 'token':
                            del params[chave_alvo]
                            removidos.append(chave_alvo)
                    if removidos:
                        print(f"   ⚠️  API não aceita: {', '.join(removidos)} — refazendo sem eles")
                        continue  # tenta de novo sem os campos rejeitados
                print(f"⚠️  Erro 400: {resp.text[:300]}")
                return None

            print(f"⚠️  Erro {resp.status_code}: {resp.text[:300]}")
            return None

        print("⚠️  Ainda com erro 400 após remover filtros; desistindo desta busca")
        return None

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
            cidades: Nomes de cidades (ex: ['Americana', 'Campinas'])
            portes: ['ME', 'EPP'] -> company.size.id.in=1,3
            limite: Registros por página (max 1000)
            paginas: Quantas páginas buscar (cada página custa créditos!)

        Returns:
            Lista de estabelecimentos no formato cru da API
        """
        if not self.api_key:
            print("⚠️  CNPJA_API_KEY não configurada")
            return []

        filtros = self.montar_filtros(
            cnae_ids=cnae_ids, uf=uf, cidades=cidades,
            portes=portes, limite=limite
        )

        registros = []
        token = None

        for pagina in range(paginas):
            params = dict(filtros)
            if token:
                params['token'] = token

            data = self._consultar_com_fallback(params)
            if data is None:
                break

            lote = data.get('records', [])
            registros.extend(lote)
            print(f"   Página {pagina+1}: {len(lote)} registros "
                  f"(total disponível: {data.get('count', '?')})")

            token = data.get('next')
            if not token:
                break  # não há mais páginas

            time.sleep(0.3)

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

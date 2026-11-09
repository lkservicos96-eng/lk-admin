"""
Módulo de busca de empresas usando API CNPJA Comercial
Endpoint: GET /office (pesquisa avançada por filtros)
Docs: https://cnpja.com/api/reference

BLINDAGEM contra erro 400 de validação:
- Autodetecção do nome correto dos filtros (cidade, CNAE) testando candidatos
- Requisições rejeitadas (400) não retornam dados = não consomem créditos
- Cache em arquivo para não repetir testes após descobrir os nomes corretos
- Avisos coletados em self.avisos (o servidor lê e repassa para a interface)
"""

import requests
import os
import re
import time
import json
from typing import List, Dict, Optional


class BuscadorCNPJA:
    """Cliente para API CNPJA Comercial com autodetecção de filtros"""

    # Candidatos para o filtro de cidade (testados em ordem até algum ser aceito)
    CANDIDATOS_CIDADE = [
        'address.city.name.in',
        'address.city.id.in',
        'address.municipality.in',
        'address.cityName.in',
        'city.name.in',
        'address.city.in'
    ]

    # Candidatos para o filtro de CNAE/atividade
    CANDIDATOS_CNAE = [
        'mainActivity.id.in',
        'mainCnae.id.in',
        'activity.id.in',
        'cnae.id.in'
    ]

    def __init__(self):
        self.api_key = os.environ.get('CNPJA_API_KEY', '')
        self.base_url = 'https://api.cnpja.com'
        self.headers = {'Authorization': self.api_key}
        self.avisos = []  # Avisos coletados durante a busca (o servidor lê)
        self._cache_arquivo = 'config_filtros_api.json'
        self._cache = self._carregar_cache()

    def _carregar_cache(self) -> Dict:
        """Carrega cache de filtros descobertos (persiste entre requests, não entre deploys)"""
        if os.path.exists(self._cache_arquivo):
            try:
                with open(self._cache_arquivo, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _salvar_cache(self, chave: str, valor: str):
        """Salva o nome do filtro descoberto no cache"""
        self._cache[chave] = valor
        try:
            with open(self._cache_arquivo, 'w') as f:
                json.dump(self._cache, f)
        except:
            pass

    def _filtro_conhecido(self, tipo: str, candidatos: List[str]) -> Optional[str]:
        """Retorna o filtro do cache se ainda estiver na lista de candidatos"""
        nome = self._cache.get(tipo)
        return nome if nome in candidatos else None

    def montar_filtros_base(self, uf: str = None, portes: List[str] = None, limite: int = 100) -> Dict:
        """Monta filtros básicos (estado, porte, status ativo, limite) sem cidade/CNAE"""
        filtros = {'limit': str(limite), 'status.id.in': '2'}  # apenas empresas ativas
        if uf:
            filtros['address.state.in'] = uf
        if portes:
            mapa = {'ME': '1', 'EPP': '3'}
            ids = [mapa.get(p) for p in portes if p in mapa]
            if ids:
                filtros['company.size.id.in'] = ','.join(ids)
        return filtros

    def _consultar_com_fallback(self, params: Dict) -> tuple:
        """
        Faz GET /office. Se a API rejeitar algum campo (erro 400 de validação),
        remove os campos rejeitados e tenta de novo (máx. 3 tentativas).
        Retorna (data, campos_removidos).
        """
        removidos = []
        for tentativa in range(3):
            try:
                resp = requests.get(f'{self.base_url}/office', headers=self.headers,
                                    params=params, timeout=30)
            except Exception as e:
                print(f"❌ Erro de rede: {e}")
                return None, removidos

            if resp.status_code == 200:
                return resp.json(), removidos

            # Erro 400 de validação: extrai campos rejeitados da mensagem
            if resp.status_code == 400:
                campos = re.findall(r'property (\S+) should not exist', resp.text)
                if campos:
                    removidos_nesta = []
                    for campo in campos:
                        # A chave pode ser exata ('names') ou sufixo ('address.city.in' quando erro diz 'city.in')
                        for chave in list(params):
                            if chave == campo or chave.endswith('.' + campo):
                                if chave != 'token':  # nunca remover o token de paginação
                                    del params[chave]
                                    removidos.append(chave)
                                    removidos_nesta.append(chave)
                                break
                    if removidos_nesta:
                        print(f"   ⚠️  API não aceita: {', '.join(removidos_nesta)} — refazendo sem eles")
                        continue
                print(f"⚠️  Erro 400: {resp.text[:300]}")
                return None, removidos

            print(f"⚠️  Erro {resp.status_code}: {resp.text[:300]}")
            return None, removidos

        print("⚠️  Ainda com erro 400 após remover filtros; desistindo")
        return None, removidos

    def _descobrir_filtro(self, filtros_base: Dict, tipo: str, candidatos: List[str],
                          valores: List[str], rotulo: str) -> tuple:
        """
        Testa nomes candidatos para um filtro incógnito (cidade ou CNAE).
        Retorna (data_da_busca_bem_sucedida, nome_do_filtro_aceito).
        Requisições rejeitadas (400) não consomem créditos; a primeira que der 200
        já retorna os dados reais (nada desperdiçado).
        """
        for candidato in candidatos:
            params = dict(filtros_base)
            params[candidato] = ','.join(valores)
            data, removidos = self._consultar_com_fallback(params)
            if data is not None and candidato not in removidos:
                print(f"   ✅ Filtro de {rotulo} aceito: {candidato}")
                self._salvar_cache(tipo, candidato)
                return data, candidato
        return None, None

    def buscar_por_filtros(self, cnae_ids: List[str] = None, uf: str = None,
                           cidades: List[str] = None, portes: List[str] = None,
                           limite: int = 100, paginas: int = 1) -> List[Dict]:
        """
        Pesquisa estabelecimentos via GET /office com filtros estruturados.
        Autodetecta os nomes corretos dos filtros de cidade e CNAE (testa candidatos).

        Args:
            cnae_ids: Códigos CNAE numéricos de 7 dígitos (ex: ['5611201', '5611203'])
            uf: Sigla do estado (ex: 'SP')
            cidades: Nomes de cidades (ex: ['Americana', 'Campinas'])
            portes: ['ME', 'EPP'] -> company.size.id.in=1,3
            limite: Registros por página (max 1000)
            paginas: Quantas páginas buscar (cada página custa créditos!)

        Returns:
            Lista de estabelecimentos no formato cru da API
        """
        self.avisos = []
        if not self.api_key:
            print("⚠️  CNPJA_API_KEY não configurada")
            return []

        filtros_base = self.montar_filtros_base(uf=uf, portes=portes, limite=limite)
        data_primeira = None

        # --- Autodetecção do filtro de CNAE (ramo/atividade) ---
        if cnae_ids:
            filtro_cnae = self._filtro_conhecido('filtro_cnae', self.CANDIDATOS_CNAE)
            if filtro_cnae:
                filtros_base[filtro_cnae] = ','.join(cnae_ids)
            else:
                # Descobre qual nome funciona (testa candidatos com a busca real)
                data_primeira, filtro_cnae = self._descobrir_filtro(
                    filtros_base, 'filtro_cnae', self.CANDIDATOS_CNAE, cnae_ids, 'atividade/CNAE'
                )
                if filtro_cnae:
                    filtros_base[filtro_cnae] = ','.join(cnae_ids)
                else:
                    self.avisos.append('A API não aceitou filtro de ramo (CNAE) — buscando sem filtro de atividade')

        # --- Autodetecção do filtro de cidade ---
        if cidades:
            filtro_cidade = self._filtro_conhecido('filtro_cidade', self.CANDIDATOS_CIDADE)
            if filtro_cidade:
                filtros_base[filtro_cidade] = ','.join(cidades)
            else:
                # Descobre qual nome funciona
                data, filtro_cidade = self._descobrir_filtro(
                    filtros_base, 'filtro_cidade', self.CANDIDATOS_CIDADE, cidades, 'cidade'
                )
                if filtro_cidade:
                    filtros_base[filtro_cidade] = ','.join(cidades)
                    if data_primeira is None:
                        data_primeira = data  # aproveitamos os dados da descoberta
                else:
                    msg = f'A API não aceitou filtro de cidade — buscando {uf or "todo o Brasil"} inteiro'
                    self.avisos.append(msg)

        # --- Consulta final (se ainda não temos dados da autodetecção) ---
        registros = []
        if data_primeira:
            registros.extend(data_primeira.get('records', []))
            print(f"   Página 1: {len(data_primeira.get('records', []))} registros "
                  f"(total disponível: {data_primeira.get('count', '?')})")
            token = data_primeira.get('next')
        else:
            # Primeira consulta normal
            data, _ = self._consultar_com_fallback(dict(filtros_base))
            if data is None:
                return []
            registros.extend(data.get('records', []))
            print(f"   Página 1: {len(data.get('records', []))} registros "
                  f"(total disponível: {data.get('count', '?')})")
            token = data.get('next')

        # --- Paginação (páginas 2+) ---
        for pagina in range(2, paginas + 1):
            if not token:
                break
            params = dict(filtros_base)
            params['token'] = token
            data, _ = self._consultar_com_fallback(params)
            if data is None:
                break
            lote = data.get('records', [])
            registros.extend(lote)
            print(f"   Página {pagina}: {len(lote)} registros")
            token = data.get('next')
            time.sleep(0.3)

        return registros

    def consultar_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Consulta detalhada de um CNPJ (GET /office/:taxId)"""
        if not self.api_key:
            return None
        cnpj_limpo = ''.join(ch for ch in cnpj if ch.isdigit())
        try:
            resp = requests.get(f'{self.base_url}/office/{cnpj_limpo}',
                                headers=self.headers, timeout=15)
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

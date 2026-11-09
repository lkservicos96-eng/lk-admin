"""
Consulta de processos judiciais via API Pública do CNJ — DataJud

- Fonte oficial e gratuita: https://api-publica.datajud.cnj.jus.br/
- Cadastro GRATUITO: https://datajud-wiki.cnj.jus.br/api-publica/
  (preencha o formulário e receba uma APIKey por e-mail)
- Header:  Authorization: APIKey <chave>
- Endpoint: POST https://api-publica.datajud.cnj.jus.br/api_publica_<tribunal>/_search

Esse módulo consulta TODOS os tribunais (27 TJs + 24 TRTs = 51) por CNPJ da empresa,
em paralelo, com timeout curto. A query usa match em vários campos candidatos de
documento da parte — o Elasticsearch simplesmente ignora campos não mapeados
(sem erro), então a consulta nunca quebra por causa do nome do campo.

O uso é controlado por limite de empresas por rodada (padrão 10) para não
exaurir o rate limit gratuito da API nem o tempo do navegador; o servidor roda
em thread de background com barra de progresso.
"""

import os
import re
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE = 'https://api-publica.datajud.cnj.jus.br'

# 27 Tribunais de Justiça (cível/família/consumidor...) + 24 TRTs (trabalhistas)
TRIBUNAIS = [
    'tjac', 'tjal', 'tjam', 'tjap', 'tjba', 'tjce', 'tjdf', 'tjes', 'tjgo',
    'tjma', 'tjmg', 'tjms', 'tjmt', 'tjpa', 'tjpb', 'tjpe', 'tjpi', 'tjpr',
    'tjrj', 'tjrn', 'tjro', 'tjrr', 'tjrs', 'tjsc', 'tjse', 'tjsp', 'tjto',
    'trt1', 'trt2', 'trt3', 'trt4', 'trt5', 'trt6', 'trt7', 'trt8', 'trt9',
    'trt10', 'trt11', 'trt12', 'trt13', 'trt14', 'trt15', 'trt16', 'trt17',
    'trt18', 'trt19', 'trt20', 'trt21', 'trt22', 'trt23', 'trt24',
]

# Estados mínimos do processo CNJ (ex: 0000837-89.2023.4.04.0001)
_CNJ_RE = re.compile(r'(\d{7})[-\.]?(\d{2})\.(\d{4})\.(\d)\.(\d{2})\.(\d{4})')

# Cache dos campos descobertos (documento/nome da parte) por tribunal-esquema
_ARQUIVO_CAMPOS = 'config_campos_datajud.json'


def _limpar(cnpj: str) -> str:
    return ''.join(ch for ch in (cnpj or '') if ch.isdigit()).zfill(14)


# ======================================================================
# AUTODETECÇÃO DE CAMPOS DA PARTE
# O esquema do DataJud pode variar entre tribunais/versões. Em vez de
# adivinhar o nome do campo que guarda o CNPJ da parte, consultamos
# 1 documento real (match_all) e varremos a estrutura JSON procurando
# paths que contenham documento/cnpj (busca por documento) e nome
# (busca por nome da empresa como fallback).
# ======================================================================

def _varrer_campos(obj, path='', achados=None):
    """Varre o _source recursivamente e coleta paths candidatos."""
    if achados is None:
        achados = {'documento': [], 'nome': []}
    if isinstance(obj, dict):
        for k, v in obj.items():
            novo = f'{path}.{k}' if path else k
            kl = k.lower()
            if ('documento' in kl or 'cnpj' in kl) and novo not in achados['documento']:
                achados['documento'].append(novo)
            if kl == 'nome' and novo not in achados['nome']:
                achados['nome'].append(novo)
            _varrer_campos(v, novo, achados)
    elif isinstance(obj, list) and obj:
        # Arrays no ES são indexados com o MESMO path (sem []), então
        # inspecionamos o primeiro elemento mantendo o path.
        _varrer_campos(obj[0], path, achados)
    return achados


def _carregar_cache_campos():
    if os.path.exists(_ARQUIVO_CAMPOS):
        try:
            with open(_ARQUIVO_CAMPOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _salvar_cache_campos(cache):
    try:
        with open(_ARQUIVO_CAMPOS, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False)
    except Exception:
        pass


def descobrir_campos(chave: str, sigla: str = 'tjsp', forcar: bool = False) -> dict:
    """
    Consulta 1 processo real no tribunal e descobre os paths de
    documento e nome da parte. Cacheia para não repetir.
    Retorna {'documento': [...], 'nome': [...], 'fonte': sigla}.
    Levanta exceção se não conseguir consultar.
    """
    cache = _carregar_cache_campos()
    chave_cache = f'campos_{sigla}'
    if not forcar and chave_cache in cache:
        return cache[chave_cache]

    url = f'{BASE}/api_publica_{sigla}/_search'
    resp = requests.post(
        url,
        headers={'Authorization': f'APIKey {chave}', 'Content-Type': 'application/json'},
        json={'size': 1, 'query': {'match_all': {}}},
        timeout=15,
    )
    if resp.status_code != 200:
        raise RuntimeError(f'{sigla}: HTTP {resp.status_code} — {resp.text[:200]}')

    hits = resp.json().get('hits', {}).get('hits', [])
    if not hits:
        raise RuntimeError(f'{sigla}: nenhum processo retornado para inspecionar')

    source = hits[0].get('_source', {})
    achados = _varrer_campos(source)

    # Prioriza campos com "pessoa"/"parte" no nome (menos ruído)
    def _priorizar(campos):
        return sorted(campos, key=lambda c: (0 if ('pessoa' in c or 'parte' in c or 'polo' in c) else 1, len(c)))

    resultado = {
        'documento': _priorizar(achados['documento'])[:8],
        'nome': _priorizar(achados['nome'])[:8],
        'fonte': sigla,
    }
    cache[chave_cache] = resultado
    _salvar_cache_campos(cache)
    print(f"   🔎 Campos descobertos em {sigla}: documento={resultado['documento'][:3]}... nome={resultado['nome'][:3]}...")
    return resultado


def _query_parte(cnpj: str, nome_empresa: str = '', campos: dict = None) -> dict:
    """
    Query Elasticsearch combinada: documento (nos campos descobertos ou
    nos padrões) + nome da empresa (match_phrase, fallback caso o
    documento venha mascarado). minimum_should_match=1.
    """
    if campos and campos.get('documento'):
        campos_doc = campos['documento']
    else:
        campos_doc = [
            'dadosBasicos.poloPassivo.pessoa.documento',
            'dadosBasicos.poloAtivo.pessoa.documento',
            'elementosPolo.pessoa.documento',
            'partes.documento',
            'documentosPartes.documento',
        ]

    should = [{'match': {c: cnpj}} for c in campos_doc]

    if nome_empresa:
        if campos and campos.get('nome'):
            campos_nome = [c for c in campos['nome'] if 'pessoa' in c or 'parte' in c or 'polo' in c] or campos['nome'][:3]
        else:
            campos_nome = [
                'dadosBasicos.poloPassivo.pessoa.nome',
                'dadosBasicos.poloAtivo.pessoa.nome',
                'partes.nome',
            ]
        should += [{'match_phrase': {c: nome_empresa}} for c in campos_nome]

    return {
        'size': 50,
        'query': {'bool': {'should': should, 'minimum_should_match': 1}},
    }


def _formatar_processo(src: dict, sigla_padrao: str) -> dict:
    """
    Converte o documento do DataJud para o formato esperado pela UI:
    {numero_cnj, classe, tribunal, assunto, data_ajuizamento, grau, orgao}
    """
    classe = src.get('classe') or {}
    assuntos = src.get('assuntos') or []
    orgao = src.get('orgaoJudicial') or {}
    primeiro_assunto = ''
    if assuntos and isinstance(assuntos[0], dict):
        primeiro_assunto = assuntos[0].get('nome', '')
    data = src.get('dataAjuizamento') or ''
    return {
        'numero_cnj': src.get('numeroProcesso') or '',
        'classe': classe.get('nome') if isinstance(classe, dict) else str(classe),
        'tribunal': src.get('tribunal') or sigla_padrao.upper(),
        'assunto': primeiro_assunto,
        'data_ajuizamento': data[:10] if data else '',
        'grau': src.get('grau') or '',
        'orgao': orgao.get('nome') if isinstance(orgao, dict) else '',
    }


def consultar_tribunal(cnpj: str, sigla: str, chave: str, timeout: int = 6,
                       nome_empresa: str = '', campos: dict = None) -> list | None:
    """
    Consulta processos de um CNPJ em um tribunal específico.
    Retorna lista de processos (formato UI) ou None se falhou.
    """
    cnpj_limpo = _limpar(cnpj)
    if not cnpj_limpo:
        return []
    url = f'{BASE}/api_publica_{sigla}/_search'
    try:
        resp = requests.post(
            url,
            headers={'Authorization': f'APIKey {chave}', 'Content-Type': 'application/json'},
            json=_query_parte(cnpj_limpo, nome_empresa, campos),
            timeout=timeout,
        )
        if resp.status_code != 200:
            print(f"   ⚠️  {sigla}: HTTP {resp.status_code}")
            return None
        hits = resp.json().get('hits', {}).get('hits', [])
        return [_formatar_processo(h.get('_source', {}), sigla) for h in hits]
    except Exception as e:
        print(f"   ⚠️  {sigla}: erro {e}")
        return None


def consultar_em_lote(
    empresas: list,
    chave: str,
    tribunais: list | None = None,
    workers: int = 12,
    timeout: int = 8,
    progresso_callback=None,
) -> dict:
    """
    Consulta processos de várias empresas em todos os tribunais (paralelizado).
    Retorna {cnpj: {'total_processos', 'tribunais_consultados', 'processos'}}.

    Empresas: lista de dicts com 'cnpj' (14 dígitos, sem máscara) e opcional 'razao_social'.
    progresso_callback(feitos, total) — chamado a cada tarefa concluída.
    """
    alvos = tribunais or TRIBUNAIS

    # Descobre os campos de parte 1x (cache) usando o 1º tribunal como referência
    campos = None
    try:
        campos = descobrir_campos(chave, sigla=alvos[0])
    except Exception as e:
        print(f"   ⚠️  Autodetecção de campos falhou ({e}); usando campos padrão")

    tarefas = [(e.get('cnpj'), e.get('razao_social') or '', t) for e in empresas for t in alvos]
    total_tarefas = len(tarefas)

    resultados = {}
    feitos = [0]
    lock = threading.Lock()

    def _tarefa(cnpj, nome, sigla):
        docs = consultar_tribunal(cnpj, sigla, chave, timeout,
                                  nome_empresa=nome, campos=campos)
        with lock:
            acc = resultados.setdefault(
                cnpj,
                {'total_processos': 0, 'tribunais_consultados': [], 'processos': []},
            )
            if docs:
                acc['processos'].extend(docs)
                acc['total_processos'] = len(acc['processos'])
                if sigla not in acc['tribunais_consultados']:
                    acc['tribunais_consultados'].append(sigla)
            feitos[0] += 1
            if progresso_callback:
                progresso_callback(feitos[0], total_tarefas)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futuros = [pool.submit(_tarefa, c, n, t) for c, n, t in tarefas]
        for fut in futuros:
            fut.result()  # levanta exceções inesperadas para serem tratadas fora

    return resultados

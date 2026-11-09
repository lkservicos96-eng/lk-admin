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


def _limpar(cnpj: str) -> str:
    return ''.join(ch for ch in (cnpj or '') if ch.isdigit()).zfill(14)


def _query_cnpj(cnpj: str) -> dict:
    """
    Query Elasticsearch 'shotgun': match em vários paths candidatos do
    documento da parte. Campos não mapeados no índice são ignorados sem erro.
    """
    return {
        'size': 50,
        'query': {
            'bool': {
                'should': [
                    {'match': {'dadosBasicos.poloPassivo.pessoa.documento': cnpj}},
                    {'match': {'dadosBasicos.poloAtivo.pessoa.documento': cnpj}},
                    {'match': {'elementosPolo.pessoa.documento': cnpj}},
                    {'match': {'partes.documento': cnpj}},
                    {'match': {'documentosPartes.documento': cnpj}},
                ],
                'minimum_should_match': 1,
            },
        },
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


def consultar_tribunal(cnpj: str, sigla: str, chave: str, timeout: int = 6) -> list | None:
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
            json=_query_cnpj(cnpj_limpo),
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
    tarefas = [(e['cnpj'], t) for e in empresas for t in alvos]
    total_tarefas = len(tarefas)

    resultados = {}
    feitos = [0]
    lock = threading.Lock()

    def _tarefa(cnpj, sigla):
        docs = consultar_tribunal(cnpj, sigla, chave, timeout)
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
        futuros = [pool.submit(_tarefa, c, t) for c, t in tarefas]
        for fut in futuros:
            fut.result()  # levanta exceções inesperadas para serem tratadas fora

    return resultados

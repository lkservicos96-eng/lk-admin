"""
Conversor de nomes de cidades → códigos IBGE de municípios.

A API CNPJA aceita o filtro de cidade apenas com código IBGE numérico
(address.municipality.in=3200607), não com o nome. Este módulo:
  1. Baixa a lista oficial dos ~5.570 municípios brasileiros (uma única vez)
  2. Cachear em arquivo local (config_cidades_ibge.json)
  3. Converte (nome da cidade, UF) → código IBGE

Fonte da lista: https://github.com/kelvins/Municipios-Brasileiros
(dados públicos do IBGE, formato: [{"codigo_ibge": 3200607, "nome": "Aracruz", "codigo_uf": 32}, ...])
"""

import json
import os
import unicodedata

import requests

URL_MUNICIPIOS = 'https://raw.githubusercontent.com/kelvins/Municipios-Brasileiros/main/json/municipios.json'
ARQUIVO_CACHE = 'config_cidades_ibge.json'

# Código da unidade federativa (IBGE) → sigla
UF_POR_CODIGO = {
    11: 'RO', 12: 'AC', 13: 'AM', 14: 'RR', 15: 'PA', 16: 'AP', 17: 'TO',
    21: 'MA', 22: 'PI', 23: 'CE', 24: 'RN', 25: 'PB', 26: 'PE', 27: 'AL',
    28: 'SE', 29: 'BA', 31: 'MG', 32: 'ES', 33: 'RJ', 35: 'SP', 41: 'PR',
    42: 'SC', 43: 'RS', 50: 'MS', 51: 'MT', 52: 'GO', 53: 'DF',
}


def normalizar_nome(texto: str) -> str:
    """Minúsculas + sem acentos. 'São Paulo' → 'sao paulo'"""
    texto = (texto or '').strip().lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(ch for ch in texto if unicodedata.category(ch) != 'Mn')
    return texto


def carregar_municipios() -> dict:
    """
    Retorna índice {nome_normalizado: {uf: codigo_ibge_str}}.
    Exemplo: {'aracruz': {'ES': '3200607'}, 'sao paulo': {'SP': '3550308'}, ...}

    Baixa da fonte oficial na primeira chamada e cacheia em arquivo local.
    Retorna {} se o download falhar (busca continua sem filtro de cidade).
    """
    # Cache em disco?
    if os.path.exists(ARQUIVO_CACHE):
        try:
            with open(ARQUIVO_CACHE, 'r', encoding='utf-8') as f:
                indice = json.load(f)
            if indice:
                return indice
        except Exception:
            pass

    # Baixa a lista completa dos municípios
    try:
        resp = requests.get(URL_MUNICIPIOS, timeout=30)
        resp.raise_for_status()
        municipios = resp.json()
    except Exception as e:
        print(f"⚠️  Não foi possível baixar a lista de municípios IBGE: {e}")
        return {}

    indice = {}
    for m in municipios:
        try:
            uf = UF_POR_CODIGO.get(m.get('codigo_uf'))
            nome = normalizar_nome(m.get('nome', ''))
            codigo = str(m.get('codigo_ibge', ''))
            if not uf or not nome or not codigo.isdigit():
                continue
            indice.setdefault(nome, {})[uf] = codigo
        except Exception:
            continue

    # Salva cache em disco
    try:
        with open(ARQUIVO_CACHE, 'w', encoding='utf-8') as f:
            json.dump(indice, f, ensure_ascii=False)
    except Exception:
        pass

    print(f"   📚 Base IBGE carregada: {len(indice)} municípios")
    return indice


def codigos_ibge_para_cidades(cidades: list, uf: str = '') -> tuple:
    """
    Converte nomes de cidades em códigos IBGE (7 dígitos, sem separadores).

    Args:
        cidades: lista de nomes, ex: ['Aracruz', 'Linhares']
        uf: sigla do estado para desambiguar, ex: 'ES' (opcional)

    Returns:
        (codigos, nao_encontradas)
        codigos: lista de códigos IBGE encontrados, ex: ['3200607', '3203200']
        nao_encontradas: nomes que não casaram com a base IBGE

    Exemplo:
        >>> codigos_ibge_para_cidades(['Aracruz'], 'ES')
        (['3200607'], [])
    """
    if not cidades:
        return [], []

    indice = carregar_municipios()
    if not indice:
        print("   ⚠️  Base IBGE indisponível (download falhou) — tentando filtro de cidade por nome")
        return [], []  # não marca como "não encontradas": é falha da base, não da cidade

    uf = (uf or '').upper()
    codigos = []
    nao_encontradas = []

    for cidade in cidades:
        nome = normalizar_nome(cidade)
        entradas = indice.get(nome, {})

        codigo = None
        if entradas:
            if uf:
                # UF informado: só casa se a cidade existir naquele estado
                codigo = entradas.get(uf)
            elif len(entradas) == 1:
                # Sem UF e nome único no Brasil → sem ambiguidade
                codigo = next(iter(entradas.values()))

        if codigo:
            codigos.append(codigo)
        else:
            nao_encontradas.append(cidade)

    return codigos, nao_encontradas

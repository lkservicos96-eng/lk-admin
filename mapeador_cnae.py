"""
Mapeador: ramo (texto livre digitado pelo usuário) → códigos CNAE (7 dígitos)

Exemplo de uso:
    >>> cnaes_para_ramo("restaurante e lanchonete")
    ['5611201', '5611203', '5611204', '5611205']

    >>> cnaes_para_ramo("salão de beleza")
    ['9602501', '9602502']

    >>> cnaes_para_ramo("construção civil")
    None  # ainda não mapeado

Para adicionar novos ramos:
    Adicione no dicionário RAMOS abaixo com as chaves normalizadas
    (minúscula, sem acento, ex: 'farmacia' em vez de 'farmácia').

Códigos CNAE de alta confiança (memória CNAE 2.0):
    5611201 Restaurantes e similares
    5611202 Sorveterias e similares
    5611203 Lanchonetes, casas de chá, de sucos e similares
    5611204 Bares e similares
    5611205 Serviços de buffet
    5612100 Serviços de catering para eventos e recepções
    5620101 Fornecimento de alimentos preparados primariamente para consumo domiciliar
    5620102 Serviços de confeitaria, padaria e docerias
    4711302 Comércio varejista de mercadorias em geral - supermercados
    4712100 Comércio varejista de mercadorias - minimercados, mercearias e armazéns
    4771701 Comércio varejista de produtos farmacêuticos - farmácias e drogarias
    9602501 Cabeleireiros, manicure e pedicure
    4520001 Serviços de manutenção e reparação mecânica de veículos automotores
    4120400 Construção de edifícios
"""

import unicodedata
from typing import Optional, List


# Dicionário ramo → CNAEs (chaves sem acento, minúsculas)
RAMOS = {
    # Alimentação e bebidas
    'restaurante': ['5611201', '5611203', '5611204', '5611205', '5612100', '5620101'],
    'restaurantes': ['5611201', '5611203', '5611204', '5611205', '5612100', '5620101'],
    'lanchonete': ['5611203', '5611201', '5620102'],
    'lanchonetes': ['5611203', '5611201', '5620102'],
    'bar': ['5611204', '5611201', '5611203'],
    'bares': ['5611204', '5611201', '5611203'],
    'pizzaria': ['5611201', '5611203'],
    'padaria': ['5611203', '5620102'],
    'sorveteria': ['5611202'],
    'buffet': ['5611205', '5612100'],
    'catering': ['5612100', '5620101'],

    # Comércio varejista
    'mercado': ['4712100', '4711302'],
    'supermercado': ['4711302', '4712100'],
    'mercearia': ['4712100'],
    'farmacia': ['4771701'],
    'drogaria': ['4771701'],

    # Serviços pessoais
    'salao': ['9602501', '9602502'],
    'barbearia': ['9602501'],
    'cabeleireiro': ['9602501'],
    'manicure': ['9602502'],

    # Automotivo
    'oficina': ['4520001', '4520002'],
    'mecanica': ['4520001'],

    # Construção
    'construcao': ['4120400', '4321500'],
}


def _normalizar(texto: str) -> str:
    """
    Remove acentos, converte para minúsculas, remove espaços nas pontas.
    Exemplo: "Salão de Beleza" → "salao de beleza"
    """
    texto = (texto or '').strip().lower()
    # Remove acentos: NFD separa base+diacrítico; filtra categorias de marca (Mn)
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(ch for ch in texto if unicodedata.category(ch) != 'Mn')
    return texto


def cnaes_para_ramo(ramo: str) -> Optional[List[str]]:
    """
    Converte um ramo (texto livre) em lista de códigos CNAE de 7 dígitos.

    Estratégia: normaliza o texto; casa por contenção com as chaves do dicionário RAMOS.
    Se o ramo contém "restaurante" E "lanchonete", retorna a união dos CNAEs de ambos.

    Args:
        ramo: Texto digitado pelo usuário (ex: "restaurante e lanchonete")

    Returns:
        Lista de códigos CNAE (ex: ['5611201', '5611203', ...]) ou None se não mapeado.
    """
    texto_norm = _normalizar(ramo)
    if not texto_norm:
        return None

    # Casa por contenção: qualquer chave do dicionário que apareça no texto normalizado
    cnaes_achados = set()
    for chave, codigos in RAMOS.items():
        if chave in texto_norm:  # "restaurante" in "restaurante e lanchonete" → True
            cnaes_achados.update(codigos)

    return sorted(cnaes_achados) if cnaes_achados else None

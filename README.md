# Sistema de Busca de Empresas com Processos Judiciais

Sistema automatizado para buscar empresas de pequeno e médio porte com processos judiciais e trabalhistas abertos.

## 📋 Arquivos Criados

1. **config_busca.json** - Arquivo de configuração
2. **cnpj_searcher.py** - Módulo principal de busca
3. **executar_busca_diaria.py** - Script de execução automática

## 🎯 Como Funciona

### Estratégia de Busca

O sistema usa uma abordagem em duas etapas:

1. **Busca de Empresas**: Consulta APIs públicas filtrando por CNAE e região
2. **Verificação de Processos**: Cruza com a base DataJud (CNJ) para encontrar processos

### APIs Utilizadas

- **CNPJA** / **OpenCNPJ** / **ReceitaWS**: Dados cadastrais de empresas
- **DataJud (CNJ)**: Processos judiciais públicos de todos os tribunais do Brasil

## ⚙️ Configuração

Edite o arquivo `config_busca.json`:

```json
{
  "busca": {
    "cnaes": [
      {
        "codigo": "6201-5/00",
        "descricao": "Desenvolvimento de software"
      }
    ],
    "estados": ["SP", "RJ", "MG"],
    "filtros": {
      "apenas_com_processos": true,
      "porte_empresa": ["ME", "EPP"]
    }
  }
}
```

### Principais CNAEs para PMEs

- **6201-5/00** - Desenvolvimento de software
- **4711-3/02** - Comércio varejista
- **4712-1/00** - Lojas de departamentos
- **4744-0/05** - Comércio varejista de material elétrico
- **5611-2/01** - Restaurantes e similares
- **5620-1/01** - Fornecimento de alimentos preparados
- **7020-4/00** - Atividades de consultoria em gestão empresarial

## 🚀 Como Usar

### 1. Teste Manual

```bash
python executar_busca_diaria.py
```

### 2. Agendar Execução Diária

Vou criar uma scheduled task que roda automaticamente.

## 📊 Resultados

O sistema gera dois arquivos:

1. **busca_automatica_YYYYMMDD_HHMMSS.json** - Dados completos em JSON
2. **relatorio_YYYYMMDD_HHMMSS.txt** - Relatório resumido legível

### Exemplo de Saída

```
CNPJ: 12.345.678/0001-90
Razão Social: EMPRESA EXEMPLO LTDA
CNAE: 6201-5/00 - Desenvolvimento de software
Cidade: São Paulo/SP
⚖️ Processos: 3
Tribunais: tjsp, trt2
```

## 🔧 Customização

### Adicionar Mais CNAEs

Edite `config_busca.json` e adicione na lista `cnaes`:

```json
{
  "codigo": "XXXX-X/XX",
  "descricao": "Descrição do ramo"
}
```

### Mudar Regiões

Modifique a lista `estados`:

```json
"estados": ["SP", "RJ", "MG", "RS", "PR", "SC"]
```

### Ajustar Filtros

```json
"filtros": {
  "apenas_com_processos": true,
  "buscar_processos_trabalhistas": true,
  "buscar_processos_civeis": true,
  "porte_empresa": ["ME", "EPP"],
  "situacao_cadastral": ["ATIVA"]
}
```

## ⚠️ Limitações Conhecidas

1. **DataJud não busca por CNPJ direto** - Usamos busca por nome da empresa
2. **APIs gratuitas têm rate limits** - Sistema inclui delays automáticos
3. **Dados podem ter delay** - APIs gratuitas podem não ser real-time
4. **Acesso web restrito** - Você precisa liberar hosts (veja README)

## 🔐 Próximos Passos

1. **Liberar acesso web** (via configurações do app)
2. **Testar APIs reais** (ajustar queries conforme resposta)
3. **Criar scheduled task** (execução automática)
4. **Refinar filtros** (conforme seus resultados)

## 📚 Fontes

- [CNPJA API](https://cnpja.com/api/open)
- [OpenCNPJ](https://opencnpj.org/)
- [DataJud CNJ](https://www.cnj.jus.br/sistemas/datajud/api-publica/)
- [DataJud Wiki](https://datajud-wiki.cnj.jus.br/api-publica/)

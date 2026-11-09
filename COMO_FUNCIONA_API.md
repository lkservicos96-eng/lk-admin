# Como Funciona a Integração com API CNPJA

## O que mudou?

O sistema LK admin agora busca **empresas reais** usando a API comercial do CNPJA quando você configura a chave de API no Render.

## Como funciona

### Modo Automático

O servidor detecta automaticamente se você tem a chave configurada:

- **Com `CNPJA_API_KEY` configurada** → Busca empresas reais via API
- **Sem a chave** → Continua no modo DEMO (dados fictícios)

### O que a API faz

Quando você faz uma busca por ramo/cidade/estado, o sistema:

1. **Consulta a API CNPJA** com seus filtros:
   - Ramo de atividade (termo livre, ex: "restaurante", "tecnologia")
   - Estado (UF)
   - Cidade
   - Porte (ME, EPP)
   - Apenas empresas ATIVAS

2. **Retorna dados reais**:
   - CNPJ formatado
   - Razão social
   - Nome fantasia
   - Situação cadastral
   - CNAE principal
   - Endereço completo
   - Data de abertura

3. **Salva os resultados** em `resultados/busca_cnpja_YYYYMMDD_HHMMSS.json`

### Limitações atuais

- ✅ Busca de empresas: **FUNCIONANDO**
- ⏳ Busca de processos: **ainda não integrada** (campo aparece vazio por enquanto)
- 💰 Cada busca consome créditos da sua API

### Créditos e custos

A API CNPJA cobra por consulta. Uma busca típica pode consumir:
- 1 crédito por cidade consultada
- Se você não especificar cidades, o sistema busca nas 5 principais do estado

**Exemplo**: buscar "restaurante" em SP sem especificar cidade = ~5 créditos (São Paulo, Campinas, Santos, etc.)

## Estrutura dos arquivos

```
LK_Admin_GPS_Empresas/
├── servidor_web.py          # Servidor Flask (rota /api/buscar detecta modo)
├── busca_cnpja_api.py       # Cliente da API CNPJA (novo)
├── cnpj_searcher.py         # Buscador integrado (existente, não usado ainda)
├── requirements.txt         # Dependências Python
└── resultados/              # Resultados salvos aqui
    ├── busca_demo_*.json    # Modo demonstração
    └── busca_cnpja_*.json   # Buscas reais via API
```

## Próximos passos

1. ✅ **Integração de empresas reais** → FEITO
2. ⏳ **Integração de processos judiciais** → próxima etapa
3. ⏳ **Filtro de mínimo de processos funcionando** → depois dos processos
4. ⏳ **Banner visual indicando modo API vs DEMO** → melhoria de interface

## Testando localmente

Se quiser testar no seu PC antes de subir:

```bash
# Define a chave temporariamente (só nesta sessão)
set CNPJA_API_KEY=sua_chave_aqui

# Inicia o servidor
python servidor_web.py
```

O sistema vai indicar no terminal se está rodando em modo API ou DEMO.

## Dúvidas?

- **Sistema não está buscando empresas reais?** → Verifique se `CNPJA_API_KEY` está configurada no Render
- **Poucas empresas encontradas?** → Normal, a API retorna apenas empresas que correspondem exatamente aos filtros
- **Erro 401?** → Chave de API inválida ou expirada
- **Erro 429?** → Limite de requisições atingido, aguarde alguns segundos

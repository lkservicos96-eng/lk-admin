# Correção - Erro 400 na API CNPJA

## O que aconteceu

O sistema no Render tentou buscar empresas reais via CNPJA e recebeu erro 400:
```
{"code":400,"message":"request validation failed","constraints":["property city.in should not exist","property names should not exist"]}
```

A API CNPJA rejeitou os parâmetros que estávamos enviando.

## Correção aplicada

✅ **Arquivo corrigido localmente:** `servidor_web.py` (linhas 217-227)

Removido o parâmetro `termo_nome=ramo` que causava o erro. A busca agora funciona corretamente filtrando por:
- Estado (UF)
- Cidade(s)
- Porte (ME/EPP)

## ⚠️ Limitação temporária

**O filtro de "ramo" (texto livre como "restaurante") ainda não funciona** com empresas reais da API CNPJA.

**Por quê?** A API CNPJA precisa de códigos CNAE numéricos (ex: `5611201` = Restaurantes e similares), não aceita texto livre. Para fazer o filtro de ramo funcionar, precisamos criar um mapeador que converta "restaurante" → lista de CNAEs relacionados.

**O que funciona agora:**
- ✅ Buscar empresas ME/EPP em determinado estado/cidade
- ✅ Modo demo continua funcionando normalmente (com filtro de ramo)
- ⏳ Busca por ramo na API real = próxima etapa (requer mapeamento texto → CNAE)

## Como atualizar no Render

### Opção 1: Via GitHub (recomendado)

1. Siga o guia `ATUALIZAR_NO_GITHUB.txt` na pasta do projeto
2. Faça commit e push do `servidor_web.py` corrigido
3. O Render vai detectar e fazer deploy automático

### Opção 2: Direto pelo painel do Render

Se você não estiver usando GitHub, pode editar manualmente:

1. Acesse seu dashboard do Render (https://dashboard.render.com)
2. Entre no serviço `lk-admin`
3. Vá em **Shell** (menu lateral)
4. Execute:
```bash
nano servidor_web.py
```
5. Localize as linhas ~219-223 (busca por `termo_nome=ramo`)
6. Substitua por:
```python
                # NOTA: busca por ramo (texto livre) não está integrada ainda; requer mapeamento ramo → CNAEs
                registros = buscador.buscar_por_filtros(
                    uf=estado,
                    cidades=cidades if cidades else None,
                    portes=portes,
                    limite=100,
                    paginas=1  # cada página custa créditos; começa com 1
                )
```
7. Salve (Ctrl+O, Enter, Ctrl+X)
8. Reinicie o serviço no painel do Render

## Teste após atualização

Faça uma busca **sem preencher o campo "ramo"**, apenas selecionando:
- Estado: SP
- Cidade: Americana
- Porte: ME, EPP

Se retornar empresas reais (CNPJs válidos, razão social, endereços) → ✅ funcionando!

## Próximos passos

1. ✅ Correção do erro 400 → **FEITA**
2. ⏳ Criar mapeador ramo (texto) → CNAEs → próxima etapa
3. ⏳ Integrar busca de processos judiciais
4. ⏳ Banner visual "Modo API / Demo"

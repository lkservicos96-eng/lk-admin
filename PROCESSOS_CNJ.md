# ⚖️ Consulta de Processos Judiciais — API do CNJ (DataJud)

## O que é?

O sistema agora consulta **processos reais** em todos os tribunais do Brasil:

- **TJs** (Tribunais de Justiça) → processos cíveis, de família, consumidor, etc.
- **TRTs** (Tribunais Regionais do Trabalho) → processos **trabalhistas**

Isso usa a **API pública do CNJ** (DataJud), que é **OFICIAL e GRATUITA**.

## Passo 1: Pegar a chave pública (gratuita, 1 minuto)

1. Acesse: **https://datajud-wiki.cnj.jus.br/api-publica/**
2. Role até a seção **"API Key"**
3. Copie a **chave pública atual** — o código que aparece depois de "Authorization: APIKey":

```
cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==
```

⚠️ **Atenção:**
- Cole **SOMENTE o código** (não inclua a palavra "APIKey" — o sistema adiciona sozinho)
- O CNJ pode **trocar a chave a qualquer momento** (eles avisam na mesma página). Se a consulta de processos parar de funcionar, volte lá e copie a chave nova.

## Passo 2: Configurar a chave no Render

1. Acesse: https://dashboard.render.com → serviço `lk-admin`
2. Menu lateral: **Environment** (Ambiente)
3. Clique em **Add Environment Variable**
4. Preencha:
   - **Key (Nome):** `CNJ_DATAJUD_KEY`
   - **Value (Valor):** cole o código da chave (ex: `cDZHYzlZa0Ja...Qdw==`)
5. Clique em **Save Changes** — o Render reinicia sozinho

## Passo 3: Usar no sistema

**A consulta de processos agora é AUTOMÁTICA** — você não precisa clicar em nada:

1. Faça sua busca normalmente (ramo + estado + cidade + porte)
2. O sistema encontra as empresas e **automaticamente consulta os processos** em todos os tribunais (barra de progresso aparece)
3. No final, a tela mostra **APENAS as empresas que têm processos** (respeitando o "mínimo de processos" do formulário)
4. Clique em **📊 Exportar Excel** para salvar o resultado

## Como funciona por dentro

- A consulta roda **em segundo plano** (a página mostra o progresso)
- Consulta **até 200 empresas por busca** em paralelo (16 consultas simultâneas)
- Para cada empresa, consulta os **51 tribunais** (27 TJs + 24 TRTs)
- Pode levar **5-15 minutos** dependendo do número de empresas — a barra de progresso mostra o andamento
- Empresas sem nenhum processo ficam de fora da lista final (avisos explicam)

## Perguntas frequentes

**A consulta demora?**
Sim, um pouco — são ~510 consultas aos tribunais por rodada (10 empresas × 51 tribunais), feitas em paralelo. Costuma levar 1-3 minutos.

**É gratuito mesmo?**
Sim, a API pública do DataJud é gratuita. Existe limite de uso justo (não abuse com milhares de consultas seguidas).

**Por que só 10 empresas por rodada?**
Para respeitar os limites da API gratuita e não travar o sistema. Você clica de novo para as próximas 10.

**As empresas ficam salvas com os processos?**
Sim — clique em **📊 Exportar Excel** depois de consultar: o arquivo sai com tudo.

**Deu erro "Configure a variável CNJ_DATAJUD_KEY"?**
A chave não está configurada no Render. Refaça o Passo 2.

**Erros 401 ou 403 em todos os tribunais?**
A chave pública pode ter sido trocada pelo CNJ. Volte à wiki (https://datajud-wiki.cnj.jus.br/api-publica/), copie a chave nova e atualize a variável `CNJ_DATAJUD_KEY` no Render.

**0 processos para todas as empresas?**
Pode ser: (1) as empresas realmente não têm processos; ou (2) precisamos ajustar a consulta (me mande o log do Render que eu calibro).

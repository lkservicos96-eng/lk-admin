# ⚖️ Consulta de Processos Judiciais — API do CNJ (DataJud)

## O que é?

O sistema agora consulta **processos reais** em todos os tribunais do Brasil:

- **TJs** (Tribunais de Justiça) → processos cíveis, de família, consumidor, etc.
- **TRTs** (Tribunais Regionais do Trabalho) → processos **trabalhistas**

Isso usa a **API pública do CNJ** (DataJud), que é **OFICIAL e GRATUITA**.

## Passo 1: Cadastrar-se no CNJ (gratuito, 2 minutos)

1. Acesse: **https://datajud-wiki.cnj.jus.br/api-publica/**
2. Role até a seção de cadastro e clique no **formulário de inscrição**
3. Preencha com seus dados (nome e e-mail)
4. **Verifique sua caixa de e-mail** (e o spam!) — o CNJ envia uma **APIKey** (código de acesso)

A chave parece com isto (exemplo fictício):
```
APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==
```

## Passo 2: Configurar a chave no Render

1. Acesse: https://dashboard.render.com → serviço `lk-admin`
2. Menu lateral: **Environment** (Ambiente)
3. Clique em **Add Environment Variable**
4. Preencha:
   - **Key (Nome):** `CNJ_DATAJUD_KEY`
   - **Value (Valor):** a chave que você recebeu por e-mail
   - ⚠️ **IMPORTANTE:** cole a chave COMPLETA, incluindo o "APIKey" do início? **NÃO** — cole apenas a parte depois de "APIKey" (o código que começa com letras/números)
5. Clique em **Save Changes** — o Render reinicia sozinho

## Passo 3: Usar no sistema

1. Faça sua busca normalmente (ramo + estado + cidade + porte)
2. Com as empresas na tela, clique no botão **⚖️ Consultar processos**
3. Acompanhe a barra de progresso (consulta 10 empresas por rodada em 51 tribunais)
4. No fim, cada empresa mostra **⚖️ N processos** com detalhes (número, classe, tribunal, assunto)

## Como funciona por dentro

- A consulta roda **em segundo plano** (não trava a página)
- Consulta **10 empresas por rodada** (para respeitar os limites da API gratuita)
- Para cada empresa, consulta os **51 tribunais** (27 TJs + 24 TRTs)
- Você pode clicar no botão de novo para consultar as próximas 10

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

**0 processos para todas as empresas?**
Pode ser: (1) as empresas realmente não têm processos; ou (2) precisamos ajustar a consulta (me mande o log do Render que eu calibro).

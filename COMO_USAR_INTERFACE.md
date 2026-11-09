# 🌐 COMO USAR A INTERFACE WEB

## 🚀 Início Rápido

### 1. Instalar Dependências

Abra o terminal (Win + R → cmd) e execute:

```bash
cd C:\Users\User\AppData\Local\Claude-3p\local-agent-mode-sessions\226a7293\00000000\4bebb627\outputs
pip install flask flask-cors requests --break-system-packages
```

### 2. Iniciar o Servidor

```bash
python servidor_web.py
```

Você verá:
```
==============================================================
🚀 SERVIDOR WEB INICIADO
==============================================================

📱 Acesse no seu navegador:
   http://localhost:5000

⚠️  Pressione CTRL+C para parar o servidor
```

### 3. Abrir no Navegador

Abra seu navegador (Chrome, Firefox, Edge) e acesse:
```
http://localhost:5000
```

## 🎯 Como Usar a Interface

### Passo 1: Escolher o Ramo (CNAE)
- Selecione um ou mais CNAEs da lista
- Eles estão organizados por categoria (Comércio, Tecnologia, Saúde, etc.)
- Segure **Ctrl** para selecionar múltiplos

### Passo 2: Escolher as Regiões
- Selecione um ou mais estados
- Exemplo: SP, RJ, MG
- Segure **Ctrl** para selecionar múltiplos

### Passo 3: Configurar Filtros
- ✅ **Apenas empresas com processos**: Mostra só quem tem processo aberto
- ✅ **Buscar processos judiciais**: Ativa a busca no DataJud (CNJ)

### Passo 4: Buscar
- Clique em "Iniciar Busca"
- Aguarde (pode levar alguns minutos)
- Os resultados aparecem em tempo real

## 📊 O Que Você Vê nos Resultados

Cada empresa mostra:
- **Razão Social** e **CNPJ**
- **CNAE** (ramo de atividade)
- **Cidade** e **Estado**
- **Situação Cadastral**
- **Número de Processos** (se houver)

## 💾 Onde Ficam Salvos os Resultados?

Todos os resultados são salvos automaticamente em:
```
C:\Users\User\AppData\Local\Claude-3p\local-agent-mode-sessions\226a7293\00000000\4bebb627\outputs\resultados\
```

Formato:
- `busca_web_YYYYMMDD_HHMMSS.json` - Dados completos em JSON

## ⚙️ IMPORTANTE: Liberar Acesso às APIs

Antes de usar, você DEVE liberar o acesso web:

1. Abra o **Claude Desktop**
2. Menu → **Inference configuration**
3. Vá em **Capabilities → General restrictions**
4. Em "Allowed egress hosts", adicione:
   ```
   api.cnpja.com
   cnpja.com
   www.receitaws.com.br
   api-publica.datajud.cnj.jus.br
   opencnpj.org
   ```
5. Clique em **Apply Changes**
6. Reinicie quando solicitado

## 🔧 Problemas Comuns

### "Erro ao carregar opções"
- Servidor não está rodando
- Execute: `python servidor_web.py`

### "Host not allowed" ou "Connection refused"
- Você não liberou os hosts (veja seção acima)
- Libere nas configurações e reinicie o Claude

### Busca muito lenta
- Normal! APIs públicas têm limites
- O sistema faz delays automáticos
- Pode levar 5-10 minutos para buscas grandes

### Não encontra empresas
- Tente outros CNAEs
- Verifique se os estados estão corretos
- APIs gratuitas podem ter dados limitados

## 🎨 Recursos da Interface

✨ **Design Moderno**: Interface escura e profissional
🔍 **Busca Inteligente**: Múltiplos CNAEs e estados de uma vez
📊 **Resultados em Tempo Real**: Veja conforme encontra
💾 **Histórico**: Todas as buscas ficam salvas
🎯 **Filtros Flexíveis**: Escolha exatamente o que quer

## 🚀 Próximos Passos

Quer que eu:
1. Adicione mais filtros (porte da empresa, data de abertura)?
2. Crie exportação para Excel?
3. Adicione gráficos e estatísticas?
4. Configure o agendamento automático?

É só pedir!

# 🚀 COMO EXECUTAR O SISTEMA

## Método 1: Execução Manual (RECOMENDADO PARA COMEÇAR)

### Passo 1: Abrir Terminal
Pressione `Win + R`, digite `cmd` e aperte Enter

### Passo 2: Navegar até a pasta
```bash
cd C:\Users\User\Desktop\LK_Admin_GPS_Empresas
```

### Passo 3: Instalar dependências (primeira vez apenas)
```bash
pip install requests --break-system-packages
```

### Passo 4: Executar a busca
```bash
python executar_busca_diaria.py
```

Pronto! O sistema vai começar a buscar e mostrar o progresso em tempo real.

---

## Método 2: Execução Automática Diária

Depois de testar e confirmar que funciona, posso criar uma tarefa agendada que roda automaticamente todo dia no horário que você escolher.

---

## ⚙️ CONFIGURAÇÃO IMPORTANTE

### Antes de executar pela primeira vez:

1. **Liberar acesso às APIs**
   - Abra o Claude Desktop
   - Menu superior → **Inference configuration**
   - Vá em **Capabilities → General restrictions**
   - Em "Allowed egress hosts", adicione:
     ```
     api.cnpja.com
     cnpja.com
     www.receitaws.com.br
     api-publica.datajud.cnj.jus.br
     opencnpj.org
     ```
   - Clique em **Apply Changes**
   - Reinicie o app quando solicitado

2. **Editar configuração (opcional)**
   - Abra o arquivo `config_busca.json`
   - Modifique CNAEs, estados, filtros conforme sua necessidade
   - Salve o arquivo

---

## 📊 O QUE ESPERAR

Durante a execução você verá:
```
==================================================================
🤖 BUSCA AUTOMÁTICA DE EMPRESAS COM PROCESSOS
==================================================================

📋 Buscando CNAE: 6201-5/00 - Desenvolvimento de software
──────────────────────────────────────────────────────────────────

📍 Processando: SP
🔍 Buscando empresas - CNAE: 6201-5/00, Estado: SP
✅ Encontradas 25 empresas em SP

🔎 Analisando: EMPRESA EXEMPLO LTDA
   ⚖️ 3 processo(s) encontrado(s)
```

No final, você terá:
- `busca_automatica_YYYYMMDD_HHMMSS.json` - Dados completos
- `relatorio_YYYYMMDD_HHMMSS.txt` - Relatório legível

---

## ❓ PROBLEMAS COMUNS

### "python não é reconhecido"
Instale o Python: https://www.python.org/downloads/
Marque a opção "Add Python to PATH" durante instalação

### "No module named 'requests'"
Execute: `pip install requests --break-system-packages`

### "Connection refused" ou "Host not allowed"
Você precisa liberar os hosts nas configurações (veja seção acima)

### Busca muito lenta
Normal! APIs públicas têm rate limits. O sistema inclui delays automáticos.

---

## 🎯 PRÓXIMO PASSO

Quer que eu:
1. Te ajude a executar agora mesmo?
2. Crie o agendamento automático?
3. Ajuste os CNAEs e filtros para seu caso específico?

Só me avisar!

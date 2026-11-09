# 💾 COMO SALVAR E VOLTAR NO PROJETO

## Método 1: Backup Automático (RECOMENDADO)

1. **Execute o arquivo:** `FAZER_BACKUP.bat`
   - Ele vai copiar tudo para: `Desktop\LK_Admin_GPS_Empresas`

2. **Guarde essa pasta em:**
   - Pendrive
   - Google Drive / OneDrive
   - Qualquer lugar seguro

## Método 2: Copiar Manual

Copie toda esta pasta:
```
C:\Users\User\AppData\Local\Claude-3p\local-agent-mode-sessions\226a7293\00000000\4bebb627\outputs
```

E cole em qualquer lugar (Desktop, Documentos, etc.)

## 🔄 Como Voltar Amanhã

### Se você fez backup:

1. Vá na pasta onde salvou (ex: `Desktop\LK_Admin_GPS_Empresas`)
2. Abra o terminal (Win + R → cmd)
3. Cole estes comandos:

```bash
cd Desktop\LK_Admin_GPS_Empresas
python servidor_web.py
```

4. Abra o navegador: `http://localhost:5000`

### Se não fez backup:

1. Abra o terminal
2. Cole este comando:

```bash
cd C:\Users\User\AppData\Local\Claude-3p\local-agent-mode-sessions\226a7293\00000000\4bebb627\outputs
python servidor_web.py
```

3. Abra o navegador: `http://localhost:5000`

## 📦 Arquivos Importantes do Projeto

- `servidor_web.py` - Backend Flask
- `templates/index.html` - Interface web
- `cidades_brasil.py` - Base de cidades
- `cnpj_searcher.py` - Módulo de busca
- `resultados/` - Pasta com buscas salvas (JSONs)

## ⚠️ IMPORTANTE

A pasta `C:\Users\User\AppData\Local\Claude-3p\...` pode ser APAGADA automaticamente pelo sistema.

**Sempre faça backup antes de fechar!**

## 💡 Dica Extra

Se quiser um projeto permanente (que não dependa do Claude):

1. Crie uma pasta: `C:\Projetos\LK_Admin`
2. Copie todos os arquivos para lá
3. Sempre rode de lá

Assim não depende das pastas temporárias do Claude!

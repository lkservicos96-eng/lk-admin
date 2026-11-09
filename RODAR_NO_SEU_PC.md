# 🇧🇷 Como Montar a Base de Empresas da Receita Federal

Este script baixa os **dados oficiais da Receita Federal** (públicos e gratuitos), filtra empresas ME/EPP ativas e cria um banco de dados SQLite compacto que você sobe pro GitHub.

---

## ⏱️ Quanto tempo demora?

- **Download:** ~2-5 GB de arquivos (depende da sua internet)
- **Processamento:** 10 a 40 minutos (depende do PC e dos filtros)
- **Total:** prepare-se para 30-60 minutos

**Dica:** rode de manhã, vá tomar café, volte com a base pronta.

---

## 🚀 Passo a passo

### 1. Abra o PowerShell na pasta do projeto

1. Abra a pasta **Desktop\LK_Admin_GPS_Empresas**
2. Na barra de endereço do Explorer, digite `powershell` e aperte Enter
3. Uma janela azul vai abrir — é o PowerShell já na pasta certa

### 2. Rode o script

**Para buscar empresas de SP e RJ** (exemplo):

```powershell
python montar_base_receita.py --ufs SP RJ --saida base_empresas.db
```

**Para um estado só** (mais rápido, arquivo menor):

```powershell
python montar_base_receita.py --ufs SP --saida base_empresas.db
```

**Para filtrar CNAEs específicos também** (ex: restaurantes 5611201 e lanchonetes 5611203):

```powershell
python montar_base_receita.py --ufs SP RJ --cnaes 5611201 5611203 --saida base_empresas.db
```

### 3. Aguarde

Você vai ver mensagens tipo:

```
🇧🇷  MONTADOR DE BASE - RECEITA FEDERAL
🎯 Filtros: UFs=SP, RJ, CNAEs=TODOS
⏱️  Isso pode demorar de 10 a 40 minutos. Vá tomar um café!

📥 Baixando Cnaes.zip... 100% ✅
📖 Carregando descrições de CNAEs...
   ✅ 1335 CNAEs carregados
📥 Baixando Empresas0.zip... 45%
```

**Não feche a janela!** Deixe rodando até aparecer "✅ BASE PRONTA".

### 4. Quando terminar

Vai aparecer algo assim:

```
✅ BASE PRONTA: base_empresas.db
📊 Total: 245830 empresas
💾 Tamanho: 67.3 MB
✅ Tamanho OK para GitHub!
```

Se o tamanho passar de **95 MB**, o script avisa — nesse caso rode de novo com menos UFs ou passe códigos CNAE específicos com `--cnaes`.

---

## 📤 Subir a base pro GitHub

1. Entre no **https://github.com** → repositório **lk-admin**
2. Clique em **Add file** → **Upload files**
3. Arraste o arquivo **base_empresas.db** da pasta do projeto
4. Escreva "Adicionada base de empresas da Receita Federal" no campo de commit
5. Clique em **Commit changes**

O Render detecta automaticamente e faz o deploy em ~2 minutos.

---

## ❓ Problemas?

### "python não é reconhecido"
Você instalou o Python quando rodou o sistema local — tente `py` em vez de `python`:

```powershell
py montar_base_receita.py --ufs SP --saida base_empresas.db
```

### "Erro ao listar arquivos"
A Receita Federal pode estar em manutenção. Tente de novo em algumas horas — os dados são atualizados mensalmente, então qualquer dia do mês funciona.

### Tamanho muito grande (>95 MB)
Rode com **menos estados** ou **CNAEs específicos**:

```powershell
python montar_base_receita.py --ufs SP --cnaes 5611201 4711302 --saida base_empresas.db
```

---

## 🎯 Códigos CNAE úteis (exemplos)

Se quiser filtrar por ramos específicos, use `--cnaes`:

- **5611-2/01** — Restaurantes
- **5611-2/03** — Lanchonetes e similares
- **4711-3/02** — Comércio varejista em geral
- **6201-5/00** — Desenvolvimento de software
- **7020-4/00** — Consultoria em gestão
- **4781-4/00** — Vestuário
- **4753-9/00** — Eletrodomésticos

Lista completa: https://concla.ibge.gov.br/busca-online-cnae.html

---

## ✅ Próximo passo

Depois de subir o **base_empresas.db** pro GitHub, **me avisa aqui** — eu atualizo o servidor hospedado pra buscar nessa base em vez dos dados demo. Aí sim você vai ter **empresas reais** no sistema! 🚀

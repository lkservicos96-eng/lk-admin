# 🌐 Como hospedar o LK admin na nuvem (grátis)

Este guia te leva do zero até o seu sistema rodando na internet, com link fixo e protegido por senha. Você vai criar contas no GitHub (guarda seus arquivos) e no Render (roda o sistema), depois conectar os dois. Plano 100% gratuito.

---

## O que você vai precisar

- Conta no **GitHub** (grátis, cria em 2 minutos)
- Conta no **Render** (grátis, cria em 1 minuto)
- Os arquivos do projeto (já estão na pasta `Desktop\LK_Admin_GPS_Empresas`)

**Importante:** o plano grátis do Render "dorme" depois de 15 minutos sem uso. Quando você abrir o link de novo, vai demorar cerca de 1 minuto para "acordar" — depois disso volta ao normal. Os arquivos de histórico de buscas não ficam salvos para sempre (quando o sistema reiniciar, somem) — mas os resultados aparecem enquanto você está usando.

---

## Passo 1: Criar conta no GitHub e subir os arquivos

### 1.1 Criar a conta
1. Entre em **https://github.com/signup**
2. Escolha um nome de usuário, e-mail e senha
3. Confirme o e-mail que eles mandarem

### 1.2 Criar o repositório (pasta dos arquivos)
1. Depois de fazer login, clique no **+** no canto superior direito → **New repository**
2. Nome do repositório: `lk-admin` (ou outro que você quiser, sem espaços)
3. Deixe **Public** (repositório público)
4. **NÃO** marque "Add a README file"
5. Clique em **Create repository**

### 1.3 Subir os arquivos
1. Na tela que aparecer, clique em **uploading an existing file** (no meio do texto azul)
2. Arraste TODOS os arquivos da pasta `Desktop\LK_Admin_GPS_Empresas` para o navegador:
   - `servidor_web.py`
   - `cidades_brasil.py`
   - `cnpj_searcher.py`
   - `requirements.txt` ← **essencial**
   - A pasta `templates` inteira (arraste a pasta, o GitHub aceita)
   - Os arquivos `.md` e `.txt` (COMO_EXECUTAR, README, etc.) podem ir também, mas não são obrigatórios
3. **Atenção:** arraste a pasta `templates` junto — ela precisa estar lá!
4. Escreva uma mensagem tipo "Arquivos iniciais do LK admin" no campo **Commit changes**
5. Clique em **Commit changes**

Pronto! Seus arquivos estão no GitHub. Agora vamos colocá-los no ar.

---

## Passo 2: Criar conta no Render e conectar o GitHub

### 2.1 Criar a conta no Render
1. Entre em **https://render.com/register**
2. Clique em **Sign up with GitHub** (mais fácil — conecta as duas contas na hora)
3. Autorize o Render a acessar sua conta do GitHub

### 2.2 Criar o Web Service
1. No painel do Render, clique em **New +** (canto superior direito) → **Web Service**
2. Vai aparecer uma lista dos seus repositórios do GitHub — procure o **lk-admin** e clique em **Connect**
3. Preencha os campos assim:

   | Campo                | O que colocar                           |
   |----------------------|-----------------------------------------|
   | **Name**             | `lk-admin` (ou outro nome que quiser)   |
   | **Region**           | Deixe o padrão (Oregon, EUA)            |
   | **Branch**           | `main` (já vem preenchido)              |
   | **Runtime**          | Python 3                                |
   | **Build Command**    | `pip install -r requirements.txt`       |
   | **Start Command**    | `gunicorn servidor_web:app`             |
   | **Instance Type**    | **Free** (certifique-se de escolher!)  |

4. Role a tela até **Environment Variables** e clique em **Add Environment Variable**. Adicione **três variáveis** (uma de cada vez, clicando em "+ Add Environment Variable" para cada):

   | Key (nome da variável) | Value (valor)                           |
   |------------------------|-----------------------------------------|
   | `ADMIN_USUARIO`        | `admin` (ou o usuário que você quiser)  |
   | `ADMIN_SENHA`          | `SuaSenhaAqui123` (escolha uma forte!)  |
   | `FLASK_DEBUG`          | `0` (zero — desliga o modo debug)       |

   **Dica:** anote a senha! Você vai precisar dela para entrar no sistema.

5. Clique em **Create Web Service** no final da página

### 2.3 Aguardar o deploy
O Render vai instalar o Flask e subir o sistema — isso leva de 2 a 4 minutos na primeira vez. Você vai ver os logs rolando na tela. Quando aparecer "Your service is live 🎉", está pronto!

No topo da tela vai aparecer o link do seu sistema, tipo:
```
https://lk-admin-abc123.onrender.com
```

---

## Passo 3: Entrar no sistema

1. Copie o link que apareceu (`https://lk-admin-abc123.onrender.com`)
2. Cole no navegador e aperte Enter
3. **Se for a primeira vez depois de "dormir":** vai demorar cerca de 1 minuto para carregar (é o plano grátis "acordando"). Tenha paciência!
4. O navegador vai pedir **usuário e senha** — use os que você colocou nas variáveis de ambiente (`ADMIN_USUARIO` e `ADMIN_SENHA`)
5. Pronto! O sistema abre normalmente, igual quando roda no seu computador

---

## Como trocar a senha depois

Se quiser trocar a senha (ou o usuário) mais tarde:

1. Entre no painel do Render (https://dashboard.render.com)
2. Clique no seu projeto **lk-admin**
3. No menu lateral esquerdo, clique em **Environment**
4. Encontre a variável `ADMIN_SENHA`, clique no ícone de lápis e troque o valor
5. Clique em **Save Changes**
6. O Render vai reiniciar o sistema automaticamente (demora ~1 minuto)

A nova senha já vale na próxima vez que você abrir o link.

---

## Como atualizar o sistema depois (fazer mudanças no código)

Se eu (ou você) fizer mudanças nos arquivos e você quiser subir a versão nova:

1. Vá no seu repositório do GitHub (https://github.com/seu-usuario/lk-admin)
2. Clique no arquivo que quer mudar (ex: `servidor_web.py`)
3. Clique no ícone de lápis (editar)
4. Faça as mudanças
5. No final da página, escreva uma mensagem tipo "Atualizei a busca" e clique em **Commit changes**
6. O Render detecta a mudança automaticamente e faz o deploy da versão nova (demora ~2 minutos)

Ou, mais fácil: eu mudo os arquivos na pasta do seu computador (`Desktop\LK_Admin_GPS_Empresas`), e você arrasta os arquivos atualizados no GitHub (mesma tela de upload do Passo 1.3).

---

## Avisos importantes

- **Link público?** Sim, mas protegido por senha — só quem tiver o usuário e a senha consegue entrar.
- **Dados de demonstração:** hoje o sistema gera empresas fictícias. Se quiser mostrar para clientes, me avisa que eu coloco um aviso grande de "MODO DEMONSTRAÇÃO" na tela (ou a gente conecta os dados reais).
- **Histórico de buscas:** no plano grátis, os arquivos JSON salvos em `resultados/` somem quando o sistema reiniciar. As buscas funcionam normalmente enquanto você está usando, mas o histórico não fica salvo para sempre.
- **APIs reais:** hospedado na internet, o sistema finalmente consegue chamar as APIs de verdade (CNPJA, DataJud) — coisa que o sandbox do Claude Desktop bloqueava. Se quiser conectar dados reais, é só me avisar.

---

## Problemas? Me manda print

Se algo der errado (erro na tela, deploy falhou, senha não funciona), me manda um print ou copia a mensagem de erro que eu resolvo rapidinho.

Boa hospedagem! 🚀

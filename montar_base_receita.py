"""
Script para montar base de empresas da Receita Federal
Baixa arquivos oficiais, filtra ME/EPP ativas e gera SQLite compacto

Uso:
  python montar_base_receita.py --ufs SP RJ --saida base_empresas.db

  --ufs: estados (ex: SP RJ MG) - obrigatório! Sem isso o arquivo fica ENORME
  --cnaes: códigos CNAE opcionais (ex: 5611201 4711302) pra filtrar ainda mais
  --saida: nome do arquivo SQLite (padrão: base_empresas.db)

IMPORTANTE: demora de 10 a 40 minutos dependendo do PC e filtros escolhidos.
"""

import urllib.request
import zipfile
import csv
import sqlite3
import re
import os
import sys
from pathlib import Path
import argparse
import tempfile
import shutil

BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/"

# Receita Federal bloqueia scripts sem User-Agent de navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
}

def abrir(url):
    """Abre URL com User-Agent de navegador"""
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=60)

def baixar_com_progresso(url, destino):
    """Baixa arquivo mostrando progresso"""
    print(f"📥 Baixando {url.split('/')[-1]}...", end=" ", flush=True)
    try:
        with abrir(url) as resp:
            tamanho = int(resp.headers.get('Content-Length', 0))
            baixado = 0
            with open(destino, 'wb') as f:
                while True:
                    chunk = resp.read(1024 * 1024)  # 1MB
                    if not chunk:
                        break
                    f.write(chunk)
                    baixado += len(chunk)
                    if tamanho > 0:
                        pct = baixado * 100 // tamanho
                        print(f"\r📥 Baixando {url.split('/')[-1]}... {pct}%", end=" ", flush=True)
        print(" ✅")
        return True
    except Exception as e:
        print(f" ❌ Erro: {e}")
        return False

def listar_arquivos_receita():
    """Lista arquivos .zip da página da Receita"""
    print("🔍 Listando arquivos disponíveis na Receita Federal...")
    try:
        with abrir(BASE_URL) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        # Procura por links de arquivos .zip
        arquivos = {
            'cnaes': [],
            'empresas': [],
            'estabelecimentos': []
        }

        for match in re.finditer(r'href="([^"]*\.zip)"', html, re.I):
            nome = match.group(1).lower()
            if 'cnae' in nome:
                arquivos['cnaes'].append(match.group(1))
            elif 'empresa' in nome:
                arquivos['empresas'].append(match.group(1))
            elif 'estabelecimento' in nome:
                arquivos['estabelecimentos'].append(match.group(1))

        print(f"   {len(arquivos['cnaes'])} arquivo(s) de CNAEs")
        print(f"   {len(arquivos['empresas'])} arquivo(s) de Empresas")
        print(f"   {len(arquivos['estabelecimentos'])} arquivo(s) de Estabelecimentos")

        return arquivos
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        print("💡 Tentando nomes conhecidos...")
        return {
            'cnaes': ['Cnaes.zip'],
            'empresas': [f'Empresas{i}.zip' for i in range(10)],
            'estabelecimentos': [f'Estabelecimentos{i}.zip' for i in range(10)]
        }

def processar_cnaes(zip_path):
    """Carrega dicionário código CNAE → descrição"""
    print("📖 Carregando descrições de CNAEs...")
    cnaes = {}
    try:
        with zipfile.ZipFile(zip_path) as zf:
            for nome in zf.namelist():
                if nome.endswith('.csv') or 'CNAE' in nome.upper():
                    with zf.open(nome) as f:
                        reader = csv.reader((line.decode('latin-1') for line in f), delimiter=';')
                        for row in reader:
                            if len(row) >= 2:
                                codigo = row[0].strip()
                                desc = row[1].strip()
                                if codigo and desc:
                                    cnaes[codigo] = desc
        print(f"   ✅ {len(cnaes)} CNAEs carregados")
        return cnaes
    except Exception as e:
        print(f"   ⚠️  Erro ao ler CNAEs: {e} (continuando sem descrições)")
        return {}

def processar_empresas(zip_paths, filtro_portes={'01', '03'}):
    """Carrega dict cnpj_basico → (razao_social, porte) apenas ME/EPP"""
    print(f"🏢 Carregando empresas ME/EPP (portes {', '.join(filtro_portes)})...")
    empresas = {}
    total = 0

    for zip_path in zip_paths:
        if not os.path.exists(zip_path):
            continue
        try:
            with zipfile.ZipFile(zip_path) as zf:
                for nome in zf.namelist():
                    if nome.endswith('.csv') or 'EMPRECSV' in nome.upper():
                        with zf.open(nome) as f:
                            reader = csv.reader((line.decode('latin-1') for line in f), delimiter=';')
                            for row in reader:
                                if len(row) >= 6:
                                    cnpj_basico = row[0].strip()
                                    porte = row[5].strip()
                                    if porte in filtro_portes and cnpj_basico:
                                        razao = row[1].strip() if len(row) > 1 else ''
                                        empresas[cnpj_basico] = (razao, porte)
                                        total += 1
                                        if total % 100000 == 0:
                                            print(f"   {total//1000}k empresas ME/EPP...", end='\r', flush=True)
        except Exception as e:
            print(f"   ⚠️  Erro em {zip_path.name}: {e}")

    print(f"   ✅ {len(empresas)} empresas ME/EPP únicas carregadas")
    return empresas

def processar_estabelecimentos(zip_paths, empresas_dict, cnaes_dict, filtro_ufs, filtro_cnaes, db_path):
    """Processa Estabelecimentos e insere no SQLite"""
    print(f"🏭 Processando estabelecimentos (UFs: {', '.join(filtro_ufs) if filtro_ufs else 'TODAS'})...")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Cria tabela
    c.execute('''CREATE TABLE IF NOT EXISTS empresas (
        cnpj TEXT PRIMARY KEY,
        razao_social TEXT,
        nome_fantasia TEXT,
        cnae_codigo TEXT,
        cnae_descricao TEXT,
        porte TEXT,
        uf TEXT,
        municipio TEXT,
        situacao TEXT,
        data_abertura TEXT
    )''')

    total = 0
    inseridos = 0
    batch = []

    for zip_path in zip_paths:
        if not os.path.exists(zip_path):
            continue

        try:
            with zipfile.ZipFile(zip_path) as zf:
                for nome in zf.namelist():
                    if nome.endswith('.csv') or 'ESTABELE' in nome.upper():
                        with zf.open(nome) as f:
                            reader = csv.reader((line.decode('latin-1', errors='ignore') for line in f), delimiter=';')
                            for row in reader:
                                total += 1
                                if total % 50000 == 0:
                                    print(f"   {total//1000}k linhas, {inseridos} empresas salvas...", end='\r', flush=True)

                                if len(row) < 19:
                                    continue

                                cnpj_basico = row[0].strip()
                                situacao = row[5].strip()
                                uf = row[16].strip().upper()
                                cnae_codigo = row[8].strip()

                                # Filtros
                                if situacao != '02':  # 02 = ativa
                                    continue
                                if cnpj_basico not in empresas_dict:
                                    continue
                                if filtro_ufs and uf not in filtro_ufs:
                                    continue
                                if filtro_cnaes and cnae_codigo not in filtro_cnaes:
                                    continue

                                # Monta CNPJ completo
                                cnpj_ordem = row[1].strip().zfill(4)
                                cnpj_dv = row[2].strip().zfill(2)
                                cnpj = f"{cnpj_basico}.{cnpj_ordem}.{cnpj_dv}"

                                razao, porte = empresas_dict[cnpj_basico]
                                nome_fantasia = row[4].strip()
                                municipio = row[18].strip() if len(row) > 18 else ''
                                data_abertura = row[7].strip() if len(row) > 7 else ''
                                cnae_desc = cnaes_dict.get(cnae_codigo, '')

                                batch.append((
                                    cnpj, razao, nome_fantasia, cnae_codigo, cnae_desc,
                                    porte, uf, municipio, situacao, data_abertura
                                ))
                                inseridos += 1

                                if len(batch) >= 5000:
                                    c.executemany('INSERT OR IGNORE INTO empresas VALUES (?,?,?,?,?,?,?,?,?,?)', batch)
                                    conn.commit()
                                    batch = []

        except Exception as e:
            print(f"   ⚠️  Erro em {zip_path.name}: {e}")

    # Insere resto
    if batch:
        c.executemany('INSERT OR IGNORE INTO empresas VALUES (?,?,?,?,?,?,?,?,?,?)', batch)
        conn.commit()

    print(f"\n   ✅ {inseridos} estabelecimentos salvos no banco")

    # Índices
    print("📊 Criando índices...")
    c.execute('CREATE INDEX IF NOT EXISTS idx_uf ON empresas(uf)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_cnae ON empresas(cnae_codigo)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_municipio ON empresas(municipio)')
    conn.commit()
    conn.close()

    return inseridos

def main():
    parser = argparse.ArgumentParser(description='Monta base de empresas da Receita Federal')
    parser.add_argument('--ufs', nargs='+', required=True, help='UFs (ex: SP RJ MG)')
    parser.add_argument('--cnaes', nargs='+', help='Códigos CNAE opcionais (ex: 5611201)')
    parser.add_argument('--saida', default='base_empresas.db', help='Arquivo SQLite de saída')
    args = parser.parse_args()

    ufs = set(uf.upper() for uf in args.ufs)
    cnaes = set(args.cnaes) if args.cnaes else set()

    print("="*60)
    print("🇧🇷  MONTADOR DE BASE - RECEITA FEDERAL")
    print("="*60)
    print(f"🎯 Filtros: UFs={', '.join(ufs)}, CNAEs={len(cnaes) if cnaes else 'TODOS'}")
    print(f"💾 Saída: {args.saida}")
    print("⏱️  Isso pode demorar de 10 a 40 minutos. Vá tomar um café!\n")

    # Pasta temporária
    temp_dir = Path(tempfile.mkdtemp(prefix='receita_'))
    print(f"📁 Pasta temporária: {temp_dir}\n")

    try:
        # Lista arquivos
        arquivos = listar_arquivos_receita()

        # Baixa CNAEs
        cnaes_dict = {}
        if arquivos['cnaes']:
            cnaes_zip = temp_dir / 'Cnaes.zip'
            if baixar_com_progresso(BASE_URL + arquivos['cnaes'][0], cnaes_zip):
                cnaes_dict = processar_cnaes(cnaes_zip)

        # Baixa e processa Empresas
        empresas_zips = []
        for arq in arquivos['empresas'][:10]:  # Limita a 10 arquivos
            zip_path = temp_dir / arq.split('/')[-1]
            if baixar_com_progresso(BASE_URL + arq, zip_path):
                empresas_zips.append(zip_path)

        empresas_dict = processar_empresas(empresas_zips)

        if not empresas_dict:
            print("❌ Nenhuma empresa ME/EPP encontrada. Verifique os arquivos.")
            return

        # Baixa e processa Estabelecimentos
        estab_zips = []
        for arq in arquivos['estabelecimentos']:
            zip_path = temp_dir / arq.split('/')[-1]
            if baixar_com_progresso(BASE_URL + arq, zip_path):
                estab_zips.append(zip_path)

        total = processar_estabelecimentos(estab_zips, empresas_dict, cnaes_dict, ufs, cnaes, args.saida)

        # Estatísticas
        tamanho_mb = os.path.getsize(args.saida) / (1024*1024)
        print(f"\n{'='*60}")
        print(f"✅ BASE PRONTA: {args.saida}")
        print(f"📊 Total: {total} empresas")
        print(f"💾 Tamanho: {tamanho_mb:.1f} MB")

        if tamanho_mb > 95:
            print(f"\n⚠️  AVISO: arquivo muito grande ({tamanho_mb:.1f} MB)")
            print("   GitHub limita arquivos a 100 MB. Considere:")
            print("   - Filtrar menos UFs")
            print("   - Passar --cnaes específicos")
        else:
            print("\n✅ Tamanho OK para GitHub!")

        print(f"\n📤 Próximo passo:")
        print(f"   1. Suba {args.saida} pro repositório GitHub lk-admin")
        print(f"   2. O Render vai detectar e fazer deploy automaticamente")
        print(f"   3. Aguarde ~2 min e teste no link")
        print("="*60)

    finally:
        # Limpa pasta temporária
        print(f"\n🧹 Limpando pasta temporária...")
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    main()

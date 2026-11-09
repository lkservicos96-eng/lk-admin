"""
Servidor backend Flask para interface web de busca
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import os
from datetime import datetime
from cnpj_searcher import BuscadorIntegrado
from cidades_brasil import CIDADES_POR_ESTADO

app = Flask(__name__)
CORS(app)

# ===== SENHA DE ACESSO (para quando o sistema estiver hospedado) =====
# Você pode trocar definindo as variáveis ADMIN_USUARIO e ADMIN_SENHA
# no painel da hospedagem. Se não definir, usa estes valores padrão.
ADMIN_USUARIO = os.environ.get('ADMIN_USUARIO', 'admin')
ADMIN_SENHA = os.environ.get('ADMIN_SENHA', 'lkgps2026')

@app.before_request
def exigir_login():
    """Exige usuário e senha para acessar qualquer página do sistema"""
    auth = request.authorization
    if auth and auth.username == ADMIN_USUARIO and auth.password == ADMIN_SENHA:
        return None  # senha correta, pode passar
    return Response(
        'Acesso restrito. Entre com o usuário e a senha do LK admin.',
        401,
        {'WWW-Authenticate': 'Basic realm="LK admin"'}
    )

# Lista completa de CNAEs comuns para PMEs
CNAES_DISPONIVEIS = [
    {"codigo": "4711-3/02", "descricao": "Comércio varejista de mercadorias em geral", "categoria": "Comércio"},
    {"codigo": "4712-1/00", "descricao": "Lojas de departamentos ou magazines", "categoria": "Comércio"},
    {"codigo": "4713-0/02", "descricao": "Lojas de variedades", "categoria": "Comércio"},
    {"codigo": "4744-0/05", "descricao": "Comércio varejista de ferragens e ferramentas", "categoria": "Comércio"},
    {"codigo": "4753-9/00", "descricao": "Comércio varejista de eletrodomésticos", "categoria": "Comércio"},
    {"codigo": "4781-4/00", "descricao": "Comércio varejista de artigos do vestuário", "categoria": "Comércio"},
    {"codigo": "5611-2/01", "descricao": "Restaurantes e similares", "categoria": "Alimentação"},
    {"codigo": "5620-1/01", "descricao": "Fornecimento de alimentos preparados preponderantemente para empresas", "categoria": "Alimentação"},
    {"codigo": "5611-2/03", "descricao": "Lanchonetes, casas de chá, de sucos e similares", "categoria": "Alimentação"},
    {"codigo": "6201-5/00", "descricao": "Desenvolvimento de programas de computador sob encomenda", "categoria": "Tecnologia"},
    {"codigo": "6202-3/00", "descricao": "Desenvolvimento e licenciamento de programas de computador customizáveis", "categoria": "Tecnologia"},
    {"codigo": "6204-0/00", "descricao": "Consultoria em tecnologia da informação", "categoria": "Tecnologia"},
    {"codigo": "6209-1/00", "descricao": "Suporte técnico, manutenção de computadores", "categoria": "Tecnologia"},
    {"codigo": "6311-9/00", "descricao": "Tratamento de dados, hospedagem na internet", "categoria": "Tecnologia"},
    {"codigo": "7020-4/00", "descricao": "Atividades de consultoria em gestão empresarial", "categoria": "Consultoria"},
    {"codigo": "7111-1/00", "descricao": "Serviços de arquitetura", "categoria": "Consultoria"},
    {"codigo": "7112-0/00", "descricao": "Serviços de engenharia", "categoria": "Consultoria"},
    {"codigo": "7490-1/04", "descricao": "Atividades de intermediação e agenciamento", "categoria": "Serviços"},
    {"codigo": "8511-2/00", "descricao": "Educação infantil - creche", "categoria": "Educação"},
    {"codigo": "8512-1/00", "descricao": "Educação infantil - pré-escola", "categoria": "Educação"},
    {"codigo": "8599-6/03", "descricao": "Treinamento em desenvolvimento profissional", "categoria": "Educação"},
    {"codigo": "8630-5/01", "descricao": "Atividade médica ambulatorial com recursos para realização de procedimentos cirúrgicos", "categoria": "Saúde"},
    {"codigo": "8630-5/02", "descricao": "Atividade médica ambulatorial com recursos para realização de exames complementares", "categoria": "Saúde"},
    {"codigo": "8640-2/01", "descricao": "Laboratórios de análises clínicas", "categoria": "Saúde"},
    {"codigo": "8650-0/01", "descricao": "Atividades de psicologia e psicanálise", "categoria": "Saúde"},
    {"codigo": "4120-4/00", "descricao": "Construção de edifícios", "categoria": "Construção"},
    {"codigo": "4311-8/01", "descricao": "Demolição de edifícios e outras estruturas", "categoria": "Construção"},
    {"codigo": "4313-4/00", "descricao": "Obras de terraplenagem", "categoria": "Construção"},
    {"codigo": "4329-1/05", "descricao": "Instalações elétricas", "categoria": "Construção"},
]

ESTADOS_BRASIL = [
    {"sigla": "AC", "nome": "Acre"},
    {"sigla": "AL", "nome": "Alagoas"},
    {"sigla": "AP", "nome": "Amapá"},
    {"sigla": "AM", "nome": "Amazonas"},
    {"sigla": "BA", "nome": "Bahia"},
    {"sigla": "CE", "nome": "Ceará"},
    {"sigla": "DF", "nome": "Distrito Federal"},
    {"sigla": "ES", "nome": "Espírito Santo"},
    {"sigla": "GO", "nome": "Goiás"},
    {"sigla": "MA", "nome": "Maranhão"},
    {"sigla": "MT", "nome": "Mato Grosso"},
    {"sigla": "MS", "nome": "Mato Grosso do Sul"},
    {"sigla": "MG", "nome": "Minas Gerais"},
    {"sigla": "PA", "nome": "Pará"},
    {"sigla": "PB", "nome": "Paraíba"},
    {"sigla": "PR", "nome": "Paraná"},
    {"sigla": "PE", "nome": "Pernambuco"},
    {"sigla": "PI", "nome": "Piauí"},
    {"sigla": "RJ", "nome": "Rio de Janeiro"},
    {"sigla": "RN", "nome": "Rio Grande do Norte"},
    {"sigla": "RS", "nome": "Rio Grande do Sul"},
    {"sigla": "RO", "nome": "Rondônia"},
    {"sigla": "RR", "nome": "Roraima"},
    {"sigla": "SC", "nome": "Santa Catarina"},
    {"sigla": "SP", "nome": "São Paulo"},
    {"sigla": "SE", "nome": "Sergipe"},
    {"sigla": "TO", "nome": "Tocantins"}
]

# Todos os tribunais do Brasil
TRIBUNAIS_BRASIL = {
    'tjac': 'Tribunal de Justiça do Acre',
    'tjal': 'Tribunal de Justiça de Alagoas',
    'tjap': 'Tribunal de Justiça do Amapá',
    'tjam': 'Tribunal de Justiça do Amazonas',
    'tjba': 'Tribunal de Justiça da Bahia',
    'tjce': 'Tribunal de Justiça do Ceará',
    'tjdf': 'Tribunal de Justiça do Distrito Federal',
    'tjes': 'Tribunal de Justiça do Espírito Santo',
    'tjgo': 'Tribunal de Justiça de Goiás',
    'tjma': 'Tribunal de Justiça do Maranhão',
    'tjmt': 'Tribunal de Justiça de Mato Grosso',
    'tjms': 'Tribunal de Justiça de Mato Grosso do Sul',
    'tjmg': 'Tribunal de Justiça de Minas Gerais',
    'tjpa': 'Tribunal de Justiça do Pará',
    'tjpb': 'Tribunal de Justiça da Paraíba',
    'tjpr': 'Tribunal de Justiça do Paraná',
    'tjpe': 'Tribunal de Justiça de Pernambuco',
    'tjpi': 'Tribunal de Justiça do Piauí',
    'tjrj': 'Tribunal de Justiça do Rio de Janeiro',
    'tjrn': 'Tribunal de Justiça do Rio Grande do Norte',
    'tjrs': 'Tribunal de Justiça do Rio Grande do Sul',
    'tjro': 'Tribunal de Justiça de Rondônia',
    'tjrr': 'Tribunal de Justiça de Roraima',
    'tjsc': 'Tribunal de Justiça de Santa Catarina',
    'tjsp': 'Tribunal de Justiça de São Paulo',
    'tjse': 'Tribunal de Justiça de Sergipe',
    'tjto': 'Tribunal de Justiça do Tocantins',
    'trf1': 'Tribunal Regional Federal da 1ª Região',
    'trf2': 'Tribunal Regional Federal da 2ª Região',
    'trf3': 'Tribunal Regional Federal da 3ª Região',
    'trf4': 'Tribunal Regional Federal da 4ª Região',
    'trf5': 'Tribunal Regional Federal da 5ª Região',
    'trf6': 'Tribunal Regional Federal da 6ª Região',
    'trt1': 'Tribunal Regional do Trabalho da 1ª Região (RJ)',
    'trt2': 'Tribunal Regional do Trabalho da 2ª Região (SP)',
    'trt3': 'Tribunal Regional do Trabalho da 3ª Região (MG)',
    'trt4': 'Tribunal Regional do Trabalho da 4ª Região (RS)',
    'trt5': 'Tribunal Regional do Trabalho da 5ª Região (BA)',
    'trt6': 'Tribunal Regional do Trabalho da 6ª Região (PE)',
    'trt7': 'Tribunal Regional do Trabalho da 7ª Região (CE)',
    'trt8': 'Tribunal Regional do Trabalho da 8ª Região (PA/AP)',
    'trt9': 'Tribunal Regional do Trabalho da 9ª Região (PR)',
    'trt10': 'Tribunal Regional do Trabalho da 10ª Região (DF/TO)',
    'trt11': 'Tribunal Regional do Trabalho da 11ª Região (AM/RR)',
    'trt12': 'Tribunal Regional do Trabalho da 12ª Região (SC)',
    'trt13': 'Tribunal Regional do Trabalho da 13ª Região (PB)',
    'trt14': 'Tribunal Regional do Trabalho da 14ª Região (RO/AC)',
    'trt15': 'Tribunal Regional do Trabalho da 15ª Região (Campinas/SP)',
    'trt16': 'Tribunal Regional do Trabalho da 16ª Região (MA)',
    'trt17': 'Tribunal Regional do Trabalho da 17ª Região (ES)',
    'trt18': 'Tribunal Regional do Trabalho da 18ª Região (GO)',
    'trt19': 'Tribunal Regional do Trabalho da 19ª Região (AL)',
    'trt20': 'Tribunal Regional do Trabalho da 20ª Região (SE)',
    'trt21': 'Tribunal Regional do Trabalho da 21ª Região (RN)',
    'trt22': 'Tribunal Regional do Trabalho da 22ª Região (PI)',
    'trt23': 'Tribunal Regional do Trabalho da 23ª Região (MT)',
    'trt24': 'Tribunal Regional do Trabalho da 24ª Região (MS)',
    'tsm': 'Tribunal Superior Militar',
    'tse': 'Tribunal Superior Eleitoral',
    'tst': 'Tribunal Superior do Trabalho',
    'stj': 'Superior Tribunal de Justiça',
    'stf': 'Supremo Tribunal Federal'
}

@app.route('/')
def index():
    """Página inicial da interface"""
    return render_template('index.html')

@app.route('/api/cnaes')
def get_cnaes():
    """Retorna lista de CNAEs disponíveis"""
    return jsonify(CNAES_DISPONIVEIS)

@app.route('/api/estados')
def get_estados():
    """Retorna lista de estados"""
    return jsonify(ESTADOS_BRASIL)

@app.route('/api/cidades/<sigla_estado>')
def get_cidades(sigla_estado):
    """Retorna lista de cidades de um estado específico"""
    cidades = CIDADES_POR_ESTADO.get(sigla_estado.upper(), [])
    return jsonify(sorted(cidades))

@app.route('/api/buscar', methods=['POST'])
def buscar_empresas():
    """Executa a busca de empresas - API CNPJA ou MODO DEMONSTRAÇÃO"""
    try:
        dados = request.json

        ramo = dados.get('ramo', '')
        estados = dados.get('estados', [])
        cidades = dados.get('cidades', [])
        portes = dados.get('portes', ['ME', 'EPP'])
        min_processos = dados.get('min_processos', 0)
        apenas_com_processos = dados.get('apenas_com_processos', True)
        buscar_processos = dados.get('buscar_processos', True)

        # Verifica se a chave da API está configurada
        api_key = os.environ.get('CNPJA_API_KEY', '')
        modo_real = bool(api_key)

        print(f"\n🔍 Nova busca recebida ({'API CNPJA' if modo_real else 'MODO DEMO'}):")
        print(f"   Ramo: {ramo}")
        print(f"   Estados: {estados}")
        print(f"   Cidades: {cidades}")
        print(f"   Portes: {portes}")
        print(f"   Mínimo de processos: {min_processos}")
        print(f"   Apenas com processos: {apenas_com_processos}")

        if modo_real:
            # Busca real via API CNPJA
            from busca_cnpja_api import BuscadorCNPJA
            buscador = BuscadorCNPJA()

            empresas_encontradas = buscador.buscar_empresas(
                ramo=ramo,
                estados=estados,
                cidades=cidades if cidades else [],
                portes=portes,
                limite_por_cidade=50
            )

            # Se não especificou cidades, busca em todas as principais do estado
            if not cidades:
                for estado in estados:
                    cidades_estado = CIDADES_POR_ESTADO.get(estado, [])[:5]  # Top 5 cidades
                    empresas_encontradas.extend(
                        buscador.buscar_empresas(
                            ramo=ramo,
                            estados=[estado],
                            cidades=cidades_estado,
                            portes=portes,
                            limite_por_cidade=10
                        )
                    )

            # Adiciona campo de processos (por enquanto vazio - integração futura)
            for empresa in empresas_encontradas:
                empresa['processos'] = {
                    'total_processos': 0,
                    'tribunais_consultados': [],
                    'processos': []
                }
                empresa['tem_processos'] = False
                empresa['data_consulta'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                empresa['modo'] = 'API CNPJA - Dados Reais'

            # Salva resultados
            pasta_saida = './resultados/'
            os.makedirs(pasta_saida, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = os.path.join(pasta_saida, f"busca_cnpja_{timestamp}.json")

            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(empresas_encontradas, f, ensure_ascii=False, indent=2)

            print(f"✅ Encontradas {len(empresas_encontradas)} empresas reais")

            return jsonify({
                'sucesso': True,
                'total': len(empresas_encontradas),
                'resultados': empresas_encontradas,
                'arquivo': nome_arquivo,
                'modo': 'API CNPJA - Empresas Reais'
            })

        # MODO DEMONSTRAÇÃO (código existente)
        print(f"\n⚠️  Rodando em modo DEMO - configure CNPJA_API_KEY para dados reais")

        # DADOS DE DEMONSTRAÇÃO (simulando resultados reais)
        import random

        empresas_demo = []

        # Gera nomes de empresas baseados no ramo digitado pelo usuário
        ramo_title = ramo.title()  # Primeira letra maiúscula

        # Prefixos e sufixos comuns para empresas (APENAS ME e EPP)
        prefixos = ['', 'Comércio de ', 'Distribuidora ', 'Indústria de ', 'Serviços de ', 'Atacado ']
        sufixos = ['ME', 'EPP']  # Apenas Microempresa e Empresa Pequeno Porte
        complementos = ['', ' do Brasil', ' Regional', ' Nacional', ' Express', ' Premium', ' Center', ' Company', ' Group']

        # Gera variações do nome baseado no ramo
        nomes_empresas = []
        for prefixo in prefixos:
            for complemento in complementos:
                nome = f"{prefixo}{ramo_title}{complemento}".strip()
                if nome:  # Evita nomes vazios
                    nomes_empresas.append(nome)

        cidades_por_estado = CIDADES_POR_ESTADO

        # Lista de todos os tribunais disponíveis
        todos_tribunais = list(TRIBUNAIS_BRASIL.keys())

        for estado in estados:
            # Determina quais cidades buscar
            cidades_buscar = []
            if cidades:
                # Filtra apenas cidades deste estado
                cidades_buscar = [c for c in cidades if c in cidades_por_estado.get(estado, [])]

            # Se não há cidades específicas, usa todas do estado
            if not cidades_buscar:
                cidades_buscar = cidades_por_estado.get(estado, ['Capital'])

            for cidade in cidades_buscar:
                # Gera entre 15 e 30 empresas por cidade
                num_empresas = random.randint(15, 30)

                for i in range(num_empresas):
                    cnpj_base = f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}/0001-{random.randint(10,99)}"

                    # 70% tem processos (aumentado de 33%)
                    tem_processos = random.random() < 0.7

                    # Se tem processos, gera entre 1 e 12 processos (aumentado de 1-5)
                    num_processos = random.randint(1, 12) if tem_processos else 0

                    # Aplica filtro de mínimo de processos
                    if min_processos > 0 and num_processos < min_processos:
                        continue

                    # Se filtrou apenas com processos, só adiciona se tiver
                    if apenas_com_processos and not tem_processos:
                        continue

                    # Filtra por porte
                    porte_empresa = random.choice(['ME', 'EPP'])
                    if porte_empresa not in portes:
                        continue

                    empresa = {
                        'cnpj': cnpj_base,
                        'razao_social': f"{random.choice(nomes_empresas)} {random.choice(sufixos)}",
                        'nome_fantasia': random.choice(nomes_empresas).split()[0],
                        'situacao': 'ATIVA',
                        'cnae_principal': f'{random.randint(1000,9999)}-{random.randint(1,9)}/00',
                        'cnae_buscado': ramo,
                        'porte': porte_empresa,
                        'estado': estado,
                        'cidade': cidade,
                        'data_abertura': f"{random.randint(2010, 2023)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                        'processos': {
                            'total_processos': num_processos,
                            'tribunais_consultados': random.sample(todos_tribunais, k=min(5, max(1, num_processos//2))) if num_processos > 0 else [],
                            'processos': [
                                {
                                    'numero_cnj': f'{random.randint(1000000,9999999)}-{random.randint(10,99)}.{random.randint(2020,2024)}.8.26.{random.randint(100,999):04d}',
                                    'classe': random.choice([
                                        'Procedimento Comum Cível',
                                        'Reclamação Trabalhista',
                                        'Execução Fiscal',
                                        'Ação de Cobrança',
                                        'Ação de Indenização',
                                        'Rescisão de Contrato',
                                        'Pedido de Recuperação Judicial'
                                    ]),
                                    'assunto': random.choice([
                                        'Indenização por Dano Moral',
                                        'Rescisão de Contrato de Trabalho',
                                        'Cobrança de Dívida',
                                        'Dano Material',
                                        'Responsabilidade Civil',
                                        'Verbas Rescisórias',
                                        'Inadimplência Contratual',
                                        'FGTS',
                                        'Horas Extras'
                                    ]),
                                    'tribunal': random.choice(random.sample(todos_tribunais, k=min(10, len(todos_tribunais))))
                                } for _ in range(num_processos)
                            ]
                        },
                        'tem_processos': tem_processos,
                        'data_consulta': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'modo': 'DEMONSTRAÇÃO'
                    }

                    empresas_demo.append(empresa)

        # Salva resultados
        pasta_saida = './resultados/'
        os.makedirs(pasta_saida, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = os.path.join(pasta_saida, f"busca_demo_{timestamp}.json")

        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(empresas_demo, f, ensure_ascii=False, indent=2)

        print(f"✅ Geradas {len(empresas_demo)} empresas de demonstração")

        return jsonify({
            'sucesso': True,
            'total': len(empresas_demo),
            'resultados': empresas_demo,
            'arquivo': nome_arquivo,
            'modo': 'DEMONSTRAÇÃO - Dados fictícios para teste'
        })

    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/historico')
def historico_buscas():
    """Lista buscas anteriores"""
    try:
        pasta_resultados = './resultados/'
        if not os.path.exists(pasta_resultados):
            return jsonify([])

        arquivos = []
        for arquivo in os.listdir(pasta_resultados):
            if arquivo.endswith('.json'):
                caminho = os.path.join(pasta_resultados, arquivo)
                stat = os.stat(caminho)

                # Carrega para ver quantas empresas
                with open(caminho, 'r', encoding='utf-8') as f:
                    dados = json.load(f)

                arquivos.append({
                    'nome': arquivo,
                    'caminho': caminho,
                    'data': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                    'tamanho': stat.st_size,
                    'total_empresas': len(dados)
                })

        # Ordena por data (mais recente primeiro)
        arquivos.sort(key=lambda x: x['data'], reverse=True)

        return jsonify(arquivos)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    # A hospedagem (Render) informa a porta pela variável PORT.
    # Rodando no seu computador, usa a 5000 como sempre.
    port = int(os.environ.get('PORT', 5000))
    modo_debug = os.environ.get('FLASK_DEBUG', '0') == '1'

    print("\n" + "="*60)
    print("🚀 SERVIDOR WEB INICIADO")
    print("="*60)
    print("\n📱 Acesse no seu navegador:")
    print(f"   http://localhost:{port}")
    print(f"   Usuário: {ADMIN_USUARIO}  |  Senha: {ADMIN_SENHA}")
    print("\n⚠️  Pressione CTRL+C para parar o servidor\n")

    # Abre o navegador automaticamente 1,5s depois que o servidor subir
    import threading
    import webbrowser
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()

    app.run(debug=modo_debug, port=port, host='0.0.0.0')

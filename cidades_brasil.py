# Base de cidades por estado do Brasil (sample - principais cidades)
# Para produção real, usar API do IBGE

CIDADES_POR_ESTADO = {
    'SP': ['São Paulo', 'Guarulhos', 'Campinas', 'São Bernardo do Campo', 'Santo André', 'Osasco', 'São José dos Campos',
           'Ribeirão Preto', 'Sorocaba', 'Santos', 'Mauá', 'São José do Rio Preto', 'Mogi das Cruzes', 'Diadema', 'Jundiaí',
           'Piracicaba', 'Carapicuíba', 'Bauru', 'Itaquaquecetuba', 'Franca', 'Guarujá', 'Taubaté', 'Limeira', 'Suzano',
           'Praia Grande', 'Taboão da Serra', 'Sumaré', 'Barueri', 'Embu das Artes', 'São Carlos', 'Marília', 'Indaiatuba',
           'Americana', 'Jacareí', 'Araraquara', 'Cotia', 'Rio Claro', 'Presidente Prudente', 'Araçatuba', 'Hortolândia'],

    'RJ': ['Rio de Janeiro', 'São Gonçalo', 'Duque de Caxias', 'Nova Iguaçu', 'Niterói', 'Belford Roxo', 'São João de Meriti',
           'Campos dos Goytacazes', 'Petrópolis', 'Volta Redonda', 'Magé', 'Itaboraí', 'Macaé', 'Cabo Frio', 'Nova Friburgo',
           'Barra Mansa', 'Angra dos Reis', 'Mesquita', 'Teresópolis', 'Nilópolis', 'Resende', 'Araruama', 'Queimados'],

    'MG': ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Betim', 'Montes Claros', 'Ribeirão das Neves',
           'Uberaba', 'Governador Valadares', 'Ipatinga', 'Santa Luzia', 'Sete Lagoas', 'Divinópolis', 'Ibirité', 'Poços de Caldas',
           'Patos de Minas', 'Teófilo Otoni', 'Sabará', 'Pouso Alegre', 'Barbacena', 'Varginha', 'Conselheiro Lafaiete', 'Araguari'],

    'BA': ['Salvador', 'Feira de Santana', 'Vitória da Conquista', 'Camaçari', 'Itabuna', 'Juazeiro', 'Lauro de Freitas',
           'Ilhéus', 'Jequié', 'Teixeira de Freitas', 'Alagoinhas', 'Barreiras', 'Paulo Afonso', 'Simões Filho', 'Santo Antônio de Jesus',
           'Valença', 'Candeias', 'Guanambi', 'Jacobina', 'Serrinha', 'Senhor do Bonfim', 'Dias d\'Ávila', 'Luís Eduardo Magalhães'],

    'PR': ['Curitiba', 'Londrina', 'Maringá', 'Ponta Grossa', 'Cascavel', 'São José dos Pinhais', 'Foz do Iguaçu', 'Colombo',
           'Guarapuava', 'Paranaguá', 'Araucária', 'Toledo', 'Apucarana', 'Pinhais', 'Campo Largo', 'Almirante Tamandaré',
           'Umuarama', 'Piraquara', 'Cambé', 'Paranavaí', 'Francisco Beltrão', 'Fazenda Rio Grande', 'Sarandi'],

    'RS': ['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Canoas', 'Santa Maria', 'Gravataí', 'Viamão', 'Novo Hamburgo',
           'São Leopoldo', 'Rio Grande', 'Alvorada', 'Passo Fundo', 'Sapucaia do Sul', 'Uruguaiana', 'Santa Cruz do Sul',
           'Cachoeirinha', 'Bagé', 'Bento Gonçalves', 'Erechim', 'Guaíba', 'Cachoeira do Sul', 'Santana do Livramento', 'Alegrete'],

    'PE': ['Recife', 'Jaboatão dos Guararapes', 'Olinda', 'Caruaru', 'Petrolina', 'Paulista', 'Cabo de Santo Agostinho',
           'Camaragibe', 'Garanhuns', 'Vitória de Santo Antão', 'Igarassu', 'São Lourenço da Mata', 'Abreu e Lima', 'Santa Cruz do Capibaribe',
           'Ipojuca', 'Serra Talhada', 'Araripina', 'Gravatá', 'Carpina', 'Goiana', 'Belo Jardim', 'Arcoverde', 'Ouricuri'],

    'CE': ['Fortaleza', 'Caucaia', 'Juazeiro do Norte', 'Maracanaú', 'Sobral', 'Crato', 'Itapipoca', 'Maranguape', 'Iguatu',
           'Quixadá', 'Canindé', 'Pacajus', 'Aquiraz', 'Quixeramobim', 'Crateús', 'Russas', 'Aracati', 'Cascavel', 'Pacatuba',
           'Icó', 'Horizonte', 'Camocim', 'Morada Nova', 'Acaraú'],

    'SC': ['Florianópolis', 'Joinville', 'Blumenau', 'São José', 'Criciúma', 'Chapecó', 'Itajaí', 'Jaraguá do Sul', 'Lages',
           'Palhoça', 'Balneário Camboriú', 'Brusque', 'Tubarão', 'São Bento do Sul', 'Caçador', 'Camboriú', 'Navegantes',
           'Concórdia', 'Rio do Sul', 'Araranguá', 'Gaspar', 'Biguaçu', 'Indaial', 'Itapema'],

    'GO': ['Goiânia', 'Aparecida de Goiânia', 'Anápolis', 'Rio Verde', 'Luziânia', 'Águas Lindas de Goiás', 'Valparaíso de Goiás',
           'Trindade', 'Formosa', 'Novo Gama', 'Itumbiara', 'Senador Canedo', 'Catalão', 'Jataí', 'Planaltina', 'Caldas Novas',
           'Santo Antônio do Descoberto', 'Goianésia', 'Cidade Ocidental', 'Mineiros', 'Cristalina', 'Inhumas'],

    'MA': ['São Luís', 'Imperatriz', 'São José de Ribamar', 'Timon', 'Caxias', 'Codó', 'Paço do Lumiar', 'Açailândia',
           'Bacabal', 'Balsas', 'Santa Inês', 'Pinheiro', 'Pedreiras', 'Chapadinha', 'Barra do Corda', 'Grajaú', 'Presidente Dutra'],

    'PB': ['João Pessoa', 'Campina Grande', 'Santa Rita', 'Patos', 'Bayeux', 'Sousa', 'Cajazeiras', 'Guarabira', 'Mamanguape',
           'Cabedelo', 'Sapé', 'Monteiro', 'Pombal', 'Princesa Isabel', 'Esperança', 'Itabaiana', 'Catolé do Rocha'],

    'ES': ['Vitória', 'Vila Velha', 'Serra', 'Cariacica', 'Viana', 'Cachoeiro de Itapemirim', 'Linhares', 'São Mateus',
           'Colatina', 'Guarapari', 'Aracruz', 'Venda Nova do Imigrante', 'Castelo', 'Itapemirim', 'Alegre', 'Afonso Cláudio'],

    'AM': ['Manaus', 'Parintins', 'Itacoatiara', 'Manacapuru', 'Coari', 'Tefé', 'Tabatinga', 'Maués', 'Humaitá', 'São Gabriel da Cachoeira'],

    'MT': ['Cuiabá', 'Várzea Grande', 'Rondonópolis', 'Sinop', 'Tangará da Serra', 'Cáceres', 'Sorriso', 'Lucas do Rio Verde',
           'Barra do Garças', 'Primavera do Leste', 'Alta Floresta', 'Colíder', 'Pontes e Lacerda', 'Juína'],

    'RN': ['Natal', 'Mossoró', 'Parnamirim', 'São Gonçalo do Amarante', 'Macaíba', 'Ceará-Mirim', 'Caicó', 'Assu', 'Currais Novos',
           'Pau dos Ferros', 'São José de Mipibu', 'Nova Cruz', 'Santa Cruz', 'Apodi'],

    'RO': ['Porto Velho', 'Ji-Paraná', 'Ariquemes', 'Vilhena', 'Cacoal', 'Jaru', 'Rolim de Moura', 'Guajará-Mirim', 'Pimenta Bueno'],

    'TO': ['Palmas', 'Araguaína', 'Gurupi', 'Porto Nacional', 'Paraíso do Tocantins', 'Colinas do Tocantins', 'Guaraí', 'Miracema do Tocantins'],

    'AL': ['Maceió', 'Arapiraca', 'Rio Largo', 'Palmeira dos Índios', 'União dos Palmares', 'Penedo', 'São Miguel dos Campos',
           'Santana do Ipanema', 'Delmiro Gouveia', 'Coruripe', 'Campo Alegre', 'Arapiraca'],

    'SE': ['Aracaju', 'Nossa Senhora do Socorro', 'Lagarto', 'Itabaiana', 'Estância', 'Propriá', 'Simão Dias', 'Tobias Barreto',
           'São Cristóvão', 'Barra dos Coqueiros', 'Laranjeiras'],

    'MS': ['Campo Grande', 'Dourados', 'Três Lagoas', 'Corumbá', 'Ponta Porã', 'Sidrolândia', 'Maracaju', 'Aquidauana', 'Nova Andradina'],

    'PI': ['Teresina', 'Parnaíba', 'Picos', 'Piripiri', 'Floriano', 'Campo Maior', 'Barras', 'União', 'Altos', 'Esperantina'],

    'AC': ['Rio Branco', 'Cruzeiro do Sul', 'Sena Madureira', 'Tarauacá', 'Feijó', 'Senador Guiomard'],

    'AP': ['Macapá', 'Santana', 'Laranjal do Jari', 'Oiapoque', 'Mazagão'],

    'RR': ['Boa Vista', 'Rorainópolis', 'Caracaraí', 'Alto Alegre', 'Mucajaí'],

    'DF': ['Brasília', 'Taguatinga', 'Ceilândia', 'Samambaia', 'Planaltina', 'Gama', 'Águas Claras', 'Santa Maria', 'São Sebastião',
           'Recanto das Emas', 'Sobradinho', 'Riacho Fundo', 'Vicente Pires', 'Guará']
}

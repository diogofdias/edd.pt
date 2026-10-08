# -*- coding: utf-8 -*-
"""Gera as páginas de /calculadoras/ do edd.pt a partir de um molde comum."""
import io, json, os, re, sys

OUT = sys.argv[1]
BASE = 'https://edd.pt/calculadoras/'

piloto = io.open(os.path.join(OUT, 'calculadoras', 'imt-imposto-selo.html'), encoding='utf-8').read()
NAV = re.search(r'(<nav class="nav".*?</div>)\n\n<div class="hero">', piloto, re.S).group(1)
FOOTER = re.search(r'(<footer>.*?</footer>\n\n<div class="mobile-cta">.*?</div>)\n\n<script', piloto, re.S).group(1)

OBJETIVOS = [('habitacao-propria-permanente', 'Habitação Própria Permanente'), ('habitacao-secundaria', 'Habitação Secundária'),
             ('terreno-rustico', 'Terreno Rústico'), ('terreno-urbano', 'Terreno Urbano')]
TAXAS = [('fixa', 'Taxa Fixa'), ('variavel', 'Taxa Variável')]


def money(id, label, valor, hint=None):
    h = '\n          <small class="field-hint">%s</small>' % hint if hint else ''
    return '''        <div class="field">
          <label class="field-label" for="%s">%s</label>
          <div class="input-wrap">
            <input type="text" id="%s" inputmode="decimal" data-money value="%s">
            <span class="input-suffix" aria-hidden="true">€</span>
          </div>%s
        </div>''' % (id, label, id, valor, h)


def dec(id, label, valor, sufixo, hint=None):
    h = '\n          <small class="field-hint">%s</small>' % hint if hint else ''
    cls = ' class="com-sufixo-longo"' if len(sufixo) > 1 else ''
    return '''        <div class="field">
          <label class="field-label" for="%s">%s</label>
          <div class="input-wrap">
            <input type="text" id="%s" inputmode="decimal"%s value="%s">
            <span class="input-suffix" aria-hidden="true">%s</span>
          </div>%s
        </div>''' % (id, label, id, cls, valor, sufixo, h)


def radios(nome, label, opcoes, marcado, hint=None):
    its = ''.join('\n            <label class="radio"><input type="radio" name="%s" value="%s"%s><span>%s</span></label>'
                  % (nome, v, ' checked' if v == marcado else '', l) for v, l in opcoes)
    h = '\n          <small class="field-hint">%s</small>' % hint if hint else ''
    return '''        <fieldset class="field">
          <legend class="field-label">%s</legend>
          <div class="radio-list">%s
          </div>%s
        </fieldset>''' % (label, its, h)


def row2(a, b):
    return '        <div class="field-row">\n%s\n%s\n        </div>' % (a, b)


JOVEM = '''        <div class="field" style="margin-bottom:0;">
          <label class="toggle" id="jovemLabel">
            <input type="checkbox" id="jovem">
            <span class="toggle-track" aria-hidden="true"></span>
            <span class="toggle-text">
              <strong>Aplicar isenção jovem</strong>
              <small id="jovemHint">Até 35 anos, primeira habitação própria e permanente. Confirme a sua elegibilidade antes de contar com este valor.</small>
            </span>
          </label>
        </div>'''


def bloco(t):
    return '        <p class="bloco-titulo">%s</p>' % t


def linha(id, label, hint=None, cls='', hidden=False, wrap=False):
    return '            <tr id="row%s"%s%s><th scope="row">%s%s</th><td id="%s"%s></td></tr>' % (
        id[3:], ' class="%s"' % cls if cls else '', ' hidden' if hidden else '', label,
        '<small>%s</small>' % hint if hint else '', id, ' class="wrap"' if wrap else '')


def ul(itens):
    return '<ul>\n' + ''.join('              <li>%s</li>\n' % i for i in itens) + '            </ul>'


def li_ids(ids):
    return '<ul>\n' + ''.join('              <li id="%s"></li>\n' % i for i in ids) + '            </ul>'


CALCS = {
    'imt-imposto-selo': ('IMT e Imposto do Selo', 'Quanto paga de impostos na compra, com as tabelas de 2026 e o cenário de isenção jovem.'),
    'prestacao-casa': ('Prestação da Casa', 'Quanto fica a pagar por mês ao banco, e quanto custa o crédito no total.'),
    'compra-casa': ('Compra de Casa', 'O total necessário para comprar: preço, impostos, escritura e custos do crédito.'),
    'venda-casa': ('Venda de Casa', 'Quanto recebe de facto depois da comissão e de liquidar a hipoteca.'),
    'troca-casa': ('Troca de Casa', 'Vender uma casa para comprar outra: quanto falta, ou quanto sobra.'),
}

PAGINAS = []

# ───────────────────────── IMT + Selo ─────────────────────────
PAGINAS.append(dict(
    slug='imt-imposto-selo',
    title='Calculadora de IMT e Imposto do Selo 2026 | EDD',
    desc='Calcule o IMT e o Imposto do Selo na compra de casa em Portugal com as tabelas de 2026. Inclui habitação própria, secundária, terrenos e isenção jovem.',
    nome='Calculadora de IMT e Imposto do Selo',
    eyebrow='Calculadora · Tabelas 2026',
    h1='Quanto vai pagar de IMT e Imposto do Selo.',
    lead='Indique o valor da casa e o fim a que se destina. O resultado actualiza de imediato, com o detalhe do escalão aplicado e o cenário de isenção jovem.',
    form='\n\n'.join([money('valor', 'Valor de aquisição', '250 000'), radios('objetivo', 'Objetivo da aquisição', OBJETIVOS, OBJETIVOS[0][0]), JOVEM]),
    res_label='Total estimado de impostos',
    linhas=[linha('outValor', 'Valor de aquisição'), linha('outObjetivo', 'Objetivo da aquisição', wrap=True), linha('outImt', 'IMT'),
            linha('outIs', 'Imposto do Selo'), linha('outIsencao', 'Poupança com isenção jovem', cls='reducao', hidden=True),
            linha('outTotal2', 'Total estimado', cls='total')],
    aviso='A isenção jovem não se aplica: o valor de aquisição ultrapassa 660 982 €.',
    detalhe=[('Como o resultado foi calculado', ul(['IMT = valor × taxa do escalão − parcela a abater, conforme a tabela de IMT de 2026.',
                                                   'Imposto do Selo = 0,8 % × valor de aquisição.',
                                                   'Na isenção jovem parcial, só o valor acima de 330 539 € é tributado.'])),
             ('Nesta simulação', li_ids(['detEscalao', 'detSemIsencao', 'detIsencao']))],
    nota='Este resultado é uma estimativa com base nos dados introduzidos. As regras fiscais devem ser confirmadas no seu caso concreto, junto da Autoridade Tributária ou de um profissional habilitado.',
    pressupostos=['Tabelas de IMT de 2026 para Portugal Continental.', 'Imposto do Selo a 0,8 % sobre o valor de aquisição (Verba 1.1 da TGIS).',
                  'Terreno rústico a 5 % e terreno urbano a 6,5 %, em taxa única.', 'Isenção jovem de acordo com o Decreto-Lei n.º 48-A/2024.'],
    nao=['Imposto do Selo sobre o crédito habitação.', 'Tabelas próprias das Regiões Autónomas.', 'Casos em que o Valor Patrimonial Tributário é superior ao preço.',
         'Permutas, aquisição de partes de prédio e compras por sociedades.', 'Taxa agravada para compradores em jurisdições de regime fiscal mais favorável.'],
    faq_h2='IMT e Imposto do Selo, sem rodeios.',
    faqs=[('Como se calcula o IMT na compra de casa?', 'Para habitação, multiplica-se o valor de aquisição pela taxa do escalão em que se insere e subtrai-se a parcela a abater desse escalão. Acima de 660 982 € aplica-se uma taxa única, sem parcela a abater. O imposto incide sobre o maior valor entre o preço declarado e o Valor Patrimonial Tributário.'),
          ('Quanto é o Imposto do Selo na compra de um imóvel?', 'É 0,8 % do valor de aquisição, ao abrigo da Verba 1.1 da Tabela Geral do Imposto do Selo. Se houver crédito habitação, acresce Imposto do Selo sobre o financiamento, que esta calculadora não inclui.'),
          ('Quem tem direito à isenção jovem de IMT?', 'Compradores até 35 anos que adquirem a primeira habitação própria e permanente e que não sejam dependentes para efeitos de IRS. A isenção é total até 330 539 € e parcial até 660 982 €; acima desse valor não se aplica.'),
          ('Quando se paga o IMT e o Imposto do Selo?', 'Antes da escritura ou do documento particular autenticado. As guias são emitidas pela Autoridade Tributária e o comprovativo de pagamento é exigido no acto.')],
    cta_h2='Os impostos são só uma parte da conta.',
    cta_p='Escritura, registos, crédito e o valor certo a oferecer. Fazemos as contas completas consigo, sem compromisso.',
    js='''    var obj = C.radio('objetivo');
    var r = C.calcularIMTSelo({ valorAquisicao: C.money('valor'), objetivo: obj, isencaoJovem: C.jovem(obj) });

    C.set('outTotal', f(r.total));
    C.set('outTotal2', f(r.total));
    C.set('outValor', f(r.valorAquisicao));
    C.set('outObjetivo', r.objetivoLabel);
    C.set('outImt', f(r.imt));
    C.set('outIs', f(r.is));
    C.show('rowIsencao', r.isencao.aplicada);
    C.set('outIsencao', '−' + f(r.isencao.reducao));
    C.show('aviso', r.isencao.cenario === 'nao-aplicavel-acima-limite');

    C.set('detEscalao', C.descreverEscalao(r.valorAquisicao, r.objetivo));
    C.set('detSemIsencao', 'Antes de isenção: IMT ' + f(r.imtSemIsencao) + ' + Imposto do Selo ' + f(r.isSemIsencao) + ' = ' + f(r.totalSemIsencao) + '.');
    C.show('detIsencao', r.isencao.aplicada);
    C.set('detIsencao', r.isencao.cenario === 'total'
      ? 'Isenção jovem total: valor até 330 539 €, IMT e Imposto do Selo ficam a zero.'
      : 'Isenção jovem parcial: 8 % de IMT e 0,8 % de Imposto do Selo apenas sobre ' + f(r.valorAquisicao - C.ISENCAO_JOVEM_LIMITE_TOTAL) + '.');''',
))

# ───────────────────────── Prestação ─────────────────────────
PAGINAS.append(dict(
    slug='prestacao-casa',
    title='Simulador de Prestação da Casa — Crédito Habitação | EDD',
    desc='Simule a prestação mensal do crédito habitação: indique o valor da casa, a entrada, o prazo e a taxa de juro. Veja o total pago ao banco e os juros.',
    nome='Simulador de Prestação da Casa',
    eyebrow='Calculadora · Crédito habitação',
    h1='Quanto vai pagar por mês pela casa.',
    lead='Valor do imóvel, entrada, prazo e taxa de juro. Fica a saber a prestação mensal, o total pago ao banco e quanto desse total são juros.',
    form='\n\n'.join([money('valor', 'Valor do imóvel', '275 000'), money('entrada', 'Entrada inicial', '50 000'),
                      row2(dec('prazo', 'Prazo do crédito', '30', 'anos'), dec('taxa', 'Taxa de juro anual', '3,5', '%')),
                      radios('tipo', 'Tipo de taxa', TAXAS, 'variavel')]),
    res_label='Prestação mensal estimada',
    linhas=[linha('outMontante', 'Montante financiado'), linha('outPrazo', 'Prazo do crédito'), linha('outTipo', 'Tipo de taxa'),
            linha('outLtv', 'Percentagem financiada', hint='Montante financiado face ao valor do imóvel'),
            linha('outJuros', 'Juros estimados'), linha('outTotalPago', 'Total pago ao banco', cls='total')],
    aviso='A entrada cobre o valor do imóvel: não há montante a financiar.',
    detalhe=[('Como o resultado foi calculado', ul(['Prestação constante: P × i ÷ (1 − (1 + i)<sup>−n</sup>).',
                                                   'P é o montante financiado, i a taxa mensal e n o prazo em meses.',
                                                   'A taxa mensal é a taxa anual nominal dividida por 12.'])),
             ('Nesta simulação', li_ids(['detFormula']))],
    nota='A prestação apresentada é uma estimativa base e não substitui uma simulação ou proposta formal de crédito habitação.',
    pressupostos=['Prestação constante durante todo o prazo (regime francês).', 'Taxa anual nominal convertida em mensal por divisão por 12.',
                  'A taxa indicada mantém-se até ao fim do contrato.', 'Prazo limitado a 40 anos e taxa a 15 %.'],
    nao=['Spread e condições reais aprovadas pelo banco.', 'Seguro de vida e seguro multirriscos.', 'Comissões bancárias e Imposto do Selo sobre o crédito.',
         'Variações futuras da Euribor em taxa variável.', 'Carências, bonificações e amortizações antecipadas.'],
    faq_h2='Prestação da casa, sem rodeios.',
    faqs=[('Como se calcula a prestação do crédito habitação?', 'Em Portugal a regra é a prestação constante: paga o mesmo valor todos os meses enquanto a taxa não mudar. No início a maior parte da prestação são juros; com o tempo, cresce a parte que amortiza capital.'),
          ('O que falta somar a esta prestação?', 'Os seguros de vida e multirriscos, que o banco exige, e eventuais comissões de manutenção. Dependendo da idade e do capital, os seguros podem representar uma fatia relevante do encargo mensal.'),
          ('Que entrada preciso de ter?', 'Para habitação própria e permanente, os bancos financiam em regra até 90 % do menor valor entre o preço e a avaliação. Além da entrada, precisa de capital para impostos, escritura e registos.'),
          ('Taxa fixa ou taxa variável?', 'A taxa fixa dá uma prestação estável e protege de subidas; a variável acompanha a Euribor, para cima e para baixo. Nesta calculadora o tipo de taxa é informativo: o cálculo usa a taxa que indicar.')],
    cta_h2='A prestação cabe no orçamento. E a casa certa?',
    cta_p='Ajudamos a definir o valor a que pode comprar com segurança e a encontrar a casa que lhe corresponde.',
    js='''    var prazo = C.dec('prazo', 40);
    var taxa = C.dec('taxa', 15);
    var tipo = C.radio('tipo');
    var r = C.calcularPrestacao({ valorImovel: C.money('valor'), entradaInicial: C.money('entrada'), prazoAnos: prazo, taxaAnual: taxa / 100 });
    var taxaTxt = taxa.toLocaleString('pt-PT', { maximumFractionDigits: 3 }) + ' %';

    C.set('outTotal', f(r.prestacaoMensal));
    C.set('outContext', prazo + ' anos, taxa ' + (tipo === 'fixa' ? 'fixa' : 'variável') + ' de ' + taxaTxt);
    C.set('outMontante', f(r.montanteFinanciado));
    C.set('outPrazo', prazo + ' anos (' + r.prazoMeses + ' meses)');
    C.set('outTipo', tipo === 'fixa' ? 'Fixa' : 'Variável');
    C.set('outLtv', C.formatPercent(r.ltv, 1));
    C.set('outJuros', f(r.jurosEstimadosPagos));
    C.set('outTotalPago', f(r.totalPago));
    C.show('aviso', r.montanteFinanciado === 0 && C.money('valor') > 0);
    C.set('detFormula', 'P = ' + f(r.montanteFinanciado) + '; i = ' + taxaTxt + ' ÷ 12; n = ' + r.prazoMeses + ' meses. Prestação: ' + f(r.prestacaoMensal) + '.');''',
))

# ───────────────────────── Compra ─────────────────────────
PAGINAS.append(dict(
    slug='compra-casa',
    title='Calculadora de Compra de Casa — Custos Totais 2026 | EDD',
    desc='Calcule quanto precisa para comprar casa em Portugal: preço, IMT, Imposto do Selo, escritura, registos e custos do crédito habitação. Tabelas de 2026.',
    nome='Calculadora de Compra de Casa',
    eyebrow='Calculadora · Tabelas 2026',
    h1='Quanto precisa, ao todo, para comprar casa.',
    lead='O preço é só o começo. Some impostos, escritura, registos e os custos do crédito, e veja quanto terá de financiar com os capitais próprios que tem.',
    form='\n\n'.join([money('valor', 'Valor de aquisição', '300 000'), radios('objetivo', 'Objetivo da aquisição', OBJETIVOS, OBJETIVOS[0][0]),
                      money('capitais', 'Capitais próprios disponíveis', '60 000', 'Usados para reduzir a necessidade de financiamento.'), JOVEM]),
    res_label='Total necessário para comprar',
    linhas=[linha('outValor', 'Valor de aquisição'), linha('outImt', 'IMT'), linha('outIs', 'Imposto do Selo'),
            linha('outEscritura', 'Escritura e registos', hint='Estimativa'),
            linha('outIsencao', 'Poupança com isenção jovem', cls='reducao', hidden=True),
            linha('outSemFin', 'Investimento sem financiamento', cls='sub'),
            linha('outFinanciar', 'Valor estimado a financiar', hint='Inclui margem de segurança de +10 %', hidden=True),
            linha('outCustosFin', 'Custos estimados do financiamento', hidden=True),
            linha('outSemNecessidade', 'Financiamento', hidden=True),
            linha('outTotal2', 'Total necessário', cls='total')],
    aviso='A isenção jovem não se aplica: o valor de aquisição ultrapassa 660 982 €.',
    detalhe=[('Como o resultado foi calculado', ul(['IMT conforme a tabela de 2026 aplicável ao objetivo da aquisição.', 'Imposto do Selo = 0,8 % do valor de aquisição.',
                                                   'Escritura e registos assumidos em 1 000 €.',
                                                   'Valor a financiar = (investimento − capitais próprios) × 1,10.',
                                                   'Havendo financiamento, somam-se custos bancários estimados e Imposto do Selo de 0,8 % sobre o montante financiado.'])),
             ('Nesta simulação', li_ids(['detEscalao', 'detBanco']))],
    nota='Este resultado é indicativo e pode variar consoante o local da escritura e a entidade bancária. Os valores estimados devem ser confirmados no seu caso concreto.',
    pressupostos=['Tabelas de IMT de 2026 e Imposto do Selo a 0,8 %.', 'Escritura e registos: 1 000 €.',
                  'Custos bancários: 250 € de avaliação, 300 € de dossier e 750 € de minutas.',
                  'Valor a financiar agravado em 10 %, por margem de segurança.'],
    nao=['Spread, seguros e comissões reais do banco.', 'Limites de financiamento face à avaliação bancária.', 'Honorários de mediação (em regra pagos pelo vendedor).',
         'Obras, mudanças e mobiliário.', 'Compras por empresas ou em compropriedade.'],
    faq_h2='Custos de compra, sem rodeios.',
    faqs=[('Que custos existem além do preço da casa?', 'IMT, Imposto do Selo, escritura e registos. Com crédito habitação, acrescem a avaliação bancária, a comissão de dossier, a preparação de minutas e o Imposto do Selo sobre o financiamento.'),
          ('Porque é que o valor a financiar tem uma margem de 10 %?', 'É uma margem de segurança herdada do modelo de cálculo: cobre diferenças entre os custos estimados e os reais e pequenos imprevistos. O montante que o banco aprova depende da avaliação e do seu perfil.'),
          ('Os valores de escritura e de custos bancários são exactos?', 'Não, são estimativas de ordem de grandeza. Variam com o local onde se faz a escritura e com o preçário de cada banco, por isso devem ser confirmados antes de fechar contas.'),
          ('A isenção jovem também reduz os custos do crédito?', 'Nesta calculadora a isenção jovem aplica-se ao IMT e ao Imposto do Selo sobre a aquisição. Os custos bancários e o Imposto do Selo sobre o financiamento mantêm-se.')],
    cta_h2='Saber quanto precisa é o primeiro passo.',
    cta_p='O segundo é saber quanto vale, de facto, a casa que quer comprar. Analisamos o imóvel e o preço consigo.',
    js='''    var obj = C.radio('objetivo');
    var r = C.calcularCompra({ valorAquisicao: C.money('valor'), objetivo: obj, capitaisProprios: C.money('capitais'), isencaoJovem: C.jovem(obj) });
    var fin = r.montanteAFinanciar > 0;

    C.set('outTotal', f(r.totalNecessarioParaComprar));
    C.set('outTotal2', f(r.totalNecessarioParaComprar));
    C.set('outContext', fin ? 'Inclui preço, impostos, escritura e custos estimados de financiamento.' : 'Inclui preço, impostos e escritura. Sem financiamento previsto.');
    C.set('outValor', f(r.valorAquisicao));
    C.set('outImt', f(r.imt));
    C.set('outIs', f(r.is));
    C.set('outEscritura', f(r.escrituraRegistos));
    C.show('rowIsencao', r.isencao.aplicada);
    C.set('outIsencao', '−' + f(r.isencao.reducao));
    C.set('outSemFin', f(r.investimentoTotalSemFin));
    C.show('rowFinanciar', fin);
    C.set('outFinanciar', f(r.montanteAFinanciar));
    C.show('rowCustosFin', fin);
    C.set('outCustosFin', f(r.custoEstimadoFinanciamento));
    C.show('rowSemNecessidade', !fin);
    C.set('outSemNecessidade', 'Não é necessário');
    C.show('aviso', r.isencao.cenario === 'nao-aplicavel-acima-limite');

    C.set('detEscalao', 'IMT: ' + C.descreverEscalao(r.valorAquisicao, r.objetivo));
    C.show('detBanco', fin);
    C.set('detBanco', 'Custos bancários: avaliação ' + f(r.custos.avaliacaoBancaria) + ', dossier ' + f(r.custos.comissaoDossier) + ', minutas ' + f(r.custos.preparacaoMinutas) + ', Imposto do Selo sobre o financiamento ' + f(r.custos.isFinanciamento) + '.');''',
))

# ───────────────────────── Venda ─────────────────────────
PAGINAS.append(dict(
    slug='venda-casa',
    title='Calculadora de Venda de Casa — Quanto Recebe Líquido | EDD',
    desc='Calcule quanto recebe líquido ao vender a sua casa: comissão de mediação com IVA, liquidação da hipoteca e penalização por amortização antecipada.',
    nome='Calculadora de Venda de Casa',
    eyebrow='Calculadora · Venda',
    h1='Quanto lhe fica, de facto, da venda da casa.',
    lead='Do preço de venda ao valor que chega à sua conta: comissão de mediação com IVA, hipoteca por liquidar e penalização do banco.',
    form='\n\n'.join([money('valor', 'Valor de venda', '320 000'), dec('comissao', 'Comissão de mediação', '5', '%', 'Acresce IVA à taxa de 23 %.'),
                      money('hipoteca', 'Hipoteca em falta', '120 000'),
                      radios('tipo', 'Tipo de taxa do crédito', TAXAS, 'variavel', 'Define a penalização por amortização antecipada: 2 % em taxa fixa, 0,5 % em variável.')]),
    res_label='Valor líquido estimado da venda',
    linhas=[linha('outValor', 'Valor de venda'), linha('outHonorarios', 'Mediação, com IVA'), linha('outHipoteca', 'Hipoteca em falta'),
            linha('outPenalizacao', 'Penalização por amortização antecipada'), linha('outIsPen', 'Imposto do Selo sobre a penalização'),
            linha('outTotal2', 'Valor líquido estimado', cls='total')],
    aviso='Com estes valores, a venda não chega para liquidar a hipoteca e os custos.',
    detalhe=[('Como o resultado foi calculado', ul(['Honorários = valor de venda × comissão. IVA = 23 % sobre os honorários.',
                                                   'Penalização = hipoteca em falta × 2 % (taxa fixa) ou 0,5 % (taxa variável).',
                                                   'Imposto do Selo = 0,8 % da penalização.',
                                                   'Valor líquido = venda − honorários com IVA − hipoteca − penalização − Imposto do Selo.'])),
             ('Nesta simulação', li_ids(['detHonorarios', 'detHipoteca']))],
    nota='O valor líquido é uma estimativa e não inclui o imposto sobre mais-valias. Em habitação própria e permanente, o reinvestimento noutra habitação pode excluir essa tributação.',
    pressupostos=['IVA sobre honorários de mediação a 23 %.', 'Penalização por amortização antecipada: 2 % em taxa fixa, 0,5 % em variável.',
                  'Imposto do Selo de 0,8 % sobre a penalização.', 'Comissão limitada a 15 % no simulador.'],
    nao=['Imposto sobre mais-valias em IRS.', 'Custos de distrate e cancelamento da hipoteca.', 'Certificado energético e outra documentação.',
         'Obras ou preparação do imóvel para venda.', 'Condições contratuais específicas do seu banco.'],
    faq_h2='Custos de venda, sem rodeios.',
    faqs=[('Quanto custa vender uma casa?', 'Os dois grandes custos são a comissão de mediação, a que acresce IVA, e a liquidação do crédito em curso, com a respectiva penalização. A isto pode somar-se o imposto sobre mais-valias, que depende do seu caso.'),
          ('Esta calculadora inclui as mais-valias?', 'Não. O imposto sobre mais-valias depende do valor e da data de compra, das despesas dedutíveis e de reinvestir ou não noutra habitação própria e permanente. Deve ser calculado à parte, de preferência com um contabilista.'),
          ('Quanto é a penalização por amortizar o crédito?', 'A lei fixa um máximo de 0,5 % do capital amortizado em contratos de taxa variável e de 2 % em taxa fixa. Sobre essa comissão incide Imposto do Selo. Confirme no seu contrato o valor aplicável.'),
          ('Quem paga a comissão da imobiliária?', 'Em regra é o vendedor, e só quando o negócio se concretiza. O valor é uma percentagem do preço de venda, acrescida de IVA.')],
    cta_h2='O valor líquido começa no preço de venda.',
    cta_p='Um preço bem fundamentado vende mais depressa e por mais. Fazemos o diagnóstico de venda do seu imóvel, sem compromisso.',
    js='''    var pct = C.dec('comissao', 15) / 100;
    var r = C.calcularVenda({ valorVenda: C.money('valor'), comissaoMediacaoPct: pct, hipotecaEmFalta: C.money('hipoteca'), tipoTaxa: C.radio('tipo') });
    var menos = function (n) { return n > 0 ? '− ' + f(n) : f(0); };

    C.set('outTotal', f(r.receitaLiquida));
    C.set('outTotal2', f(r.receitaLiquida));
    C.set('outValor', f(r.valorVenda));
    C.set('outHonorarios', menos(r.custoHonorarios));
    C.set('outHipoteca', menos(r.hipoteca));
    C.set('outPenalizacao', menos(r.penalizacaoAmortizacao));
    C.set('outIsPen', menos(r.isPenalizacao));
    C.show('aviso', r.receitaLiquida < 0);

    C.set('detHonorarios', 'Honorários: ' + C.formatPercent(pct) + ' de ' + f(r.valorVenda) + ' = ' + f(r.comissaoMediacao) + ', mais ' + f(r.ivaHonorarios) + ' de IVA.');
    C.set('detHipoteca', 'Liquidação da hipoteca: ' + f(r.hipoteca) + ' + penalização de ' + C.formatPercent(r.penalizacaoTaxa) + ' (' + f(r.penalizacaoAmortizacao) + ') + Imposto do Selo (' + f(r.isPenalizacao) + ') = ' + f(r.liquidacaoHipoteca) + '.');''',
))

# ───────────────────────── Troca ─────────────────────────
PAGINAS.append(dict(
    slug='troca-casa',
    title='Calculadora de Troca de Casa — Vender para Comprar | EDD',
    desc='Vai vender a sua casa para comprar outra? Calcule quanto recebe da venda, quanto custa a nova compra e quanto falta, ou sobra, para trocar de casa.',
    nome='Calculadora de Troca de Casa',
    eyebrow='Calculadora · Tabelas 2026',
    h1='Vender esta casa para comprar a próxima.',
    lead='Junta as duas operações numa só conta: o que recebe da venda, o que custa a nova compra e quanto falta, ou sobra, no fim.',
    form='\n\n'.join([bloco('A · Casa que vende'), money('valorVenda', 'Valor de venda', '320 000'),
                      dec('comissao', 'Comissão de mediação', '5', '%', 'Acresce IVA à taxa de 23 %.'), money('hipoteca', 'Hipoteca em falta', '90 000'),
                      radios('tipo', 'Tipo de taxa do crédito actual', TAXAS, 'variavel'),
                      bloco('B · Casa que compra'), money('valor', 'Valor de aquisição', '380 000'),
                      radios('objetivo', 'Objetivo da aquisição', OBJETIVOS, OBJETIVOS[0][0]),
                      money('capitais', 'Capitais próprios adicionais', '15 000', 'Para além do valor líquido da venda.'), JOVEM]),
    res_label='Valor adicional necessário para trocar de casa',
    linhas=[linha('outReceita', 'Valor líquido da venda'), linha('outCapitais', 'Capitais próprios adicionais'),
            linha('outInvest', 'Investimento na nova compra', hint='Preço + impostos + escritura'),
            linha('outIsencao', 'Poupança com isenção jovem', hint='Já reflectida no investimento', cls='reducao', hidden=True),
            linha('outFinanciar', 'Valor estimado a financiar', hint='Inclui margem de segurança de +10 %', hidden=True),
            linha('outCustosFin', 'Custos estimados do financiamento', hidden=True),
            linha('outTotal2', '<span id="outTotalLabel">Valor adicional necessário</span>', cls='total')],
    aviso='A isenção jovem não se aplica: o valor de aquisição ultrapassa 660 982 €.',
    detalhe=[('Como o resultado foi calculado', ul(['A venda é calculada à parte: preço − mediação com IVA − liquidação da hipoteca.',
                                                   'A compra soma IMT, Imposto do Selo e escritura ao preço de aquisição.',
                                                   'O valor líquido da venda e os capitais próprios adicionais abatem ao investimento.',
                                                   'Havendo défice, é agravado em 10 % como montante a financiar, com custos bancários estimados.',
                                                   'Resultado = défice + custos do financiamento. Se for negativo, sobra capital.'])),
             ('Nesta simulação', li_ids(['detVenda', 'detCompra', 'detBanco']))],
    nota='Este resultado combina uma estimativa de venda com uma estimativa de compra. Não inclui o imposto sobre mais-valias e pode variar consoante a operação concreta.',
    pressupostos=['Venda e compra tratadas como operações separadas, ligadas financeiramente.', 'Tabelas de IMT de 2026 e Imposto do Selo a 0,8 %.',
                  'Escritura e registos: 1 000 €. Custos bancários: 1 300 € mais Imposto do Selo.', 'Penalização de 2 % em taxa fixa e 0,5 % em variável.'],
    nao=['Imposto sobre mais-valias em IRS.', 'Crédito ponte ou crédito intercalar.', 'Escrituras em datas desencontradas.', 'Reforços de sinal e cláusulas contratuais específicas.',
         'Custos de mudança, obras e mobiliário.'],
    faq_h2='Troca de casa, sem rodeios.',
    faqs=[('Devo vender primeiro ou comprar primeiro?', 'Depende da sua margem financeira e do mercado. Vender primeiro dá certeza sobre o valor disponível; comprar primeiro evita uma mudança intermédia, mas exige capacidade para suportar as duas casas durante algum tempo.'),
          ('O que significa capital excedente?', 'Significa que o valor líquido da venda, somado aos seus capitais próprios, cobre o preço, os impostos e a escritura da nova casa, e ainda sobra dinheiro. Nesse cenário não precisa de financiamento.'),
          ('A calculadora considera crédito ponte?', 'Não. Assume que a venda e a compra se resolvem na mesma altura. Se precisar de comprar antes de receber o dinheiro da venda, há custos de crédito intercalar que devem ser avaliados com o banco.'),
          ('E o imposto sobre mais-valias da casa que vendo?', 'Não está incluído. Se vender habitação própria e permanente e reinvestir noutra com o mesmo fim, a mais-valia pode ficar total ou parcialmente excluída de tributação, cumpridos os requisitos legais.')],
    cta_h2='Trocar de casa é coordenar duas operações.',
    cta_p='Preço de venda, prazo, proposta de compra e financiamento têm de bater certo. Planeamos a sequência consigo.',
    js='''    var obj = C.radio('objetivo');
    var pct = C.dec('comissao', 15) / 100;
    var r = C.calcularTroca({
      valorVenda: C.money('valorVenda'), comissaoMediacaoPct: pct, hipotecaEmFalta: C.money('hipoteca'), tipoTaxa: C.radio('tipo'),
      valorAquisicao: C.money('valor'), objetivo: obj, capitaisProprios: C.money('capitais'), isencaoJovem: C.jovem(obj)
    });
    var fin = r.montanteAFinanciar > 0;
    var total = f(Math.abs(r.valorAdicionalParaTrocar));

    C.set('outLabel', r.capitalExcedente ? 'Capital excedente estimado' : 'Valor adicional necessário para trocar de casa');
    C.set('outTotalLabel', r.capitalExcedente ? 'Capital excedente' : 'Valor adicional necessário');
    document.getElementById('resultado').classList.toggle('positivo', r.capitalExcedente);
    C.set('outTotal', total);
    C.set('outTotal2', total);
    C.set('outContext', r.capitalExcedente ? 'A venda cobre a nova compra e ainda sobra capital.' : fin ? 'Inclui custos estimados de financiamento.' : 'Sem necessidade de financiamento.');
    C.set('outReceita', f(r.receitaLiquidaVenda));
    C.set('outCapitais', f(r.capitaisProprios));
    C.set('outInvest', f(r.investimentoTotalSemFin));
    C.show('rowIsencao', r.compra.isencao.aplicada);
    C.set('outIsencao', '−' + f(r.compra.isencao.reducao));
    C.show('rowFinanciar', fin);
    C.set('outFinanciar', f(r.montanteAFinanciar));
    C.show('rowCustosFin', fin);
    C.set('outCustosFin', f(r.custoEstimadoFinanciamento));
    C.show('aviso', r.compra.isencao.cenario === 'nao-aplicavel-acima-limite');

    C.set('detVenda', 'Venda: ' + f(r.venda.valorVenda) + ' − mediação com IVA ' + f(r.venda.custoHonorarios) + ' − liquidação da hipoteca ' + f(r.venda.liquidacaoHipoteca) + ' = ' + f(r.receitaLiquidaVenda) + '.');
    C.set('detCompra', 'Compra: ' + f(r.compra.valorAquisicao) + ' + IMT ' + f(r.compra.imt) + ' + Imposto do Selo ' + f(r.compra.is) + ' + escritura ' + f(r.compra.escrituraRegistos) + ' = ' + f(r.investimentoTotalSemFin) + '.');
    C.show('detBanco', fin);
    C.set('detBanco', 'Custos bancários: ' + f(r.custos.avaliacaoBancaria + r.custos.comissaoDossier + r.custos.preparacaoMinutas) + ' fixos + Imposto do Selo sobre o financiamento ' + f(r.custos.isFinanciamento) + '.');''',
))


def head(title, desc, url, lds):
    scripts = ''.join('\n  <script type="application/ld+json">\n  %s\n  </script>' % json.dumps(d, ensure_ascii=False, separators=(',', ':')) for d in lds)
    return '''<!DOCTYPE html>
<html lang="pt-PT">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>%(t)s</title>
  <meta name="description" content="%(d)s">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="%(u)s">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="shortcut icon" href="/assets/favicon.svg">
  <meta property="og:title" content="%(t)s">
  <meta property="og:description" content="%(d)s">
  <meta property="og:type" content="website">
  <meta property="og:url" content="%(u)s">
  <meta property="og:locale" content="pt_PT">
  <meta property="og:image" content="https://edd.pt/assets/og-edd.webp">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://edd.pt/assets/og-edd.webp">
%(s)s

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,400&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/calculadoras.css">

  <script src="/assets/analytics.js"></script>
</head>

<body>

%(n)s
''' % dict(t=title, d=desc, u=url, s=scripts, n=NAV)


def crumbs(itens):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(itens)]}


FIM = '''
%s

%%s<script>
  var _t = document.getElementById('navToggle');
  var _m = document.getElementById('mobileMenu');
  var _c = document.getElementById('mobileClose');
  if (_t && _m && _c) {
    _t.addEventListener('click', function(){ _m.classList.add('open'); });
    _c.addEventListener('click', function(){ _m.classList.remove('open'); });
  }
</script>
<script src="/assets/cookie-consent.js"></script>
</body>
</html>
''' % FOOTER


def pagina(p):
    url = BASE + p['slug'] + '.html'
    lds = [crumbs([('Início', 'https://edd.pt/'), ('Calculadoras', BASE), (p['nome'], url)]),
           {"@context": "https://schema.org", "@type": "WebApplication", "@id": url + "#app", "name": p['nome'], "description": p['desc'], "url": url,
            "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "inLanguage": "pt-PT",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "provider": {"@type": "RealEstateAgent", "@id": "https://edd.pt/#organization", "name": "Equipa Diogo Dias", "url": "https://edd.pt"}},
           {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p['faqs']]}]
    detalhe = ''.join('\n            <h3>%s</h3>\n            %s' % (t, c) for t, c in p['detalhe'])
    faqs = ''.join('''
      <div class="faq-item">
        <button class="faq-q"><span class="faq-q-text">%s</span><span class="faq-icon">+</span></button>
        <div class="faq-a"><p>%s</p></div>
      </div>''' % qa for qa in p['faqs'])
    outras = ''.join('\n      <a href="/calculadoras/%s.html" class="related-card"><span class="related-title">%s</span><span class="related-arrow">&rarr;</span></a>' % (s, n)
                     for s, (n, _) in CALCS.items() if s != p['slug'])
    corpo = '''
<div class="hero">
  <div class="container">
    <div class="breadcrumb"><a href="/">Início</a> / <a href="/calculadoras/">Calculadoras</a> / %(curto)s</div>
    <span class="eyebrow">%(eyebrow)s</span>
    <h1>%(h1)s</h1>
    <p class="hero-lead">%(lead)s</p>
  </div>
</div>

<section class="calc-section">
  <div class="container">
    <div class="calc-grid">

      <form class="calc-panel" id="calcForm" autocomplete="off" onsubmit="return false">
        <h2>Dados para simulação</h2>
        <p class="calc-panel-desc">O resultado actualiza à medida que preenche.</p>

%(form)s
      </form>

      <div class="calc-panel" aria-live="polite">
        <div class="result-primary" id="resultado">
          <span class="eyebrow" id="outLabel">%(res_label)s</span>
          <div class="result-value" id="outTotal">—</div>
          <p class="result-context" id="outContext">%(context)s</p>
        </div>

        <table class="resumo">
          <tbody>
%(linhas)s
          </tbody>
        </table>

        <p class="notice warning" id="aviso" hidden>%(aviso)s</p>

        <details class="detalhe">
          <summary>Ver detalhe do cálculo</summary>
          <div class="detalhe-body">%(detalhe)s
          </div>
        </details>

        <p class="notice">%(nota)s</p>
      </div>

    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Notas e pressupostos</span>
      <h2>O que esta calculadora considera.</h2>
    </div>
    <div class="two-col">
      <div class="nota">
        <h3>Pressupostos</h3>
        %(pressupostos)s
      </div>
      <div class="nota">
        <h3>Não contempla</h3>
        %(nao)s
      </div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0;">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Perguntas frequentes</span>
      <h2>%(faq_h2)s</h2>
    </div>
    <div class="faq-list">%(faqs)s
    </div>
  </div>
</section>

<section class="related-section">
  <div class="container">
    <h3>Outras calculadoras</h3>
    <div class="related-links">%(outras)s
    </div>
  </div>
</section>

<section class="cta-section">
  <div class="container">
    <h2>%(cta_h2)s</h2>
    <p>%(cta_p)s</p>
    <div class="cta-actions">
      <a href="/contacto.html" class="btn-primary">Falar com Diogo Dias</a>
      <a href="tel:+351963399343" class="btn-outline">Ligar Agora</a>
    </div>
  </div>
</section>
''' % dict(p, curto=CALCS[p['slug']][0], linhas='\n'.join(p['linhas']), detalhe=detalhe, faqs=faqs, outras=outras,
           context={'imt-imposto-selo': 'IMT + Imposto do Selo sobre a aquisição', 'venda-casa': 'Depois da mediação e da liquidação da hipoteca.'}.get(p['slug'], ''),
           pressupostos=ul(p['pressupostos']).replace('              <li>', '          <li>').replace('            </ul>', '        </ul>'),
           nao=ul(p['nao']).replace('              <li>', '          <li>').replace('            </ul>', '        </ul>'))
    script = '''<script src="/assets/calc-imobiliario.js"></script>
<script>
  EDDCalc.iniciar(function () {
    var C = EDDCalc;
    var f = C.formatEuro;
%s
  });
</script>
''' % p['js']
    return head(p['title'], p['desc'], url, lds) + corpo + FIM % script


def indice():
    title = 'Calculadoras Imobiliárias — IMT, Prestação, Compra e Venda | EDD'
    desc = 'Calculadoras imobiliárias gratuitas para Portugal: IMT e Imposto do Selo, prestação da casa, custos de compra, valor líquido de venda e troca de casa.'
    lds = [crumbs([('Início', 'https://edd.pt/'), ('Calculadoras', BASE)]),
           {"@context": "https://schema.org", "@type": "ItemList", "name": "Calculadoras imobiliárias",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "url": BASE + s + '.html'} for i, (s, (n, _)) in enumerate(CALCS.items())]}]
    cards = ''.join('''
      <a href="/calculadoras/%s.html" class="calc-card">
        <h2>%s</h2>
        <p>%s</p>
        <span>Abrir calculadora &rarr;</span>
      </a>''' % (s, n, d) for s, (n, d) in CALCS.items())
    corpo = '''
<div class="hero">
  <div class="container">
    <div class="breadcrumb"><a href="/">Início</a> / Calculadoras</div>
    <span class="eyebrow">Calculadoras imobiliárias</span>
    <h1>Faça as contas antes de decidir.</h1>
    <p class="hero-lead">Cinco calculadoras para comprar, vender ou trocar de casa em Portugal. Gratuitas, sem registo, com os pressupostos à vista.</p>
  </div>
</div>

<section class="calc-section">
  <div class="container">
    <div class="calc-cards">%s
    </div>
  </div>
</section>

<section class="cta-section">
  <div class="container">
    <h2>Os números são o ponto de partida.</h2>
    <p>A decisão pede contexto: o imóvel, a zona e o momento. Falamos sobre o seu caso, sem compromisso.</p>
    <div class="cta-actions">
      <a href="/contacto.html" class="btn-primary">Falar com Diogo Dias</a>
      <a href="tel:+351963399343" class="btn-outline">Ligar Agora</a>
    </div>
  </div>
</section>
''' % cards
    return head(title, desc, BASE, lds) + corpo + FIM % ''


for p in PAGINAS:
    io.open(os.path.join(OUT, 'calculadoras', p['slug'] + '.html'), 'w', encoding='utf-8', newline='\n').write(pagina(p))
    print('ok', p['slug'])
io.open(os.path.join(OUT, 'calculadoras', 'index.html'), 'w', encoding='utf-8', newline='\n').write(indice())
print('ok index')

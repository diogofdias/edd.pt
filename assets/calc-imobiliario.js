/**
 * Cálculos imobiliários partilhados pelas calculadoras do edd.pt.
 * Fonte única das tabelas fiscais — todas as páginas em /calculadoras/ usam este ficheiro.
 *
 * Portado de re-pro-tools/src/lib/calc (imt.ts, selo.ts, isencao-jovem.ts, imt-selo.ts).
 *
 * IMT = valor × taxa do escalão − parcela a abater (Código do IMT, art. 17.º, tabelas 2026).
 * Acima de 660 982 € aplica-se taxa única. Terrenos: taxa única.
 */
(function (global) {
  'use strict';

  var IS_RATE_AQUISICAO = 0.008; // Verba 1.1 da TGIS

  /** Isenção jovem (DL n.º 48-A/2024): total até ao 1.º limite, parcial até ao 2.º. */
  var ISENCAO_JOVEM_LIMITE_TOTAL = 330539;
  var ISENCAO_JOVEM_LIMITE_PARCIAL = 660982;

  /** Habitação Própria Permanente. */
  var TABELA_HPP = [
    { limite: 0, taxa: 0, parcela: 0 },
    { limite: 106346, taxa: 0.02, parcela: 2126.92 },
    { limite: 145470, taxa: 0.05, parcela: 6491.02 },
    { limite: 198347, taxa: 0.07, parcela: 10457.96 },
    { limite: 330539, taxa: 0.08, parcela: 13763.35 },
    { limite: 660982, taxa: 0.06, parcela: 0, taxaUnica: true },
    { limite: 1150853, taxa: 0.075, parcela: 0, taxaUnica: true }
  ];

  /** Habitação Secundária. */
  var TABELA_HS = [
    { limite: 0, taxa: 0.01, parcela: 0 },
    { limite: 106346, taxa: 0.02, parcela: 1063.46 },
    { limite: 145470, taxa: 0.05, parcela: 5427.56 },
    { limite: 198347, taxa: 0.07, parcela: 9394.5 },
    { limite: 330539, taxa: 0.08, parcela: 12699.89 },
    { limite: 660982, taxa: 0.06, parcela: 0, taxaUnica: true },
    { limite: 1150853, taxa: 0.075, parcela: 0, taxaUnica: true }
  ];

  var OBJETIVO_LABELS = {
    'habitacao-propria-permanente': 'Habitação Própria Permanente',
    'habitacao-secundaria': 'Habitação Secundária',
    'terreno-rustico': 'Terreno Rústico',
    'terreno-urbano': 'Terreno Urbano'
  };

  function escalaoDe(valor, tabela) {
    var aplicavel = tabela[0];
    for (var i = 0; i < tabela.length; i++) {
      if (valor >= tabela[i].limite) aplicavel = tabela[i];
      else break;
    }
    return aplicavel;
  }

  function tabelaDe(objetivo) {
    return objetivo === 'habitacao-propria-permanente' ? TABELA_HPP : TABELA_HS;
  }

  /** IMT sem qualquer isenção. */
  function calcularIMT(valor, objetivo) {
    if (!(valor > 0)) return 0;
    if (objetivo === 'terreno-rustico') return valor * 0.05;
    if (objetivo === 'terreno-urbano') return valor * 0.065;
    var esc = escalaoDe(valor, tabelaDe(objetivo));
    return Math.max(0, valor * esc.taxa - esc.parcela);
  }

  function impostoSeloAquisicao(valor) {
    return valor > 0 ? valor * IS_RATE_AQUISICAO : 0;
  }

  function isencaoJovemCompativel(objetivo) {
    return objetivo === 'habitacao-propria-permanente';
  }

  function descreverEscalao(valor, objetivo) {
    if (objetivo === 'terreno-rustico') return 'Taxa única de 5 % (prédio rústico).';
    if (objetivo === 'terreno-urbano') return 'Taxa única de 6,5 % (outros prédios urbanos).';
    var esc = escalaoDe(valor, tabelaDe(objetivo));
    var pct = (esc.taxa * 100).toLocaleString('pt-PT', { maximumFractionDigits: 2 });
    return 'Escalão com taxa de ' + pct + ' %' + (esc.taxaUnica ? ' (taxa única).' : ', com parcela a abater de ' + formatEuro(esc.parcela) + '.');
  }

  /**
   * IMT + Imposto do Selo, com cenário de isenção jovem.
   * cenario: 'desativada' | 'total' | 'parcial' | 'nao-aplicavel-objetivo' | 'nao-aplicavel-acima-limite'
   */
  function calcularIMTSelo(input) {
    var valor = input.valorAquisicao > 0 ? input.valorAquisicao : 0;
    var objetivo = input.objetivo;
    var imtSem = calcularIMT(valor, objetivo);
    var isSem = impostoSeloAquisicao(valor);
    var imt = imtSem;
    var is = isSem;
    var cenario = 'desativada';

    if (input.isencaoJovem) {
      if (!isencaoJovemCompativel(objetivo)) {
        cenario = 'nao-aplicavel-objetivo';
      } else if (valor > ISENCAO_JOVEM_LIMITE_PARCIAL) {
        cenario = 'nao-aplicavel-acima-limite';
      } else if (valor <= ISENCAO_JOVEM_LIMITE_TOTAL) {
        cenario = 'total';
        imt = 0;
        is = 0;
      } else {
        // Parcial: só o excedente acima de 330 539 € é tributado (8 % IMT + 0,8 % IS).
        cenario = 'parcial';
        var excedente = valor - ISENCAO_JOVEM_LIMITE_TOTAL;
        imt = excedente * 0.08;
        is = excedente * IS_RATE_AQUISICAO;
      }
    }

    var totalSem = imtSem + isSem;
    var total = imt + is;
    return {
      valorAquisicao: valor,
      objetivo: objetivo,
      objetivoLabel: OBJETIVO_LABELS[objetivo],
      imtSemIsencao: imtSem,
      isSemIsencao: isSem,
      totalSemIsencao: totalSem,
      imt: imt,
      is: is,
      total: total,
      isencao: {
        cenario: cenario,
        aplicada: cenario === 'total' || cenario === 'parcial',
        reducao: totalSem - total
      }
    };
  }

  /* ─── Prestação, Compra, Venda e Troca (portado de prestacao.ts, compra.ts, venda.ts, troca.ts) ─── */

  var IS_RATE_FINANCIAMENTO = 0.008;
  var IS_RATE_PENALIZACAO = 0.008;
  var IVA_HONORARIOS = 0.23;
  var PENALIZACAO_AMORT_TAXA_FIXA = 0.02;
  var PENALIZACAO_AMORT_TAXA_VARIAVEL = 0.005;
  /** Custos fixos estimados (em euros) — assumidos por defeito. */
  var ESCRITURA_E_REGISTOS_ESTIMADO = 1000;
  var AVALIACAO_BANCARIA_ESTIMADA = 250;
  var COMISSAO_DOSSIER_ESTIMADA = 300;
  var PREPARACAO_MINUTAS_ESTIMADA = 750;
  /** Factor conservador aplicado ao montante teórico a financiar (+10 %). */
  var FACTOR_CONSERVADOR_FINANCIAMENTO = 1.1;

  /** Prestação constante (regime francês): PMT = P × i / (1 − (1 + i)^(−n)). */
  function calcularPrestacao(input) {
    var montante = Math.max(0, input.valorImovel - input.entradaInicial);
    var prazoMeses = Math.max(0, Math.round(input.prazoAnos * 12));
    var i = input.taxaAnual / 12;
    var pmt = 0;
    if (montante > 0 && prazoMeses > 0) {
      pmt = i === 0 ? montante / prazoMeses : (montante * i) / (1 - Math.pow(1 + i, -prazoMeses));
    }
    var totalPago = pmt * prazoMeses;
    return {
      montanteFinanciado: montante,
      prestacaoMensal: pmt,
      totalPago: totalPago,
      jurosEstimadosPagos: Math.max(0, totalPago - montante),
      prazoMeses: prazoMeses,
      ltv: input.valorImovel > 0 ? montante / input.valorImovel : 0
    };
  }

  /** Custos bancários estimados para um dado montante a financiar. */
  function custosFinanciamento(montante) {
    var tem = montante > 0;
    var c = {
      avaliacaoBancaria: tem ? AVALIACAO_BANCARIA_ESTIMADA : 0,
      comissaoDossier: tem ? COMISSAO_DOSSIER_ESTIMADA : 0,
      preparacaoMinutas: tem ? PREPARACAO_MINUTAS_ESTIMADA : 0,
      isFinanciamento: tem ? montante * IS_RATE_FINANCIAMENTO : 0
    };
    c.total = c.avaliacaoBancaria + c.comissaoDossier + c.preparacaoMinutas + c.isFinanciamento;
    return c;
  }

  function calcularCompra(input) {
    var imp = calcularIMTSelo(input);
    var valor = imp.valorAquisicao;
    var escrituraRegistos = valor > 0 ? ESCRITURA_E_REGISTOS_ESTIMADO : 0;
    var impostosERegistos = imp.imt + imp.is + escrituraRegistos;
    var investimentoTotalSemFin = valor + impostosERegistos;

    // Montante teórico a financiar (com factor conservador, só se positivo).
    var diferenca = investimentoTotalSemFin - Math.max(0, input.capitaisProprios);
    var montanteAFinanciar = diferenca > 0 ? diferenca * FACTOR_CONSERVADOR_FINANCIAMENTO : 0;
    var custos = custosFinanciamento(montanteAFinanciar);
    var investimentoTotalComFin = investimentoTotalSemFin + custos.total;

    return {
      valorAquisicao: valor,
      objetivo: input.objetivo,
      imt: imp.imt,
      imtSemIsencao: imp.imtSemIsencao,
      is: imp.is,
      isSemIsencao: imp.isSemIsencao,
      isencao: imp.isencao,
      escrituraRegistos: escrituraRegistos,
      impostosERegistos: impostosERegistos,
      investimentoTotalSemFin: investimentoTotalSemFin,
      montanteAFinanciar: montanteAFinanciar,
      custos: custos,
      custoEstimadoFinanciamento: custos.total,
      investimentoTotalComFin: investimentoTotalComFin,
      totalNecessarioParaComprar: montanteAFinanciar > 0 ? investimentoTotalComFin : investimentoTotalSemFin
    };
  }

  function calcularVenda(input) {
    var valorVenda = Math.max(0, input.valorVenda);
    var comissaoMediacao = valorVenda * Math.max(0, input.comissaoMediacaoPct);
    var ivaHonorarios = comissaoMediacao * IVA_HONORARIOS;
    var custoHonorarios = comissaoMediacao + ivaHonorarios;

    var penalizacaoTaxa = input.tipoTaxa === 'fixa' ? PENALIZACAO_AMORT_TAXA_FIXA : PENALIZACAO_AMORT_TAXA_VARIAVEL;
    var hipoteca = Math.max(0, input.hipotecaEmFalta);
    var penalizacaoAmortizacao = hipoteca * penalizacaoTaxa;
    var isPenalizacao = penalizacaoAmortizacao * IS_RATE_PENALIZACAO;
    var liquidacaoHipoteca = hipoteca + penalizacaoAmortizacao + isPenalizacao;

    return {
      valorVenda: valorVenda,
      comissaoMediacao: comissaoMediacao,
      ivaHonorarios: ivaHonorarios,
      custoHonorarios: custoHonorarios,
      hipoteca: hipoteca,
      penalizacaoTaxa: penalizacaoTaxa,
      penalizacaoAmortizacao: penalizacaoAmortizacao,
      isPenalizacao: isPenalizacao,
      liquidacaoHipoteca: liquidacaoHipoteca,
      receitaLiquida: valorVenda - custoHonorarios - liquidacaoHipoteca
    };
  }

  /** Troca = Venda + Compra; a receita líquida da venda abate ao investimento na nova casa. */
  function calcularTroca(input) {
    var venda = calcularVenda(input);
    var capitais = Math.max(0, input.capitaisProprios);
    var compra = calcularCompra({
      valorAquisicao: input.valorAquisicao,
      objetivo: input.objetivo,
      capitaisProprios: capitais + Math.max(0, venda.receitaLiquida),
      isencaoJovem: input.isencaoJovem
    });

    // Positivo = falta capital; negativo = sobra.
    var defice = compra.investimentoTotalSemFin - venda.receitaLiquida - capitais;
    var montanteAFinanciar = defice > 0 ? defice * FACTOR_CONSERVADOR_FINANCIAMENTO : 0;
    var custos = custosFinanciamento(montanteAFinanciar);

    return {
      venda: venda,
      compra: compra,
      investimentoTotalSemFin: compra.investimentoTotalSemFin,
      receitaLiquidaVenda: venda.receitaLiquida,
      capitaisProprios: capitais,
      capitalAdicionalNecessario: defice,
      montanteAFinanciar: montanteAFinanciar,
      custos: custos,
      custoEstimadoFinanciamento: custos.total,
      valorAdicionalParaTrocar: defice > 0 ? defice + custos.total : defice,
      capitalExcedente: defice < 0
    };
  }

  function formatEuro(n) {
    return (n || 0).toLocaleString('pt-PT', {
      style: 'currency',
      currency: 'EUR',
      useGrouping: 'always', // pt-PT não agrupa milhares abaixo de 10 000 por omissão
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  /** Lê um valor escrito à portuguesa ("250 000", "250.000,50") como número. */
  function parseValor(texto) {
    var limpo = String(texto || '').replace(/[^\d,]/g, '').replace(',', '.');
    var n = parseFloat(limpo);
    return isFinite(n) ? n : 0;
  }

  /** Lê percentagens e prazos: aceita vírgula ou ponto decimal, limitado a [0, max]. */
  function parseDecimal(texto, max) {
    var n = parseFloat(String(texto || '').replace(/[^\d.,]/g, '').replace(',', '.'));
    if (!isFinite(n) || n < 0) return 0;
    return max != null && n > max ? max : n;
  }

  function formatPercent(fracao, casas) {
    return (fracao * 100).toLocaleString('pt-PT', { maximumFractionDigits: casas == null ? 2 : casas }) + ' %';
  }

  /* ─── Ligação ao HTML das páginas ─── */

  function el(id) { return document.getElementById(id); }
  function set(id, texto) { el(id).textContent = texto; }
  function show(id, visivel) { el(id).hidden = !visivel; }
  function money(id) { return parseValor(el(id).value); }
  function dec(id, max) { return parseDecimal(el(id).value, max); }
  function radio(nome) { return document.querySelector('input[name="' + nome + '"]:checked').value; }

  /** Actualiza o estado do interruptor de isenção jovem e devolve se está activo. */
  function jovem(objetivo) {
    var input = el('jovem');
    var hint = el('jovemHint');
    if (!hint.dataset.elegivel) hint.dataset.elegivel = hint.textContent;
    var compat = isencaoJovemCompativel(objetivo);
    input.disabled = !compat;
    if (!compat) input.checked = false;
    el('jovemLabel').classList.toggle('disabled', !compat);
    hint.textContent = compat ? hint.dataset.elegivel : 'A isenção jovem só se aplica a Habitação Própria Permanente.';
    return input.checked;
  }

  /** Liga o formulário #calcForm à função de cálculo da página e trata das FAQ. */
  function iniciar(render) {
    document.querySelectorAll('#calcForm input').forEach(function (input) {
      input.addEventListener(input.type === 'text' ? 'input' : 'change', render);
      if (input.hasAttribute('data-money')) {
        input.addEventListener('blur', function () {
          var n = parseValor(input.value);
          input.value = n ? n.toLocaleString('pt-PT', { useGrouping: 'always', maximumFractionDigits: 2 }).replace(/ /g, ' ') : '0';
        });
      }
    });
    document.querySelectorAll('.faq-q').forEach(function (btn) {
      btn.addEventListener('click', function () {
        btn.closest('.faq-item').classList.toggle('open');
      });
    });
    render();
  }

  global.EDDCalc = {
    calcularPrestacao: calcularPrestacao,
    calcularCompra: calcularCompra,
    calcularVenda: calcularVenda,
    calcularTroca: calcularTroca,
    formatPercent: formatPercent,
    parseDecimal: parseDecimal,
    set: set,
    show: show,
    money: money,
    dec: dec,
    radio: radio,
    jovem: jovem,
    iniciar: iniciar,
    ISENCAO_JOVEM_LIMITE_TOTAL: ISENCAO_JOVEM_LIMITE_TOTAL,
    ISENCAO_JOVEM_LIMITE_PARCIAL: ISENCAO_JOVEM_LIMITE_PARCIAL,
    OBJETIVO_LABELS: OBJETIVO_LABELS,
    calcularIMT: calcularIMT,
    impostoSeloAquisicao: impostoSeloAquisicao,
    isencaoJovemCompativel: isencaoJovemCompativel,
    descreverEscalao: descreverEscalao,
    calcularIMTSelo: calcularIMTSelo,
    formatEuro: formatEuro,
    parseValor: parseValor
  };
})(window);

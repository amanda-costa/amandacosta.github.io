/* ==========================================================================
   Interações da interface: menu, progresso de rolagem, paralaxe da prancha
   e revelação escalonada dos blocos.
   ========================================================================== */

(function () {
  'use strict';

  var parado = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- Menu (mobile) -------------------------------------------------- */

  var toggle = document.getElementById('menuToggle');
  var panel = document.getElementById('menuPanel');

  if (toggle && panel) {
    function menu(aberto) {
      panel.classList.toggle('is-open', aberto);
      toggle.setAttribute('aria-expanded', String(aberto));
      toggle.textContent = aberto ? 'Fechar' : 'Menu';
      // O painel cobre a tela inteira: sem travar o corpo, a rolagem do dedo
      // atravessa e a página anda por baixo do menu.
      document.body.classList.toggle('menu-aberto', aberto);
    }

    toggle.addEventListener('click', function () {
      menu(!panel.classList.contains('is-open'));
    });

    panel.addEventListener('click', function (e) {
      // O alvo pode ser o <span> do nome ou o pinheiro, não só o <a>.
      if (!e.target.closest || !e.target.closest('a')) return;
      menu(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.classList.contains('is-open')) menu(false);
    });

  }

  /* --- Dock (desktop): os ícones crescem perto do cursor --------------- */

  // Como no Dock do macOS, cada ícone cresce conforme a distância vertical
  // até o cursor, numa curva de cosseno: o mais próximo chega a 1,5× e o
  // efeito some a 110px. Só com mouse e sem pedido de movimento reduzido.
  var dock = document.querySelector('.dock');

  if (dock && !parado && window.matchMedia('(hover: hover)').matches) {
    var icones = [].slice.call(dock.querySelectorAll('.dock__item'));
    var cursorY = null;
    var ampliando = false;

    function ampliar() {
      ampliando = false;
      icones.forEach(function (el) {
        var s = 1;
        if (cursorY !== null) {
          var r = el.getBoundingClientRect();
          var d = Math.abs(cursorY - (r.top + r.height / 2));
          if (d < 110) s = 1 + 0.5 * (Math.cos(Math.PI * d / 110) + 1) / 2;
        }
        el.style.setProperty('--s', s.toFixed(3));
      });
    }

    dock.addEventListener('mousemove', function (e) {
      cursorY = e.clientY;
      if (ampliando) return;
      ampliando = true;
      requestAnimationFrame(ampliar);
    });

    dock.addEventListener('mouseleave', function () {
      cursorY = null;
      ampliar();
    });
  }

  /* --- Rolagem: progresso e paralaxe ---------------------------------- */

  var barra = document.getElementById('progresso');
  var prancha = document.querySelector('.hero__prancha');
  var agendado = false;

  function aoRolar() {
    if (barra) {
      var total = document.documentElement.scrollHeight - window.innerHeight;
      var pct = total > 0 ? Math.min(1, window.scrollY / total) : 0;
      barra.style.transform = 'scaleX(' + pct + ')';
    }

    // A prancha sobe a 12% da velocidade da página, só enquanto o hero
    // ainda está visível — depois disso não há o que animar.
    if (prancha && !parado && window.scrollY < window.innerHeight * 1.4) {
      prancha.style.setProperty('--py', (-window.scrollY * 0.12).toFixed(1) + 'px');
    }

    pintar();
    marcarEntrada();

    agendado = false;
  }

  if (barra || prancha) {
    window.addEventListener('scroll', function () {
      if (agendado) return;
      agendado = true;
      requestAnimationFrame(aoRolar);
    }, { passive: true });
    aoRolar();
  }

  /* --- Cor de fundo interpolada na rolagem ----------------------------- */

  // Cada bloco declara em que papel vive. Em vez de trocar a cor de uma vez
  // quando o bloco cruza o meio da tela, a cor é interpolada em oklch ao
  // longo de mais de uma tela de rolagem — a passagem entre claro e escuro
  // vira um esmaecimento contínuo, sem degrau.
  var blocos = [].slice.call(document.querySelectorAll('[data-bg]'))
    .filter(function (el) { return el !== document.body; });

  function tokens(nome) {
    var raiz = getComputedStyle(document.documentElement);
    function ler(v) { return raiz.getPropertyValue(v).trim(); }
    if (nome === 'petroleo') {
      return [ler('--petroleo'), ler('--on-dark'), ler('--muted-on-dark'), ler('--rule-dark')];
    }
    if (nome === 'rosa') {
      return [ler('--papel-rosa'), ler('--petroleo'), ler('--cinza'), ler('--traco-rosa')];
    }
    return [ler('--papel'), ler('--petroleo'), ler('--cinza'), ler('--traco')];
  }

  function paraOklch(valor) {
    var m = /oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)/.exec(valor);
    if (!m) return null;
    var L = parseFloat(m[1]);
    if (m[2]) L /= 100;
    return [L, parseFloat(m[3]), parseFloat(m[4])];
  }

  // Interpola matiz pelo arco curto: entre o petróleo (243°) e o rosa (18°)
  // o caminho longo passaria pelo verde.
  function misturar(a, b, t) {
    var dh = b[2] - a[2];
    if (dh > 180) dh -= 360;
    else if (dh < -180) dh += 360;
    var h = (a[2] + dh * t) % 360;
    if (h < 0) h += 360;
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, h];
  }

  // Smoothstep, e não smootherstep: o smootherstep amacia mais as pontas,
  // mas em troca amontoa a mudança no meio — inclinação de pico 1,875 contra
  // 1,5. O que se percebe como choque é justamente o trecho mais rápido, e
  // não a partida. Aqui o que importa é achatar o pico.
  function suave(t) {
    return t * t * (3 - 2 * t);
  }

  function escrever(c) {
    return 'oklch(' + c[0].toFixed(4) + ' ' + c[1].toFixed(4) + ' ' + c[2].toFixed(2) + ')';
  }

  var paletas = blocos.map(function (el) {
    return tokens(el.getAttribute('data-bg')).map(paraOklch);
  });

  var VARS = ['--bg', '--fg', '--muted', '--rule'];

  function pintar() {
    // Pode ser chamada pelo laço de rolagem antes deste bloco ser avaliado.
    if (!blocos || !blocos.length) return;

    var meio = window.innerHeight / 2;
    // A passagem se estende por mais de uma tela de rolagem: quanto mais
    // longo o percurso, menor o salto de cor por quadro. Com 1.2 de tela e a
    // trava de bloco em 0.95, a mudança de claridade no trecho mais rápido
    // cai de 0,28 para 0,16 por 100px de rolagem.
    var base = window.innerHeight * 1.2;
    var caixas = blocos.map(function (el) { return el.getBoundingClientRect(); });
    var atual = paletas[0].slice();

    for (var i = 1; i < blocos.length; i++) {
      // A zona é centrada na fronteira, então come metade de cada bloco
      // vizinho: acima de 1 altura duas passagens se sobrepõem e a cor cheia
      // nunca chega. 0.95 é o máximo com folga — e é essa trava, não a base,
      // que limita a passagem junto dos blocos curtos.
      var zona = Math.min(base, caixas[i - 1].height * 0.95, caixas[i].height * 0.95);
      var f = (meio - (caixas[i].top - zona / 2)) / zona;
      if (f <= 0) break;
      if (f > 1) f = 1;

      // O fundo desliza por toda a zona; a tinta (texto, fios) segura a cor
      // de origem e vira no terço do meio. Assim o instante em que as duas se
      // cruzam em tons médios — e o contraste cai — fica curto.
      var fFundo = suave(f);
      var fTinta = suave(Math.max(0, Math.min(1, (f - 0.36) / 0.28)));

      atual[0] = misturar(atual[0], paletas[i][0], fFundo);
      for (var v = 1; v < VARS.length; v++) {
        atual[v] = misturar(atual[v], paletas[i][v], fTinta);
      }
      if (f < 1) break;
    }

    for (var k = 0; k < VARS.length; k++) {
      document.body.style.setProperty(VARS[k], escrever(atual[k]));
    }
  }

  pintar();

  /* --- Linha do tempo: a entrada onde a leitura está ------------------ */

  var entradas = [].slice.call(document.querySelectorAll('.tempo__item'));

  function marcarEntrada() {
    // Pode ser chamada pelo laço de rolagem antes deste bloco ser avaliado.
    if (!entradas || !entradas.length) return;
    var leitura = window.innerHeight * 0.45;
    var atual = -1;
    entradas.forEach(function (item, i) {
      if (item.getBoundingClientRect().top <= leitura) atual = i;
    });
    entradas.forEach(function (item, i) {
      item.classList.toggle('is-atual', i === atual);
    });
  }

  /* --- Trilha horizontal: o fio se desenha ao entrar ------------------- */

  var trilhas = [].slice.call(document.querySelectorAll('.trilha'));

  function medirTrilha(ol) {
    // Só a trilha acadêmica precisa medir onde o fio cai; nos selos ele é
    // fixo no topo da lista.
    var corpo = ol.querySelector('.trilha__corpo');
    if (!corpo) return;
    var y = corpo.getBoundingClientRect().top - ol.getBoundingClientRect().top;
    ol.style.setProperty('--trilho-y', y.toFixed(1) + 'px');
  }

  if (trilhas.length) {
    trilhas.forEach(medirTrilha);
    window.addEventListener('resize', function () { trilhas.forEach(medirTrilha); });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { trilhas.forEach(medirTrilha); });
    }

    if (!('IntersectionObserver' in window) || parado) {
      trilhas.forEach(function (ol) { ol.classList.add('is-desenhada'); });
    } else {
      var obsTrilha = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (e) {
          if (!e.isIntersecting) return;
          medirTrilha(e.target);
          e.target.classList.add('is-desenhada');
          obsTrilha.unobserve(e.target);
        });
      }, { rootMargin: '0px 0px -18% 0px' });
      trilhas.forEach(function (ol) { obsTrilha.observe(ol); });
    }
  }

  marcarEntrada();

  /* --- Detalhes expansíveis das experiências --------------------------- */

  [].forEach.call(document.querySelectorAll('.detalhe__botao'), function (botao) {
    var alvo = document.getElementById(botao.getAttribute('aria-controls'));
    if (!alvo) return;

    botao.addEventListener('click', function () {
      var aberto = alvo.classList.toggle('is-aberto');
      botao.setAttribute('aria-expanded', String(aberto));
      botao.querySelector('.detalhe__rotulo').textContent =
        aberto ? 'Ocultar detalhes' : 'Ver detalhes';
    });
  });

  /* --- Revelação em rolagem ------------------------------------------- */

  var alvos = document.querySelectorAll('.reveal');

  if (!('IntersectionObserver' in window) || parado) {
    Array.prototype.forEach.call(alvos, function (el) { el.classList.add('is-in'); });
    return;
  }

  var obs = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (entrada) {
      if (!entrada.isIntersecting) return;
      entrada.target.classList.add('is-in');
      obs.unobserve(entrada.target);
    });
  }, { rootMargin: '0px 0px -10% 0px' });

  Array.prototype.forEach.call(alvos, function (el) { obs.observe(el); });
})();

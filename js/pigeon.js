/* ==========================================================================
   Pombo pixel art que segue o mouse.
   Voa enquanto o cursor se mexe; quando o cursor para, desce até o fim
   da página e fica ciscando o chão até o mouse mexer de novo.
   ========================================================================== */

(function () {
  'use strict';

  // Sem cursor (touch) ou com movimento reduzido, o pombo não aparece.
  if (!window.matchMedia('(pointer: fine)').matches) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  /* --- Sprites -------------------------------------------------------- */

  var PX = 4;    // tamanho do "pixel" do sprite
  var GW = 18;   // grid do sprite
  var GH = 15;
  var FOOT_Y = 15; // linha dos pés, ancorada no chão

  // Paleta da identidade: azul-petróleo, cinza-azulado, papel frio e o
  // rosa antigo como único gesto quente (olho e patas).
  var COLORS = {
    D: '#2c3945', // penas escuras (cabeça, asa, cauda) — petróleo
    G: '#6c7c8c', // cinza do corpo — cinza-azulado
    L: '#dde3e8', // barriga — papel frio
    T: '#4f6c78', // brilho do pescoço
    B: '#1d262e', // bico
    E: '#c98a92', // olho — rosa antigo
    O: '#c98a92'  // patas — rosa antigo
  };

  // Parado / andando. Dividido em cabeça, pescoço e corpo para a cabeça
  // poder se deslocar à parte (o balanço de quem anda). As patas são
  // desenhadas à parte, mais abaixo.
  var HEAD = [
    '..........DDDD....',
    '.........DDDDDD...',
    '.........DDEDDD...',
    '.........DDDDDDBBB',
    '..........DDDDDB..'
  ];

  var NECK = [
    '.........TTTTT....',
    '........TTTTTG....'
  ];

  var BODY = [
    '......GGGGGGGGG...',
    '....GGGGGGGGGGG...',
    '..DDGGDDDDGGGGG...',
    '.DDDDGDDDDDGGGG...',
    '.DDDDLLLLLLLLL....',
    '....LLLLLLLLL.....'
  ];

  var NECK_Y = 5;
  var BODY_Y = 7;

  // Ciscando: corpo no lugar, pescoço curvado à frente e cabeça em pé
  // junto ao chão, com o bico apontando para baixo.
  var PECK = [
    '..................',
    '..................',
    '..................',
    '..................',
    '..................',
    '.....GGGG.........',
    '...GGGGGGGG.......',
    '..GGGGGGGGGGG.....',
    '..GGGGGGGGGGGT....',
    '..DDGGDDDDGGGTT...',
    '.DDDDGDDDDDGGTTT..',
    '.DDDDLLLLLLLLDDDD.',
    '....LLLLLLLLLDEDD.',
    '............DDDDD.',
    '..............BBB.'
  ];

  // Voando, asas para cima (patas recolhidas já incluídas)
  var FLY_UP = [
    '...DD.............',
    '..DDDD....DDDD....',
    '..DDDDD..DDEDDD...',
    '...DDDDD.DDDDDDBBB',
    '....DDDDDDDDDDB...',
    '.....LLLGGTTTT....',
    '....GGGGGGGGGG....',
    '..DDGGGGGGGGGG....',
    '.DDDGGGGGGGGG.....',
    '...DLLLLLLLLL.....',
    '.....LLLLLL.......',
    '..................',
    '..................',
    '.......OO.........',
    '........O.........'
  ];

  // Voando, asas para baixo
  var FLY_DOWN = [
    '..................',
    '..........DDDD....',
    '.........DDEDDD...',
    '.........DDDDDDBBB',
    '..........DDDDDB..',
    '......GGGGTTTT....',
    '....GGGGGGGGGG....',
    '..DDGGGGGGGGGG....',
    '.DDDDDDDDDGGGG....',
    '...DDDDDDDDDLL....',
    '....DDDDDDDD......',
    '.....DDDDDD.......',
    '......LLLL........',
    '.......OO.........',
    '........O.........'
  ];

  var LEGS_A = [
    '......O...O.......',
    '.....OOO.OOO......'
  ];

  var LEGS_B = [
    '.......OO.........',
    '......OOOO........'
  ];

  var LEGS_Y = 13;

  /* --- Canvas --------------------------------------------------------- */

  var canvas = document.createElement('canvas');
  var dpr = window.devicePixelRatio || 1;
  canvas.width = GW * PX * dpr;
  canvas.height = GH * PX * dpr;
  canvas.style.cssText =
    'position:fixed;left:0;top:0;width:' + GW * PX + 'px;height:' + GH * PX + 'px;' +
    'pointer-events:none;z-index:9999;will-change:transform;';
  canvas.setAttribute('aria-hidden', 'true');

  var ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.imageSmoothingEnabled = false;

  // ox/oy em células do grid; ox desloca o sprite no eixo do corpo
  // (positivo = para a frente, já que o sprite é espelhado ao virar).
  function drawSprite(rows, oy, ox) {
    ox = ox || 0;
    for (var r = 0; r < rows.length; r++) {
      var row = rows[r];
      for (var c = 0; c < row.length; c++) {
        var ch = row.charAt(c);
        if (ch === '.') continue;
        ctx.fillStyle = COLORS[ch];
        ctx.fillRect((c + ox) * PX, (oy + r) * PX, PX, PX);
      }
    }
  }

  /* --- Estado --------------------------------------------------------- */

  var IDLE_TIME = 0.26;   // cursor parado por esse tempo (s) -> desce ao chão
  var MOVE_EPS = 2;       // deslocamento acumulado (px) para contar como movimento
  var FLOOR_GAP = 6;      // distância dos pés até a base da janela

  var CHASE_K = 13;       // rigidez da perseguição (rad/s) — maior = mais colado
  var MAX_SPEED = 1400;   // teto de velocidade em voo (px/s)
  var HOVER_Y = 26;       // voa um pouco acima do cursor, para não cobri-lo

  var WALK_SPEED = 48;    // velocidade de caminhada (px/s)
  var WANDER_RANGE = 320; // alcance de cada trecho de caminhada (px)
  var HEAD_BOB = 3;       // recuo máximo da cabeça, em células do grid
  var THRUST_MULT = 5;    // quão mais rápido é o arranco da cabeça para a frente

  var state = 'fly';
  var x = window.innerWidth * 0.5;
  var y = window.innerHeight * 0.35;
  var vx = 0, vy = 0;
  var facing = 1;
  var wanderX = null;
  var pecksLeft = 0;
  var walksLeft = 0;
  var peckT = 0;
  var clock = 0;
  var headBob = 0;        // 0 = cabeça à frente (repouso); negativo = recuada
  var bobPhase = 'hold';  // 'hold' = parada no espaço; 'thrust' = arranco
  var sinceMove = 999;    // começa "parado": desce e cisca até o mouse mexer
  var moveAccum = 0;

  var mouse = { x: window.innerWidth * 0.5, y: window.innerHeight * 0.5 };

  document.addEventListener('mousemove', function (e) {
    var dx = e.clientX - mouse.x;
    var dy = e.clientY - mouse.y;
    mouse.x = e.clientX;
    mouse.y = e.clientY;

    // Acumula: movimentos lentos também contam, só tremidas isoladas são ignoradas.
    moveAccum += Math.hypot(dx, dy);
    if (moveAccum < MOVE_EPS) return;

    moveAccum = 0;
    sinceMove = 0;
    if (state !== 'fly') takeOff();
  }, { passive: true });

  // Mola criticamente amortecida, integração implícita: converge sem oscilar
  // e é estável para qualquer dt (não depende da taxa de quadros).
  function spring(pos, vel, target, k, dt) {
    var f = 1 + 2 * dt * k;
    var hoo = dt * k * k;
    var hhoo = dt * hoo;
    var detInv = 1 / (f + hhoo);
    return {
      p: (f * pos + dt * vel + hhoo * target) * detInv,
      v: (vel + hoo * (target - pos)) * detInv
    };
  }

  // O chão é a base da janela visível (o canvas é position:fixed).
  function floorY() {
    return window.innerHeight - FLOOR_GAP;
  }

  function newWanderTarget() {
    var tx = x + (Math.random() * 2 - 1) * WANDER_RANGE;
    wanderX = Math.max(30, Math.min(window.innerWidth - 30, tx));
  }

  // Ciclo de cabeça do pombo: ela fica cravada no espaço enquanto o corpo
  // avança (por isso recua em relação ao corpo) e então dá um arranco à frente.
  function updateHeadBob(dt, walking) {
    if (!walking) {
      headBob += (0 - headBob) * Math.min(1, 10 * dt);
      bobPhase = 'hold';
      return;
    }

    var cells = WALK_SPEED / PX; // células por segundo

    if (bobPhase === 'hold') {
      headBob -= cells * dt;
      if (headBob <= -HEAD_BOB) {
        headBob = -HEAD_BOB;
        bobPhase = 'thrust';
      }
    } else {
      headBob += cells * THRUST_MULT * dt;
      if (headBob >= 0) {
        headBob = 0;
        bobPhase = 'hold';
      }
    }
  }

  function takeOff() {
    state = 'fly';
    vy = -170;
    vx = facing * 40;
    headBob = 0;
    bobPhase = 'hold';
  }

  /* --- Atualização ---------------------------------------------------- */

  function update(dt) {
    clock += dt;
    sinceMove += dt;

    var moving = sinceMove < IDLE_TIME;
    if (!moving) moveAccum = 0;

    if (state === 'fly') {
      // Persegue um ponto logo acima do cursor.
      var sx = spring(x, vx, mouse.x, CHASE_K, dt);
      var sy = spring(y, vy, mouse.y - HOVER_Y, CHASE_K, dt);
      vx = sx.v;
      vy = sy.v;

      var sp = Math.hypot(vx, vy);
      if (sp > MAX_SPEED) {
        // Acima do teto, integra na mão para o corte valer na posição também.
        var m = MAX_SPEED / sp;
        vx *= m;
        vy *= m;
        x += vx * dt;
        y += vy * dt;
      } else {
        x = sx.p;
        y = sy.p;
      }

      if (Math.abs(vx) > 8) facing = vx > 0 ? 1 : -1;

      // Cursor parou: planeia para o chão.
      if (!moving) {
        state = 'descend';
        wanderX = Math.max(30, Math.min(window.innerWidth - 30, x + facing * 40));
      }

    } else if (state === 'descend') {
      var g = floorY();

      vx += (wanderX - x) * 1.6 * dt;
      vx *= 0.94;
      vy += 300 * dt;
      if (vy > 320) vy = 320;

      x += vx * dt;
      y += vy * dt;

      if (Math.abs(vx) > 12) facing = vx > 0 ? 1 : -1;

      if (y >= g) {
        y = g;
        vx = vy = 0;
        state = 'walk';
        wanderX = null;
      }

    } else if (state === 'walk') {
      y = floorY();

      if (wanderX === null) newWanderTarget();

      var dx = wanderX - x;
      if (Math.abs(dx) < 3) {
        if (walksLeft > 0) {
          // Ainda tem trecho para andar: escolhe outro destino sem parar.
          walksLeft--;
          wanderX = null;
        } else {
          state = 'peck';
          pecksLeft = 1 + Math.floor(Math.random() * 3);
          peckT = 0;
        }
        updateHeadBob(dt, false);
      } else {
        facing = dx > 0 ? 1 : -1;
        x += facing * WALK_SPEED * dt;
        updateHeadBob(dt, true);
      }

    } else if (state === 'peck') {
      y = floorY();
      updateHeadBob(dt, false);

      peckT += dt;
      if (peckT > 0.5) {
        peckT = 0;
        pecksLeft--;
        if (pecksLeft <= 0) {
          state = 'walk';
          wanderX = null;
          walksLeft = 1 + Math.floor(Math.random() * 3);
        }
      }
    } else {
      updateHeadBob(dt, false);
    }

    // Mantém o pombo dentro da janela.
    x = Math.max(20, Math.min(window.innerWidth - 20, x));
    y = Math.max(40, Math.min(floorY(), y));
  }

  /* --- Desenho -------------------------------------------------------- */

  function render() {
    ctx.clearRect(0, 0, GW * PX, GH * PX);

    ctx.save();
    if (facing < 0) {
      ctx.translate(GW * PX, 0);
      ctx.scale(-1, 1);
    }

    if (state === 'fly' || state === 'descend') {
      var wingsUp = Math.floor(clock * 11) % 2 === 0;
      drawSprite(wingsUp ? FLY_UP : FLY_DOWN, 0);
    } else if (state === 'peck' && peckT < 0.3) {
      drawSprite(PECK, 0);
      drawSprite(LEGS_A, LEGS_Y);
    } else {
      var stepping = state === 'walk' && Math.floor(clock * 6) % 2 === 1;
      var lift = stepping ? -1 : 0;
      var hx = Math.round(headBob);

      // O corpo sobe e desce no passo; a cabeça fica estável, como no
      // pombo de verdade — o pescoço absorve a diferença.
      drawSprite(BODY, BODY_Y + lift, 0);
      drawSprite(NECK, NECK_Y + lift, Math.round(hx / 2));
      drawSprite(HEAD, 0, hx);
      drawSprite(stepping ? LEGS_B : LEGS_A, LEGS_Y, 0);
    }

    ctx.restore();

    canvas.style.transform =
      'translate3d(' + (x - (GW * PX) / 2) + 'px,' + (y - FOOT_Y * PX) + 'px,0)';
  }

  /* --- Loop ----------------------------------------------------------- */

  var last = null;
  function frame(now) {
    if (last === null) last = now;
    var dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    update(dt);
    render();
    requestAnimationFrame(frame);
  }

  function start() {
    document.body.appendChild(canvas);
    requestAnimationFrame(frame);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();

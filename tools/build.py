# -*- coding: utf-8 -*-
"""Gera as páginas estáticas do portfólio a partir de parciais comuns.

    python3 tools/build.py

IMPORTANTE: index.html e projetos/*.html são GERADOS por este script.
Editar esses arquivos à mão funciona até a próxima execução, quando são
sobrescritos. Toda mudança de conteúdo ou de marcação deve ser feita aqui.
O CSS (style.css, styleguide.css) e o JS (js/site.js) são escritos à mão e
o script não encosta neles.

O script carimba a data/hora nos links de CSS e JS (?v=...), o que força o
navegador a buscar os arquivos novos em vez de servir o cache.
"""
import os
import time

ROOT = '/Users/amandacosta/amandacosta.github.io'

# Carimbo de versão nos links de CSS/JS: sem isso o navegador serve a folha
# antiga do cache e as mudanças parecem não ter saído.
V = time.strftime('%Y%m%d%H%M')

# O pinheiro da marca como SVG no próprio HTML. Inline em vez de máscara CSS
# porque a cor precisa mudar (cinza -> rosa) e o fill funciona em qualquer
# navegador, sem depender de suporte a mask-image.
PINHEIRO = ('<svg class="marca" viewBox="0 0 316 416" aria-hidden="true" focusable="false">'
            '<path d="M158 0 244 142 72 142Z M158 84 280 250 36 250Z'
            ' M158 176 316 359 0 359Z M140 359 176 359 176 416 140 416Z"/></svg>')

# Currículo: fora do menu desde 26/08/2026, mas o link fica guardado aqui
CV = 'https://drive.google.com/file/d/1pjZBLQrplAM-iKHVY3zq04LbxBkUVY1t/view?usp=drivesdk'

LINKEDIN = 'https://www.linkedin.com/in/amanda-costa-142053214/'
MAIL = LINKEDIN  # e-mail ainda não informado — contato pelo LinkedIn

ICONS = {
 'LinkedIn': '<path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>',
 'GitHub': '<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>',
 'Behance': '<path d="M22 7h-7v-2h7v2zm1.726 10c-.442 1.297-2.029 3-5.101 3-3.074 0-5.564-1.729-5.564-5.675 0-3.91 2.325-5.92 5.466-5.92 3.082 0 4.964 1.782 5.375 4.426.078.506.109 1.188.095 2.14h-8.027c.13 3.211 3.483 3.312 4.588 2.029h3.168zm-7.686-4h5.025c-.154-1.545-1.085-2.348-2.537-2.348-1.49 0-2.285.852-2.488 2.348zm-9.574 6.988h-6.466v-14.967h6.953c5.476.081 5.58 5.444 2.72 6.906 3.461 1.26 3.577 8.061-3.207 8.061zm-3.466-8.988h3.584c2.508 0 2.906-3-.312-3h-3.272v3zm3.391 3h-3.391v3.016h3.341c3.055 0 2.868-3.016.05-3.016z"/>',
}
LINKS = {
 'LinkedIn': 'https://www.linkedin.com/in/amanda-costa-142053214/',
 'GitHub': 'https://github.com/amanda-costa',
 'Behance': 'https://www.behance.net/amandacosta72',
}


def social(indent=6):
    pad = ' ' * indent
    rows = []
    for name, url in LINKS.items():
        rows.append(
            f'{pad}<a href="{url}" target="_blank" rel="noopener" aria-label="{name}">'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
            f'{ICONS[name]}</svg></a>'
        )
    return f'{pad}<div class="social">\n' + '\n'.join(rows) + f'\n{pad}</div>'


def head(title, desc, base, og='img/capa-petzoo.png', bg=None):
    attr = f' data-bg="{bg}"' if bg else ''
    return f'''<!DOCTYPE html>
<html lang="pt-BR">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="https://amandacosta.net/{og}">
  <meta name="theme-color" content="#3d4a57">
  <link rel="icon" href="{base}favicon.ico" sizes="16x16 32x32 48x48 64x64">
  <link rel="icon" type="image/png" sizes="128x128" href="{base}img/favicon-128.png">
  <link rel="icon" type="image/png" sizes="512x512" href="{base}img/favicon-512.png">
  <link rel="apple-touch-icon" href="{base}img/favicon-512.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300..800&family=Courier+Prime:wght@400;700&family=EB+Garamond:ital,wght@1,400;1,500&family=Work+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{base}styleguide.css?v={V}">
  <link rel="stylesheet" href="{base}style.css?v={V}">
  <script>document.documentElement.classList.add('js');</script>
</head>

<body{attr}>
'''


def header(base, active):
    def a(href, rotulo, key):
        cur = ' aria-current="page"' if key == active else ''
        return f'<a href="{href}"{cur}>{rotulo}</a>'
    return f'''
  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>

  <div class="progresso" id="progresso" aria-hidden="true"></div>

  <header class="site-header">
    <div class="shell site-header__inner">
      <a class="site-header__logo" href="{base}index.html">
        <img src="{base}img/logo-claro.png" alt="Amanda Costa" width="1040" height="240">
      </a>
      <nav class="nav" aria-label="Principal">
        {a(base + 'index.html', 'Sobre', 'sobre')}
        {a(base + 'projetos/index.html', 'Projetos', 'projetos')}
        <a href="{base}index.html#contato">Contato</a>
      </nav>
{social(6)}
      <button class="menu-toggle" id="menuToggle" aria-expanded="false" aria-controls="menuPanel">Menu</button>
    </div>
    <div class="menu-panel" id="menuPanel">
      <a href="{base}index.html">Sobre</a>
      <a href="{base}projetos/index.html">Projetos</a>
      <a href="{base}index.html#contato">Contato</a>
{social(6)}
    </div>
  </header>
'''


def footer(base):
    return f'''
  <footer class="site-footer" id="contato">
    <div class="shell">
      <div class="site-footer__topo">
        <div>
          <img class="site-footer__marca" src="{base}img/logo-claro.png"
               alt="Amanda Costa" width="1040" height="240" loading="lazy">
        </div>
{social(8)}
      </div>
      <div class="colofao">
        <span>© 2026 Amanda Costa</span>
        <a href="{LINKEDIN}" target="_blank" rel="noopener">linkedin.com/in/amanda-costa</a>
      </div>
    </div>
  </footer>

  <script src="{base}js/site.js?v={V}" defer></script>
</body>

</html>
'''


PROJETOS = [
    dict(slug='petzoo', num='01', nome='Petzoo', cta='Ver projeto',
         tags='UX · UI · Design System', ano='2025',
         thumb='img/projetos/petzoo-thumb.png',
         resumo='Plataforma de busca de cuidadores de pet, integrada a um sistema de agendamento e gestão para os cuidadores.'),
    dict(slug='event', num='02', nome='Event', cta='Ver estudo de caso',
         tags='UX Research · UI', ano='2025',
         thumb='img/projetos/event/capa2.png',
         resumo='Aplicativo para facilitar a busca de imóveis para locação para eventos.'),
    dict(slug='iduimoveis', num='03', nome='IDU Imóveis', cta='Ver estudo de caso',
         tags='UX · UI · Locação', ano='2024',
         thumb='img/projetos/iduimoveis-thumb.png',
         resumo='Plataforma de busca e anúncio de imóveis para vender ou alugar.'),
]

def destaques(qtd=2, base='projetos/', recuo='          '):
    cards = []
    for i, p in enumerate(PROJETOS[:qtd]):
        cards.append(f'''{recuo}<a class="destaque reveal" style="--d:{i}" href="{base}{p['slug']}.html">
            <div class="destaque__img">
              <img src="{'' if base else '../'}{p['thumb']}" alt="{p['nome']}" loading="lazy">
            </div>
            <div class="destaque__corpo">
              <span class="label destaque__ano">{p['ano']}</span>
              <h3>{p['nome']}</h3>
              <p>{p['resumo']}</p>
              <span class="destaque__cta">{p['cta']} <span aria-hidden="true">&rarr;</span></span>
            </div>
          </a>''')
    return '\n'.join(cards)


# --------------------------------------------------------------------------
# Home
# --------------------------------------------------------------------------

home = head('Amanda Costa — Product Designer',
            'Portfólio de Amanda Costa, product designer com foco em UX, UI e design systems. '
            'Projetos para Grupo Madero, Spoleto, Domino’s e KFC.',
            '', bg='petroleo') + header('', 'sobre') + f'''
  <main id="conteudo">

    <!-- Hero -->
    <section class="hero" data-bg="petroleo">
      <div class="hero__fundo" aria-hidden="true">
        <img class="hero__prancha" src="img/prancha-conurus.jpg" alt=""
             width="1424" height="1984" fetchpriority="high">
        <span class="hero__veu"></span>
      </div>

      <div class="shell hero__inner">
        <div class="hero__topo">
          <p class="hero__credito">Ilustração — <em>Conurus</em> · Jean Théodore Descourtilz</p>
        </div>

        <div class="hero__display">
          <span class="hero__intro">olá, sou a</span>
          <h1>Amanda<br>Costa</h1>
        </div>

        <div class="hero__pe">
          <p class="hero__lead">Product Designer situada em São Paulo. Atuo com múltiplos
            formatos de produtos digitais, ajudando a entregar a melhor experiência para as
            pessoas. Amo a natureza, árvores, pássaros e filmes de terror.</p>
          <a class="btn btn--grande" href="projetos/index.html">Conheça os meus projetos <span aria-hidden="true">&rarr;</span></a>
        </div>
      </div>
    </section>

    <!-- 01 · Sobre -->
    <section class="section" id="sobre" data-bg="papel">
      <div class="shell">
        <div class="section-head">
          <div>
            <h2>Um pouco sobre mim</h2>
          </div>
        </div>
        <div class="sobre">
          <!-- Para trocar a foto, basta substituir o arquivo img/retrato.jpg -->
          <div class="retrato reveal">
            <div class="retrato__moldura">
              <img class="retrato__foto" src="img/retrato.jpg" alt="Retrato de Amanda Costa" loading="lazy">
              <img class="retrato__selo" src="img/icone.png" alt="" aria-hidden="true"
                   width="512" height="512" loading="lazy">
            </div>
          </div>
          <div class="sobre__texto">
            <p>Minha jornada começou na faculdade de Análise e Desenvolvimento de Sistemas, onde
              percebi rapidamente que o meu foco não era analisar a fundo a parte técnica dos
              sistemas, mas sim entender as pessoas que interagem com eles. Foi assim que descobri
              minha verdadeira vocação e decidi buscar uma pós-graduação em Experiência do
              Usuário.</p>
            <p>Meu grande objetivo é facilitar o dia a dia das pessoas. Trabalho para que qualquer
              usuário consiga realizar suas tarefas em produtos digitais sem lidar com
              complexidades desnecessárias. Para mim, um bom design é aquele que encontra o ponto
              de equilíbrio ideal, garantindo uma interface altamente satisfatória para o usuário
              e, ao mesmo tempo, gerando resultados estratégicos valiosos para a empresa.</p>
          </div>
          <dl class="ficha-campo reveal">
            <div><dt>Atuação</dt><dd>Product Design — UX &amp; UI</dd></div>
            <div><dt>Marcas</dt><dd>Grupo Madero, Spoleto, Domino&rsquo;s, KFC, Unilever, Volvo, Equifax | BoaVista</dd></div>
            <div><dt>Segmentos</dt><dd>Financeiro, marketplace, social, locação, agendamento, delivery e SaaS</dd></div>
            <div><dt>Idiomas</dt><dd>Português e inglês</dd></div>
            <div><dt>Base</dt><dd>São Paulo, Brasil</dd></div>
          </dl>
        </div>
      </div>
    </section>

    <!-- 02 · Projetos em destaque -->
    <section class="section" id="projetos" data-bg="papel">
      <div class="shell">
        <div class="section-head">
          <div>
            <h2>Conheça alguns dos meus projetos</h2>
          </div>
        </div>
        <div class="destaques">
{destaques()}
        </div>
        <p class="destaques__pe">
          <a class="btn btn--grande" href="projetos/index.html">Ver todos os projetos <span aria-hidden="true">&rarr;</span></a>
        </p>
      </div>
    </section>

    <!-- 03 · Conhecimento técnico -->
    <section class="section shell" data-bg="petroleo">
      <div class="section-head">
        <div>
          <h2>Habilidades e Foco</h2>
        </div>
      </div>
      <div class="disciplinas">
        <div class="disciplina reveal" style="--d:0">
          <h3>UX Design — <em>Pesquisa e Jornada</em></h3>
          <p>Trabalho para garantir que a experiência do usuário seja fluida e sem atritos.
            Foco no mapeamento detalhado da jornada, na escuta ativa e na análise de métricas
            via Analytics. Transformo esses dados em ações práticas para evoluir o produto
            continuamente.</p>
        </div>
        <div class="disciplina reveal" style="--d:1">
          <h3>UI Design — <em>Design Systems e Componentes</em></h3>
          <p>Desenho interfaces limpas e organizadas, com foco na escalabilidade. Construo e
            gerencio Design Systems utilizando princípios de Atomic Design, configurando
            componentes e bibliotecas no Figma para padronizar produtos e acelerar entregas.</p>
        </div>
        <div class="disciplina reveal" style="--d:2">
          <h3>Otimização com <em>Inteligência Artificial</em></h3>
          <p>Como diferencial, utilizo IAs como Gemini e Claude para turbinar meu fluxo de
            trabalho. Elas são minhas aliadas para processar dados de pesquisa, estruturar
            informações complexas e trazer muito mais agilidade e inovação para o processo
            de design.</p>
        </div>
      </div>
    </section>

    <!-- 04 · Experiência -->
    <section class="section" id="experiencia" data-bg="papel">
      <div class="shell">
      <div class="section-head">
        <div>
          <h2>Trajetória profissional</h2>
          <p class="section-note">Produtos digitais para marcas de grande alcance e para
            operações de financeiro, marketplace, locação, agendamento e SaaS.</p>
        </div>
      </div>
      <ol class="tempo">
        <li class="tempo__item reveal" style="--d:0">
          <span class="tempo__ano" aria-hidden="true">2026</span>
          <div class="tempo__quando">
            {PINHEIRO}
            <span class="label">jul 2026 — o momento</span>
          </div>
          <div class="tempo__oque">
            <h3>Experience Designer — Pleno</h3>
            <p class="tempo__org">Equifax | BoaVista · Barueri, SP · Híbrido</p>
            <p>Atuação focada no design de produtos e na melhoria contínua de interfaces, utilizando as práticas de Customer Experience (CX) e a análise da Voz do Cliente (VoC) como ferramentas estratégicas complementares para embasar e validar as decisões de design.</p>
            <div class="detalhe" id="exp-cx">
              <ul class="detalhe__lista">
              <li><strong>Evolução de Jornadas e Portais:</strong> Mapeamento aprofundado de jornadas do usuário e condução do redesign de portais de clientes. Estruturação de materiais de apoio focados em melhorar a usabilidade e reduzir fricções, impactando diretamente na redução de chamados de suporte.</li>
              <li><strong>Melhorias no Portal Financeiro:</strong> Atuação dedicada a evoluir a usabilidade da plataforma. Conduzi o redesign da fatura para simplificar e promover o entendimento do cliente em relação as informações e aos dados de consumo. Desenvolvi soluções focadas em UI e Arquitetura da Informação para garantir clareza e facilitar a navegação entre fluxos complexos.</li>
              <li><strong>Alinhamento Estratégico (Design e Operação):</strong> Trabalho colaborativo e contínuo com as equipes de Produto e Suporte, traduzindo dados quantitativos e feedbacks qualitativos da operação em soluções de design de interface e experiência cada vez mais assertivas.</li>
              </ul>
            </div>
            <button class="detalhe__botao" type="button" aria-expanded="false" aria-controls="exp-cx">
              <span class="detalhe__rotulo">Ver detalhes</span>
              <span class="detalhe__sinal" aria-hidden="true"></span>
            </button>
          </div>
        </li>
        <li class="tempo__item reveal" style="--d:1">
          <span class="tempo__ano" aria-hidden="true">2025</span>
          <div class="tempo__quando">
            {PINHEIRO}
            <span class="label">set 2025 — jul 2026</span>
          </div>
          <div class="tempo__oque">
            <h3>UX/UI Designer — Pleno</h3>
            <p class="tempo__org">Equifax | BoaVista · Barueri, SP · Híbrido</p>
            <p>Responsável por estruturar e evoluir plataformas internas e externas, liderando o design de ponta a ponta com uma abordagem fortemente orientada a dados (data-driven) e foco em eficiência operacional.</p>
            <div class="detalhe" id="exp-ux">
              <ul class="detalhe__lista">
              <li><strong>Design Zero-to-One:</strong> Liderança no design completo do produto Access Manager. O processo abrangeu desde estudos de mercado e definição da arquitetura da informação até a criação de interfaces acessíveis e validação de viabilidade técnica frente aos sistemas legados.</li>
              <li><strong>UX Research e Validação com Dados:</strong> Análise contínua de volumetria de chamados e casos de uso para identificar reais pontos de dor na jornada do usuário. Esse acompanhamento constante permitiu validar hipóteses de design com precisão e mensurar o impacto das entregas.</li>
              <li><strong>Inovação e Automação no Design:</strong> Utilização de Inteligência Artificial (Gemini e NotebookLM) para sintetizar e agilizar a análise de dados de pesquisa de UX. Construção de dashboards operacionais no Looker Studio para acompanhar o impacto do design nos números do negócio, além do uso de Apps Script para estruturação de páginas.</li>
              </ul>
            </div>
            <button class="detalhe__botao" type="button" aria-expanded="false" aria-controls="exp-ux">
              <span class="detalhe__rotulo">Ver detalhes</span>
              <span class="detalhe__sinal" aria-hidden="true"></span>
            </button>
          </div>
        </li>
        <li class="tempo__item reveal" style="--d:2">
          <span class="tempo__ano" aria-hidden="true">2023</span>
          <div class="tempo__quando">
            {PINHEIRO}
            <span class="label">ago 2023 — jun 2025</span>
          </div>
          <div class="tempo__oque">
            <h3>UI/UX Designer</h3>
            <p class="tempo__org">Alphacode IT Solutions · São Paulo, SP · Presencial</p>
            <p>Atuei no ciclo completo de design (end-to-end) em um ambiente dinâmico de consultoria, projetando aplicativos mobile, sites e CRMs para grandes contas do mercado (como Madero, KFC, Domino’s, Unilever e Volvo) em segmentos como bancos digitais, delivery e marketplaces.</p>
            <div class="detalhe" id="exp-alpha">
              <ul class="detalhe__lista">
              <li><strong>Design de Interfaces e Usabilidade:</strong> Responsável pela criação de fluxos de navegação (user flows), wireframes e protótipos de alta fidelidade, sempre com foco em usabilidade avançada e otimização de conversão para produtos de alto tráfego.</li>
              <li><strong>Construção de Design Systems:</strong> Liderei a criação e estruturação de bibliotecas de componentes do zero. Esse trabalho garantiu consistência visual através de múltiplos produtos e escalabilidade técnica para os times de desenvolvimento.</li>
              <li><strong>Discovery e Qualidade de Entrega:</strong> Conduzi imersões em modelos de negócio, benchmarks e testes de usabilidade. Na ponta final do processo, atuei lado a lado com os desenvolvedores, garantindo a viabilidade técnica das propostas, realizando o handoff detalhado e conduzindo auditorias de design (Design QA) em ambiente de homologação.</li>
              </ul>
            </div>
            <button class="detalhe__botao" type="button" aria-expanded="false" aria-controls="exp-alpha">
              <span class="detalhe__rotulo">Ver detalhes</span>
              <span class="detalhe__sinal" aria-hidden="true"></span>
            </button>
          </div>
        </li>
      </ol>
      </div>
    </section>

    <!-- 05 · Formação -->
    <section class="section section--rosa shell" data-bg="rosa">
      <div class="section-head">
        <div>
          <h2>Percurso acadêmico</h2>
          <p class="section-note">Da base técnica em desenvolvimento à especialização
            em experiência do usuário.</p>
        </div>
      </div>
      <ol class="trilha">
        <li class="trilha__item reveal" style="--d:0">
          <span class="trilha__ano">2021</span>
          <div class="trilha__corpo">
            {PINHEIRO}
            <h3>Análise e Desenvolvimento de Sistemas</h3>
            <p class="trilha__org">UNIP</p>
            <p class="trilha__nota">Tecnologia e desenvolvimento de aplicações</p>
          </div>
        </li>
        <li class="trilha__item reveal" style="--d:1">
          <span class="trilha__ano">2022</span>
          <div class="trilha__corpo">
            {PINHEIRO}
            <h3>UX Design</h3>
            <p class="trilha__org">How Bootcamps</p>
            <p class="trilha__nota">Imersão em criação de interfaces e usabilidade</p>
          </div>
        </li>
        <li class="trilha__item reveal" style="--d:2">
          <span class="trilha__ano">2023</span>
          <div class="trilha__corpo">
            {PINHEIRO}
            <h3>User Experience Design</h3>
            <p class="trilha__org">Tera</p>
            <p class="trilha__nota">Foco em pesquisa, métricas e visão de produto</p>
          </div>
        </li>
        <li class="trilha__item reveal" style="--d:3">
          <span class="trilha__ano">2025</span>
          <div class="trilha__corpo">
            {PINHEIRO}
            <h3>Pós-graduação em User Experience Design</h3>
            <p class="trilha__org">Universidade Belas Artes de São Paulo</p>
            <p class="trilha__nota">Especialização em Experiência do Usuário</p>
          </div>
        </li>
      </ol>
    </section>

  </main>

''' + footer('')

open(os.path.join(ROOT, 'index.html'), 'w').write(home)

# --------------------------------------------------------------------------
# Índice de projetos
# --------------------------------------------------------------------------

fichas = destaques(len(PROJETOS), base='', recuo='        ')

projetos = head('Projetos | Amanda Costa',
                'Índice dos estudos de caso de UX/UI Design de Amanda Costa.',
                '../') + header('../', 'projetos') + f'''
  <main id="conteudo">

    <section class="page-head page-head--indice shell">
      <div>
        <h1>Projetos</h1>
      </div>
    </section>

    <section class="section shell" data-bg="papel">
      <div class="destaques destaques--indice">
{fichas}
      </div>
    </section>

  </main>
''' + footer('../')

open(os.path.join(ROOT, 'projetos/index.html'), 'w').write(projetos)

# --------------------------------------------------------------------------
# Estudos de caso
# --------------------------------------------------------------------------

ROMANOS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

CASOS = {
 'petzoo': dict(
    titulo='Petzoo', papel='Product Designer', ano='2025',
    escopo='UX · UI · Design System', entrega='App e site',
    intro='Plataforma de busca de cuidadores de pet, integrada a um sistema de agendamento '
          'e gestão para os cuidadores.',
    pecas=[('../img/projetos/petzoo/1.png', 'Capa do projeto', 'img'),
           ('../img/projetos/petzoo/2.png', 'Visão geral', 'img'),
           ('../img/projetos/petzoo/3.jpg', 'Processo de pesquisa', 'img'),
           ('../img/projetos/petzoo/4.jpg', 'Detalhes de interface', 'img'),
           ('../img/projetos/petzoo/5.jpg', 'Resultados', 'img'),
           ('../img/projetos/petzoo/6.jpg', 'Conclusão', 'img'),
           ('../img/projetos/petzoo/video-preview.mp4', 'Protótipo navegável', 'video'),
           ('../img/projetos/petzoo/frame-final.png', 'Telas finais', 'img')],
    ant=None, prox=('event.html', 'Event')),
 'event': dict(
    titulo='Event', papel='Product Designer', ano='2025',
    escopo='UX Research · UI', entrega='Estudo de caso',
    intro='Aplicativo para facilitar a busca de imóveis para locação para eventos.',
    pecas=[('../img/projetos/event/1.png', 'Capa do projeto', 'img'),
           ('../img/projetos/event/apresentacao.jpg', 'Apresentação completa', 'img'),
           ('../img/projetos/event/18.png', 'Conclusão', 'img')],
    ant=('petzoo.html', 'Petzoo'), prox=('iduimoveis.html', 'IDU Imóveis')),
 'iduimoveis': dict(
    titulo='IDU Imóveis', papel='Product Designer', ano='2024',
    escopo='UX · UI', entrega='Estudo de caso',
    intro='Plataforma de busca e anúncio de imóveis para vender ou alugar.',
    pecas=[('../img/projetos/iduimoveis/case-study.jpg', 'Estudo de caso completo', 'img')],
    ant=('event.html', 'Event'), prox=None),
}

for slug, c in CASOS.items():
    pecas = []
    for i, (src, legenda, tipo) in enumerate(c['pecas']):
        media = (f'<img src="{src}" alt="{c["titulo"]} — {legenda}" '
                 f'loading="{"eager" if i < 2 else "lazy"}">' if tipo == 'img'
                 else f'<video autoplay loop muted playsinline aria-label="{legenda}">'
                      f'<source src="{src}" type="video/mp4"></video>')
        pecas.append('      ' + media)
    pecas = '\n'.join(pecas)

    if c['ant']:
        ant = (f'''      <div>
        <span class="label">Anterior</span>
        <a href="{c['ant'][0]}">&larr; {c['ant'][1]}</a>
      </div>''')
    else:
        ant = '      <div></div>'
    if c['prox']:
        prox = (f'''      <div>
        <span class="label">Próximo</span>
        <a href="{c['prox'][0]}">{c['prox'][1]} &rarr;</a>
      </div>''')
    else:
        prox = (f'''      <div>
        <span class="label">Índice</span>
        <a href="index.html">Todos os projetos &rarr;</a>
      </div>''')

    pagina = head(f'{c["titulo"]} | Amanda Costa',
                  f'Estudo de caso do projeto {c["titulo"]}, por Amanda Costa.',
                  '../', og=CASOS[slug]['pecas'][0][0].replace('../', '')) \
        + header('../', 'projetos') + f'''
  <main id="conteudo">

    <section class="caso-head shell">
      <h1>{c['titulo']}</h1>
      <p class="hero__lead">{c['intro']}</p>
      <dl class="ficha-tecnica">
        <div><dt>Papel</dt><dd>{c['papel']}</dd></div>
        <div><dt>Escopo</dt><dd>{c['escopo']}</dd></div>
        <div><dt>Entrega</dt><dd>{c['entrega']}</dd></div>
        <div><dt>Ano</dt><dd>{c['ano']}</dd></div>
      </dl>
    </section>

    <div class="pranchas-caso">
{pecas}
    </div>

    <nav class="paginacao shell" aria-label="Navegação entre projetos">
{ant}
{prox}
    </nav>

  </main>
''' + footer('../')

    open(os.path.join(ROOT, f'projetos/{slug}.html'), 'w').write(pagina)

print('ok')

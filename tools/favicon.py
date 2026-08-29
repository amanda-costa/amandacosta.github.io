#!/usr/bin/env python3
"""Gera os ícones do site a partir do pinheiro da marca.

Fonte única: o mesmo caminho vetorial que o build injeta nas páginas
(tools/build.py, PINHEIRO). As cores saem dos tokens de styleguide.css
convertidas de oklch para hex — o navegador entende oklch, o PNG e o ICO não.

Uso: python3 tools/favicon.py
"""
import io
import math
import os
import struct
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- oklch -> sRGB ---------------------------------------------------------
_M1 = [[1.0, 0.3963377774, 0.2158037573],
       [1.0, -0.1055613458, -0.0638541728],
       [1.0, -0.0894841775, -1.2914855480]]
_M2 = [[4.0767416621, -3.3077115913, 0.2309699292],
       [-1.2684380046, 2.6097574011, -0.3413193965],
       [-0.0041960863, -0.7034186147, 1.7076147010]]


def oklch(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    lms = [(r[0] * L + r[1] * a + r[2] * b) ** 3 for r in _M1]
    out = []
    for m in _M2:
        v = min(1.0, max(0.0, sum(m[i] * lms[i] for i in range(3))))
        v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        out.append(round(v * 255))
    return tuple(out)


PETROLEO = oklch(.31, .032, 243)   # --petroleo
ROSA = oklch(.66, .095, 12)        # --rosa
HEX = lambda c: '#%02x%02x%02x' % c

# --- O pinheiro, em coordenadas de tools/build.py --------------------------
CAIXA = (316, 416)
FORMAS = [
    [(158, 0), (244, 142), (72, 142)],
    [(158, 84), (280, 250), (36, 250)],
    [(158, 176), (316, 359), (0, 359)],
    [(140, 359), (176, 359), (176, 416), (140, 416)],
]
# Quanto do lado o pinheiro ocupa. Escala óptica: na aba do navegador o ícone
# tem 16px e a margem generosa some antes do desenho — os tamanhos pequenos
# apertam a moldura para o pinheiro ainda ser um pinheiro.
ALTURA = 0.60


def altura(lado):
    return 0.78 if lado <= 32 else 0.70 if lado <= 64 else ALTURA


def desenha(lado, escala=8):
    """Pinheiro rosa sobre petróleo, com supersampling para a borda ficar lisa."""
    px = lado * escala
    img = Image.new('RGB', (px, px), PETROLEO)
    d = ImageDraw.Draw(img)
    k = px * altura(lado) / CAIXA[1]
    dx = (px - CAIXA[0] * k) / 2
    dy = (px - CAIXA[1] * k) / 2
    for forma in FORMAS:
        d.polygon([(dx + x * k, dy + y * k) for x, y in forma], fill=ROSA)
    return img.resize((lado, lado), Image.LANCZOS)


def svg():
    caminho = ('M158 0 244 142 72 142Z M158 84 280 250 36 250Z'
               ' M158 176 316 359 0 359Z M140 359 176 359 176 416 140 416Z')
    k = ALTURA * 512 / CAIXA[1]
    dx, dy = (512 - CAIXA[0] * k) / 2, (512 - CAIXA[1] * k) / 2
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
        f'  <rect width="512" height="512" fill="{HEX(PETROLEO)}"/>\n'
        f'  <g transform="translate({dx:.2f} {dy:.2f}) scale({k:.4f})">\n'
        f'    <path fill="{HEX(ROSA)}" d="{caminho}"/>\n'
        '  </g>\n</svg>\n'
    )


def escreve_ico(caminho, tamanhos):
    """Monta o .ico à mão, com um PNG por tamanho.

    O `sizes=` do Pillow reamostra um único desenho para os outros tamanhos —
    e, do jeito que dá para chamá-lo aqui, saiu um .ico com uma entrada só de
    16x16, que o navegador tinha de ampliar em tela retina. Um .ico é só um
    cabeçalho seguido dos arquivos embutidos, então escrevê-lo direto custa
    pouco e mantém cada tamanho com o desenho que foi feito para ele.
    """
    quadros = []
    for lado in tamanhos:
        buf = io.BytesIO()
        desenha(lado).save(buf, format='PNG', optimize=True)
        quadros.append(buf.getvalue())

    cabecalho = struct.pack('<HHH', 0, 1, len(quadros))  # reservado, tipo 1, nº de ícones
    offset = 6 + 16 * len(quadros)
    diretorio = b''
    for lado, png in zip(tamanhos, quadros):
        diretorio += struct.pack(
            '<BBBBHHII',
            lado if lado < 256 else 0, lado if lado < 256 else 0,
            0, 0,      # paleta e reservado
            1, 32,     # planos de cor, bits por pixel
            len(png), offset,
        )
        offset += len(png)

    with open(caminho, 'wb') as f:
        f.write(cabecalho + diretorio + b''.join(quadros))


def main():
    with open(os.path.join(RAIZ, 'img', 'favicon.svg'), 'w') as f:
        f.write(svg())
    for lado in (128, 512):
        desenha(lado).save(os.path.join(RAIZ, 'img', f'favicon-{lado}.png'))
    # O .ico guarda os tamanhos pequenos, cada um redesenhado — reduzir o
    # grande borra o tronco de 36 unidades de largura.
    escreve_ico(os.path.join(RAIZ, 'favicon.ico'), [16, 32, 48, 64])
    print('img/favicon.svg, img/favicon-128.png, img/favicon-512.png, favicon.ico')


if __name__ == '__main__':
    main()

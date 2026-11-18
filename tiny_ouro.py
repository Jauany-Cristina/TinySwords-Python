import math
import os
import random
import sys

import pygame

pygame.init()
LARGURA, ALTURA = 1000, 640
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Tiny Swords - Ouro e Goblins")
relogio = pygame.time.Clock()

PASTA = os.path.dirname(os.path.abspath(__file__))
MARROM = (84, 56, 40)
BRANCO = (255, 252, 246)

fonte_titulo = pygame.font.SysFont("georgia", 54, bold=True)
fonte_grande = pygame.font.SysFont("georgia", 34, bold=True)
fonte = pygame.font.SysFont("georgia", 24)
fonte_pequena = pygame.font.SysFont("georgia", 19)

META_OURO = 10
VIDAS_MAX = 3

def carregar(nome, escala=1.0):
    img = pygame.image.load(os.path.join(PASTA, "assets", nome)).convert_alpha()
    if escala != 1.0:
        img = pygame.transform.scale(img, (int(img.get_width() * escala), int(img.get_height() * escala)))
    return img

def cortar(folha, linha, quantidade, tamanho, escala=1.0):
    quadros = []
    for n in range(quantidade):
        q = folha.subsurface((n * tamanho, linha * tamanho, tamanho, tamanho))
        if escala != 1.0:
            q = pygame.transform.scale(q, (int(tamanho * escala), int(tamanho * escala)))
        quadros.append(q)
    return quadros

def espelhar(quadros):
    return [pygame.transform.flip(q, True, False) for q in quadros]

def fatiar(img):
    return [[img.subsurface((c * 128, l * 128, 64, 64)) for c in range(3)] for l in range(3)]

def criar_painel(fatias, largura, altura, t=48):
    painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
    xs = [0, t, largura - t]
    larguras = [t, largura - 2 * t, t]
    ys = [0, t, altura - t]
    alturas = [t, altura - 2 * t, t]
    for linha in range(3):
        for coluna in range(3):
            pedaco = pygame.transform.scale(fatias[linha][coluna], (larguras[coluna], alturas[linha]))
            painel.blit(pedaco, (xs[coluna], ys[linha]))
    return painel

tile_grama = carregar("grama.png").subsurface((64, 64, 64, 64))
fundo = pygame.Surface((LARGURA, ALTURA))
for gx in range(0, LARGURA, 64):
    for gy in range(0, ALTURA, 64):
        fundo.blit(tile_grama, (gx, gy))

folha_guerreiro = carregar("guerreiro.png")
guer_parado = cortar(folha_guerreiro, 0, 6, 192)
guer_correr = cortar(folha_guerreiro, 1, 6, 192)
guer_ataque = cortar(folha_guerreiro, 2, 6, 192)
guer_parado_e = espelhar(guer_parado)
guer_correr_e = espelhar(guer_correr)
guer_ataque_e = espelhar(guer_ataque)

folha_goblin = carregar("goblin.png")
gob_correr = cortar(folha_goblin, 1, 6, 192)
gob_correr_e = espelhar(gob_correr)

explosao = cortar(carregar("explosao.png"), 0, 9, 192, 0.7)
ouro_surge = cortar(carregar("ouro_surge.png"), 0, 7, 128, 0.7)
ouro_img = carregar("ouro.png", 0.7)
carne_img = carregar("carne.png", 0.7)
ovelha = cortar(carregar("ovelha.png"), 0, 8, 128, 0.8)

cogumelo = carregar("cogumelo.png", 1.5)
abobora = carregar("abobora.png", 1.5)
arbusto = carregar("arbusto.png", 1.5)
pedra = carregar("pedra.png", 1.5)
DECORACAO = [(cogumelo, 90, 130), (cogumelo, 905, 570), (arbusto, 940, 330), (arbusto, 55, 360),
             (abobora, 470, 595), (pedra, 310, 95), (pedra, 720, 590), (abobora, 880, 120)]
OVELHAS = [(150, 540, 0), (840, 220, 3)]

papel = fatiar(carregar("papel.png"))
botao_normal = criar_painel(fatiar(carregar("botao.png")), 280, 96, 40)
botao_apertado = criar_painel(fatiar(carregar("botao_apertado.png")), 280, 96, 40)
painel_menu = criar_painel(papel, 700, 540)
painel_fim = criar_painel(papel, 560, 340)
painel_hud = criar_painel(papel, 330, 84, 36)
icone_moeda = carregar("icone_moeda.png", 0.6)
icone_carne = carregar("icone_carne.png", 0.55)
icone_espadas = carregar("icone_espadas.png", 0.6)
icone_seta = carregar("icone_seta.png", 0.6)
icone_x = carregar("icone_x.png", 0.6)

botao_start = pygame.Rect(360, 450, 280, 96)

def escrever(txt, fnt, cor, x, y, centro=False, sombra=None):
    if sombra is not None:
        img_s = fnt.render(txt, True, sombra)
        rect_s = img_s.get_rect()
        if centro:
            rect_s.center = (x + 2, y + 2)
        else:
            rect_s.topleft = (x + 2, y + 2)
        tela.blit(img_s, rect_s)
    img = fnt.render(txt, True, cor)
    rect = img.get_rect()
    if centro:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    tela.blit(img, rect)

def desenhar_botao(rect, texto_botao, mouse_pos, apertado):
    if rect.collidepoint(mouse_pos) and apertado:
        tela.blit(botao_apertado, rect.topleft)
        escrever(texto_botao, fonte_grande, BRANCO, rect.centerx, rect.centery + 4, centro=True, sombra=MARROM)
    else:
        tela.blit(botao_normal, rect.topleft)
        escrever(texto_botao, fonte_grande, BRANCO, rect.centerx, rect.centery - 2, centro=True, sombra=MARROM)

def desenhar_menu(mouse_pos, apertado, tempo_ms):
    tela.blit(painel_menu, (150, 50))
    escrever("Tiny Swords", fonte_titulo, MARROM, LARGURA // 2, 125, centro=True)
    escrever("Ouro e Goblins", fonte_grande, MARROM, LARGURA // 2, 175, centro=True)

    quadro = guer_parado[(tempo_ms // 130) % 6]
    tela.blit(quadro, quadro.get_rect(center=(755, 300)))

    escrever("Controles", fonte, MARROM, 215, 222)
    linhas = [
        (icone_seta, "Mover:  W A S D  ou  SETAS"),
        (icone_espadas, "Atacar:  ESPAÇO"),
        (icone_x, "Voltar ao menu:  ESC"),
        (icone_moeda, "Objetivo: colete " + str(META_OURO) + " moedas"),
        (icone_carne, "Carne devolve uma vida"),
    ]
    for n in range(len(linhas)):
        icone, txt = linhas[n]
        y = 262 + n * 36
        tela.blit(icone, icone.get_rect(center=(232, y + 12)))
        escrever(txt, fonte_pequena, MARROM, 262, y)

    desenhar_botao(botao_start, "Start Game", mouse_pos, apertado)
    escrever("ou aperte ENTER", fonte_pequena, MARROM, LARGURA // 2, 558, centro=True)

J = {}

def novo_jogo():
    J["estado"] = "jogo"
    J["px"] = LARGURA / 2
    J["py"] = ALTURA / 2
    J["olha_esq"] = False
    J["correndo"] = False
    J["atacando"] = False
    J["ataque_t"] = 0
    J["vidas"] = VIDAS_MAX
    J["invul"] = 0
    J["ouro"] = 0
    J["goblins"] = []
    J["efeitos"] = []
    J["carnes"] = []
    J["spawn_t"] = 1500
    J["tempo"] = 0
    J["venceu"] = False
    novo_ouro()

def novo_ouro():
    J["ouro_x"] = random.randint(90, LARGURA - 90)
    J["ouro_y"] = random.randint(120, ALTURA - 90)
    J["ouro_t"] = 0

def criar_goblin():
    lado = random.choice(["esq", "dir", "cima", "baixo"])
    if lado == "esq":
        gx_novo, gy_novo = -40, random.randint(80, ALTURA - 60)
    elif lado == "dir":
        gx_novo, gy_novo = LARGURA + 40, random.randint(80, ALTURA - 60)
    elif lado == "cima":
        gx_novo, gy_novo = random.randint(40, LARGURA - 40), -40
    else:
        gx_novo, gy_novo = random.randint(40, LARGURA - 40), ALTURA + 40
    J["goblins"].append({"x": gx_novo, "y": gy_novo, "off": random.randint(0, 5)})

def distancia(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)

def atualizar(dt, teclas):
    J["tempo"] = J["tempo"] + dt
    if J["invul"] > 0:
        J["invul"] = J["invul"] - dt
    dx = 0
    dy = 0
    if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
        dx = dx - 1
    if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
        dx = dx + 1
    if teclas[pygame.K_w] or teclas[pygame.K_UP]:
        dy = dy - 1
    if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
        dy = dy + 1
    J["correndo"] = dx != 0 or dy != 0
    if J["correndo"]:
        tam = math.hypot(dx, dy)
        vel = 0.27 if not J["atacando"] else 0.12
        J["px"] = min(max(J["px"] + dx / tam * vel * dt, 50), LARGURA - 50)
        J["py"] = min(max(J["py"] + dy / tam * vel * dt, 90), ALTURA - 50)
        if dx < 0:
            J["olha_esq"] = True
        elif dx > 0:
            J["olha_esq"] = False

    if J["atacando"]:
        J["ataque_t"] = J["ataque_t"] + dt
        if J["ataque_t"] >= 6 * 70:
            J["atacando"] = False
        elif 140 <= J["ataque_t"] <= 350:
            for gob in list(J["goblins"]):
                frente = (gob["x"] - J["px"]) * (-1 if J["olha_esq"] else 1)
                if frente > -30 and abs(gob["x"] - J["px"]) < 120 and abs(gob["y"] - J["py"]) < 80:
                    J["goblins"].remove(gob)
                    J["efeitos"].append({"x": gob["x"], "y": gob["y"], "t": 0})
                    if random.random() < 0.3:
                        J["carnes"].append((gob["x"], gob["y"]))

    J["spawn_t"] = J["spawn_t"] - dt
    if J["spawn_t"] <= 0:
        if len(J["goblins"]) < 6:
            criar_goblin()
        J["spawn_t"] = max(1200, 3000 - J["ouro"] * 180)
    for gob in J["goblins"]:
        ang = math.atan2(J["py"] - gob["y"], J["px"] - gob["x"])
        vel_g = 0.09 + J["ouro"] * 0.008
        gob["x"] = gob["x"] + math.cos(ang) * vel_g * dt
        gob["y"] = gob["y"] + math.sin(ang) * vel_g * dt
        if J["invul"] <= 0 and distancia(gob["x"], gob["y"], J["px"], J["py"]) < 42:
            J["vidas"] = J["vidas"] - 1
            J["invul"] = 1500
            if J["vidas"] <= 0:
                J["venceu"] = False
                J["estado"] = "fim"

    for ef in list(J["efeitos"]):
        ef["t"] = ef["t"] + dt
        if ef["t"] > 9 * 60:
            J["efeitos"].remove(ef)

    J["ouro_t"] = J["ouro_t"] + dt
    if distancia(J["ouro_x"], J["ouro_y"], J["px"], J["py"]) < 50:
        J["ouro"] = J["ouro"] + 1
        if J["ouro"] >= META_OURO:
            J["venceu"] = True
            J["estado"] = "fim"
        else:
            novo_ouro()
    for carne in list(J["carnes"]):
        if distancia(carne[0], carne[1], J["px"], J["py"]) < 50:
            J["carnes"].remove(carne)
            J["vidas"] = min(VIDAS_MAX, J["vidas"] + 1)

def desenhar_jogo(tempo_ms):
    itens = []
    for img, ix, iy in DECORACAO:
        itens.append((iy, img, (ix, iy)))
    for ox, oy, desloc in OVELHAS:
        q = ovelha[(tempo_ms // 120 + desloc) % 8]
        itens.append((oy, q, (ox, oy)))

    if J["ouro_t"] < 7 * 80:
        q_ouro = ouro_surge[min(J["ouro_t"] // 80, 6)]
    else:
        q_ouro = ouro_img
    itens.append((J["ouro_y"] - 40, q_ouro, (J["ouro_x"], J["ouro_y"])))
    for cx, cy in J["carnes"]:
        itens.append((cy - 40, carne_img, (cx, cy)))

    for gob in J["goblins"]:
        lista = gob_correr_e if J["px"] < gob["x"] else gob_correr
        q = lista[(tempo_ms // 110 + gob["off"]) % 6]
        itens.append((gob["y"], q, (gob["x"], gob["y"] - 10)))

    piscando = J["invul"] > 0 and (tempo_ms // 100) % 2 == 0
    if not piscando:
        if J["atacando"]:
            lista = guer_ataque_e if J["olha_esq"] else guer_ataque
            q = lista[min(J["ataque_t"] // 70, 5)]
        elif J["correndo"]:
            lista = guer_correr_e if J["olha_esq"] else guer_correr
            q = lista[(tempo_ms // 90) % 6]
        else:
            lista = guer_parado_e if J["olha_esq"] else guer_parado
            q = lista[(tempo_ms // 130) % 6]
        itens.append((J["py"], q, (J["px"], J["py"] - 10)))

    itens.sort(key=lambda item: item[0])
    for _, img, centro in itens:
        tela.blit(img, img.get_rect(center=centro))

    for ef in J["efeitos"]:
        q = explosao[min(int(ef["t"] // 60), 8)]
        tela.blit(q, q.get_rect(center=(ef["x"], ef["y"])))

    tela.blit(painel_hud, (10, 8))
    tela.blit(icone_moeda, icone_moeda.get_rect(center=(55, 50)))
    escrever(str(J["ouro"]) + " / " + str(META_OURO), fonte, MARROM, 80, 36)
    for n in range(VIDAS_MAX):
        icone_vida = icone_carne
        if n >= J["vidas"]:
            icone_vida = icone_carne.copy()
            icone_vida.set_alpha(70)
        tela.blit(icone_vida, icone_vida.get_rect(center=(205 + n * 42, 50)))

def desenhar_fim():
    tela.blit(painel_fim, (220, 150))
    if J["venceu"]:
        escrever("Vitória!", fonte_titulo, MARROM, LARGURA // 2, 235, centro=True)
        escrever("Você juntou todo o ouro!", fonte, MARROM, LARGURA // 2, 295, centro=True)
    else:
        escrever("Fim de jogo", fonte_titulo, MARROM, LARGURA // 2, 235, centro=True)
        escrever("Os goblins levaram a melhor...", fonte, MARROM, LARGURA // 2, 295, centro=True)
    escrever("Moedas: " + str(J["ouro"]) + " / " + str(META_OURO), fonte, MARROM, LARGURA // 2, 335, centro=True)
    escrever("ENTER: jogar de novo      ESC: menu", fonte_pequena, MARROM, LARGURA // 2, 395, centro=True)

def main():
    J["estado"] = "menu"
    novo_ouro()
    J["goblins"] = []
    J["efeitos"] = []
    J["carnes"] = []
    J["ouro"] = 0
    J["vidas"] = VIDAS_MAX
    J["invul"] = 0
    J["px"] = LARGURA / 2
    J["py"] = ALTURA / 2
    J["olha_esq"] = False
    J["correndo"] = False
    J["atacando"] = False
    J["ataque_t"] = 0
    J["venceu"] = False

    while True:
        dt = min(relogio.tick(60), 50)
        tempo_ms = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        apertado = pygame.mouse.get_pressed()[0]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if J["estado"] == "menu" and botao_start.collidepoint(evento.pos):
                    novo_jogo()

            if evento.type == pygame.KEYDOWN:
                if J["estado"] == "menu" and evento.key == pygame.K_RETURN:
                    novo_jogo()
                elif J["estado"] == "jogo":
                    if evento.key == pygame.K_SPACE and not J["atacando"]:
                        J["atacando"] = True
                        J["ataque_t"] = 0
                    if evento.key == pygame.K_ESCAPE:
                        J["estado"] = "menu"
                elif J["estado"] == "fim":
                    if evento.key == pygame.K_RETURN:
                        novo_jogo()
                    if evento.key == pygame.K_ESCAPE:
                        J["estado"] = "menu"

        if J["estado"] == "jogo":
            atualizar(dt, pygame.key.get_pressed())

        tela.blit(fundo, (0, 0))
        if J["estado"] == "menu":
            for img, ix, iy in DECORACAO:
                tela.blit(img, img.get_rect(center=(ix, iy)))
            desenhar_menu(mouse_pos, apertado, tempo_ms)
        else:
            desenhar_jogo(tempo_ms)
            if J["estado"] == "fim":
                desenhar_fim()

        pygame.display.flip()

main()

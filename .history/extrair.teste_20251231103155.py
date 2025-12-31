import pyautogui
import keyboard
import img2pdf
import pygetwindow as gw
import os
import time
import re
import shutil
import json
from datetime import datetime
import sys

# ===== CONFIGURAÇÕES GERAIS =====
PASTA_BACKUPS = "Backups"
ARQUIVO_MAPA = "restore_map.json"
TECLA_CAPTURA = "enter"
TECLA_SAIR = "esc"

# Ajustes de corte (Pixels)
CORTE_TOPO = 160
CORTE_BAIXO = 20
CORTE_LADOS = 10

class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def limpar_buffer_teclado():
    """Remove teclas 'presas' na memória para não pular perguntas"""
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        pass # Se não for Windows, ignora (mas a maioria dos users de pyautogui é Windows)

def preparar_ambiente():
    if not os.path.exists(PASTA_BACKUPS):
        os.makedirs(PASTA_BACKUPS)

def atualizar_mapa_recuperacao(nome_pasta_backup, caminho_destino_original):
    caminho_mapa = os.path.join(PASTA_BACKUPS, ARQUIVO_MAPA)
    dados = {}
    
    if os.path.exists(caminho_mapa):
        try:
            with open(caminho_mapa, "r", encoding='utf-8') as f:
                dados = json.load(f)
        except:
            dados = {}
    
    dados[nome_pasta_backup] = caminho_destino_original
    
    with open(caminho_mapa, "w", encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    
    print(f"{Cores.AZUL}[INFO] Mapeado para recuperação: {ARQUIVO_MAPA}{Cores.RESET}")

def detectar_janela():
    print(f"\n{Cores.AMARELO}--- CALIBRAGEM ---{Cores.RESET}")
    print("Clique na janela da aula AGORA.")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        janela = gw.getActiveWindow()
        if not janela: return None
        
        print(f"{Cores.VERDE}Alvo: {janela.title}{Cores.RESET}")
        return (janela.left + CORTE_LADOS, janela.top + CORTE_TOPO, 
                janela.width - (CORTE_LADOS*2), janela.height - CORTE_TOPO - CORTE_BAIXO)
    except:
        return None

def limpar_nome(nome):
    return re.sub(r'[<>:"/\\|?*]', '_', nome).strip()

def solicitar_destino():
    print("-" * 40)
    print("Onde salvar o PDF final? (Deixe vazio para pasta atual)")
    # Limpeza de buffer antes de pedir input importante
    limpar_buffer_teclado()
    caminho = input(">> Caminho: ").strip().replace('"', '')
    if not caminho or not os.path.isdir(caminho):
        return os.getcwd()
    return caminho

def iniciar_robo():
    preparar_ambiente()
    
    # 1. Configuração Inicial
    limpar_buffer_teclado() # Garante que inputs antigos não atrapalhem
    nome_arq = input(f"\n{Cores.VERDE}>> Nome do Arquivo: {Cores.RESET}").strip()
    if not nome_arq: nome_arq = f"Aula_{datetime.now().strftime('%H%M')}"
    
    nome_limpo = limpar_nome(nome_arq)
    dir_destino = solicitar_destino()
    
    nome_pasta_temp = f"temp_{nome_limpo}"
    caminho_backup_imgs = os.path.join(PASTA_BACKUPS, nome_pasta_temp)
    
    if not os.path.exists(caminho_backup_imgs):
        os.makedirs(caminho_backup_imgs)
        
    # 2. Calibragem
    regiao = detectar_janela()
    if not regiao: return

    print(f"\n{Cores.VERDE}=== CAPTURANDO ==={Cores.RESET}")
    print(f"ENTER = Print | ESC = Salvar e Sair")
    
    capturas = []
    count = 1
    
    # 3. Loop de Captura
    try:
        while True:
            if keyboard.is_pressed(TECLA_CAPTURA):
                fname = f"slide_{count:03d}.png"
                fpath = os.path.join(caminho_backup_imgs, fname)
                
                pyautogui.screenshot(fpath, region=regiao)
                capturas.append(fpath)
                print(f"{Cores.VERDE}[+] Slide {count} salvo no Backup{Cores.RESET}")
                count += 1
                time.sleep(0.4) # Delay para não tirar foto duplicada
            
            if keyboard.is_pressed(TECLA_SAIR):
                print(f"\n{Cores.AMARELO}Encerrando captura... Aguarde...{Cores.RESET}")
                time.sleep(1) # Pausa dramática para evitar clique fantasma
                break
            
            time.sleep(0.05)
            
    except KeyboardInterrupt: pass

    # 4. Finalização
    if capturas:
        print(f"\nGerando PDF em: {dir_destino}")
        caminho_pdf = os.path.join(dir_destino, f"{nome_limpo}.pdf")
        
        try:
            capturas.sort()
            with open(caminho_pdf, "wb") as f:
                f.write(img2pdf.convert(capturas))
            
            print(f"{Cores.VERDE}[SUCESSO] PDF Criado!{Cores.RESET}")
            print(f"Arquivo: {caminho_pdf}")
            
            atualizar_mapa_recuperacao(nome_pasta_temp, dir_destino)
            
        except Exception as e:
            print(f"{Cores.VERMELHO}Erro ao gerar PDF: {e}{Cores.RESET}")
    else:
        print(f"{Cores.VERMELHO}Nenhuma imagem capturada. Cancelando...{Cores.RESET}")
        try: os.rmdir(caminho_backup_imgs)
        except: pass

if __name__ == "__main__":
    while True:
        limpar_tela()
        print(f"{Cores.AZUL}ROBÔ ARCHITECT V4.1 (Estável){Cores.RESET}")
        
        iniciar_robo()
        
        print("\n" + "="*40)
        # Limpa o buffer de novo para o ENTER do print não pular essa pergunta
        limpar_buffer_teclado()
        resp = input("Pressione [ENTER] para Novo Arquivo ou digite [S] para Sair: ").lower()
        
        if resp == 's':
            print("Saindo...")
            break
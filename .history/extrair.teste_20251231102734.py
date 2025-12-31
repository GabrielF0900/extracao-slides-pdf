import pyautogui
import keyboard
import img2pdf
import pygetwindow as gw
import os
import time
import re
import shutil
import json  # <--- O CÉREBRO DA RECUPERAÇÃO
from datetime import datetime
import sys

# ===== CONFIGURAÇÕES GERAIS =====
PASTA_BACKUPS = "Backups"      # Onde ficam as imagens brutas (Cofre)
ARQUIVO_MAPA = "restore_map.json" # O mapa do tesouro
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

def preparar_ambiente():
    if not os.path.exists(PASTA_BACKUPS):
        os.makedirs(PASTA_BACKUPS)

def atualizar_mapa_recuperacao(nome_pasta_backup, caminho_destino_original):
    """Salva no JSON onde esse arquivo deve morar caso precise ser restaurado"""
    caminho_mapa = os.path.join(PASTA_BACKUPS, ARQUIVO_MAPA)
    dados = {}
    
    # Carrega mapa existente
    if os.path.exists(caminho_mapa):
        try:
            with open(caminho_mapa, "r", encoding='utf-8') as f:
                dados = json.load(f)
        except:
            dados = {}
    
    # Atualiza o registro
    # Chave: temp_NomeArquivo | Valor: C:\Users\...\Matematica
    dados[nome_pasta_backup] = caminho_destino_original
    
    # Salva
    with open(caminho_mapa, "w", encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    
    print(f"{Cores.AZUL}[INFO] Localização mapeada para recuperação futura.{Cores.RESET}")

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
    caminho = input(">> Caminho: ").strip().replace('"', '')
    if not caminho or not os.path.isdir(caminho):
        return os.getcwd()
    return caminho

def iniciar_robo():
    preparar_ambiente()
    
    # 1. Configuração Inicial
    nome_arq = input(f"\n{Cores.VERDE}>> Nome do Arquivo: {Cores.RESET}").strip()
    if not nome_arq: nome_arq = f"Aula_{datetime.now().strftime('%H%M')}"
    
    nome_limpo = limpar_nome(nome_arq)
    dir_destino = solicitar_destino() # Pergunta onde salvar o PDF
    
    # Define caminhos
    nome_pasta_temp = f"temp_{nome_limpo}"
    # Caminho temporário real (dentro de Backups para já ficar seguro)
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
                # Salva direto na pasta de Backup
                fname = f"slide_{count:03d}.png"
                fpath = os.path.join(caminho_backup_imgs, fname)
                
                pyautogui.screenshot(fpath, region=regiao)
                capturas.append(fpath)
                print(f"{Cores.VERDE}[+] Slide {count} salvo no Backup{Cores.RESET}")
                count += 1
                time.sleep(0.4)
            
            if keyboard.is_pressed(TECLA_SAIR):
                break
            time.sleep(0.05)
            
    except KeyboardInterrupt: pass

    # 4. Finalização (Gera PDF + Mapeia JSON)
    if capturas:
        print(f"\nGerando PDF em: {dir_destino}")
        caminho_pdf = os.path.join(dir_destino, f"{nome_limpo}.pdf")
        
        try:
            capturas.sort()
            with open(caminho_pdf, "wb") as f:
                f.write(img2pdf.convert(capturas))
            
            print(f"{Cores.VERDE}[SUCESSO] PDF Criado!{Cores.RESET}")
            
            # --- O PULO DO GATO: ATUALIZA O MAPA JSON ---
            atualizar_mapa_recuperacao(nome_pasta_temp, dir_destino)
            # --------------------------------------------
            
        except Exception as e:
            print(f"{Cores.VERMELHO}Erro ao gerar PDF: {e}{Cores.RESET}")
    else:
        # Se não tirou prints, limpa a pasta vazia
        try: os.rmdir(caminho_backup_imgs)
        except: pass

if __name__ == "__main__":
    while True:
        limpar_tela()
        print(f"{Cores.AZUL}ROBÔ ARCHITECT V4.0 (Captura + Backup + Mapa){Cores.RESET}")
        iniciar_robo()
        resp = input("\n[ENTER] Novo Arquivo | [S] Sair: ").lower()
        if resp == 's': break
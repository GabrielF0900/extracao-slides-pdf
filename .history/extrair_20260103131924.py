import mss
import mss.tools
import keyboard
import img2pdf
import pygetwindow as gw
import os
import time
import re
import shutil
import random
import ctypes
import sys
from datetime import datetime

# ===== CONFIGURAÇÕES DE FURTIVIDADE =====
# 1. Camufla o nome da janela do console
try:
    ctypes.windll.kernel32.SetConsoleTitleW("System Audio Service - Host")
except:
    pass

# --- CONFIGURAÇÕES DE CORTE (PIXELS) ---
CORTE_TOPO = 160
CORTE_BAIXO = 20
CORTE_LADOS = 10

def detectar_janela_ativa():
    print("\n--- DETECÇÃO AUTOMÁTICA ---")
    print("1. Clique no navegador AGORA.")
    
    for i in range(3, 0, -1):
        print(f"Calibrando em {i}...")
        time.sleep(1)
    
    try:
        janela = gw.getActiveWindow()
        if janela is None:
            print("Erro: Nenhuma janela detectada!")
            return None

        print(f"Alvo Detectado: '{janela.title}'")
        
        # Conversão para formato MSS (top, left, width, height)
        monitor = {
            "top": int(janela.top + CORTE_TOPO),
            "left": int(janela.left + CORTE_LADOS),
            "width": int(janela.width - (CORTE_LADOS * 2)),
            "height": int(janela.height - CORTE_TOPO - CORTE_BAIXO)
        }
        return monitor
    except Exception as e:
        print(f"Erro ao detectar janela: {e}")
        return None

def limpar_nome_arquivo(nome):
    return re.sub(r'[<>:"/\\|?*]', '_', nome)

def solicitar_nome_arquivo():
    print("-" * 30)
    nome_input = input(">> Digite o NOME do arquivo: ").strip()
    
    if not nome_input:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome_final = f"slide_padrao_{timestamp}.pdf"
    else:
        nome_limpo = limpar_nome_arquivo(nome_input)
        nome_final = nome_limpo + ".pdf" if not nome_limpo.lower().endswith(".pdf") else nome_limpo
    return nome_final

def iniciar_captura_inteligente():
    nome_arquivo = solicitar_nome_arquivo()
    
    # Define onde salvar (padrão pasta atual se der Enter)
    pasta_destino_pdf = os.getcwd()
    caminho_completo_pdf = os.path.join(pasta_destino_pdf, nome_arquivo)

    # Pasta temporária
    nome_base = os.path.splitext(nome_arquivo)[0] 
    pasta_temp_dinamica = f"temp_{nome_base}"
    if not os.path.exists(pasta_temp_dinamica):
        os.makedirs(pasta_temp_dinamica)

    # Calibração
    monitor_region = detectar_janela_ativa()
    if not monitor_region: return

    print(f"\n✅ MODO STEALTH ATIVO!")
    print(f"📂 Cache de imagens: {pasta_temp_dinamica}")
    print("\n--- COMANDOS ---")
    print(" [ENTER] -> Capturar (Delay Humano)")
    print(" [ESC]   -> Gerar PDF")
    
    capturas = []
    contador = 1
    
    # Inicializa engine MSS (Rápida e Invisível)
    with mss.mss() as sct:
        try:
            while True:
                if keyboard.is_pressed('enter'):
                    # --- FURTIVIDADE: Delay Aleatório ---
                    tempo_espera = random.uniform(0.15, 0.45)
                    time.sleep(tempo_espera) 

                    timestamp = datetime.now().strftime("%H%M%S")
                    nome_imagem = f"{pasta_temp_dinamica}/slide_{contador:03d}_{timestamp}.png"
                    
                    # Captura via MSS
                    sct_img = sct.grab(monitor_region)
                    mss.tools.to_png(sct_img.rgb, sct_img.size, output=nome_imagem)
                    
                    capturas.append(nome_imagem)
                    
                    print(f"[+] Slide {contador} (Delay: {tempo_espera:.2f}s)")
                    contador += 1
                    time.sleep(0.4) # Evita captura dupla

                elif keyboard.is_pressed('esc'):
                    print("\nGerando PDF...")
                    break
                
                time.sleep(0.02) # Alivia CPU

        except KeyboardInterrupt: pass

    if capturas:
        print(f"Processando PDF...")
        try:
            capturas.sort() # Garante ordem correta
            with open(caminho_completo_pdf, "wb") as f:
                f.write(img2pdf.convert(capturas))
            print(f"\n✅ SUCESSO! PDF: {nome_arquivo}")
            
            # Move para pasta de backups
            try:
                pasta_backups = os.path.join(os.getcwd(), "Backups")
                if not os.path.exists(pasta_backups): os.makedirs(pasta_backups)
                
                caminho_temp_em_backups = os.path.join(pasta_backups, pasta_temp_dinamica)
                if os.path.exists(caminho_temp_em_backups): shutil.rmtree(caminho_temp_em_backups)
                shutil.move(pasta_temp_dinamica, caminho_temp_em_backups)
                print(f"📂 Imagens movidas para backup seguro.")
            except: pass
            
        except Exception as e:
            print(f"Erro crítico ao gerar PDF: {e}")
            # Tenta salvar backup de emergência das imagens
    else:
        try: os.rmdir(pasta_temp_dinamica)
        except: pass

if __name__ == "__main__":
    while True:
        iniciar_captura_inteligente()
        print("\n[ENTER] Novo Arquivo | [DIGITE 'SAIR'] Fechar")
        if input(">> ").strip().upper() == "SAIR": break
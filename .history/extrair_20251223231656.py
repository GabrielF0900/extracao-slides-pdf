import pyautogui
import keyboard
import img2pdf
import pygetwindow as gw
import os
import time
from datetime import datetime

# --- Configurações ---
NOME_PDF_SAIDA = "conteudo_auto.pdf"
PASTA_TEMP = "temp_auto"

# AJUSTE FINO (pixels):
# Quanto cortar do topo da janela (Abas + Barra de Endereço + Favoritos)
# Se o print estiver cortando o site, diminua. Se aparecer a URL, aumente.
CORTE_TOPO = 110 
CORTE_LADOS = 0    # Caso tenha borda lateral indesejada

def detectar_janela_ativa():
    print("\n--- DETECÇÃO AUTOMÁTICA ---")
    print("1. Vou capturar a janela que estiver ATIVA (em foco).")
    print("2. Você tem 3 SEGUNDOS para clicar no seu navegador após iniciar.")
    
    # Contagem regressiva visual
    for i in range(3, 0, -1):
        print(f"Detectando em {i}...")
        time.sleep(1)
    
    try:
        # Pega a janela ativa no momento
        janela = gw.getActiveWindow()
        
        if janela is None:
            print("Erro: Nenhuma janela detectada!")
            return None

        print(f"Janela detectada: '{janela.title}'")
        
        # Calcula a região de corte
        # (left, top, width, height)
        x = janela.left + CORTE_LADOS
        y = janela.top + CORTE_TOPO
        width = janela.width - (CORTE_LADOS * 2)
        
        # Remove o cabeçalho da altura total
        height = janela.height - CORTE_TOPO 
        
        # Ajuste de segurança para não pegar barra de tarefas se a janela não estiver maximizada
        if janela.isMaximized:
             # Se maximizado, geralmente tiramos uns 40px do fundo (barra de tarefas) se ela estiver visível
             # Mas vamos tentar pegar a altura da janela menos o topo
             pass

        return (x, y, width, height)

    except Exception as e:
        print(f"Erro ao detectar janela: {e}")
        return None

def iniciar_captura_inteligente():
    if not os.path.exists(PASTA_TEMP):
        os.makedirs(PASTA_TEMP)

    # 1. Detecta a janela automaticamente
    region_capture = detectar_janela_ativa()
    
    if not region_capture:
        print("Falha na calibração. Tente novamente.")
        return

    print(f"\nÁrea definida: {region_capture}")
    print("--- PRONTO PARA CAPTURAR ---")
    print(" [ENTER] -> Salva o slide")
    print(" [ESC]   -> Gera o PDF")
    
    capturas = []
    contador = 1
    
    try:
        while True:
            if keyboard.is_pressed('enter'):
                timestamp = datetime.now().strftime("%H%M%S")
                nome_imagem = f"{PASTA_TEMP}/auto_{contador:03d}_{timestamp}.png"
                
                # Captura a região detectada automaticamente
                pyautogui.screenshot(nome_imagem, region=region_capture)
                capturas.append(nome_imagem)
                
                print(f"[FOTO] Página {contador} salva.")
                contador += 1
                time.sleep(0.5) 

            elif keyboard.is_pressed('esc'):
                print("\nGerando PDF...")
                break
            
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    # --- Gerar PDF ---
    if capturas:
        try:
            with open(NOME_PDF_SAIDA, "wb") as f:
                f.write(img2pdf.convert(capturas))
            print(f"SUCESSO! Salvo em: {os.path.abspath(NOME_PDF_SAIDA)}")
            
            # Limpeza
            # for img in capturas: os.remove(img)
            # os.rmdir(PASTA_TEMP)
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    iniciar_captura_inteligente()
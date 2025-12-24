import pyautogui
import keyboard
import img2pdf
import pygetwindow as gw
import os
import time
from datetime import datetime

# --- Configurações ---
NOME_PDF_SAIDA = "conteudo_slides.pdf"
PASTA_TEMP = "temp_slides"

# --- AJUSTE FINO (EM PIXELS) ---
# Aumente este valor se ainda aparecerem abas ou barra de favoritos
CORTE_TOPO = 160  

# Aumente este valor se aparecer rodapé do site ou barra de tarefas
CORTE_BAIXO = 20  

# Ajuste se tiver bordas pretas ou scroll lateral
CORTE_LADOS = 10   

def detectar_janela_ativa():
    print("\n--- DETECÇÃO AUTOMÁTICA ---")
    print("1. Vou capturar a janela que estiver ATIVA.")
    print("2. Clique no navegador AGORA.")
    
    # Contagem regressiva
    for i in range(3, 0, -1):
        print(f"Calibrando em {i}...")
        time.sleep(1)
    
    try:
        janela = gw.getActiveWindow()
        
        if janela is None:
            print("Erro: Nenhuma janela detectada!")
            return None

        print(f"Janela Alvo: '{janela.title}'")
        
        # --- CÁLCULO DA ÁREA DE CORTE ---
        # X: Posição inicial horizontal (Esquerda + Corte lateral)
        x = janela.left + CORTE_LADOS
        
        # Y: Posição inicial vertical (Topo original + Corte das abas)
        y = janela.top + CORTE_TOPO
        
        # Width: Largura total - cortes da esquerda e direita
        width = janela.width - (CORTE_LADOS * 2)
        
        # Height: Altura total - (Corte do Topo + Corte de Baixo)
        # É aqui que garantimos que o final da janela não entre
        height = janela.height - CORTE_TOPO - CORTE_BAIXO
        
        return (x, y, width, height)

    except Exception as e:
        print(f"Erro ao detectar janela: {e}")
        return None

def iniciar_captura_inteligente():
    if not os.path.exists(PASTA_TEMP):
        os.makedirs(PASTA_TEMP)

    region_capture = detectar_janela_ativa()
    
    if not region_capture:
        print("Falha na calibração. Tente novamente.")
        return

    print(f"\nÁrea de captura (X, Y, L, A): {region_capture}")
    print("--- COMANDOS ---")
    print(" [ENTER] -> Tirar Print")
    print(" [ESC]   -> Finalizar e Criar PDF")
    
    capturas = []
    contador = 1
    
    try:
        while True:
            if keyboard.is_pressed('enter'):
                timestamp = datetime.now().strftime("%H%M%S")
                nome_imagem = f"{PASTA_TEMP}/slide_{contador:03d}_{timestamp}.png"
                
                # Captura apenas a região calculada
                pyautogui.screenshot(nome_imagem, region=region_capture)
                capturas.append(nome_imagem)
                
                print(f"[SUCESSO] Slide {contador} capturado.")
                contador += 1
                time.sleep(0.5) # Evita capturas duplas acidentais

            elif keyboard.is_pressed('esc'):
                print("\nEncerrando captura...")
                break
            
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    # --- Gerar PDF ---
    if capturas:
        print("Gerando PDF, aguarde...")
        try:
            with open(NOME_PDF_SAIDA, "wb") as f:
                f.write(img2pdf.convert(capturas))
            print(f"\nPDF PRONTO: {os.path.abspath(NOME_PDF_SAIDA)}")
            
            # Limpeza automática das imagens temporárias (Opcional - descomente para ativar)
            # for img in capturas: os.remove(img)
            # os.rmdir(PASTA_TEMP)
            
        except Exception as e:
            print(f"Erro ao salvar PDF: {e}")
    else:
        print("Nenhuma imagem foi capturada.")

if __name__ == "__main__":
    iniciar_captura_inteligente()
import pyautogui
import keyboard
import img2pdf
import os
import time
from datetime import datetime

# --- Configurações ---
NOME_PDF_SAIDA = "documento_final.pdf"
PASTA_TEMP = "temp_manual"

def iniciar_captura_manual():
    # Cria a pasta temporária se não existir
    if not os.path.exists(PASTA_TEMP):
        os.makedirs(PASTA_TEMP)
        
    print("--- MODO DE CAPTURA MANUAL ---")
    print("1. Posicione sua apresentação/tela.")
    print("2. Pressione [ENTER] para capturar a tela atual.")
    print("3. Pressione [ESC] para finalizar e gerar o PDF.")
    print("------------------------------")
    
    capturas = []
    contador = 1
    
    try:
        while True:
            # CAPTURAR (ENTER)
            if keyboard.is_pressed('enter'):
                # Gera nome do arquivo
                timestamp = datetime.now().strftime("%H%M%S")
                nome_imagem = f"{PASTA_TEMP}/slide_{contador:03d}_{timestamp}.png"
                
                # Tira o print
                pyautogui.screenshot(nome_imagem)
                capturas.append(nome_imagem)
                
                print(f"[OK] Slide {contador} capturado!")
                contador += 1
                
                # IMPORTANTÍSSIMO: Espera um pouco para você soltar a tecla
                # Senão ele tira 50 fotos em 1 segundo que você segurou o Enter
                time.sleep(0.5) 

            # FINALIZAR (ESC)
            elif keyboard.is_pressed('esc'):
                print("\nFinalizando captura...")
                break
            
            # Pequena pausa para não usar 100% da CPU verificando o teclado
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    # --- Compilação do PDF ---
    if capturas:
        print(f"\nGerando PDF com {len(capturas)} páginas...")
        try:
            with open(NOME_PDF_SAIDA, "wb") as f:
                f.write(img2pdf.convert(capturas))
            print(f"SUCESSO! Arquivo salvo em: {os.path.abspath(NOME_PDF_SAIDA)}")
            
            # Limpeza das imagens temporárias (Opcional - Remova o # abaixo para ativar)
            # for img in capturas: os.remove(img)
            # os.rmdir(PASTA_TEMP)
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
    else:
        print("Nenhuma imagem foi capturada. PDF não gerado.")

if __name__ == "__main__":
    iniciar_captura_manual()
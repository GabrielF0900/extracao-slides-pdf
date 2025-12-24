import pyautogui
import keyboard
import img2pdf
import pygetwindow as gw
import os
import time
from datetime import datetime

# --- CONFIGURAÇÕES DE CORTE (PIXELS) ---
PASTA_TEMP = "temp_slides"

# Ajuste conforme necessário (baseado na nossa última conversa)
CORTE_TOPO = 160   # Remove abas e barra de endereço
CORTE_BAIXO = 20   # Remove rodapé/barra de status
CORTE_LADOS = 10   # Remove bordas laterais

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
        x = janela.left + CORTE_LADOS
        y = janela.top + CORTE_TOPO
        width = janela.width - (CORTE_LADOS * 2)
        height = janela.height - CORTE_TOPO - CORTE_BAIXO
        
        return (x, y, width, height)

    except Exception as e:
        print(f"Erro ao detectar janela: {e}")
        return None

def solicitar_nome_arquivo():
    print("-" * 30)
    nome = input(">> Digite o nome para o PDF final (ex: aula_01): ").strip()
    print("-" * 30)
    
    if not nome:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome = f"slide_padrao_{timestamp}.pdf"
        print(f"Nenhum nome digitado. Usando: {nome}")
    
    # Garante a extensão .pdf
    if not nome.lower().endswith(".pdf"):
        nome += ".pdf"
        
    return nome

def iniciar_captura_inteligente():
    # 1. Pergunta o nome do arquivo PRIMEIRO
    nome_pdf_final = solicitar_nome_arquivo()

    if not os.path.exists(PASTA_TEMP):
        os.makedirs(PASTA_TEMP)

    # 2. Calibra a janela
    region_capture = detectar_janela_ativa()
    
    if not region_capture:
        print("Falha na calibração. Tente novamente.")
        return

    print(f"\nÁrea configurada. Salvando em: '{nome_pdf_final}'")
    print("--- COMANDOS ---")
    print(" [ENTER] -> Capturar Slide")
    print(" [ESC]   -> Finalizar e Gerar PDF")
    
    capturas = []
    contador = 1
    
    try:
        while True:
            if keyboard.is_pressed('enter'):
                timestamp = datetime.now().strftime("%H%M%S")
                nome_imagem = f"{PASTA_TEMP}/slide_{contador:03d}_{timestamp}.png"
                
                # Captura a região
                pyautogui.screenshot(nome_imagem, region=region_capture)
                capturas.append(nome_imagem)
                
                print(f"[SUCESSO] Slide {contador} salvo.")
                contador += 1
                time.sleep(0.5) 

            elif keyboard.is_pressed('esc'):
                print("\nEncerrando captura...")
                break
            
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    # --- Gerar PDF com o nome escolhido ---
    if capturas:
        print(f"Gerando arquivo '{nome_pdf_final}', aguarde...")
        try:
            with open(nome_pdf_final, "wb") as f:
                f.write(img2pdf.convert(capturas))
            print(f"\nPDF PRONTO: {os.path.abspath(nome_pdf_final)}")
            
            # Limpeza opcional (remova o # abaixo para ativar)
            # for img in capturas: os.remove(img)
            # os.rmdir(PASTA_TEMP)
            
        except Exception as e:
            print(f"Erro ao salvar PDF: {e}")
            # Tenta salvar com nome de emergência caso o nome contenha caracteres inválidos
            try:
                print("Tentando salvar com nome de emergência...")
                with open("backup_emergencia.pdf", "wb") as f:
                    f.write(img2pdf.convert(capturas))
            except:
                pass
    else:
        print("Nenhuma imagem foi capturada. PDF não gerado.")

if __name__ == "__main__":
    iniciar_captura_inteligente()
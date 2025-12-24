import pyautogui
import keyboard
import img2pdf
import pygetwindow as gw
import os
import time
import re  # Import para limpar caracteres inválidos
from datetime import datetime

# --- CONFIGURAÇÕES DE CORTE (PIXELS) ---
PASTA_TEMP = "temp_slides"
CORTE_TOPO = 160   
CORTE_BAIXO = 20   
CORTE_LADOS = 10   

def detectar_janela_ativa():
    print("\n--- DETECÇÃO AUTOMÁTICA ---")
    print("1. Vou capturar a janela que estiver ATIVA.")
    print("2. Clique no navegador AGORA.")
    
    for i in range(3, 0, -1):
        print(f"Calibrando em {i}...")
        time.sleep(1)
    
    try:
        janela = gw.getActiveWindow()
        if janela is None:
            print("Erro: Nenhuma janela detectada!")
            return None

        print(f"Janela Alvo: '{janela.title}'")
        
        x = janela.left + CORTE_LADOS
        y = janela.top + CORTE_TOPO
        width = janela.width - (CORTE_LADOS * 2)
        height = janela.height - CORTE_TOPO - CORTE_BAIXO
        
        return (x, y, width, height)
    except Exception as e:
        print(f"Erro ao detectar janela: {e}")
        return None

def limpar_nome_arquivo(nome):
    # Remove caracteres proibidos no Windows: < > : " / \ | ? *
    # Substitui por underline (_)
    nome_limpo = re.sub(r'[<>:"/\\|?*]', '_', nome)
    return nome_limpo

def solicitar_nome_arquivo():
    print("-" * 30)
    nome_input = input(">> Digite o nome do arquivo: ").strip()
    print("-" * 30)
    
    if not nome_input:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome_final = f"slide_padrao_{timestamp}.pdf"
        print(f"Nada digitado. Usando: {nome_final}")
    else:
        # 1. Limpa o nome (remove caracteres proibidos)
        nome_limpo = limpar_nome_arquivo(nome_input)
        
        # 2. Garante a extensão .pdf
        if not nome_limpo.lower().endswith(".pdf"):
            nome_final = nome_limpo + ".pdf"
        else:
            nome_final = nome_limpo
            
        if nome_input != nome_final:
            print(f"Aviso: Nome ajustado para '{nome_final}' (removemos caracteres proibidos)")
            
    return nome_final

def iniciar_captura_inteligente():
    nome_pdf_final = solicitar_nome_arquivo()

    if not os.path.exists(PASTA_TEMP):
        os.makedirs(PASTA_TEMP)

    region_capture = detectar_janela_ativa()
    
    if not region_capture:
        print("Falha na calibração. Tente novamente.")
        return

    print(f"\nÁrea configurada. Salvando como: '{nome_pdf_final}'")
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

    if capturas:
        print(f"Gerando arquivo '{nome_pdf_final}', aguarde...")
        try:
            with open(nome_pdf_final, "wb") as f:
                f.write(img2pdf.convert(capturas))
            print(f"\n✅ SUCESSO! PDF salvo em: {os.path.abspath(nome_pdf_final)}")
            
            # Limpeza das imagens (Opcional - Remova o # abaixo para ativar)
            # for img in capturas: os.remove(img)
            # os.rmdir(PASTA_TEMP)
            
        except Exception as e:
            print("\n❌ ERRO AO SALVAR COM O NOME ESCOLHIDO!")
            print(f"Motivo do erro: {e}")
            print("-" * 30)
            
            # Backup
            try:
                print("⚠️ Tentando salvar como 'backup_emergencia.pdf'...")
                with open("backup_emergencia.pdf", "wb") as f:
                    f.write(img2pdf.convert(capturas))
                print("Arquivo salvo como backup_emergencia.pdf")
            except:
                print("Erro crítico: Não foi possível salvar nem o backup.")
    else:
        print("Nenhuma imagem capturada.")

if __name__ == "__main__":
    iniciar_captura_inteligente()
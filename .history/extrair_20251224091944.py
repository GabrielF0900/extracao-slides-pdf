import pyautogui
import keyboard
import img2pdf
import pygetwindow as gw
import os
import time
import re
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
    nome_limpo = re.sub(r'[<>:"/\\|?*]', '_', nome)
    return nome_limpo

def solicitar_nome_arquivo():
    print("-" * 30)
    nome_input = input(">> Digite o NOME do arquivo: ").strip()
    
    if not nome_input:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome_final = f"slide_padrao_{timestamp}.pdf"
        print(f"Nada digitado. Usando: {nome_final}")
    else:
        nome_limpo = limpar_nome_arquivo(nome_input)
        if not nome_limpo.lower().endswith(".pdf"):
            nome_final = nome_limpo + ".pdf"
        else:
            nome_final = nome_limpo
            
        if nome_input != nome_final:
            print(f"Aviso: Nome ajustado para '{nome_final}'")
            
    return nome_final

def solicitar_diretorio_destino():
    print("-" * 30)
    print("Onde deseja salvar? (Deixe em branco para salvar na pasta atual)")
    print("Exemplo: C:\\Users\\gabri\\Desktop\\Material")
    caminho_input = input(">> Cole o CAMINHO da pasta: ").strip()
    print("-" * 30)

    # Se deixar em branco, usa a pasta atual
    if not caminho_input:
        print("Usando diretório atual do script.")
        return os.getcwd()

    # Remove aspas que o Windows coloca ao usar "Copiar como caminho"
    caminho_limpo = caminho_input.replace('"', '').replace("'", "")

    # Verifica se a pasta existe
    if os.path.isdir(caminho_limpo):
        return caminho_limpo
    else:
        print(f"❌ A pasta '{caminho_limpo}' não foi encontrada.")
        print("⚠️  Salvando na pasta atual para garantir.")
        return os.getcwd()

def iniciar_captura_inteligente():
    # 1. Solicita Nome
    nome_arquivo = solicitar_nome_arquivo()
    
    # 2. Solicita Pasta
    pasta_destino = solicitar_diretorio_destino()
    
    # 3. Monta o caminho completo (Pasta + Nome)
    caminho_completo_final = os.path.join(pasta_destino, nome_arquivo)

    if not os.path.exists(PASTA_TEMP):
        os.makedirs(PASTA_TEMP)

    # 4. Calibragem
    region_capture = detectar_janela_ativa()
    
    if not region_capture:
        print("Falha na calibração. Tente novamente.")
        return

    print(f"\n✅ Tudo pronto! O arquivo será salvo em:\n📂 {caminho_completo_final}")
    print("\n--- COMANDOS ---")
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
        print(f"Gerando PDF em: {pasta_destino} ...")
        try:
            # Tenta salvar no caminho escolhido pelo usuário
            with open(caminho_completo_final, "wb") as f:
                f.write(img2pdf.convert(capturas))
            print(f"\n✅ SUCESSO! Arquivo criado:\n{caminho_completo_final}")
            
            # Limpeza (Opcional)
            # for img in capturas: os.remove(img)
            # os.rmdir(PASTA_TEMP)
            
        except Exception as e:
            print("\n❌ ERRO AO SALVAR NA PASTA DE DESTINO!")
            print(f"Erro: {e}")
            print("-" * 30)
            
            # Backup na pasta do script (plano B)
            try:
                backup_name = "backup_" + nome_arquivo
                print(f"⚠️ Tentando salvar aqui mesmo como '{backup_name}'...")
                with open(backup_name, "wb") as f:
                    f.write(img2pdf.convert(capturas))
                print(f"✅ Salvo como backup: {os.path.abspath(backup_name)}")
            except:
                print("Erro crítico: Não foi possível salvar o backup.")
    else:
        print("Nenhuma imagem capturada.")

if __name__ == "__main__":
    iniciar_captura_inteligente()
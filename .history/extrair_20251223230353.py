import pyautogui
import keyboard
import img2pdf
import os
import time
from PIL import Image, ImageChops

# --- Configurações ---
NOME_SAIDA = "apresentacao_capturada.pdf"
PASTA_TEMP = "temp_robot"
INTERVALO_CHECK = 0.5  # Verifica mudanças a cada 0.5 segundos

def imagens_sao_iguais(img1, img2):
    """
    Compara duas imagens. Retorna True se forem idênticas.
    Usa diferença de pixels (ImageChops) para ser muito rápido.
    """
    if img1 is None or img2 is None:
        return False
        
    # Calcula a diferença absoluta entre as imagens
    diff = ImageChops.difference(img1, img2)
    
    # Se getbbox() retornar None, significa que não há diferenças (pixels pretos)
    return diff.getbbox() is None

def iniciar_robo_observador():
    if not os.path.exists(PASTA_TEMP):
        os.makedirs(PASTA_TEMP)
        
    print("--- ROBÔ OBSERVADOR INICIADO ---")
    print("1. O script vai monitorar sua tela.")
    print("2. Ele só salva quando você MUDAR o slide/tela.")
    print("3. Pressione 'ESC' para finalizar e gerar o PDF.")
    print("Começando em 5 segundos...")
    time.sleep(5)
    
    capturas = []
    ultima_imagem_salva = None
    contador = 1
    
    try:
        while True:
            if keyboard.is_pressed('esc'):
                print("\nComando de parada recebido...")
                break
            
            # Tira print da tela atual (em memória, sem salvar no disco ainda)
            imagem_atual = pyautogui.screenshot()
            
            # A MÁGICA: Compara com a última imagem salva
            # Se for a primeira imagem OU se for diferente da anterior
            if ultima_imagem_salva is None or not imagens_sao_iguais(ultima_imagem_salva, imagem_atual):
                
                # Salva no disco
                nome_arq = f"{PASTA_TEMP}/slide_{contador:03d}.png"
                imagem_atual.save(nome_arq)
                capturas.append(nome_arq)
                
                # Atualiza a referência
                ultima_imagem_salva = imagem_atual
                print(f"[NOVO] Slide {contador} detectado e capturado.")
                contador += 1
            else:
                # Se for igual, apenas ignora (passa o loop)
                pass
            
            # Pequena pausa para não fritar a CPU
            time.sleep(INTERVALO_CHECK)
            
    except KeyboardInterrupt:
        pass

    # --- Gerar PDF ---
    if capturas:
        print(f"\nCompilando {len(capturas)} slides únicos em PDF...")
        with open(NOME_SAIDA, "wb") as f:
            f.write(img2pdf.convert(capturas))
        print(f"Sucesso! PDF gerado: {os.path.abspath(NOME_SAIDA)}")
        
        # Limpeza (opcional)
        # for img in capturas: os.remove(img)
        # os.rmdir(PASTA_TEMP)
    else:
        print("Nenhuma imagem foi capturada.")

if __name__ == "__main__":
    iniciar_robo_observador()
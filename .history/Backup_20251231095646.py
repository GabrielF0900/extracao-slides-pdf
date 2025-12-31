import os
import sys
import keyboard
import img2pdf  # Usando a biblioteca do segundo script (mais eficiente)
from pathlib import Path
import time
from datetime import datetime

# ===== CONFIGURAÇÕES =====
PASTA_ORIGEM = "Backups"
PASTA_DESTINO = "Pdfs_Backup"  # Nome solicitado
EXTENSOES_IMAGEM = {'.jpg', '.jpeg', '.png', '.bmp'}
TECLA_INICIO = "f9"  # Tecla para iniciar o processo

# ===== CORES PARA TERMINAL =====
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    RESET = '\033[0m'

# ===== FUNÇÕES DE LOG =====
def log_info(mensagem):
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} {mensagem}")

def log_sucesso(mensagem):
    print(f"{Cores.VERDE}[✓]{Cores.RESET} {mensagem}")

def log_aviso(mensagem):
    print(f"{Cores.AMARELO}[!]{Cores.RESET} {mensagem}")

def log_erro(mensagem):
    print(f"{Cores.VERMELHO}[✗]{Cores.RESET} {mensagem}")

# ===== LÓGICA DO PROGRAMA =====

def preparar_diretorios():
    """Verifica se a origem existe e cria o destino"""
    if not os.path.exists(PASTA_ORIGEM):
        log_erro(f"A pasta '{PASTA_ORIGEM}' não existe! Rode o robô de captura primeiro.")
        return False
    
    if not os.path.exists(PASTA_DESTINO):
        os.makedirs(PASTA_DESTINO)
        log_sucesso(f"Pasta de destino '{PASTA_DESTINO}' criada.")
    
    return True

def limpar_nome_pasta(nome_pasta):
    """Remove o prefixo 'temp_' para o nome do PDF ficar bonito"""
    if nome_pasta.startswith("temp_"):
        return nome_pasta.replace("temp_", "")
    return nome_pasta

def gerar_pdf_da_pasta(caminho_pasta, nome_pasta):
    """Lógica de conversão usando img2pdf (do seu segundo script)"""
    
    # 1. Encontrar todas as imagens
    imagens = []
    for arquivo in os.listdir(caminho_pasta):
        ext = Path(arquivo).suffix.lower()
        if ext in EXTENSOES_IMAGEM:
            imagens.append(os.path.join(caminho_pasta, arquivo))
    
    if not imagens:
        log_aviso(f"A pasta '{nome_pasta}' está vazia ou sem imagens.")
        return

    # 2. Ordenar imagens (slide_001, slide_002...)
    # A ordenação padrão de strings funciona bem aqui por causa dos zeros à esquerda
    imagens.sort()
    
    # 3. Definir nome e caminho do PDF
    nome_pdf_limpo = limpar_nome_pasta(nome_pasta) + ".pdf"
    caminho_pdf_final = os.path.join(PASTA_DESTINO, nome_pdf_limpo)

    log_info(f"Processando '{nome_pasta}' ({len(imagens)} slides)...")

    # 4. Converter usando img2pdf (Mais rápido e mantém qualidade)
    try:
        with open(caminho_pdf_final, "wb") as f:
            f.write(img2pdf.convert(imagens))
        log_sucesso(f"PDF Gerado: {nome_pdf_limpo}")
    except Exception as e:
        log_erro(f"Falha ao criar PDF de '{nome_pasta}': {e}")

def processar_backups():
    """Itera sobre todas as pastas em Backups"""
    print("\n" + "="*50)
    print(f"{Cores.CIANO}INICIANDO CONVERSÃO EM MASSA{Cores.RESET}")
    print("="*50 + "\n")

    if not preparar_diretorios():
        return

    # Lista todas as subpastas em Backups
    itens = os.listdir(PASTA_ORIGEM)
    subpastas = [d for d in itens if os.path.isdir(os.path.join(PASTA_ORIGEM, d))]

    if not subpastas:
        log_aviso("Nenhuma pasta encontrada dentro de 'Backups'.")
        return

    # Processa cada pasta
    total = len(subpastas)
    for i, pasta in enumerate(subpastas, 1):
        caminho_completo = os.path.join(PASTA_ORIGEM, pasta)
        print(f"\n[{i}/{total}] Verificando: {pasta}")
        gerar_pdf_da_pasta(caminho_completo, pasta)

    print("\n" + "="*50)
    print(f"{Cores.VERDE}TODOS OS PDFs FORAM PROCESSADOS!{Cores.RESET}")
    print(f"Verifique a pasta: {os.path.abspath(PASTA_DESTINO)}")
    print("="*50 + "\n")

def aguardar_comando():
    """Loop principal aguardando o usuário"""
    print("\n" + "="*60)
    print(f"{Cores.VERDE}   GERADOR DE PDFs AUTOMÁTICO (Pós-Robô){Cores.RESET}")
    print("="*60)
    print(f"Monitorando pasta: {Cores.AMARELO}{PASTA_ORIGEM}{Cores.RESET}")
    print(f"Destino dos PDFs : {Cores.AMARELO}{PASTA_DESTINO}{Cores.RESET}")
    print("-" * 60)
    print(f"PRESSIONE {Cores.CIANO}[F9]{Cores.RESET} PARA PROCESSAR TUDO AGORA")
    print(f"PRESSIONE {Cores.VERMELHO}[ESC]{Cores.RESET} PARA SAIR")
    print("="*60 + "\n")

    while True:
        try:
            if keyboard.is_pressed(TECLA_INICIO):
                processar_backups()
                time.sleep(1) # Delay para não repetir comando
                print("\nAguardando novo comando (F9 para rodar novamente, ESC para sair)...")

            if keyboard.is_pressed("esc"):
                print("\nSaindo...")
                sys.exit(0)
            
            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nEncerrado pelo usuário.")
            sys.exit(0)

if __name__ == "__main__":
    aguardar_comando()
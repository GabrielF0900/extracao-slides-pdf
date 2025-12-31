import os
import sys
import keyboard
import img2pdf
from PIL import Image
from pathlib import Path
import time
from datetime import datetime

# ===== CONFIGURAÇÕES =====
PASTA_BACKUPS = r"Backups"
PASTA_PDFS = r"Pdfs_Backups"
EXTENSOES_IMAGEM = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
TECLA_ESPECIAL = "f9"  # Tecla especial para ativar o backup (F9)

# ===== CORES PARA TERMINAL =====
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

def log_info(mensagem):
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} {mensagem}")

def log_sucesso(mensagem):
    print(f"{Cores.VERDE}[✓]{Cores.RESET} {mensagem}")

def log_aviso(mensagem):
    print(f"{Cores.AMARELO}[!]{Cores.RESET} {mensagem}")

def log_erro(mensagem):
    print(f"{Cores.VERMELHO}[✗]{Cores.RESET} {mensagem}")

def criar_pasta_pdfs():
    """Cria a pasta Pdfs_Backups se não existir"""
    if not os.path.exists(PASTA_PDFS):
        os.makedirs(PASTA_PDFS)
        log_sucesso(f"Pasta '{PASTA_PDFS}' criada!")
    else:
        log_info(f"Pasta '{PASTA_PDFS}' já existe!")

def mapear_pastas_com_imagens():
    """Mapeia todas as subpastas dentro de Backups que contêm imagens"""
    pastas_mapeadas = {}
    
    if not os.path.exists(PASTA_BACKUPS):
        log_erro(f"Pasta '{PASTA_BACKUPS}' não encontrada!")
        return pastas_mapeadas
    
    log_info(f"Mapeando pastas em '{PASTA_BACKUPS}'...")
    
    for pasta_nome in os.listdir(PASTA_BACKUPS):
        caminho_pasta = os.path.join(PASTA_BACKUPS, pasta_nome)
        
        if os.path.isdir(caminho_pasta):
            imagens = []
            
            # Busca por imagens na pasta
            for arquivo in os.listdir(caminho_pasta):
                extensao = Path(arquivo).suffix.lower()
                if extensao in EXTENSOES_IMAGEM:
                    caminho_imagem = os.path.join(caminho_pasta, arquivo)
                    imagens.append((arquivo, caminho_imagem))
            
            if imagens:
                # Ordena as imagens pelo nome (ordem de prints)
                imagens.sort(key=lambda x: x[0])
                pastas_mapeadas[pasta_nome] = imagens
                log_sucesso(f"Pasta '{pasta_nome}' mapeada: {len(imagens)} imagem(ns)")
    
    if not pastas_mapeadas:
        log_aviso("Nenhuma pasta com imagens encontrada em 'Backups'!")
    
    return pastas_mapeadas

def converter_imagens_para_pdf(pasta_nome, imagens):
    """Converte todas as imagens de uma pasta em um único PDF"""
    
    # Cria subpasta dentro de Pdfs_Backups com o mesmo nome
    pasta_saida = os.path.join(PASTA_PDFS, pasta_nome)
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
    
    try:
        # Lista para armazenar caminhos das imagens em formato PIL
        imagens_pil = []
        
        log_info(f"Convertendo {len(imagens)} imagem(ns) de '{pasta_nome}'...")
        
        for nome_arquivo, caminho_imagem in imagens:
            try:
                # Abre a imagem e converte para RGB (necessário para PDF)
                imagem = Image.open(caminho_imagem)
                
                # Se for RGBA ou outro modo, converte para RGB
                if imagem.mode != 'RGB':
                    imagem = imagem.convert('RGB')
                
                imagens_pil.append(imagem)
                log_info(f"  → Processada: {nome_arquivo}")
                
            except Exception as e:
                log_erro(f"  Erro ao processar '{nome_arquivo}': {str(e)}")
        
        if imagens_pil:
            # Cria um PDF com todas as imagens
            caminho_pdf = os.path.join(pasta_saida, f"{pasta_nome}.pdf")
            
            # Salva o PDF
            imagens_pil[0].save(
                caminho_pdf,
                save_all=True,
                append_images=imagens_pil[1:],
                duration=200,
                loop=0
            )
            
            log_sucesso(f"PDF criado: '{caminho_pdf}'")
            
            # Cria também PDFs individuais para cada imagem
            criar_pdfs_individuais(pasta_saida, imagens_pil, imagens)
            
        else:
            log_erro(f"Nenhuma imagem pôde ser processada em '{pasta_nome}'!")
            
    except Exception as e:
        log_erro(f"Erro ao converter imagens de '{pasta_nome}': {str(e)}")

def criar_pdfs_individuais(pasta_saida, imagens_pil, imagens_originais):
    """Cria PDFs individuais para cada imagem"""
    
    log_info("Criando PDFs individuais...")
    
    for i, (imagem, (nome_arquivo, _)) in enumerate(zip(imagens_pil, imagens_originais)):
        nome_sem_extensao = Path(nome_arquivo).stem
        caminho_pdf_individual = os.path.join(pasta_saida, f"{nome_sem_extensao}.pdf")
        
        try:
            imagem.save(caminho_pdf_individual)
            log_info(f"  → PDF individual: {nome_sem_extensao}.pdf")
        except Exception as e:
            log_erro(f"  Erro ao criar PDF individual '{nome_sem_extensao}': {str(e)}")

def processar_backups():
    """Função principal que coordena todo o processo de backup"""
    
    print("\n" + "="*50)
    print(f"{Cores.VERDE}INICIANDO PROCESSAMENTO DE BACKUPS{Cores.RESET}")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*50 + "\n")
    
    # Cria pasta de PDFs
    criar_pasta_pdfs()
    
    # Mapeia pastas com imagens
    pastas_mapeadas = mapear_pastas_com_imagens()
    
    if not pastas_mapeadas:
        log_aviso("Nenhuma pasta para processar!")
        return
    
    print(f"\n{Cores.AMARELO}Iniciando conversão de imagens...{Cores.RESET}\n")
    
    # Processa cada pasta
    total_pastas = len(pastas_mapeadas)
    for idx, (pasta_nome, imagens) in enumerate(pastas_mapeadas.items(), 1):
        print(f"\n[{idx}/{total_pastas}] Processando '{pasta_nome}'...")
        converter_imagens_para_pdf(pasta_nome, imagens)
    
    print("\n" + "="*50)
    print(f"{Cores.VERDE}PROCESSAMENTO CONCLUÍDO!{Cores.RESET}")
    print("="*50 + "\n")

def aguardar_entrada():
    """Aguarda entrada do usuário (digitação 'Backup' ou tecla F9)"""
    
    print("\n" + "="*60)
    print(f"{Cores.AZUL}MONITORANDO ENTRADAS{Cores.RESET}")
    print(f"{Cores.VERDE}• Digite 'Backup' + ENTER para iniciar{Cores.RESET}")
    print(f"{Cores.VERDE}• Ou pressione F9 para iniciar{Cores.RESET}")
    print(f"{Cores.VERDE}• Pressione ESC para sair{Cores.RESET}")
    print("="*60 + "\n")
    
    entrada = ""
    
    while True:
        try:
            # Monitora a tecla especial (F9)
            if keyboard.is_pressed(TECLA_ESPECIAL):
                log_sucesso(f"Tecla F9 pressionada!")
                processar_backups()
                time.sleep(1)  # Evita múltiplas ativações
                entrada = ""
            
            # Monitora ESC para sair
            if keyboard.is_pressed("esc"):
                log_aviso("Saindo do programa...")
                sys.exit(0)
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            log_aviso("Programa interrompido pelo usuário!")
            sys.exit(0)

if __name__ == "__main__":
    print(f"\n{Cores.VERDE}╔════════════════════════════════════════════╗{Cores.RESET}")
    print(f"{Cores.VERDE}║     FERRAMENTA DE BACKUP PARA PDFs         ║{Cores.RESET}")
    print(f"{Cores.VERDE}║  Converte imagens de Backups em PDFs       ║{Cores.RESET}")
    print(f"{Cores.VERDE}╚════════════════════════════════════════════╝{Cores.RESET}\n")
    
    aguardar_entrada()

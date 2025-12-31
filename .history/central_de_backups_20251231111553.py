import os
import shutil
import time
import re
import sys
from datetime import datetime
from pathlib import Path

# --- IMPORTAÇÕES DO ROBÔ (Necessário instalar: pip install pyautogui keyboard img2pdf pygetwindow) ---
try:
    import pyautogui
    import keyboard
    import img2pdf
    import pygetwindow as gw
except ImportError:
    print("ERRO: Faltam bibliotecas. Instale: pip install pyautogui keyboard img2pdf pygetwindow")
    sys.exit()

# ===== CONFIGURAÇÕES DO USUÁRIO (BACKUP) =====
DIR_PRINCIPAL = r"C:\Users\gabri\OneDrive\Desktop\Projetos\Material Escola da Nuvem_Teste"
DIR_BACKUP = r"C:\Users\gabri\OneDrive\Desktop\Backups_Blindados"

# ===== CONFIGURAÇÕES DO ROBÔ (CAPTURE) =====
CORTE_TOPO = 160
CORTE_BAIXO = 20
CORTE_LADOS = 10

# ===== CORES E VISUAL =====
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'

def log(msg, tipo="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    cor = Cores.AZUL
    if tipo == "SUCESSO": cor = Cores.VERDE
    elif tipo == "AVISO": cor = Cores.AMARELO
    elif tipo == "ERRO": cor = Cores.VERMELHO
    elif tipo == "PERIGO": cor = Cores.VERMELHO + Cores.NEGRITO
    print(f"{Cores.RESET}[{timestamp}] {cor}{msg}{Cores.RESET}")

# ===== UTILITÁRIOS GERAIS =====
def forcar_caminho_longo(caminho):
    try:
        caminho_abs = os.path.abspath(caminho)
        if os.name == 'nt':
            if not caminho_abs.startswith('\\\\?\\'):
                return f"\\\\?\\{caminho_abs}"
        return caminho_abs
    except Exception:
        return caminho

def limpar_visual(caminho):
    return caminho.replace("\\\\?\\", "")

# ==============================================================================
# MÓDULO 1: SISTEMA DE BACKUP E RESTAURAÇÃO
# ==============================================================================

def backup_blindado():
    print(f"\n{Cores.NEGRITO}=== MODO 1: BACKUP BLINDADO ==={Cores.RESET}")
    raiz_origem = forcar_caminho_longo(DIR_PRINCIPAL)
    raiz_backup = forcar_caminho_longo(DIR_BACKUP)

    if not os.path.exists(raiz_origem):
        log(f"Origem não encontrada: {DIR_PRINCIPAL}", "ERRO")
        return

    novos, atualizados, erros = 0, 0, 0

    for root, dirs, files in os.walk(raiz_origem):
        root_limpo = limpar_visual(root)
        origem_limpa = limpar_visual(raiz_origem)
        try: relativo = os.path.relpath(root_limpo, origem_limpa)
        except: continue

        pasta_dest = os.path.join(raiz_backup, relativo)
        pasta_dest_longa = forcar_caminho_longo(pasta_dest)

        if not os.path.exists(pasta_dest_longa):
            try: os.makedirs(pasta_dest_longa)
            except: pass

        for file in files:
            origem_file = forcar_caminho_longo(os.path.join(root, file))
            dest_file = forcar_caminho_longo(os.path.join(pasta_dest_longa, file))
            copiar = False
            try:
                if not os.path.exists(dest_file):
                    copiar = True; motivo = "Novo"; novos += 1
                elif os.path.getmtime(origem_file) > os.path.getmtime(dest_file) + 2:
                    copiar = True; motivo = "Atualizado"; atualizados += 1
                
                if copiar:
                    shutil.copy2(origem_file, dest_file)
                    log(f"[{motivo}] {file[:50]}...", "SUCESSO")
            except Exception as e: erros += 1

    print(f"\n{Cores.VERDE}Concluído. Novos: {novos} | Atualizados: {atualizados} | Erros: {erros}{Cores.RESET}")

def backup_espelho_sincronizado():
    print(f"\n{Cores.VERMELHO}=== MODO 2: BACKUP ESPELHO (LIMPEZA) ==={Cores.RESET}")
    print(f"{Cores.AMARELO}AVISO: Apagará do Backup o que não existe na Origem.{Cores.RESET}")
    if input("Digite 'LIMPAR' para confirmar: ") != "LIMPAR": return

    backup_blindado()
    print(f"\n{Cores.AMARELO}>>> Verificando itens excluídos...{Cores.RESET}")
    
    raiz_origem = forcar_caminho_longo(DIR_PRINCIPAL)
    raiz_backup = forcar_caminho_longo(DIR_BACKUP)
    deletados_arq, deletados_pastas = 0, 0

    for root, dirs, files in os.walk(raiz_backup, topdown=False):
        root_limpo = limpar_visual(root)
        backup_limpo = limpar_visual(raiz_backup)
        try: relativo = os.path.relpath(root_limpo, backup_limpo)
        except: continue
            
        pasta_origem_corresp = forcar_caminho_longo(os.path.join(raiz_origem, relativo))
        
        for file in files:
            arquivo_backup = os.path.join(root, file)
            arquivo_origem = os.path.join(pasta_origem_corresp, file)
            if not os.path.exists(arquivo_origem):
                try:
                    os.remove(arquivo_backup)
                    log(f"[ARQUIVO EXCLUÍDO] {file}", "PERIGO")
                    deletados_arq += 1
                except: pass

        if not os.path.exists(pasta_origem_corresp):
            try:
                shutil.rmtree(root)
                log(f"[PASTA EXCLUÍDA] {relativo}", "PERIGO")
                deletados_pastas += 1
            except: pass

    print(f"\n{Cores.VERDE}Limpeza Finalizada. Removidos: {deletados_arq} arq / {deletados_pastas} pastas.{Cores.RESET}")

def restaurar_disastre():
    print(f"\n{Cores.CIANO}=== MODO 3: RESTAURAÇÃO ==={Cores.RESET}")
    raiz_backup = forcar_caminho_longo(DIR_BACKUP)
    if not os.path.exists(raiz_backup):
        log("Backup não encontrado.", "ERRO"); return

    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
    nome_recup = f"{os.path.basename(DIR_PRINCIPAL)}_RECUPERADO_{timestamp}"
    caminho_final = forcar_caminho_longo(os.path.join(os.path.dirname(DIR_PRINCIPAL), nome_recup))

    print(f"Restaurando em: {caminho_final}")
    if input("Confirmar (S/N)? ").upper() == "S":
        try:
            log("Clonando... Aguarde...", "AVISO")
            shutil.copytree(raiz_backup, caminho_final)
            print("\n" + "="*50); log("SUCESSO TOTAL!", "SUCESSO"); print("="*50)
        except Exception as e: log(f"Erro na restauração: {e}", "ERRO")

# ==============================================================================
# MÓDULO 2: ROBÔ DE CAPTURA (EXTRAÇÃO)
# ==============================================================================

def detectar_janela_ativa():
    print(f"\n{Cores.AMARELO}--- DETECÇÃO AUTOMÁTICA ---{Cores.RESET}")
    print("1. Vou capturar a janela ATIVA.")
    print("2. Clique no navegador AGORA.")
    for i in range(3, 0, -1):
        print(f"Calibrando em {i}...")
        time.sleep(1)
    
    try:
        janela = gw.getActiveWindow()
        if janela is None: return None
        print(f"Alvo: '{janela.title}'")
        return (janela.left + CORTE_LADOS, janela.top + CORTE_TOPO, 
                janela.width - (CORTE_LADOS * 2), janela.height - CORTE_TOPO - CORTE_BAIXO)
    except Exception as e:
        print(f"Erro ao detectar: {e}")
        return None

def limpar_nome_arquivo(nome):
    return re.sub(r'[<>:"/\\|?*]', '_', nome)

def loop_robo_captura():
    """Função que gerencia o loop do robô dentro do menu principal"""
    while True:
        print("\n" + "-"*40)
        print(f"{Cores.CIANO}   ROBÔ DE CAPTURA DE PDF{Cores.RESET}")
        print("-"*40)
        
        # 1. Solicita Nome
        nome_input = input(">> Digite o NOME do arquivo: ").strip()
        if not nome_input:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            nome_final = f"slide_padrao_{timestamp}.pdf"
        else:
            nome_limpo = limpar_nome_arquivo(nome_input)
            nome_final = nome_limpo + ".pdf" if not nome_limpo.lower().endswith(".pdf") else nome_limpo

        # 2. Solicita Pasta Destino
        print(">> Onde salvar? (Enter para pasta atual)")
        caminho_input = input(">> Caminho: ").strip().replace('"', '').replace("'", "")
        if not caminho_input: pasta_destino_pdf = os.getcwd()
        elif os.path.isdir(caminho_input): pasta_destino_pdf = caminho_input
        else:
            print("❌ Caminho inválido. Usando pasta atual.")
            pasta_destino_pdf = os.getcwd()

        caminho_completo_pdf = os.path.join(pasta_destino_pdf, nome_final)
        
        # 3. Prepara Temp
        nome_base = os.path.splitext(nome_final)[0]
        pasta_temp_dinamica = f"temp_{nome_base}"
        if not os.path.exists(pasta_temp_dinamica): os.makedirs(pasta_temp_dinamica)

        # 4. Calibragem
        region_capture = detectar_janela_ativa()
        if not region_capture:
            print("Falha na calibração.")
            continue

        print(f"\n{Cores.VERDE}✅ PRONTO!{Cores.RESET}")
        print(f"[ENTER] -> Capturar | [ESC] -> Gerar PDF")
        
        capturas = []
        contador = 1
        
        # Loop de captura
        try:
            while True:
                if keyboard.is_pressed('enter'):
                    ts = datetime.now().strftime("%H%M%S")
                    nome_img = os.path.join(pasta_temp_dinamica, f"slide_{contador:03d}_{ts}.png")
                    pyautogui.screenshot(nome_img, region=region_capture)
                    capturas.append(nome_img)
                    print(f"{Cores.VERDE}[+] Slide {contador} capturado{Cores.RESET}")
                    contador += 1
                    time.sleep(0.5)
                elif keyboard.is_pressed('esc'):
                    print("\nGerando PDF...")
                    break
                time.sleep(0.05)
        except KeyboardInterrupt: pass

        # Gera PDF
        if capturas:
            try:
                with open(caminho_completo_pdf, "wb") as f:
                    f.write(img2pdf.convert(capturas))
                print(f"\n{Cores.VERDE}[SUCESSO] Arquivo criado:{Cores.RESET}\n{caminho_completo_pdf}")
                
                # Move imagens para pasta 'Backups' local para organização
                try:
                    pasta_backups_local = os.path.join(os.getcwd(), "Backups")
                    if not os.path.exists(pasta_backups_local): os.makedirs(pasta_backups_local)
                    
                    destino_imgs = os.path.join(pasta_backups_local, pasta_temp_dinamica)
                    if os.path.exists(destino_imgs): shutil.rmtree(destino_imgs)
                    shutil.move(pasta_temp_dinamica, destino_imgs)
                    print(f"Imagens movidas para: {destino_imgs}")
                except Exception as e: print(f"Erro ao mover imagens raw: {e}")
                
            except Exception as e:
                print(f"❌ Erro ao salvar PDF: {e}")
                # Backup de emergência
                try:
                    with open(f"backup_{nome_final}", "wb") as f: f.write(img2pdf.convert(capturas))
                except: pass
        else:
            print("Nenhuma imagem capturada.")
            try: os.rmdir(pasta_temp_dinamica)
            except: pass

        print("\n" + "="*40)
        decisao = input("Pressione [ENTER] para Novo PDF ou digite [S] para voltar ao Menu Principal: ").upper()
        if decisao == "S": break

# ==============================================================================
# MENU PRINCIPAL (CENTRAL)
# ==============================================================================
def menu():
    while True:
        print("\n" + "="*60)
        print(f"{Cores.NEGRITO}   CENTRAL DE COMANDO V5.0 (GERENCIADOR + ROBÔ){Cores.RESET}")
        print("="*60)
        print(f"{Cores.VERDE}1. Backup Blindado{Cores.RESET} (Segurança Incremental)")
        print(f"{Cores.VERMELHO}2. Backup Espelho{Cores.RESET} (Sincronizar e Limpar)")
        print(f"{Cores.CIANO}3. Restaurar/Clonar{Cores.RESET} (Recuperação de Desastre)")
        print("-" * 60)
        print(f"{Cores.AMARELO}4. 📸 ROBÔ DE CAPTURA (Extrair PDF){Cores.RESET}")
        print("-" * 60)
        print("5. Sair")
        
        op = input("\nEscolha uma opção: ")
        
        if op == "1": backup_blindado(); input("\n[Enter] voltar...")
        elif op == "2": backup_espelho_sincronizado(); input("\n[Enter] voltar...")
        elif op == "3": restaurar_disastre(); input("\n[Enter] voltar...")
        elif op == "4": loop_robo_captura() # O robô tem seu próprio loop, não precisa de input aqui
        elif op == "5": break

if __name__ == "__main__":
    if not os.path.exists(forcar_caminho_longo(DIR_BACKUP)):
        try: os.makedirs(forcar_caminho_longo(DIR_BACKUP))
        except: pass
    menu()
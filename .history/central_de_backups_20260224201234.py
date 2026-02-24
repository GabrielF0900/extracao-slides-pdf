import os
import shutil
import time
import re
import sys
import random
import ctypes
from datetime import datetime

# --- IMPORTAÇÕES DO ROBÔ ---
# Tentativa de importar; se faltar, tenta instalar automaticamente
try:
    import pyautogui
    import keyboard
    import img2pdf
    import pygetwindow as gw
    import mss
    import mss.tools
except Exception:
    required = ["mss", "pyautogui", "keyboard", "img2pdf", "pygetwindow", "Pillow"]
    missing = []
    for pkg in required:
        try:
            if pkg == "Pillow":
                import PIL  # type: ignore
            else:
                __import__(pkg)
        except Exception:
            missing.append(pkg)

    if missing:
        print(f"ERRO: Faltam bibliotecas: {' '.join(missing)}")
        print("Tentando instalar automaticamente (pode pedir permissão)...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("Instalação concluída. Reinicie o script.")
        except Exception as e:
            print(f"Falha na instalação automática: {e}")
            print("Instale manualmente com: python -m pip install " + ' '.join(missing))
    else:
        # Se não identificou pacotes faltantes, ainda assim informa erro genérico
        print("Erro ao importar módulos necessários. Verifique suas instalações.")
    sys.exit()

# ===== CAMUFLAGEM DE PROCESSO =====
# Muda o título da janela do console para parecer algo do sistema
try:
    ctypes.windll.kernel32.SetConsoleTitleW("Service Host Monitor - Runtime Broker")
except:
    pass

# ===== CONFIGURAÇÕES DO USUÁRIO =====
DIR_PRINCIPAL = r"C:\Users\gabri\OneDrive\Desktop\Projetos\Material Escola da Nuvem_Teste"
DIR_BACKUP = r"C:\Users\gabri\OneDrive\Desktop\Backups_Blindados"

# Configurações de Corte (Ajuste fino)
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
# MÓDULO 1: GESTÃO DE ARQUIVOS (MANTIDO IGUAL)
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
# MÓDULO 2: ROBÔ DE CAPTURA (VERSÃO FURTIVA - MSS)
# ==============================================================================

def detectar_janela_ativa():
    print(f"\n{Cores.AMARELO}--- DETECÇÃO AUTOMÁTICA ---{Cores.RESET}")
    print("1. Clique no navegador AGORA.")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        janela = gw.getActiveWindow()
        if janela is None: return None
        print(f"Alvo detectado: '{janela.title}'")
        
        # Conversão para formato MSS (top, left, width, height)
        monitor = {
            "top": int(janela.top + CORTE_TOPO),
            "left": int(janela.left + CORTE_LADOS),
            "width": int(janela.width - (CORTE_LADOS * 2)),
            "height": int(janela.height - CORTE_TOPO - CORTE_BAIXO)
        }
        return monitor
    except Exception as e:
        print(f"Erro ao detectar: {e}")
        return None

def limpar_nome_arquivo(nome):
    return re.sub(r'[<>:"/\\|?*]', '_', nome)

def loop_robo_captura():
    # Inicializa o MSS uma única vez para performance
    with mss.mss() as sct:
        while True:
            print("\n" + "-"*40)
            print(f"{Cores.CIANO}   ROBÔ FURTIVO DE CAPTURA (MSS ENGINE){Cores.RESET}")
            print("-"*40)
            
            nome_input = input(">> Digite o NOME do arquivo: ").strip()
            if not nome_input:
                ts = datetime.now().strftime("%Y%m%d_%H%M")
                nome_final = f"slide_{ts}.pdf"
            else:
                n = limpar_nome_arquivo(nome_input)
                nome_final = n + ".pdf" if not n.lower().endswith(".pdf") else n

            print(">> Onde salvar? (Enter para pasta atual)")
            caminho_input = input(">> Caminho: ").strip().replace('"', '').replace("'", "")
            pasta_destino_pdf = caminho_input if caminho_input and os.path.isdir(caminho_input) else os.getcwd()

            caminho_completo_pdf = os.path.join(pasta_destino_pdf, nome_final)
            
            nome_base = os.path.splitext(nome_final)[0]
            pasta_temp_dinamica = f"temp_{nome_base}"
            if not os.path.exists(pasta_temp_dinamica): os.makedirs(pasta_temp_dinamica)

            monitor_region = detectar_janela_ativa()
            if not monitor_region: continue

            print(f"\n{Cores.VERDE}✅ MODO SILENCIOSO ATIVO!{Cores.RESET}")
            # --- ATUALIZADO: NOVOS COMANDOS ---
            print(f"{Cores.NEGRITO}[1] Capturar (c/ delay variável){Cores.RESET}")
            print(f"{Cores.NEGRITO}[ESC] Finalizar e Gerar PDF{Cores.RESET}")
            
            capturas = []
            contador = 1
            
            try:
                while True:
                    # --- ATUALIZADO: Tecla de captura mudada para '1' ---
                    if keyboard.is_pressed('1'):
                        # --- FURTIVIDADE: DELAY ALEATÓRIO ---
                        # Evita padrões exatos de tempo que bots simples têm
                        tempo_sleep = random.uniform(0.15, 0.4) 
                        time.sleep(tempo_sleep) 
                        
                        ts = datetime.now().strftime("%H%M%S")
                        nome_img = os.path.join(pasta_temp_dinamica, f"slide_{contador:03d}_{ts}.png")
                        
                        # --- CAPTURA FURTIVA COM MSS ---
                        sct_img = sct.grab(monitor_region)
                        mss.tools.to_png(sct_img.rgb, sct_img.size, output=nome_img)
                        
                        capturas.append(nome_img)
                        print(f"{Cores.VERDE}[+] Slide {contador} (Delay: {tempo_sleep:.2f}s){Cores.RESET}")
                        contador += 1
                        
                        # Evita captura dupla se segurar a tecla
                        time.sleep(0.5)
                        
                    # --- ATUALIZADO: Tecla de sair mudada para 'ESC' ---
                    elif keyboard.is_pressed('esc'):
                        print("\nGerando PDF...")
                        break
                    time.sleep(0.01) # Reduz uso de CPU no loop
            except KeyboardInterrupt: pass

            if capturas:
                try:
                    # Ordenação segura
                    capturas.sort()
                    with open(caminho_completo_pdf, "wb") as f:
                        f.write(img2pdf.convert(capturas))
                    print(f"\n{Cores.VERDE}[SUCESSO] PDF criado em silêncio.{Cores.RESET}")
                    
                    print(f"{Cores.AMARELO}Movendo imagens brutas para Backups...{Cores.RESET}")
                    time.sleep(1)
                    try:
                        pasta_bkp_local = os.path.join(os.getcwd(), "Backups")
                        if not os.path.exists(pasta_bkp_local): os.makedirs(pasta_bkp_local)
                        destino_imgs = os.path.join(pasta_bkp_local, pasta_temp_dinamica)
                        if os.path.exists(destino_imgs): shutil.rmtree(destino_imgs)
                        shutil.move(pasta_temp_dinamica, destino_imgs)
                        print(f"Backup seguro das imagens: OK")
                    except Exception as e: print(f"Erro ao mover imgs: {e}")
                except Exception as e:
                    print(f"❌ Erro ao salvar PDF: {e}")
            else:
                try: os.rmdir(pasta_temp_dinamica)
                except: pass

            try:
                # Limpa buffer se o usuário apertou Enter antes (opcional, mas bom pra evitar bugs no menu)
                while keyboard.is_pressed('enter'): pass
            except: pass
            if input("\n[ENTER] Novo | [S] Sair: ").upper() == "S": break

# ==============================================================================
# MÓDULO 3: REGENERADOR DE PDF (MANTIDO IGUAL)
# ==============================================================================

def regenerar_pdfs_do_backup():
    print(f"\n{Cores.CIANO}=== MODO 5: REGENERADOR DE PDFS (DO BACKUP) ==={Cores.RESET}")
    print("Este modo pega pastas de imagens em 'Backups' e cria PDFs novos.")
    
    pasta_origem = os.path.join(os.getcwd(), "Backups")
    if not os.path.exists(pasta_origem):
        log("Pasta 'Backups' não encontrada na raiz do script.", "ERRO")
        return

    pasta_destino = os.path.join(os.getcwd(), "Pdfs_Recuperados")
    if not os.path.exists(pasta_destino): os.makedirs(pasta_destino)

    itens = [d for d in os.listdir(pasta_origem) if os.path.isdir(os.path.join(pasta_origem, d))]
    
    if not itens:
        log("Nenhuma pasta de imagens encontrada em Backups.", "AVISO")
        return

    print(f"Encontrados {len(itens)} projetos para converter.")
    
    for i, pasta in enumerate(itens, 1):
        caminho_pasta = os.path.join(pasta_origem, pasta)
        imagens = []
        for f in os.listdir(caminho_pasta):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                imagens.append(os.path.join(caminho_pasta, f))
        
        if not imagens: continue
        imagens.sort()
        nome_pdf = pasta.replace("temp_", "") + ".pdf"
        caminho_pdf = os.path.join(pasta_destino, nome_pdf)
        
        print(f"[{i}/{len(itens)}] Gerando: {nome_pdf} ({len(imagens)} slides)...")
        try:
            with open(caminho_pdf, "wb") as f:
                f.write(img2pdf.convert(imagens))
            log(f"Criado em: Pdfs_Recuperados/{nome_pdf}", "SUCESSO")
        except Exception as e:
            log(f"Erro em {pasta}: {e}", "ERRO")

# ==============================================================================
# MENU PRINCIPAL
# ==============================================================================
def menu():
    while True:
        print("\n" + "="*60)
        print(f"{Cores.NEGRITO}   CENTRAL V6.0 - STEALTH EDITION{Cores.RESET}")
        print("="*60)
        print(f"{Cores.VERDE}1. Backup Blindado{Cores.RESET}")
        print(f"{Cores.VERMELHO}2. Backup Espelho{Cores.RESET}")
        print(f"{Cores.CIANO}3. Restaurar Pastas{Cores.RESET}")
        print("-" * 60)
        print(f"{Cores.AMARELO}4. 📸 ROBÔ FURTIVO (MSS + Delay Random){Cores.RESET}")
        print(f"{Cores.AZUL}5. ♻️   REGENERAR PDFs{Cores.RESET}")
        print("-" * 60)
        print("6. Sair")
        
        op = input("\nEscolha uma opção: ")
        
        if op == "1": backup_blindado(); input("\n[Enter]...")
        elif op == "2": backup_espelho_sincronizado(); input("\n[Enter]...")
        elif op == "3": restaurar_disastre(); input("\n[Enter]...")
        elif op == "4": loop_robo_captura()
        elif op == "5": regenerar_pdfs_do_backup(); input("\n[Enter]...")
        elif op == "6": break

if __name__ == "__main__":
    if not os.path.exists(forcar_caminho_longo(DIR_BACKUP)):
        try: os.makedirs(forcar_caminho_longo(DIR_BACKUP))
        except: pass
    menu()
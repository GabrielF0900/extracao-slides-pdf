import os
import shutil
import time
from datetime import datetime
from pathlib import Path

# ===== CONFIGURAÇÕES DO USUÁRIO =====
DIR_PRINCIPAL = r"C:\Users\gabri\OneDrive\Desktop\Projetos\Material Escola da Nuvem_Teste"
DIR_BACKUP = r"C:\Users\gabri\OneDrive\Desktop\Backups_Blindados"

# ===== CORES E VISUAL =====
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'  # <--- ADICIONADO (Estava faltando e causava o erro na Opção 3)
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

# ===== SUPORTE A NOMES LONGOS =====
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
    """Remove o prefixo \\?\ apenas para mostrar no terminal"""
    return caminho.replace("\\\\?\\", "")

# ==============================================================================
# 1. BACKUP BLINDADO
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
        # Cálculos de caminho
        root_limpo = limpar_visual(root)
        origem_limpa = limpar_visual(raiz_origem)
        try:
            relativo = os.path.relpath(root_limpo, origem_limpa)
        except: continue

        # Cria pasta no backup
        pasta_dest = os.path.join(raiz_backup, relativo)
        pasta_dest_longa = forcar_caminho_longo(pasta_dest)

        if not os.path.exists(pasta_dest_longa):
            try:
                os.makedirs(pasta_dest_longa)
            except: pass

        # Copia arquivos
        for file in files:
            origem_file = forcar_caminho_longo(os.path.join(root, file))
            dest_file = forcar_caminho_longo(os.path.join(pasta_dest_longa, file))

            copiar = False
            try:
                if not os.path.exists(dest_file):
                    copiar = True
                    motivo = "Novo"
                    novos += 1
                elif os.path.getmtime(origem_file) > os.path.getmtime(dest_file) + 2:
                    copiar = True
                    motivo = "Atualizado"
                    atualizados += 1
                
                if copiar:
                    shutil.copy2(origem_file, dest_file)
                    log(f"[{motivo}] {file[:50]}...", "SUCESSO")
            except Exception as e:
                # log(f"Erro ao copiar {file}: {e}", "ERRO") # Silenciado para não poluir
                erros += 1

    print(f"\n{Cores.VERDE}Concluído. Novos: {novos} | Atualizados: {atualizados} | Erros: {erros}{Cores.RESET}")

# ==============================================================================
# 2. BACKUP ESPELHO (Correção do Log de Exclusão)
# ==============================================================================
def backup_espelho_sincronizado():
    print(f"\n{Cores.VERMELHO}=== MODO 2: BACKUP ESPELHO (LIMPEZA) ==={Cores.RESET}")
    print(f"{Cores.AMARELO}AVISO: Isso apagará do Backup o que não existe na Origem.{Cores.RESET}")
    
    if input("Digite 'LIMPAR' para confirmar: ") != "LIMPAR":
        return

    # 1. Garante cópia dos novos
    backup_blindado()
    
    print(f"\n{Cores.AMARELO}>>> Verificando itens excluídos...{Cores.RESET}")
    
    raiz_origem = forcar_caminho_longo(DIR_PRINCIPAL)
    raiz_backup = forcar_caminho_longo(DIR_BACKUP)
    
    deletados_arq = 0
    deletados_pastas = 0

    # Varre de baixo para cima (arquivos primeiro, depois pastas)
    for root, dirs, files in os.walk(raiz_backup, topdown=False):
        root_limpo = limpar_visual(root)
        backup_limpo = limpar_visual(raiz_backup)
        
        try:
            relativo = os.path.relpath(root_limpo, backup_limpo)
        except: continue
            
        # Onde deveria estar na origem?
        pasta_origem_corresp = forcar_caminho_longo(os.path.join(raiz_origem, relativo))
        
        # A. Verifica Arquivos
        for file in files:
            arquivo_backup = os.path.join(root, file)
            arquivo_origem = os.path.join(pasta_origem_corresp, file)
            
            if not os.path.exists(arquivo_origem):
                try:
                    os.remove(arquivo_backup)
                    log(f"[ARQUIVO EXCLUÍDO] {file}", "PERIGO")
                    deletados_arq += 1
                except Exception as e:
                    log(f"Erro ao excluir arquivo {file}: {e}", "ERRO")

        # B. Verifica Pastas (Agora com log explícito)
        # Se a pasta correspondente não existe na origem, tenta apagar no backup
        if not os.path.exists(pasta_origem_corresp):
            try:
                # Tenta remover. Se tiver arquivos ocultos (Thumbs.db), vai dar erro
                os.rmdir(root) 
                log(f"[PASTA EXCLUÍDA] {relativo}", "PERIGO")
                deletados_pastas += 1
            except OSError as e:
                # Se a pasta não estiver vazia (lixo de sistema), forçamos com shutil
                try:
                    shutil.rmtree(root)
                    log(f"[PASTA FORÇADA] {relativo}", "PERIGO")
                    deletados_pastas += 1
                except Exception as e_force:
                    # Só mostra erro se não for a raiz
                    if relativo != ".":
                        log(f"Não foi possível excluir pasta {relativo}: {e_force}", "ERRO")

    print(f"\n{Cores.VERDE}Limpeza Finalizada.{Cores.RESET}")
    print(f"Arquivos removidos: {deletados_arq} | Pastas removidas: {deletados_pastas}")

# ==============================================================================
# 3. RESTAURAÇÃO (Correção do Erro CIANO)
# ==============================================================================
def restaurar_disastre():
    # Agora CIANO existe na classe, o erro vai sumir
    print(f"\n{Cores.CIANO}=== MODO 3: RESTAURAÇÃO ==={Cores.RESET}")
    
    raiz_backup = forcar_caminho_longo(DIR_BACKUP)
    
    if not os.path.exists(raiz_backup):
        log("Backup não encontrado.", "ERRO")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
    nome_recup = f"{os.path.basename(DIR_PRINCIPAL)}_RECUPERADO_{timestamp}"
    
    caminho_final = os.path.join(os.path.dirname(DIR_PRINCIPAL), nome_recup)
    caminho_final_longo = forcar_caminho_longo(caminho_final)

    print(f"Restaurando em: {caminho_final}")
    
    if input("Confirmar (S/N)? ").upper() == "S":
        try:
            log("Clonando... Aguarde...", "AVISO")
            shutil.copytree(raiz_backup, caminho_final_longo)
            print("\n" + "="*50)
            log("SUCESSO TOTAL!", "SUCESSO")
            print("="*50)
        except Exception as e:
            log(f"Erro na restauração: {e}", "ERRO")

def menu():
    while True:
        print("\n" + "="*50)
        print("   CENTRAL DE BACKUPS V4.1 (CORRIGIDO)")
        print("="*50)
        print("1. Backup Blindado (Incremental)")
        print("2. Backup Espelho (Sincronizar e Limpar)")
        print("3. Restaurar")
        print("4. Sair")
        
        op = input("\nOpção: ")
        if op == "1": backup_blindado()
        elif op == "2": backup_espelho_sincronizado()
        elif op == "3": restaurar_disastre()
        elif op == "4": break

if __name__ == "__main__":
    if not os.path.exists(forcar_caminho_longo(DIR_BACKUP)):
        try: os.makedirs(forcar_caminho_longo(DIR_BACKUP))
        except: pass
    menu()
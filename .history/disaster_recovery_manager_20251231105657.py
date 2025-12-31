import os
import shutil
import time
from datetime import datetime
from pathlib import Path

# ===== CONFIGURAÇÕES DO USUÁRIO =====
# Verifique se os caminhos estão corretos
DIR_PRINCIPAL = r"C:\Users\gabri\OneDrive\Desktop\Projetos\Material Escola da Nuvem_Teste"
DIR_BACKUP = r"C:\Users\gabri\OneDrive\Desktop\Backups_Blindados"

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

def tratar_caminho_longo(caminho):
    """Adiciona suporte a caminhos > 260 caracteres no Windows"""
    caminho_abs = os.path.abspath(caminho)
    if os.name == 'nt':
        if not caminho_abs.startswith('\\\\?\\'):
            return f"\\\\?\\{caminho_abs}"
    return caminho_abs

# ==============================================================================
# FUNÇÃO 1: BACKUP BLINDADO (Adiciona novos, mas NUNCA deleta nada do backup)
# ==============================================================================
def backup_blindado():
    print(f"\n{Cores.NEGRITO}=== MODO 1: BACKUP BLINDADO (INCREMENTAL) ==={Cores.RESET}")
    print("Neste modo, arquivos apagados na origem SERÃO MANTIDOS no backup.")
    
    if not os.path.exists(DIR_PRINCIPAL):
        log("Pasta principal não encontrada!", "ERRO")
        return

    novos = 0
    atualizados = 0

    for raiz, pastas, arquivos in os.walk(DIR_PRINCIPAL):
        caminho_relativo = os.path.relpath(raiz, DIR_PRINCIPAL)
        pasta_destino = os.path.join(DIR_BACKUP, caminho_relativo)
        
        # Cria pasta (com suporte a long path)
        pasta_dest_longa = tratar_caminho_longo(pasta_destino)
        if not os.path.exists(pasta_dest_longa):
            try:
                os.makedirs(pasta_dest_longa)
            except Exception as e:
                log(f"Erro ao criar pasta: {e}", "ERRO")

        for arquivo in arquivos:
            origem = tratar_caminho_longo(os.path.join(raiz, arquivo))
            destino = tratar_caminho_longo(os.path.join(pasta_destino, arquivo))
            
            copiar = False
            if not os.path.exists(destino):
                copiar = True
                motivo = "Novo"
                novos += 1
            else:
                if os.path.getmtime(origem) > os.path.getmtime(destino) + 2:
                    copiar = True
                    motivo = "Atualizado"
                    atualizados += 1
            
            if copiar:
                try:
                    shutil.copy2(origem, destino)
                    log(f"[{motivo}] {arquivo}", "SUCESSO")
                except Exception as e:
                    log(f"Erro ao copiar {arquivo}: {e}", "ERRO")

    print(f"\n{Cores.VERDE}Backup Blindado Concluído!{Cores.RESET}")
    print(f"Novos: {novos} | Atualizados: {atualizados}")

# ==============================================================================
# FUNÇÃO 2: BACKUP ESPELHO (Sincroniza EXATAMENTE igual, deletando excessos)
# ==============================================================================
def backup_espelho_sincronizado():
    print(f"\n{Cores.VERMELHO}=== MODO 2: BACKUP ESPELHO (SYNC TOTAL) ==={Cores.RESET}")
    print(f"{Cores.AMARELO}AVISO: Se você apagou um arquivo na pasta Principal,")
    print(f"ele será APAGADO PERMANENTEMENTE do Backup agora.{Cores.RESET}")
    
    confirmar = input("Tem certeza que deseja limpar o backup? (DIGITE 'LIMPAR'): ")
    if confirmar != "LIMPAR":
        log("Operação cancelada por segurança.", "AVISO")
        return

    # Passo 1: Faz o Backup Blindado primeiro (Garante que os novos estão lá)
    backup_blindado()
    
    print(f"\n{Cores.AMARELO}>>> Iniciando limpeza do Backup (Removendo excluídos)...{Cores.RESET}")
    
    deletados = 0
    
    # Passo 2: Varre o BACKUP procurando coisas que não existem mais na Principal
    # Usamos topdown=False para apagar arquivos antes de tentar apagar a pasta
    for raiz, pastas, arquivos in os.walk(DIR_BACKUP, topdown=False):
        caminho_relativo = os.path.relpath(raiz, DIR_BACKUP)
        
        # Onde essa pasta/arquivo deveria estar na Principal?
        correspondente_principal = os.path.join(DIR_PRINCIPAL, caminho_relativo)
        
        # 2.1 Verifica Arquivos
        for arquivo in arquivos:
            arquivo_backup_path = os.path.join(raiz, arquivo)
            arquivo_principal_path = os.path.join(correspondente_principal, arquivo)
            
            # Se não existe na principal, DELETA do backup
            if not os.path.exists(tratar_caminho_longo(arquivo_principal_path)):
                try:
                    os.remove(tratar_caminho_longo(arquivo_backup_path))
                    log(f"[REMOVIDO] {arquivo} (Não existe mais na origem)", "PERIGO")
                    deletados += 1
                except Exception as e:
                    log(f"Erro ao deletar {arquivo}: {e}", "ERRO")

        # 2.2 Verifica Pastas (Se estiver vazia e não existir na principal, apaga)
        if not os.path.exists(tratar_caminho_longo(correspondente_principal)):
            try:
                os.rmdir(tratar_caminho_longo(raiz)) # rmdir só apaga se estiver vazia
                log(f"[PASTA REMOVIDA] {caminho_relativo}", "PERIGO")
            except OSError:
                pass # Pasta não estava vazia ou erro de permissão

    print(f"\n{Cores.VERDE}Sincronização Espelho Concluída!{Cores.RESET}")
    print(f"Itens removidos do backup: {deletados}")

# ==============================================================================
# FUNÇÃO 3: RESTAURAÇÃO (Disaster Recovery)
# ==============================================================================
def restaurar_disastre():
    print(f"\n{Cores.CIANO}=== MODO 3: RESTAURAÇÃO (CLONAGEM) ==={Cores.RESET}")
    
    if not os.path.exists(DIR_BACKUP):
        log("Backup não encontrado.", "ERRO")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
    nome_recuperada = f"{os.path.basename(DIR_PRINCIPAL)}_RECUPERADO_{timestamp}"
    dir_pai = os.path.dirname(DIR_PRINCIPAL)
    caminho_final = os.path.join(dir_pai, nome_recuperada)
    
    origem_backup_longa = tratar_caminho_longo(DIR_BACKUP)
    destino_final_longo = tratar_caminho_longo(caminho_final)

    print(f"Clonando backup para:\n -> {Cores.AZUL}{caminho_final}{Cores.RESET}")
    
    if input("\nConfirmar Clonagem? (S/N): ").upper() == "S":
        try:
            log("Copiando arquivos... Isso pode demorar.", "AVISO")
            shutil.copytree(origem_backup_longa, destino_final_longo)
            print("\n" + "="*50)
            log("SUCESSO! PASTA RECUPERADA CRIADA.", "SUCESSO")
            print("="*50)
            print(f"Local: {caminho_final}")
        except Exception as e:
            log(f"Erro na restauração: {e}", "ERRO")
    else:
        log("Cancelado.", "AVISO")

# ==============================================================================
# MENU PRINCIPAL
# ==============================================================================
def menu():
    while True:
        print("\n" + "="*60)
        print(f"{Cores.NEGRITO}   MASTER SYNC MANAGER - GESTÃO DE ARQUIVOS{Cores.RESET}")
        print("="*60)
        print(f"{Cores.VERDE}1. BACKUP BLINDADO{Cores.RESET} (Copia novos, mantém excluídos)")
        print(f"   -> Use no dia-a-dia para segurança máxima.")
        print("-" * 60)
        print(f"{Cores.VERMELHO}2. BACKUP ESPELHO{Cores.RESET} (Sincroniza total, deleta excluídos)")
        print(f"   -> Use quando quiser limpar o backup para ficar igual à origem.")
        print("-" * 60)
        print(f"{Cores.CIANO}3. RESTAURAR/CLONAR{Cores.RESET} (Recria a pasta em outro lugar)")
        print(f"   -> Use se der tudo errado ou precisar de uma cópia.")
        print("-" * 60)
        print("4. Sair")
        
        op = input("\nEscolha uma opção: ")
        
        if op == "1":
            backup_blindado()
            input("\n[Enter] para voltar...")
        elif op == "2":
            backup_espelho_sincronizado()
            input("\n[Enter] para voltar...")
        elif op == "3":
            restaurar_disastre()
            input("\n[Enter] para voltar...")
        elif op == "4":
            break

if __name__ == "__main__":
    if not os.path.exists(DIR_BACKUP):
        try: os.makedirs(DIR_BACKUP)
        except: pass
    menu()
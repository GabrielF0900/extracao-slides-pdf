import os
import shutil
import time
from datetime import datetime
from pathlib import Path

# ===== CONFIGURAÇÕES DO USUÁRIO =====

# ATENÇÃO: Se sua pasta real tem ESPAÇOS em vez de UNDERLINE, mude abaixo:
# Ex: r"C:\Users\gabri\OneDrive\Desktop\Projetos\Material Escola da Nuvem Teste"
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
    """
    Adiciona o prefixo mágico \\?\ do Windows para permitir caminhos
    com mais de 260 caracteres (Long Paths).
    """
    try:
        caminho_abs = os.path.abspath(caminho)
        if os.name == 'nt':
            if not caminho_abs.startswith('\\\\?\\'):
                return f"\\\\?\\{caminho_abs}"
        return caminho_abs
    except Exception:
        return caminho

# ==============================================================================
# FUNÇÃO 1: BACKUP BLINDADO (Incremental)
# ==============================================================================
def backup_blindado():
    print(f"\n{Cores.NEGRITO}=== MODO 1: BACKUP BLINDADO (INCREMENTAL) ==={Cores.RESET}")
    
    # Prepara caminhos longos logo no início
    dir_principal_longo = tratar_caminho_longo(DIR_PRINCIPAL)
    dir_backup_longo = tratar_caminho_longo(DIR_BACKUP)

    if not os.path.exists(dir_principal_longo):
        log(f"ERRO: Pasta principal não encontrada!", "ERRO")
        log(f"O script tentou ler: {DIR_PRINCIPAL}", "AVISO")
        log("Verifique se o nome da pasta tem '_' (underline) ou espaço.", "AVISO")
        return

    novos = 0
    atualizados = 0
    pastas_verificadas = 0

    print("Mapeando arquivos... aguarde.")

    # Usa o caminho longo no os.walk para garantir que veja pastas profundas
    for raiz, pastas, arquivos in os.walk(dir_principal_longo):
        pastas_verificadas += 1
        
        # Remove o prefixo \\?\ para cálculos relativos
        raiz_limpa = raiz.replace("\\\\?\\", "")
        dir_princ_limpo = dir_principal_longo.replace("\\\\?\\", "")
        
        try:
            caminho_relativo = os.path.relpath(raiz_limpa, dir_princ_limpo)
        except ValueError:
            continue # Ignora erros de caminho relativo
            
        pasta_destino = os.path.join(dir_backup_longo, caminho_relativo)
        
        # Cria a pasta no backup se não existir
        if not os.path.exists(pasta_destino):
            try:
                os.makedirs(pasta_destino)
                # Só loga se for uma pasta realmente nova (não a raiz)
                if caminho_relativo != ".":
                    log(f"[NOVA PASTA] {caminho_relativo}", "SUCESSO")
            except Exception as e:
                log(f"Erro ao criar pasta {caminho_relativo}: {e}", "ERRO")

        for arquivo in arquivos:
            origem = os.path.join(raiz, arquivo)
            destino = os.path.join(pasta_destino, arquivo)
            
            copiar = False
            try:
                if not os.path.exists(destino):
                    copiar = True
                    motivo = "Novo"
                    novos += 1
                else:
                    # Compara data de modificação
                    if os.path.getmtime(origem) > os.path.getmtime(destino) + 2:
                        copiar = True
                        motivo = "Atualizado"
                        atualizados += 1
                
                if copiar:
                    shutil.copy2(origem, destino)
                    log(f"[{motivo}] {arquivo}", "SUCESSO")
                    
            except PermissionError:
                log(f"Permissão negada (Arquivo aberto?): {arquivo}", "ERRO")
            except Exception as e:
                log(f"Erro ao copiar {arquivo}: {e}", "ERRO")

    if pastas_verificadas == 0:
        log("Nenhuma pasta foi lida. O caminho da pasta Principal está errado!", "ERRO")
    else:
        print(f"\n{Cores.VERDE}Backup Blindado Concluído!{Cores.RESET}")
        print(f"Pastas escaneadas: {pastas_verificadas}")
        print(f"Novos arquivos: {novos} | Atualizados: {atualizados}")

# ==============================================================================
# FUNÇÃO 2: BACKUP ESPELHO (Sincroniza total)
# ==============================================================================
def backup_espelho_sincronizado():
    print(f"\n{Cores.VERMELHO}=== MODO 2: BACKUP ESPELHO (SYNC TOTAL) ==={Cores.RESET}")
    print(f"{Cores.AMARELO}AVISO: Isso vai DELETAR arquivos do backup que não existem na origem.{Cores.RESET}")
    
    if input("Digite 'LIMPAR' para confirmar: ") != "LIMPAR":
        return

    # 1. Roda o blindado para garantir que tudo novo foi copiado
    backup_blindado()
    
    print(f"\n{Cores.AMARELO}>>> Removendo itens obsoletos do Backup...{Cores.RESET}")
    
    dir_principal_longo = tratar_caminho_longo(DIR_PRINCIPAL)
    dir_backup_longo = tratar_caminho_longo(DIR_BACKUP)
    
    deletados = 0

    for raiz, pastas, arquivos in os.walk(dir_backup_longo, topdown=False):
        raiz_limpa = raiz.replace("\\\\?\\", "")
        dir_back_limpo = dir_backup_longo.replace("\\\\?\\", "")
        
        try:
            caminho_relativo = os.path.relpath(raiz_limpa, dir_back_limpo)
        except: continue
            
        correspondente_principal = os.path.join(dir_principal_longo, caminho_relativo)
        
        # Verifica arquivos para deletar
        for arquivo in arquivos:
            arq_backup = os.path.join(raiz, arquivo)
            arq_principal = os.path.join(correspondente_principal, arquivo)
            
            if not os.path.exists(arq_principal):
                try:
                    os.remove(arq_backup)
                    log(f"[DELETADO] {arquivo}", "PERIGO")
                    deletados += 1
                except Exception as e:
                    log(f"Erro ao deletar {arquivo}: {e}", "ERRO")

        # Verifica pastas vazias para deletar
        if not os.path.exists(correspondente_principal):
            try:
                os.rmdir(raiz)
                log(f"[PASTA DELETADA] {caminho_relativo}", "PERIGO")
            except: pass

    print(f"\n{Cores.VERDE}Espelhamento Concluído. {deletados} itens removidos.{Cores.RESET}")

# ==============================================================================
# FUNÇÃO 3: RESTAURAÇÃO
# ==============================================================================
def restaurar_disastre():
    print(f"\n{Cores.CIANO}=== MODO 3: RESTAURAÇÃO ==={Cores.RESET}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
    nome_recuperada = f"{os.path.basename(DIR_PRINCIPAL)}_RECUPERADO_{timestamp}"
    dir_pai = os.path.dirname(DIR_PRINCIPAL)
    caminho_final = os.path.join(dir_pai, nome_recuperada)
    
    origem = tratar_caminho_longo(DIR_BACKUP)
    destino = tratar_caminho_longo(caminho_final)

    print(f"Restaurando para: {caminho_final}")
    
    if input("Confirmar (S/N)? ").upper() == "S":
        try:
            shutil.copytree(origem, destino)
            log("SUCESSO NA RESTAURAÇÃO!", "SUCESSO")
        except Exception as e:
            log(f"Erro: {e}", "ERRO")

def menu():
    while True:
        print("\n" + "="*50)
        print("   MASTER SYNC MANAGER V3.1 (DIAGNOSTIC MODE)")
        print("="*50)
        print("1. Backup Blindado (Incremental)")
        print("2. Backup Espelho (Limpeza)")
        print("3. Restaurar")
        print("4. Sair")
        
        op = input("\nOpção: ")
        if op == "1": backup_blindado()
        elif op == "2": backup_espelho_sincronizado()
        elif op == "3": restaurar_disastre()
        elif op == "4": break

if __name__ == "__main__":
    if not os.path.exists(DIR_BACKUP):
        try: os.makedirs(DIR_BACKUP)
        except: pass
    menu()
import os
import shutil
import time
from datetime import datetime
from pathlib import Path

# ===== CONFIGURAÇÕES DO USUÁRIO =====
# Verifique se o nome da pasta está exato (Espaços ou Underline)
DIR_PRINCIPAL = r"C:\Users\gabri\OneDrive\Desktop\Projetos\Material Escola da Nuvem_Teste"
DIR_BACKUP = r"C:\Users\gabri\OneDrive\Desktop\Backups_Blindados"

# ===== CORES E VISUAL =====
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
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

# ===== NÚCLEO DO SUPORTE A NOMES LONGOS =====
def forcar_caminho_longo(caminho):
    """
    Transforma qualquer caminho em um caminho estendido do Windows.
    Permite nomes maiores que 260 caracteres.
    """
    try:
        # Obtém o caminho absoluto
        caminho_abs = os.path.abspath(caminho)
        
        # Se for Windows e não tiver o prefixo, adiciona
        if os.name == 'nt':
            if not caminho_abs.startswith('\\\\?\\'):
                return f"\\\\?\\{caminho_abs}"
        return caminho_abs
    except Exception:
        return caminho

def limpar_caminho_para_visualizacao(caminho):
    """Remove o prefixo feio \\?\ apenas para mostrar no log ou calcular caminhos relativos"""
    return caminho.replace("\\\\?\\", "")

# ==============================================================================
# FUNÇÃO 1: BACKUP BLINDADO (Incremental - Suporta Nomes Gigantes)
# ==============================================================================
def backup_blindado():
    print(f"\n{Cores.NEGRITO}=== MODO 1: BACKUP BLINDADO (NOMES LONGOS ATIVADO) ==={Cores.RESET}")
    
    # Prepara as raízes com o prefixo mágico
    raiz_origem_longa = forcar_caminho_longo(DIR_PRINCIPAL)
    raiz_backup_longa = forcar_caminho_longo(DIR_BACKUP)

    if not os.path.exists(raiz_origem_longa):
        log(f"Pasta Principal não encontrada: {DIR_PRINCIPAL}", "ERRO")
        return

    novos = 0
    atualizados = 0
    erros = 0

    # O os.walk agora percorre usando o caminho longo
    for root, dirs, files in os.walk(raiz_origem_longa):
        # Para calcular o caminho relativo, precisamos tirar o prefixo temporariamente
        root_limpo = limpar_caminho_para_visualizacao(root)
        origem_limpa = limpar_caminho_para_visualizacao(raiz_origem_longa)
        
        try:
            caminho_relativo = os.path.relpath(root_limpo, origem_limpa)
        except ValueError:
            continue

        # Monta a pasta de destino e força caminho longo nela
        pasta_destino_backup = os.path.join(raiz_backup_longa, caminho_relativo)
        pasta_destino_longa = forcar_caminho_longo(pasta_destino_backup)

        # Cria a pasta no backup
        if not os.path.exists(pasta_destino_longa):
            try:
                os.makedirs(pasta_destino_longa)
                # log(f"Pasta criada: {caminho_relativo}", "SUCESSO") # Comentei para poluir menos
            except Exception as e:
                log(f"Erro ao criar pasta: {e}", "ERRO")

        # Processa arquivos
        for file in files:
            origem_arquivo = os.path.join(root, file) # Já está em long path pois root é long
            destino_arquivo = os.path.join(pasta_destino_longa, file)
            
            # Garante long path no destino final
            destino_arquivo = forcar_caminho_longo(destino_arquivo)

            copiar = False
            try:
                if not os.path.exists(destino_arquivo):
                    copiar = True
                    motivo = "Novo"
                    novos += 1
                else:
                    # Compara datas
                    if os.path.getmtime(origem_arquivo) > os.path.getmtime(destino_arquivo) + 2:
                        copiar = True
                        motivo = "Atualizado"
                        atualizados += 1
                
                if copiar:
                    shutil.copy2(origem_arquivo, destino_arquivo)
                    # Mostra só o nome do arquivo para não poluir
                    log(f"[{motivo}] {file[:50]}...", "SUCESSO")

            except PermissionError:
                log(f"Arquivo em uso (feche o Word/PDF): {file}", "ERRO")
                erros += 1
            except Exception as e:
                log(f"Erro ao copiar {file}: {e}", "ERRO")
                erros += 1

    print(f"\n{Cores.VERDE}Backup Blindado Concluído!{Cores.RESET}")
    print(f"Novos: {novos} | Atualizados: {atualizados} | Erros: {erros}")

# ==============================================================================
# FUNÇÃO 2: BACKUP ESPELHO (Remove o que foi excluído)
# ==============================================================================
def backup_espelho_sincronizado():
    print(f"\n{Cores.VERMELHO}=== MODO 2: BACKUP ESPELHO (LIMPEZA) ==={Cores.RESET}")
    print(f"{Cores.AMARELO}AVISO: Arquivos que não existem mais na origem serão apagados do backup.{Cores.RESET}")
    
    if input("Digite 'LIMPAR' para confirmar: ") != "LIMPAR":
        return

    # 1. Roda o blindado para garantir que tudo novo foi copiado
    backup_blindado()
    
    print(f"\n{Cores.AMARELO}>>> Removendo itens antigos do Backup...{Cores.RESET}")
    
    raiz_origem_longa = forcar_caminho_longo(DIR_PRINCIPAL)
    raiz_backup_longa = forcar_caminho_longo(DIR_BACKUP)
    
    deletados = 0

    for root, dirs, files in os.walk(raiz_backup_longa, topdown=False):
        root_limpo = limpar_caminho_para_visualizacao(root)
        backup_limpo = limpar_caminho_para_visualizacao(raiz_backup_longa)
        
        try:
            caminho_relativo = os.path.relpath(root_limpo, backup_limpo)
        except: continue
            
        # Onde deveria estar na origem?
        pasta_origem_correspondente = os.path.join(raiz_origem_longa, caminho_relativo)
        pasta_origem_correspondente = forcar_caminho_longo(pasta_origem_correspondente)
        
        # Verifica Arquivos
        for file in files:
            arquivo_backup = os.path.join(root, file)
            arquivo_origem = os.path.join(pasta_origem_correspondente, file)
            
            if not os.path.exists(arquivo_origem):
                try:
                    os.remove(arquivo_backup)
                    log(f"[DELETADO] {file}", "PERIGO")
                    deletados += 1
                except Exception as e:
                    log(f"Erro ao deletar: {e}", "ERRO")

        # Verifica Pastas Vazias
        if not os.path.exists(pasta_origem_correspondente):
            try:
                os.rmdir(root)
                log(f"[PASTA REMOVIDA] {caminho_relativo}", "PERIGO")
            except: pass

    print(f"\n{Cores.VERDE}Limpeza Concluída. {deletados} itens removidos.{Cores.RESET}")

# ==============================================================================
# FUNÇÃO 3: RESTAURAÇÃO
# ==============================================================================
def restaurar_disastre():
    print(f"\n{Cores.CIANO}=== MODO 3: RESTAURAÇÃO ==={Cores.RESET}")
    
    raiz_backup_longa = forcar_caminho_longo(DIR_BACKUP)
    
    if not os.path.exists(raiz_backup_longa):
        log("Backup não encontrado.", "ERRO")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
    nome_recuperada = f"{os.path.basename(DIR_PRINCIPAL)}_RECUPERADO_{timestamp}"
    
    # Define destino
    dir_pai = os.path.dirname(DIR_PRINCIPAL)
    caminho_final = os.path.join(dir_pai, nome_recuperada)
    caminho_final_longo = forcar_caminho_longo(caminho_final)

    print(f"Restaurando para: {caminho_final}")
    
    if input("Confirmar (S/N)? ").upper() == "S":
        try:
            log("Copiando... (Isso suporta nomes gigantes)", "AVISO")
            shutil.copytree(raiz_backup_longa, caminho_final_longo)
            log("SUCESSO NA RESTAURAÇÃO!", "SUCESSO")
        except Exception as e:
            log(f"Erro: {e}", "ERRO")

def menu():
    while True:
        print("\n" + "="*50)
        print("   MASTER SYNC V4.0 (SUPORTE A NOMES GIGANTES)")
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
    # Garante criação da pasta de backup com suporte a long path
    backup_path = forcar_caminho_longo(DIR_BACKUP)
    if not os.path.exists(backup_path):
        try: os.makedirs(backup_path)
        except: pass
    menu()
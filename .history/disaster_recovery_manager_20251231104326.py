import os
import shutil
import time
from datetime import datetime
from pathlib import Path

# ===== CONFIGURAÇÕES DO USUÁRIO =====

# ATENÇÃO AQUI: Verifique se o nome da pasta tem "_" ou espaço. 
# Ajustei para o que parece ser o correto no seu Windows:
DIR_PRINCIPAL = r"C:\Users\gabri\OneDrive\Desktop\Projetos\Material Escola da Nuvem_Teste"

# Pasta de destino
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
    
    print(f"{Cores.RESET}[{timestamp}] {cor}{msg}{Cores.RESET}")

def sincronizar_principais_para_backup():
    """
    Copia arquivos novos ou modificados da Principal para o Backup.
    Detecta automaticamente novas pastas criadas.
    """
    print(f"\n{Cores.NEGRITO}=== INICIANDO SINCRONIZAÇÃO BLINDADA ==={Cores.RESET}")
    print(f"Origem: {DIR_PRINCIPAL}")
    print(f"Backup: {DIR_BACKUP}\n")

    if not os.path.exists(DIR_PRINCIPAL):
        log(f"ERRO CRÍTICO: A pasta principal não foi encontrada no caminho:\n{DIR_PRINCIPAL}", "ERRO")
        return

    arquivos_copiados = 0
    pastas_criadas = 0

    # Percorre toda a árvore de diretórios da pasta PRINCIPAL
    for raiz, pastas, arquivos in os.walk(DIR_PRINCIPAL):
        # Calcula o caminho relativo (ex: "NovasPastas\Pasta1")
        caminho_relativo = os.path.relpath(raiz, DIR_PRINCIPAL)
        
        # Determina a pasta correspondente no BACKUP
        pasta_destino_backup = os.path.join(DIR_BACKUP, caminho_relativo)

        # 1. Cria a estrutura de pastas no backup se não existir (Isso resolve seu problema)
        if not os.path.exists(pasta_destino_backup):
            os.makedirs(pasta_destino_backup)
            log(f"Nova pasta detectada e criada no backup: {caminho_relativo}", "SUCESSO")
            pastas_criadas += 1

        # 2. Verifica os arquivos dentro dessas pastas
        for arquivo in arquivos:
            origem_arquivo = os.path.join(raiz, arquivo)
            destino_arquivo = os.path.join(pasta_destino_backup, arquivo)

            copiar = False

            # Se o arquivo não existe no backup, copia
            if not os.path.exists(destino_arquivo):
                copiar = True
                motivo = "Novo arquivo"
            else:
                # Se existe, verifica se o da Principal é mais recente
                tempo_origem = os.path.getmtime(origem_arquivo)
                tempo_destino = os.path.getmtime(destino_arquivo)
                
                if tempo_origem > tempo_destino + 2:
                    copiar = True
                    motivo = "Atualizado"

            if copiar:
                try:
                    shutil.copy2(origem_arquivo, destino_arquivo)
                    log(f"[{motivo}] {arquivo}", "SUCESSO")
                    arquivos_copiados += 1
                except Exception as e:
                    log(f"Falha ao copiar {arquivo}: {e}", "ERRO")

    print(f"\n{Cores.VERDE}Sincronização Concluída!{Cores.RESET}")
    print(f"Resumo: {pastas_criadas} novas pastas, {arquivos_copiados} arquivos sincronizados.")

def restaurar_disastre():
    print(f"\n{Cores.VERMELHO}=== MODO DE RECUPERAÇÃO DE DESASTRES ==={Cores.RESET}")
    
    if not os.path.exists(DIR_BACKUP):
        log("A pasta de Backup não existe! Nada para restaurar.", "ERRO")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
    nome_pasta_recuperada = f"{os.path.basename(DIR_PRINCIPAL)}_RECUPERADO_{timestamp}"
    
    diretorio_pai = os.path.dirname(DIR_PRINCIPAL)
    caminho_nova_principal = os.path.join(diretorio_pai, nome_pasta_recuperada)

    print(f"Restaurando backup para:\n -> {Cores.AZUL}{caminho_nova_principal}{Cores.RESET}")
    
    confirmacao = input("\nConfirmar restauração? (SIM/NAO): ").upper()
    
    if confirmacao == "SIM":
        try:
            log("Clonando arquivos... Aguarde...", "AVISO")
            shutil.copytree(DIR_BACKUP, caminho_nova_principal)
            log("RESTAURAÇÃO BEM SUCEDIDA!", "SUCESSO")
            print(f"Local: {caminho_nova_principal}")
        except Exception as e:
            log(f"Erro na restauração: {e}", "ERRO")
    else:
        log("Cancelado.", "AVISO")

def menu():
    while True:
        print("\n" + "="*50)
        print(f"{Cores.NEGRITO}   GERENCIADOR DE BACKUP BLINDADO{Cores.RESET}")
        print("="*50)
        print("1. 🔄 SINCRONIZAR (Copia pastas novas e arquivos)")
        print("2. 🚑 RESTAURAR (Recupera tudo em caso de erro)")
        print("3. ❌ Sair")
        
        op = input("\nOpção: ")
        
        if op == "1":
            sincronizar_principais_para_backup()
            input("\nEnter para continuar...")
        elif op == "2":
            restaurar_disastre()
            input("\nEnter para continuar...")
        elif op == "3":
            break

if __name__ == "__main__":
    if not os.path.exists(DIR_BACKUP):
        try: os.makedirs(DIR_BACKUP)
        except: pass
    menu()
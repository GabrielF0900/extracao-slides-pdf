import os
import shutil
import time
from datetime import datetime
from pathlib import Path

# ===== CONFIGURAÇÕES DO USUÁRIO =====

# 1. SUA PASTA DE TRABALHO ATUAL (A "Principal")
DIR_PRINCIPAL = r"C:\Users\gabri\OneDrive\Desktop\Projetos\Material Escola da Nuvem_Teste\"

# 2. SUA PASTA DE SEGURANÇA (Onde tudo fica guardado para sempre)
DIR_BACKUP = r"C:\Users\gabri\OneDrive\Desktop\Backups_Blindados\Modulos Re_Start_Backup"

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
    NUNCA deleta nada do Backup.
    """
    print(f"\n{Cores.NEGRITO}=== INICIANDO SINCRONIZAÇÃO BLINDADA ==={Cores.RESET}")
    print(f"De: {DIR_PRINCIPAL}")
    print(f"Para: {DIR_BACKUP}\n")

    if not os.path.exists(DIR_PRINCIPAL):
        log("Pasta Principal não encontrada!", "ERRO")
        return

    arquivos_copiados = 0
    pastas_criadas = 0

    # Percorre toda a árvore de diretórios da pasta PRINCIPAL
    for raiz, pastas, arquivos in os.walk(DIR_PRINCIPAL):
        # Calcula o caminho relativo (ex: "Semestre1\Matematica")
        caminho_relativo = os.path.relpath(raiz, DIR_PRINCIPAL)
        
        # Determina a pasta correspondente no BACKUP
        pasta_destino_backup = os.path.join(DIR_BACKUP, caminho_relativo)

        # 1. Cria a estrutura de pastas no backup se não existir
        if not os.path.exists(pasta_destino_backup):
            os.makedirs(pasta_destino_backup)
            log(f"Pasta criada no backup: {caminho_relativo}", "SUCESSO")
            pastas_criadas += 1

        # 2. Verifica os arquivos
        for arquivo in arquivos:
            origem_arquivo = os.path.join(raiz, arquivo)
            destino_arquivo = os.path.join(pasta_destino_backup, arquivo)

            copiar = False

            # Se o arquivo não existe no backup, copia
            if not os.path.exists(destino_arquivo):
                copiar = True
                motivo = "Novo arquivo"
            else:
                # Se existe, verifica se o da Principal é mais recente (modificado)
                tempo_origem = os.path.getmtime(origem_arquivo)
                tempo_destino = os.path.getmtime(destino_arquivo)
                
                # Margem de 2 segundos para evitar diferenças de sistema de arquivos
                if tempo_origem > tempo_destino + 2:
                    copiar = True
                    motivo = "Arquivo atualizado"

            if copiar:
                try:
                    shutil.copy2(origem_arquivo, destino_arquivo)
                    log(f"[{motivo}] {arquivo}", "SUCESSO")
                    arquivos_copiados += 1
                except Exception as e:
                    log(f"Falha ao copiar {arquivo}: {e}", "ERRO")

    print(f"\n{Cores.VERDE}Sincronização Concluída!{Cores.RESET}")
    print(f"Resumo: {pastas_criadas} pastas criadas, {arquivos_copiados} arquivos copiados.")
    print(f"{Cores.AMARELO}Nota: Nenhum arquivo foi excluído do backup.{Cores.RESET}")

def restaurar_disastre():
    """
    Cria uma NOVA pasta principal baseada no backup completo.
    """
    print(f"\n{Cores.VERMELHO}=== MODO DE RECUPERAÇÃO DE DESASTRES ==={Cores.RESET}")
    
    if not os.path.exists(DIR_BACKUP):
        log("A pasta de Backup não existe! Nada para restaurar.", "ERRO")
        return

    # Gera um nome para a nova pasta recuperada com Data e Hora
    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
    nome_pasta_recuperada = f"{os.path.basename(DIR_PRINCIPAL)}_RECUPERADO_{timestamp}"
    
    # Define onde será criada (no mesmo diretório pai da pasta original)
    diretorio_pai = os.path.dirname(DIR_PRINCIPAL)
    caminho_nova_principal = os.path.join(diretorio_pai, nome_pasta_recuperada)

    print(f"O Backup será clonado para uma nova pasta:\n -> {Cores.AZUL}{caminho_nova_principal}{Cores.RESET}")
    
    confirmacao = input("\nConfirmar restauração completa? (Digite 'SIM'): ").upper()
    
    if confirmacao == "SIM":
        try:
            log("Iniciando clonagem... Isso pode levar um tempo dependendo do tamanho.", "AVISO")
            shutil.copytree(DIR_BACKUP, caminho_nova_principal)
            
            print("\n" + "="*50)
            log("RESTAURAÇÃO BEM SUCEDIDA!", "SUCESSO")
            print("="*50)
            print("Sua estrutura foi recriada.")
            print("1. Verifique a nova pasta criada.")
            print("2. Se estiver tudo certo, você pode renomear a antiga e passar a usar essa como Principal.")
            print(f"Local: {caminho_nova_principal}")
            
        except Exception as e:
            log(f"Erro crítico na restauração: {e}", "ERRO")
    else:
        log("Operação cancelada pelo usuário.", "AVISO")

def menu():
    while True:
        print("\n" + "="*50)
        print(f"{Cores.NEGRITO}   SISTEMA DE BACKUP & RECOVERY (FILESYSTEM){Cores.RESET}")
        print("="*50)
        print("1. 🔄 SINCRONIZAR (Principal -> Backup)")
        print("      (Salva novidades, NÃO apaga nada no backup)")
        print("2. 🚑 RESTAURAR (Backup -> Nova Pasta)")
        print("      (Recria toda a estrutura em caso de desastre)")
        print("3. ❌ Sair")
        
        op = input("\nEscolha uma opção: ")
        
        if op == "1":
            sincronizar_principais_para_backup()
            input("\nPressione ENTER para voltar...")
        elif op == "2":
            restaurar_disastre()
            input("\nPressione ENTER para voltar...")
        elif op == "3":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    # Cria a pasta de backup inicial se não existir
    if not os.path.exists(DIR_BACKUP):
        try:
            os.makedirs(DIR_BACKUP)
        except:
            pass
            
    menu()
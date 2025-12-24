#!/usr/bin/env python3
import subprocess
import time
import os
import sys
import signal

def find_browser():
    """Encontra o caminho do navegador instalado"""
    browsers = [
        ("Chrome", ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"]),
        ("Edge", ["C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
                  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"]),
        ("Firefox", ["C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                     "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"]),
    ]
    
    for browser_name, paths in browsers:
        for path in paths:
            if os.path.exists(path):
                return browser_name, path
    
    return None, None

def kill_browser_processes():
    """Mata processos de navegadores abertos"""
    processes = ['chrome.exe', 'msedge.exe', 'firefox.exe']
    for proc in processes:
        try:
            subprocess.run(['taskkill', '/F', '/IM', proc], 
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except:
            pass
    time.sleep(2)

def open_browser_debug(browser_name, browser_path, port):
    """Abre navegador em modo debug"""
    print(f"\n📱 Abrindo {browser_name} em modo debug (porta {port})...")
    print(f"📍 Caminho: {browser_path}")
    
    if "firefox" in browser_path.lower():
        cmd = [browser_path, '--remote-debugging-protocol', '-start-debugger-server', str(port)]
    else:
        cmd = [browser_path, f'--remote-debugging-port={port}']
    
    try:
        subprocess.Popen(cmd)
        print(f"✅ {browser_name} aberto com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao abrir {browser_name}: {e}")
        return False

def wait_for_browser(port, timeout=30):
    """Aguarda o navegador estar pronto"""
    import socket
    
    print(f"\n⏳ Aguardando navegador ficar pronto (porta {port})...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"✅ Navegador pronto! Conectando...")
                return True
        except:
            pass
        
        time.sleep(1)
    
    return False

def run_extraction_script():
    """Executa o script de extração"""
    print(f"\n🔍 Iniciando extração de conteúdo...\n")
    
    try:
        result = subprocess.run(["node", "capturar.js"])
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar script: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("   🔥 EXTRATOR DE CONTEÚDO PARA PDF 🔥")
    print("="*50 + "\n")
    
    # Encontra navegador
    browser_name, browser_path = find_browser()
    
    if not browser_name:
        print("❌ Nenhum navegador (Chrome, Edge ou Firefox) foi encontrado!")
        print("\n💡 Instale um dos seguintes navegadores:")
        print("   - Google Chrome")
        print("   - Microsoft Edge")
        print("   - Mozilla Firefox")
        input("\nPressione ENTER para sair...")
        return
    
    # Mata processos antigos
    print("🧹 Encerrando instâncias antigas do navegador...")
    kill_browser_processes()
    
    # Abre navegador em modo debug
    if browser_name.lower() == "firefox":
        port = 9223
    else:
        port = 9222
    
    if not open_browser_debug(browser_name, browser_path, port):
        return
    
    # Aguarda navegador
    if not wait_for_browser(port):
        print("❌ Timeout: Navegador não respondeu a tempo!")
        return
    
    # Aguarda interação do usuário
    print(f"\n📌 {browser_name} está aberto!")
    print(f"🌐 Digite a URL ou procure o conteúdo que deseja extrair")
    print(f"⏱️  Aguardando seu comando...\n")
    
    input("🎯 Pressione ENTER quando estiver pronto para extrair o conteúdo ")
    
    # Executa script de extração
    print("\n" + "="*50)
    subprocess.run(["node", "capturar.js"])
    
    print("\n✅ Processo concluído!")
    print("👋 Você pode continuar usando o navegador normalmente.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operação cancelada!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    finally:
        input("\nPressione ENTER para fechar...")

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def main():
    print("\n" + "="*60)
    print(" 📄 EXTRATOR PYTHON PARA EDGE (PORTA 9222) 📄")
    print("="*60 + "\n")

    async with async_playwright() as p:
        try:
            # 1. Tenta conectar ao Edge que você abriu com o comando manual
            print("🔗 Conectando ao Edge em localhost:9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            # Pega o contexto padrão
            if not browser.contexts:
                print("❌ Nenhum contexto encontrado.")
                return

            context = browser.contexts[0]
            
            # Garante que pega uma página aberta (não fechada)
            if not context.pages:
                page = await context.new_page()
            else:
                page = context.pages[-1]

            titulo = await page.title()
            print(f"📍 Página encontrada: {titulo}")

            # 2. ROLAGEM AUTOMÁTICA
            # CORREÇÃO: Removidos comentários com '#' e adicionado '()' no final para executar
            print("⏳ Rolando página para carregar imagens...")
            await page.evaluate("""(async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 100;
                    const timer = setInterval(() => {
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;

                        if(totalHeight >= scrollHeight - window.innerHeight){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100); // Velocidade do scroll (comentário corrigido para JS)
                });
                window.scrollTo(0, 0); // Volta pro topo (comentário corrigido para JS)
            })()""") 

            # 3. LIMPEZA (Remove menus, barras laterais, etc)
            print("🧹 Limpando visual (removendo menus)...")
            await page.evaluate("""() => {
                const seletores_lixo = [
                    'header', 'footer', 'nav', 'aside', 
                    '.sidebar', '.menu-lateral', '.navigation', 
                    '.botoes-curso', '#barra-progresso'
                ];
                seletores_lixo.forEach(seletor => {
                    document.querySelectorAll(seletor).forEach(el => el.style.display = 'none');
                });

                // Força o conteúdo a usar 100% da largura
                const main = document.querySelector('main') || document.body;
                if (main) {
                    main.style.width = '100%';
                    main.style.margin = '0';
                    main.style.padding = '20px';
                }
            }""")

            # 4. GERA O PDF
            print("🎨 Gerando PDF...")
            # Aguarda um pouco para garantir que as imagens carregaram após o scroll
            await page.wait_for_timeout(2000) 
            
            await page.emulate_media(media="print") 
            
            nome_arquivo = f"AWS_Material_{datetime.now().strftime('%H%M%S')}.pdf"
            
            await page.pdf(
                path=nome_arquivo,
                format="A4",
                print_background=True, 
                margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"}
            )

            print(f"\n✅ SUCESSO! Arquivo salvo: {nome_arquivo}")
            print(f"📂 Caminho: {os.path.abspath(nome_arquivo)}")
            
            # Desconecta mantendo o navegador aberto
            print("🔌 Desconectando do navegador...")
            await browser.close()

        except Exception as e:
            print("\n❌ ERRO DURANTE A EXECUÇÃO:")
            if "ECONNREFUSED" in str(e):
                print("O Edge não foi encontrado na porta 9222.")
                print("Execute no PowerShell:")
                print('Start-Process "msedge" -ArgumentList "--remote-debugging-port=9222", "--user-data-dir=C:\\EdgeDebug"')
            else:
                print(f"Detalhe do erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
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
            # 1. Tenta conectar ao Edge que você abriu com o .bat
            print("🔗 Conectando ao Edge em localhost:9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            # Pega o contexto padrão e a última página ativa
            context = browser.contexts[0]
            if not context.pages:
                print("❌ Nenhuma aba encontrada no Edge.")
                return
            
            page = context.pages[-1]
            titulo = await page.title()
            print(f"📍 Página encontrada: {titulo}")

            # 2. ROLAGEM AUTOMÁTICA (Essencial para carregar imagens)
            print("⏳ Rolando página para carregar imagens...")
            await page.evaluate("""async () => {
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
                    }, 100); # Velocidade do scroll
                });
                window.scrollTo(0, 0); # Volta pro topo depois de carregar
            }""")

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
                main.style.width = '100%';
                main.style.margin = '0';
                main.style.padding = '20px';
            }""")

            # 4. GERA O PDF
            print("🎨 Gerando PDF...")
            # Força CSS de impressão
            await page.emulate_media(media="print") 
            
            nome_arquivo = f"AWS_Material_{datetime.now().strftime('%H%M%S')}.pdf"
            
            await page.pdf(
                path=nome_arquivo,
                format="A4",
                print_background=True, # IMPORTANTE: Mantém as cores e imagens de fundo
                margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"}
            )

            print(f"\n✅ SUCESSO! Arquivo salvo: {nome_arquivo}")
            print(f"📂 Caminho: {os.path.abspath(nome_arquivo)}")
            
            # Desconecta sem fechar o navegador
            await browser.close()

        except Exception as e:
            print("\n❌ ERRO DE CONEXÃO:")
            print("Verifique se você abriu o Edge usando o arquivo .bat ou o comando:")
            print('start msedge --remote-debugging-port=9222 --user-data-dir="C:\\EdgeDebug"')
            print(f"\nDetalhe do erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
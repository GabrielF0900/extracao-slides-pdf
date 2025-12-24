import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def main():
    print("\n" + "="*60)
    print(" 📄 EXTRATOR PYTHON - VERSÃO FORCE EXPAND 📄")
    print("="*60 + "\n")

    async with async_playwright() as p:
        try:
            print("🔗 Conectando ao Edge em localhost:9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            if not browser.contexts:
                print("❌ Nenhum contexto encontrado.")
                return

            context = browser.contexts[0]
            if not context.pages:
                page = await context.new_page()
            else:
                page = context.pages[-1]

            titulo = await page.title()
            print(f"📍 Página alvo: {titulo}")

            # ---------------------------------------------------------
            # 1. TRUQUE DE CSS (ESSENCIAL PARA PDF COMPLETO)
            # ---------------------------------------------------------
            print("🔧 Injetando CSS para expandir o conteúdo...")
            await page.evaluate("""() => {
                // 1. Força todos os containers principais a ficarem visíveis e sem scroll interno
                const style = document.createElement('style');
                style.innerHTML = `
                    html, body, #root, #app, .main-content, #main, .scrollable-area {
                        height: auto !important;
                        min-height: 100% !important;
                        overflow: visible !important;
                        overflow-y: visible !important;
                        position: static !important;
                        display: block !important;
                    }
                    
                    // Esconde barras de rolagem feias no PDF
                    ::-webkit-scrollbar { display: none; }
                    
                    // Força largura total
                    body { width: 100% !important; }
                `;
                document.head.appendChild(style);
            }""")

            # ---------------------------------------------------------
            # 2. ROLAGEM (Para carregar imagens preguiçosas/lazy load)
            # ---------------------------------------------------------
            print("⏳ Rolando para carregar imagens...")
            await page.evaluate("""async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 300; // Pulo maior para ser mais rápido
                    const timer = setInterval(() => {
                        // Tenta rolar o body
                        window.scrollBy(0, distance);
                        totalHeight += distance;

                        // Verifica se chegamos ao fim visualmente ou por limite
                        if(totalHeight >= 50000 || (document.body.scrollHeight > 0 && totalHeight >= document.body.scrollHeight)) {
                            clearInterval(timer);
                            resolve();
                        }
                    }, 150);
                });
                // Não voltamos ao topo para não esconder elementos lazy load
            }""")
            
            # Aguarda um momento para as imagens terminarem de renderizar
            await page.wait_for_timeout(3000)

            # ---------------------------------------------------------
            # 3. GERA O PDF
            # ---------------------------------------------------------
            print("🎨 Gerando PDF...")
            
            # Mudei para 'screen'. 'print' costuma esconder conteúdo em sites de curso.
            await page.emulate_media(media="screen") 
            
            nome_arquivo = f"AWS_Completo_{datetime.now().strftime('%H%M%S')}.pdf"
            
            await page.pdf(
                path=nome_arquivo,
                format="A4",
                print_background=True,
                margin={"top": "10px", "bottom": "10px", "left": "10px", "right": "10px"},
                # A escala pode ajudar a caber melhor se o site for largo
                scale=0.8 
            )

            print(f"\n✅ SUCESSO! PDF gerado: {nome_arquivo}")
            print(f"📂 Local: {os.path.abspath(nome_arquivo)}")
            
            print("🔌 Desconectando...")
            await browser.close()

        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            if "ECONNREFUSED" in str(e):
                print("⚠️ O Edge Debug não está aberto.")

if __name__ == "__main__":
    asyncio.run(main())
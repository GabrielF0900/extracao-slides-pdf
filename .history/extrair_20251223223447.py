import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def main():
    print("\n" + "="*60)
    print(" 📄 EXTRATOR VIA TECLADO (SIMULAÇÃO HUMANA) 📄")
    print("="*60 + "\n")

    async with async_playwright() as p:
        try:
            print("🔗 Conectando ao Edge em localhost:9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            context = browser.contexts[0]
            if not context.pages:
                page = await context.new_page()
            else:
                page = context.pages[-1]

            titulo = await page.title()
            print(f"📍 Página alvo: {titulo}")

            # ---------------------------------------------------------
            # 1. ROLAGEM VIA TECLADO (Mais robusto que JS)
            # ---------------------------------------------------------
            print("🖱️ Clicando no centro da tela para focar...")
            # Clica no centro para garantir que o teclado vai rolar o conteúdo certo
            await page.mouse.click(500, 500) 
            
            print("⏳ Pressionando 'PageDown' para carregar tudo...")
            
            # Loop de rolagem via teclado
            last_scroll_position = 0
            same_position_count = 0
            max_retries = 5  # Quantas vezes tentar se a tela não mexer

            for _ in range(200): # Limite de segurança de 200 "PageDowns"
                # Pressiona a tecla de descer página
                await page.keyboard.press("PageDown")
                
                # Espera carregar imagens (ajuste se sua net for lenta)
                await page.wait_for_timeout(500) 
                
                # Verifica onde estamos na página (eixo Y)
                current_scroll = await page.evaluate("() => window.scrollY || document.querySelector('main, .content, #root')?.scrollTop || 0")
                
                # Se a posição não mudou (chegou no fim ou travou)
                if current_scroll == last_scroll_position:
                    same_position_count += 1
                    print(f"   ...sem movimento ({same_position_count}/{max_retries})")
                else:
                    same_position_count = 0 # Reset se mexeu
                    print(f"   ⬇️ Rolando... (Pos: {current_scroll})")
                
                last_scroll_position = current_scroll

                # Se tentou 5 vezes e não saiu do lugar, assume que acabou
                if same_position_count >= max_retries:
                    print("✅ Fim da página detectado.")
                    break
            
            # Aguarda um pouco extra para imagens finais
            await page.wait_for_timeout(2000)

            # ---------------------------------------------------------
            # 2. INJEÇÃO CSS PARA PDF (Evita corte do conteúdo)
            # ---------------------------------------------------------
            print("🔧 Ajustando CSS para o PDF não cortar...")
            await page.evaluate("""() => {
                const style = document.createElement('style');
                style.innerHTML = `
                    /* Força altura automática em tudo para o PDF pegar tudo */
                    html, body, #root, #app, main, div {
                        height: auto !important;
                        overflow: visible !important;
                    }
                    /* Esconde botões flutuantes que atrapalham */
                    button, nav, header, footer {
                        display: none !important;
                    }
                `;
                document.head.appendChild(style);
            }""")

            # ---------------------------------------------------------
            # 3. GERA O PDF
            # ---------------------------------------------------------
            print("🎨 Gerando PDF...")
            await page.emulate_media(media="screen")
            
            nome_arquivo = f"Curso_Conteudo_{datetime.now().strftime('%H%M%S')}.pdf"
            
            await page.pdf(
                path=nome_arquivo,
                format="A4",
                print_background=True,
                margin={"top": "10px", "bottom": "10px", "left": "10px", "right": "10px"}
            )

            print(f"\n✅ SUCESSO! PDF salvo: {nome_arquivo}")
            print(f"📂 Caminho: {os.path.abspath(nome_arquivo)}")
            
            print("🔌 Desconectando...")
            await browser.close()

        except Exception as e:
            print(f"\n❌ ERRO: {e}")

if __name__ == "__main__":
    asyncio.run(main())
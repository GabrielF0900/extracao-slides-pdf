import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import os

async def main():
    print("\n" + "="*60)
    print(" 🖱️ EXTRATOR VIA MOUSE WHEEL (RODA DO MOUSE) 🖱️")
    print("="*60 + "\n")

    # 1. PERGUNTA AO USUÁRIO
    try:
        qtd_capturas = int(input("👉 Quantas 'roladas' de tela devo dar? (ex: 15): "))
    except ValueError:
        print("❌ Digite apenas números.")
        return

    async with async_playwright() as p:
        try:
            print("\n🔗 Conectando ao Edge em localhost:9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            context = browser.contexts[0]
            if not context.pages:
                page = await context.new_page()
            else:
                page = context.pages[-1]
            
            print(f"📍 Página conectada: {await page.title()}")
            print("-" * 50)
            print("⚠️ ATENÇÃO: Não mexa no mouse enquanto o script roda!")
            print("⏳ Começando em 5 segundos...")
            print("-" * 50)
            await asyncio.sleep(5)

            # Define o tamanho da tela para garantir prints padronizados
            viewport = page.viewport_size
            if not viewport:
                # Se não tiver tamanho definido, define um padrão Full HD
                await page.set_viewport_size({"width": 1920, "height": 1080})
                altura_tela = 1080
                largura_tela = 1920
            else:
                altura_tela = viewport['height']
                largura_tela = viewport['width']

            lista_imagens = []

            # Posiciona o mouse no CENTRO da tela (importante para o scroll funcionar na div certa)
            await page.mouse.move(largura_tela / 2, altura_tela / 2)
            
            # Clica uma vez para garantir foco
            await page.mouse.click(largura_tela / 2, altura_tela / 2)

            # 2. LOOP DE CAPTURA
            for i in range(1, qtd_capturas + 1):
                print(f"📸 Capturando parte {i} de {qtd_capturas}...")
                
                nome_img = f"temp_scroll_{i:03d}.png"
                
                # Tira o print
                await page.screenshot(path=nome_img, full_page=False)
                lista_imagens.append(nome_img)

                if i < qtd_capturas:
                    print("   ⬇️ Girando a roda do mouse (Scroll)...")
                    
                    # Simula a roda do mouse descendo (deltaY positivo = descer)
                    # O valor 800 geralmente é uma "tela cheia" de rolagem, ajuste se necessário
                    await page.mouse.wheel(0, 800)
                    
                    # Espera a rolagem acontecer visualmente
                    await asyncio.sleep(2)

            # 3. GERA PDF
            print("\n📚 Compilando PDF...")
            
            if lista_imagens:
                imagem_capa = Image.open(lista_imagens[0])
                outras_imagens = [Image.open(img).convert("RGB") for img in lista_imagens[1:]]
                
                nome_pdf = "Material_Rolagem_Mouse.pdf"
                
                imagem_capa.save(
                    nome_pdf, 
                    save_all=True, 
                    append_images=outras_imagens
                )
                
                print(f"✅ SUCESSO! PDF salvo: {os.path.abspath(nome_pdf)}")
                
                # Limpeza
                for img in lista_imagens:
                    if os.path.exists(img):
                        os.remove(img)

            print("🔌 Desconectando...")
            await browser.close()

        except Exception as e:
            print(f"\n❌ ERRO: {e}")

if __name__ == "__main__":
    asyncio.run(main())
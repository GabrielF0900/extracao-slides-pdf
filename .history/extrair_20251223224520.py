import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import os

async def main():
    print("\n" + "="*60)
    print(" 📜 EXTRATOR VERTICAL (SCROLL TELA A TELA) 📜")
    print("="*60 + "\n")

    # 1. PERGUNTA AO USUÁRIO
    try:
        qtd_capturas = int(input("👉 Quantas vezes devo rolar e tirar print? (ex: 18): "))
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
            print("⚠️ Prepare a página no topo (início). Começando em 5 segundos...")
            await asyncio.sleep(5)

            # Oculta a barra de rolagem lateral para não sair feio no print
            await page.add_style_tag(content="::-webkit-scrollbar { display: none; }")

            lista_imagens = []

            # 2. LOOP DE CAPTURA VERTICAL
            for i in range(1, qtd_capturas + 1):
                print(f"📸 Capturando tela {i} de {qtd_capturas}...")
                
                nome_img = f"temp_v_slide_{i:03d}.png"
                
                # Tira o print do que está visível agora
                await page.screenshot(path=nome_img, full_page=False)
                lista_imagens.append(nome_img)

                if i < qtd_capturas:
                    print("   ⬇️ Rolando uma tela para baixo...")
                    
                    # Rola exatamente a altura da janela (100% da viewport)
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    
                    # Espera a rolagem acontecer e imagens carregarem
                    await asyncio.sleep(2)

            # 3. CRIAÇÃO DO PDF
            print("\n📚 Compilando PDF Vertical...")
            
            if lista_imagens:
                imagem_capa = Image.open(lista_imagens[0])
                outras_imagens = [Image.open(img).convert("RGB") for img in lista_imagens[1:]]
                
                nome_pdf = "Material_Vertical_Completo.pdf"
                
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
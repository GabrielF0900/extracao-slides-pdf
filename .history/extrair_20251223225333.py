import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import os

async def main():
    print("\n" + "="*60)
    print(" 📸 MODO FOTÓGRAFO MANUAL (Enquadramento Perfeito) 📸")
    print("="*60)
    print("Instruções:")
    print("1. O navegador vai abrir.")
    print("2. Posicione a tela onde você quer.")
    print("3. Volte aqui e aperte ENTER para tirar a foto.")
    print("4. Digite 'f' e ENTER quando acabar para gerar o PDF.")
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
            
            print(f"📍 Conectado à página: {await page.title()}")
            
            # Ajuste de visualização para garantir qualidade (Full HD)
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Oculta a barra de rolagem lateral para o print ficar limpo
            await page.add_style_tag(content="::-webkit-scrollbar { display: none; }")

            lista_imagens = []
            contador = 1

            while True:
                # Aguarda o comando do usuário
                comando = input(f"\n👉 Posicione a tela {contador} e pressione ENTER (ou 'f' para fechar): ").strip().lower()

                if comando == 'f':
                    break
                
                # Nome do arquivo temporário
                nome_img = f"temp_foto_{contador:03d}.png"
                
                print(f"   📸 Capturando tela {contador}...", end="")
                
                # Tira o print exato do que você está vendo
                await page.screenshot(path=nome_img, full_page=False)
                lista_imagens.append(nome_img)
                print(" Feito!")
                
                contador += 1

            # --- GERAÇÃO DO PDF ---
            print("\n📚 Compilando PDF Final...")
            
            if lista_imagens:
                imagem_capa = Image.open(lista_imagens[0])
                outras_imagens = [Image.open(img).convert("RGB") for img in lista_imagens[1:]]
                
                nome_pdf = "Material_Enquadrado_Perfeito.pdf"
                
                imagem_capa.save(
                    nome_pdf, 
                    save_all=True, 
                    append_images=outras_imagens
                )
                
                print(f"✅ SUCESSO! PDF salvo: {os.path.abspath(nome_pdf)}")
                
                # Limpeza
                print("🧹 Limpando arquivos temporários...")
                for img in lista_imagens:
                    if os.path.exists(img):
                        os.remove(img)
            else:
                print("⚠️ Nenhuma foto foi tirada.")

            print("🔌 Desconectando...")
            await browser.close()

        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            print("Verifique se o Edge Debug está rodando.")

if __name__ == "__main__":
    asyncio.run(main())
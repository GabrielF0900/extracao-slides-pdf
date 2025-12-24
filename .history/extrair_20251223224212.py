import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import os
import time

async def main():
    print("\n" + "="*60)
    print(" 📸 EXTRATOR MANUAL (VOCÊ DIZ O TOTAL) 📸")
    print("="*60 + "\n")

    # 1. PERGUNTA AO USUÁRIO
    try:
        qtd_paginas = int(input("👉 Digite o número TOTAL de páginas/slides (ex: 18): "))
    except ValueError:
        print("❌ Por favor, digite apenas números.")
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
            
            titulo = await page.title()
            print(f"📍 Página conectada: {titulo}")
            print("-" * 50)
            print("⚠️ ATENÇÃO: Deixe a janela do Edge VISÍVEL na sua tela (não minimize).")
            print("⏳ Iniciando em 5 segundos... Prepare o slide na página 1.")
            print("-" * 50)
            await asyncio.sleep(5)

            lista_imagens = []

            # 2. LOOP DE CAPTURA
            for i in range(1, qtd_paginas + 1):
                print(f"📸 Capturando página {i} de {qtd_paginas}...")
                
                # Nome da imagem temporária
                nome_img = f"temp_slide_{i:03d}.png" # Ex: temp_slide_001.png
                
                # Garante que o mouse está "acordando" a tela antes do print
                await page.mouse.move(100, 100)
                await page.mouse.move(500, 500)
                
                # Tira o print exato do que está na tela
                await page.screenshot(path=nome_img, full_page=False)
                lista_imagens.append(nome_img)

                # Se não for a última página, avança para a próxima
                if i < qtd_paginas:
                    print("   ➡️ Indo para a próxima página...")
                    
                    # CLICA NO CENTRO para garantir que o teclado funcione
                    await page.mouse.click(500, 400)
                    
                    # Pressiona SETA PARA DIREITA
                    await page.keyboard.press("ArrowRight")
                    
                    # TENTA TAMBÉM ENTER/ESPAÇO (Caso a seta falhe em alguns cursos)
                    # await page.keyboard.press("Enter") 
                    
                    # Espera 3 segundos para a animação do slide acontecer
                    await asyncio.sleep(3)

            # 3. CRIAÇÃO DO PDF
            print("\n📚 Compilando PDF final...")
            
            if lista_imagens:
                imagem_capa = Image.open(lista_imagens[0])
                # Converte todas para o modo RGB (necessário para PDF)
                outras_imagens = [Image.open(img).convert("RGB") for img in lista_imagens[1:]]
                
                nome_pdf = "Curso_Completo_Manual.pdf"
                
                imagem_capa.save(
                    nome_pdf, 
                    save_all=True, 
                    append_images=outras_imagens
                )
                
                print(f"✅ SUCESSO! PDF gerado: {os.path.abspath(nome_pdf)}")
                
                # Limpa arquivos temporários
                print("🧹 Limpando imagens temporárias...")
                for img in lista_imagens:
                    if os.path.exists(img):
                        os.remove(img)
            else:
                print("❌ Nenhuma imagem foi capturada.")

            print("🔌 Desconectando...")
            await browser.close()

        except Exception as e:
            print(f"\n❌ ERRO TÉCNICO: {e}")
            print("Dica: Verifique se o Edge Debug está aberto.")

if __name__ == "__main__":
    asyncio.run(main())
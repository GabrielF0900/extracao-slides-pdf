import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import os
import re # Importante para achar os números no texto

async def main():
    print("\n" + "="*60)
    print(" 🕵️‍♂️ EXTRATOR INTELIGENTE (AUTO-DETECTAR SLIDES) 🕵️‍♂️")
    print("="*60 + "\n")

    async with async_playwright() as p:
        try:
            print("🔗 Conectando ao Edge em localhost:9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            context = browser.contexts[0]
            page = context.pages[-1] if context.pages else await context.new_page()
            
            print("⏳ Analisando a página para achar o contador de slides...")
            # Clica no centro para garantir foco
            await page.mouse.click(500, 300)
            await page.wait_for_timeout(2000) # Espera carregar a barra de progresso

            # ---------------------------------------------------------
            # 1. LÓGICA DE DETECÇÃO DE PÁGINAS
            # ---------------------------------------------------------
            total_slides = 30 # Valor padrão de segurança caso falhe
            encontrou_total = False

            try:
                # Procura por textos que tenham o formato "Número OF Número" ou "Número / Número"
                # O regex abaixo procura: Digito + espaço + (of/de//) + espaço + Digito
                conteudo_texto = await page.evaluate("() => document.body.innerText")
                
                # Procura o padrão "X of Y" (ex: "4 of 18")
                match = re.search(r"(\d+)\s*(?:of|de|/)\s*(\d+)", conteudo_texto, re.IGNORECASE)
                
                if match:
                    slide_atual = int(match.group(1))
                    total_detectado = int(match.group(2))
                    
                    # Validação simples: O total deve ser maior que 1 e menor que 500 (pra não pegar números errados)
                    if 1 < total_detectado < 500:
                        total_slides = total_detectado
                        encontrou_total = True
                        print(f"✅ DETECTADO: Slide {slide_atual} de {total_slides} slides totais.")
                        
                        # Se não estivermos no slide 1, podemos tentar voltar (opcional)
                        # Mas vamos assumir que você quer continuar de onde parou ou vai pro inicio manualmente
            except Exception as e:
                print(f"⚠️ Não foi possível ler o contador automaticamente: {e}")

            if not encontrou_total:
                print(f"⚠️ Contador não encontrado. Usando valor padrão: {total_slides} slides.")

            # ---------------------------------------------------------
            # 2. CAPTURA DOS SLIDES
            # ---------------------------------------------------------
            lista_imagens = []
            print(f"🔄 Iniciando captura de {total_slides} slides...")

            for i in range(1, total_slides + 1):
                print(f"   📸 Capturando {i}/{total_slides}...")
                
                nome_img = f"temp_slide_{i}.png"
                await page.screenshot(path=nome_img, full_page=False)
                lista_imagens.append(nome_img)

                # Se for o último slide, não precisa clicar em próximo
                if i < total_slides:
                    # Tenta ir para o próximo
                    await page.keyboard.press("ArrowRight")
                    await page.wait_for_timeout(2000) # Tempo para carregar o próximo slide

            # ---------------------------------------------------------
            # 3. GERAÇÃO DO PDF
            # ---------------------------------------------------------
            print("\n📚 Compilando PDF final...")
            if lista_imagens:
                imagem_capa = Image.open(lista_imagens[0])
                outras_imagens = [Image.open(img).convert("RGB") for img in lista_imagens[1:]]
                
                # Nome do arquivo com timestamp
                from datetime import datetime
                nome_pdf = f"Material_Completo_{datetime.now().strftime('%H%M')}.pdf"
                
                imagem_capa.save(nome_pdf, save_all=True, append_images=outras_imagens)
                
                print(f"✅ SUCESSO! Arquivo criado: {os.path.abspath(nome_pdf)}")
                
                # Limpa o lixo
                for img in lista_imagens:
                    try: os.remove(img)
                    except: pass
            
            print("🔌 Desconectando...")
            await browser.close()

        except Exception as e:
            print(f"\n❌ ERRO: {e}")

if __name__ == "__main__":
    asyncio.run(main())
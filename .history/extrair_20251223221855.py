#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import os

async def main():
    print("\n" + "="*60)
    print("   📄 EXTRATOR COMPLETO PARA PDF 📄")
    print("="*60 + "\n")
    
    print("Qual navegador?\n")
    print("1 - Chrome")
    print("2 - Firefox")
    print("3 - Safari\n")
    
    opcao = input("Digite (1-3): ").strip()
    
    browser_name = None
    launch_args = {}
    
    if opcao == "1":
        browser_name = "chromium"
    elif opcao == "2":
        browser_name = "firefox"
    elif opcao == "3":
        browser_name = "webkit"
    else:
        print("❌ Inválido!")
        return
    
    print(f"\n🚀 Abrindo...\n")
    
    async with async_playwright() as p:
        # Seleciona o navegador
        if browser_name == "chromium":
            browser = await p.chromium.launch(headless=False)
        elif browser_name == "firefox":
            browser = await p.firefox.launch(headless=False)
        else:
            browser = await p.webkit.launch(headless=False)
        
        page = await browser.new_page()
        
        await page.goto("about:blank")
        print(f"✅ Navegador aberto!\n")
        
        # URL
        url = input("URL (ou ENTER): ").strip()
        print()
        
        if url:
            print(f"🌐 Carregando...\n")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except:
                print("⚠️  Continuando...\n")
        else:
            print("👉 Navegue manualmente\n")
            input("ENTER quando carregar: ")
            print()
        
        print("⏳ Aguardando 3s...")
        await page.wait_for_timeout(3000)
        print("✅ Página carregada!\n")
        
        # Aguarda confirmação
        print("=" * 60)
        input("\n🎯 Pressione ENTER para EXTRAIR e gerar PDF: ")
        print()
        
        # Detecta páginas
        print("🔍 Detectando páginas...")
        total_paginas = await detectar_paginas(page)
        print(f"📊 Total detectado: {total_paginas} página(s)")
        
        # Debug: mostra o texto que foi analisado
        try:
            preview = await page.evaluate("() => document.body.innerText.substring(0, 300)")
            print(f"📋 Preview do conteúdo:\n{preview}\n")
        except:
            pass
        
        # Coleta conteúdo
        print("📥 Coletando conteúdo...\n")
        paginas = []
        
        for i in range(1, total_paginas + 1):
            try:
                print(f"   ⏳ Página {i}/{total_paginas}...")
                
                # Aguarda renderização
                await page.wait_for_timeout(2000)
                
                # Verifica se a página ainda está ativa
                if page.is_closed():
                    print(f"   ⚠️  Página foi fechada. Parando.")
                    break
                
                # Extrai conteúdo com timeout
                try:
                    conteudo = await asyncio.wait_for(
                        page.evaluate("""() => {
                            // Remove elementos desnecessários
                            const elementos = document.querySelectorAll(
                                'header, footer, nav, [class*="nav"], [class*="menu"], [class*="button-next"], [class*="button-prev"], .ads, [id*="cookie"], script, style'
                            );
                            elementos.forEach(el => {
                                try { el.remove(); } catch(e) {}
                            });
                            
                            // Encontra container principal (múltiplas tentativas)
                            let container = document.querySelector(
                                'main, article, [role="main"], .content, .page, [class*="slide"], [class*="lesson"], [class*="container"], .lesson-content, .course-content, .material, [class*="body-content"]'
                            );
                            
                            // Se não achou, tenta o body
                            if (!container || container.innerHTML.length < 100) {
                                container = document.body;
                            }
                            
                            // Remove scripts e styles antes de retornar
                            const clone = container.cloneNode(true);
                            clone.querySelectorAll('script, style').forEach(el => el.remove());
                            
                            return clone.innerHTML;
                        }"""),
                        timeout=5
                    )
                except asyncio.TimeoutError:
                    print(f"   ⚠️  Timeout ao extrair. Continuando...")
                    conteudo = None
                
                if conteudo and len(conteudo.strip()) > 50:
                    paginas.append(conteudo)
                    tamanho = len(conteudo)
                    print(f"   ✅ Coletada ({tamanho} caracteres)")
                else:
                    if not conteudo:
                        print(f"   ⚠️  Nenhum conteúdo extraído")
                    else:
                        print(f"   ⚠️  Conteúdo muito pequeno ({len(conteudo) if conteudo else 0} caracteres)")
                    paginas.append("<p>Conteúdo indisponível</p>")
                
                # Clica próximo
                if i < total_paginas:
                    clicou = await clicar_proximo(page)
                    if not clicou:
                        print(f"   ⚠️  Não consegui avançar. Parando.")
                        total_paginas = i
                        break
                    
                    # Aguarda próxima página carregar
                    await page.wait_for_timeout(2000)
            
            except Exception as e:
                print(f"   ⚠️  Erro na página {i}: {str(e)}")
                if len(paginas) == 0:
                    paginas.append("<p>Conteúdo indisponível</p>")
                continue
        
        print()
        
        # Gera HTML
        print("🎨 Montando PDF...")
        
        if len(paginas) == 0:
            print("❌ Nenhuma página foi coletada!")
            await browser.close()
            return
        
        html_completo = gerar_html(paginas)
        
        titulo = await page.title()
        data_str = datetime.now().strftime("%Y-%m-%d")
        nome_arquivo = f"{titulo[:30]}_{data_str}.pdf"
        caminho_completo = os.path.join(os.getcwd(), nome_arquivo)
        
        try:
            # Navega para o HTML com timeout maior
            await asyncio.wait_for(
                page.goto(f"data:text/html,{html_completo}", wait_until="domcontentloaded"),
                timeout=15
            )
            await page.wait_for_timeout(3000)
            
            # Gera PDF
            print("📄 Gerando PDF...")
            await page.pdf(
                path=caminho_completo,
                format="A4",
                print_background=True,
                margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"}
            )
            
            if os.path.exists(caminho_completo):
                size_bytes = os.path.getsize(caminho_completo)
                size_mb = size_bytes / (1024 * 1024)
                
                print("\n✅ PRONTO!\n")
                print(f"📄 {nome_arquivo}")
                print(f"📊 Páginas: {len(paginas)}")
                print(f"📏 {size_mb:.2f} MB")
                print(f"📍 {caminho_completo}\n")
                
                abrir = input("Abrir? (s/n): ").strip().lower()
                if abrir == "s":
                    os.startfile(caminho_completo)
            else:
                print("❌ Erro ao criar PDF\n")
        
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {str(e)}\n")
        
        finally:
            await browser.close()

async def detectar_paginas(page):
    """Detecta o número de páginas"""
    try:
        num = await asyncio.wait_for(
            page.evaluate("""() => {
                const texto = document.body.innerText;
                
                // "página X de Y"
                let match = texto.match(/página\\s+(\\d+)\\s+d[ae]\\s+(\\d+)/i);
                if (match) return parseInt(match[2]);
                
                // "page X of Y"
                match = texto.match(/page\\s+(\\d+)\\s+of\\s+(\\d+)/i);
                if (match) return parseInt(match[2]);
                
                // "X / Y"
                match = texto.match(/(\\d+)\\s*\\/\\s*(\\d+)/);
                if (match) {
                    const n = parseInt(match[2]);
                    if (n > 0 && n < 200) return n;
                }
                
                return null;
            }"""),
            timeout=5
        )
        
        return num if num else 1
    except Exception as e:
        print(f"   ⚠️  Erro ao detectar páginas: {str(e)}")
        return 1

async def clicar_proximo(page):
    """Clica no botão próximo"""
    try:
        clicou = await asyncio.wait_for(
            page.evaluate("""() => {
                const botoes = Array.from(
                    document.querySelectorAll('button, a, [role="button"]')
                );
                const botao = botoes.find(b => {
                    const texto = b.innerText.toLowerCase().trim();
                    return (
                        texto.includes('próximo') ||
                        texto.includes('next') ||
                        texto.includes('avançar') ||
                        texto === '>' ||
                        texto === '→'
                    );
                });
                
                if (botao && botao.offsetHeight > 0) {
                    botao.click();
                    return true;
                }
                return false;
            }"""),
            timeout=5
        )
        
        return clicou
    except Exception as e:
        print(f"   ⚠️  Erro ao clicar próximo: {str(e)}")
        return False

def gerar_html(paginas):
    """Gera HTML completo para PDF"""
    paginas_html = "\n".join([
        f'<div class="pagina">\n{html}\n</div>'
        for html in paginas
    ])
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: Arial, sans-serif; 
            background: white;
        }}
        .pagina {{ 
            page-break-after: always; 
            padding: 30px;
            min-height: 100vh;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            background: white;
        }}
        .pagina:last-child {{
            page-break-after: avoid;
        }}
        img {{ 
            max-width: 100%; 
            height: auto; 
            margin: 15px 0;
            display: block;
            border-radius: 4px;
        }}
        p {{ margin: 12px 0; }}
        h1 {{ margin: 25px 0 15px 0; font-size: 28px; }}
        h2 {{ margin: 20px 0 12px 0; font-size: 22px; }}
        h3 {{ margin: 18px 0 10px 0; font-size: 18px; }}
        h4, h5, h6 {{ margin: 15px 0 8px 0; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            border: 1px solid #ddd;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        ul, ol {{ margin: 12px 0 12px 20px; }}
        li {{ margin: 6px 0; }}
        pre {{
            background: #f5f5f5;
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 12px 0;
        }}
        code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    {paginas_html}
</body>
</html>
"""

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Cancelado!")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}\n")

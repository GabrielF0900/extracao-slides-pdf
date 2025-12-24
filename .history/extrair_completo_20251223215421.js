const { chromium, firefox, webkit } = require("playwright");
const fs = require("fs");
const path = require("path");
const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function pergunta(texto) {
  return new Promise((resolve) => {
    rl.question(texto, resolve);
  });
}

(async () => {
  let browser = null;
  let page = null;

  try {
    console.log("\n" + "=".repeat(60));
    console.log("   🔥 EXTRATOR DE CONTEÚDO PARA PDF 🔥");
    console.log("=".repeat(60) + "\n");

    // 1. Pergunta qual navegador usar
    console.log("Qual navegador você quer usar?\n");
    console.log("1 - Chrome/Edge (recomendado)");
    console.log("2 - Firefox");
    console.log("3 - Safari/Webkit\n");

    const opcao = await pergunta("Digite 1, 2 ou 3: ");

    let browserType;
    let browserName;

    if (opcao === "1") {
      browserType = chromium;
      browserName = "Chrome/Edge";
    } else if (opcao === "2") {
      browserType = firefox;
      browserName = "Firefox";
    } else if (opcao === "3") {
      browserType = webkit;
      browserName = "Safari/Webkit";
    } else {
      console.log("❌ Opção inválida!");
      rl.close();
      return;
    }

    console.log(`\n🚀 Abrindo ${browserName}...\n`);

    // 2. Abre o navegador
    browser = await browserType.launch({
      headless: false,
    });

    page = await browser.newPage();
    page.setDefaultTimeout(60000);
    page.setDefaultNavigationTimeout(60000);
    
    await page.goto("about:blank");

    console.log(`✅ ${browserName} aberto com sucesso!\n`);

    // 3. Pergunta a URL
    console.log("=" + "=".repeat(58) + "=");
    const url = await pergunta(
      "\n📌 Digite a URL ou pressione ENTER se já está na página: "
    );
    console.log();

    // Se forneceu URL, navega
    if (url.trim()) {
      console.log(`🌐 Navegando para: ${url}\n`);
      try {
        await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
      } catch (err) {
        console.log("⚠️  Timeout ao carregar (continuando mesmo assim)...\n");
      }
    } else {
      console.log("📌 Navegue manualmente para a página desejada.");
      console.log("⏳ Aguardando você estar na página certa...\n");
      await pergunta("Pressione ENTER quando estiver pronto: ");
      console.log();
    }

    // 4. Aguarda carregamento
    console.log("⏳ Aguardando carregamento completo...");
    await Promise.race([
      page.waitForLoadState("networkidle").catch(() => {}),
      new Promise((resolve) => setTimeout(resolve, 5000)),
    ]);
    console.log("✅ Página pronta!\n");

    // 5. Coleta TODAS as páginas/slides
    console.log("🔍 Detectando e coletando todas as páginas...\n");
    const todasAsPaginas = await coletarTodasAsPaginas(page);
    
    console.log(`📊 Total de páginas coletadas: ${todasAsPaginas.length}\n`);

    // 6. Obtém informações
    const titulo = await page.title();
    console.log(`📑 Título: "${titulo}"`);
    console.log(`🌐 URL: ${page.url()}\n`);

    // 7. Combina conteúdo
    console.log("🧹 Combinando conteúdo de todas as páginas...");
    await page.evaluate((paginas) => {
      // Limpa a página
      document.body.innerHTML = "";

      // Cria container
      const container = document.createElement("div");
      container.style.margin = "0";
      container.style.padding = "20px";
      container.style.width = "100%";
      container.style.boxSizing = "border-box";
      container.style.fontSize = "14px";
      container.style.lineHeight = "1.6";
      container.style.fontFamily = "Arial, sans-serif";

      // Adiciona cada página
      paginas.forEach((html, index) => {
        const paginaDiv = document.createElement("div");
        paginaDiv.style.pageBreakAfter = "always";
        paginaDiv.style.paddingBottom = "20px";
        paginaDiv.style.minHeight = "500px";
        paginaDiv.innerHTML = html;

        // Ajusta conteúdo dentro da página
        paginaDiv.querySelectorAll("img").forEach((img) => {
          img.style.maxWidth = "100%";
          img.style.height = "auto";
          img.style.display = "block";
          img.style.margin = "15px 0";
          img.style.pageBreakInside = "avoid";
        });

        paginaDiv.querySelectorAll("table").forEach((table) => {
          table.style.width = "100%";
          table.style.borderCollapse = "collapse";
          table.style.margin = "15px 0";
          table.style.pageBreakInside = "avoid";
        });

        paginaDiv.querySelectorAll("th, td").forEach((cell) => {
          cell.style.padding = "10px";
          cell.style.border = "1px solid #ccc";
        });

        paginaDiv.querySelectorAll("p, h1, h2, h3, h4, h5, h6").forEach(
          (el) => {
            el.style.pageBreakInside = "avoid";
          }
        );

        container.appendChild(paginaDiv);
      });

      document.body.appendChild(container);
    }, todasAsPaginas);

    console.log("✅ Conteúdo combinado!\n");

    // 8. Ativa modo de impressão
    await page.emulateMedia({ media: "print" });
    await page.waitForTimeout(1000);

    // 9. Gera o PDF
    const nomeArquivo = gerarNomePDF(titulo);
    const caminhoCompleto = path.join(process.cwd(), nomeArquivo);

    console.log("📄 Gerando PDF com alta qualidade...");
    console.log(`   📊 Páginas: ${todasAsPaginas.length}`);
    console.log(`   🖼️  Incluindo todas as imagens`);
    console.log(`   📝 Incluindo todos os textos`);
    console.log(`   ⏱️  Isto pode levar alguns segundos...\n`);

    await page.pdf({
      path: caminhoCompleto,
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
      timeout: 120000,
      margin: {
        top: "30px",
        bottom: "30px",
        left: "20px",
        right: "20px",
      },
      scale: 1.0,
      displayHeaderFooter: false,
    });

    // Verifica e mostra resultado
    if (fs.existsSync(caminhoCompleto)) {
      const stats = fs.statSync(caminhoCompleto);
      const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
      const sizeKB = (stats.size / 1024).toFixed(2);

      console.log("✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!\n");
      console.log(`💾 Arquivo: ${nomeArquivo}`);
      console.log(
        `📏 Tamanho: ${sizeMB > 0.1 ? sizeMB + " MB" : sizeKB + " KB"}`
      );
      console.log(`📍 Caminho: ${caminhoCompleto}\n`);

      // Pergunta se quer abrir
      const abrir = await pergunta("Deseja abrir o PDF? (s/n): ");
      if (abrir.toLowerCase() === "s" || abrir.toLowerCase() === "y") {
        const { exec } = require("child_process");
        exec(`start "" "${caminhoCompleto}"`);
        console.log("📂 Abrindo PDF...\n");
      }
    } else {
      console.log("❌ Erro: Arquivo PDF não foi criado!\n");
    }
  } catch (err) {
    console.error("\n❌ ERRO NA EXTRAÇÃO:\n");
    console.error(`${err.message}\n`);

    console.log("💡 Dicas para resolver:");
    console.log("   1. Aguarde a página carregar completamente");
    console.log("   2. Se houver login, faça login antes de rodar");
    console.log("   3. Verifique se o navegador está respondendo");
    console.log("   4. Tente novamente\n");
  } finally {
    if (browser) {
      await browser.close();
    }
    rl.close();
  }
})();

// ==================== FUNÇÕES AUXILIARES ====================

async function coletarTodasAsPaginas(page) {
  const paginas = [];

  try {
    // Estratégia 1: Detectar e navegar por slides/páginas com botões
    console.log("   📌 Procurando por slides/páginas com navegação...");
    
    // Aguarda conteúdo carregar em iframes
    await page.waitForTimeout(3000);

    // Tenta extrair conteúdo do iframe principal
    const frames = page.frames();
    console.log(`   📌 Encontrado ${frames.length} frame(s) - analisando...\n`);

    // Tenta de cada frame
    for (let frameIdx = 0; frameIdx < frames.length; frameIdx++) {
      try {
        const frame = frames[frameIdx];
        
        // Procura por indicadores de múltiplas páginas
        const temNavegacao = await frame.evaluate(() => {
          // Procura botões de navegação
          const botoes = document.querySelectorAll(
            'button, [role="button"], a[href*="next"], [class*="nav"], [class*="next"]'
          );
          return botoes.length > 0;
        }).catch(() => false);

        if (temNavegacao) {
          console.log(`   ✅ Frame ${frameIdx} detectado com navegação`);
          const paginasFrame = await extrairPaginasDoFrame(frame);
          paginas.push(...paginasFrame);
        }
      } catch (e) {
        // continua para o próximo frame
      }
    }

    // Estratégia 2: Se não encontrou nada, extrai conteúdo visível diretamente
    if (paginas.length === 0) {
      console.log("   📌 Extraindo conteúdo visível...\n");
      
      const conteudo = await page.evaluate(() => {
        // Remove elementos desnecessários
        const seletoresLixo = [
          "header",
          "footer",
          "nav",
          "aside",
          "noscript",
          "script",
          ".sidebar",
          ".menu-lateral",
          '[role="navigation"]',
          "[class*='button-next']",
          "[class*='button-prev']",
          "[class*='pagination']",
        ];

        seletoresLixo.forEach((seletor) => {
          document.querySelectorAll(seletor).forEach((el) => {
            el.remove();
          });
        });

        // Encontra conteúdo principal
        let main = document.querySelector(
          "main, article, [role='main'], .main, #main, .content, #content, .page-content, iframe"
        );

        if (!main) {
          main = document.body;
        }

        // Cria cópia do HTML limpo
        const clone = main.cloneNode(true);

        // Remove scripts
        clone.querySelectorAll("script, style").forEach((el) => {
          el.remove();
        });

        return clone.innerHTML;
      });

      if (conteudo && conteudo.trim().length > 100) {
        paginas.push(conteudo);
      }
    }

    // Se ainda estiver vazio, tenta extrair da página inteira
    if (paginas.length === 0) {
      console.log("   📌 Extraindo conteúdo completo da página...\n");
      
      const conteudoCompleto = await page.evaluate(() => {
        // Cria cópia da página inteira
        const clone = document.documentElement.cloneNode(true);

        // Remove elementos desnecessários
        const seletoresLixo = [
          "header",
          "footer",
          "nav",
          "aside",
          "noscript",
          "script",
          "style",
          ".sidebar",
          ".menu-lateral",
          '[role="navigation"]',
        ];

        seletoresLixo.forEach((seletor) => {
          clone.querySelectorAll(seletor).forEach((el) => {
            el.remove();
          });
        });

        return clone.body.innerHTML;
      });

      if (conteudoCompleto && conteudoCompleto.trim().length > 100) {
        paginas.push(conteudoCompleto);
      }
    }
  } catch (err) {
    console.log(`   ⚠️  Erro ao coletar: ${err.message}`);
  }

  return paginas.length > 0 ? paginas : [""]; // Retorna pelo menos uma página vazia
}

async function extrairPaginasDoFrame(frame) {
  const paginas = [];
  let tentativas = 0;
  const maxTentativas = 50;

  try {
    while (tentativas < maxTentativas) {
      // Extrai conteúdo da página atual
      const conteudo = await frame.evaluate(() => {
        // Remove lixo
        const seletoresLixo = [
          "header",
          "footer",
          "nav",
          "aside",
          "noscript",
          "script",
          ".sidebar",
          ".menu-lateral",
          '[role="navigation"]',
          "[class*='button-']",
          "[class*='nav-']",
        ];

        seletoresLixo.forEach((seletor) => {
          try {
            document.querySelectorAll(seletor).forEach((el) => {
              el.remove();
            });
          } catch (e) {}
        });

        // Encontra conteúdo
        let main = document.querySelector(
          "main, article, [role='main'], .main, #main, .content, #content, .page-content, body"
        );

        if (!main) {
          main = document.body;
        }

        const clone = main.cloneNode(true);
        clone.querySelectorAll("script, style").forEach((el) => {
          el.remove();
        });

        return {
          html: clone.innerHTML,
          temProximo: !!Array.from(document.querySelectorAll("button, a, [role='button']")).find(
            (b) =>
              b.innerText.toLowerCase().includes("próximo") ||
              b.innerText.toLowerCase().includes("next") ||
              b.innerText.toLowerCase().includes("avançar")
          ),
        };
      });

      if (conteudo.html && conteudo.html.trim().length > 50) {
        paginas.push(conteudo.html);
        console.log(`   ✅ Página ${paginas.length} extraída`);
      }

      // Tenta clicar no botão próximo
      if (conteudo.temProximo) {
        const clicou = await frame.evaluate(() => {
          const botoes = Array.from(
            document.querySelectorAll("button, a, [role='button']")
          );
          const botao = botoes.find(
            (b) =>
              b.innerText.toLowerCase().includes("próximo") ||
              b.innerText.toLowerCase().includes("next") ||
              b.innerText.toLowerCase().includes("avançar")
          );

          if (botao) {
            botao.click();
            return true;
          }
          return false;
        });

        if (clicou) {
          await frame.waitForTimeout(1500);
          tentativas++;
        } else {
          break;
        }
      } else {
        break;
      }
    }
  } catch (err) {
    console.log(`   ⚠️  Erro no frame: ${err.message}`);
  }

  return paginas;
}

function gerarNomePDF(titulo) {
  const nomeLimpo = titulo
    .replace(/[<>:"|?*\/\\]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 50);

  const timestamp = new Date().toISOString().slice(0, 10);
  return `${nomeLimpo}_${timestamp}.pdf`;
}
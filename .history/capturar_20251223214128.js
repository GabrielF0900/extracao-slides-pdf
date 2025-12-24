const { chromium, firefox, webkit } = require("playwright");
const fs = require("fs");
const path = require("path");

// ==================== CONFIGURAÇÕES ====================
const BROWSERS = [
  { name: "Chrome/Edge", port: 9222, browser: chromium },
  { name: "Firefox", port: 9223, browser: firefox },
  { name: "Safari/Webkit", port: 9224, browser: webkit },
];

// ==================== FUNÇÃO PRINCIPAL ====================
(async () => {
  let browser = null;
  let page = null;

  try {
    console.log("🔍 Iniciando extração de conteúdo...\n");

    // 1. Tenta conectar a qualquer navegador disponível
    let conectado = false;
    for (const browserConfig of BROWSERS) {
      try {
        console.log(
          `⚙️  Tentando conectar em ${browserConfig.name} (porta ${browserConfig.port})...`
        );
        browser = await browserConfig.browser.connectOverCDP(
          `http://127.0.0.1:${browserConfig.port}`,
          {
            timeout: 5000,
          }
        );
        console.log(`✅ Conectado em ${browserConfig.name}!\n`);
        conectado = true;
        break;
      } catch (err) {
        continue;
      }
    }

    if (!conectado) {
      console.log("❌ ERRO: Nenhum navegador com modo debug foi encontrado!");
      console.log(
        "\n📋 Para usar este script, abra seu navegador em modo debug:"
      );
      console.log("   Chrome/Edge: chrome --remote-debugging-port=9222");
      console.log(
        "   Firefox:     firefox --remote-debugging-protocol -start-debugger-server 9223"
      );
      console.log("   Safari/Webkit: webkit [com suporte a CDP]\n");
      return;
    }

    // 2. Obtém a aba ativa
    const context = browser.contexts()[0];
    const pages = context.pages();
    page = pages[pages.length - 1];

    if (!page) {
      console.log("❌ Erro: Nenhuma aba encontrada!");
      return;
    }

    const urlAtual = page.url();
    const titulo = await page.title();
    console.log(`📑 Página: "${titulo}"`);
    console.log(`🌐 URL: ${urlAtual}\n`);

    // 3. Aguarda carregamento mais agressivo
    console.log("⏳ Aguardando carregamento completo da página...");
    await Promise.race([
      page.waitForLoadState("networkidle").catch(() => {}),
      new Promise((resolve) => setTimeout(resolve, 8000)), // Timeout de 8 segundos
    ]);
    console.log("✅ Página carregada!\n");

    // 4. Aguarda e processa iframes
    console.log("🔍 Processando iframes...");
    await page.waitForTimeout(2000); // Aguarda iframes carregarem
    const frames = page.frames();
    console.log(`   📌 Encontrado ${frames.length} frame(s)`);
    for (const frame of frames) {
      try {
        await frame.waitForLoadState("networkidle").catch(() => {});
      } catch (e) {}
    }
    console.log("✅ Iframes processados!\n");

    // 5. Limpa e prepara o conteúdo
    console.log("🧹 Limpando elementos desnecessários...");
    await page.evaluate(() => {
      // Remove elementos que atrapalham
      const seletoresLixo = [
        "header",
        "footer",
        "nav",
        "aside",
        "noscript",
        "script",
        "style:not([data-keep])",
        ".sidebar",
        ".menu-lateral",
        ".navigation-bar",
        ".botoes-proximo-anterior",
        "#barra-progresso",
        '[role="navigation"]',
        '[role="complementary"]',
        ".cookies-banner",
        ".popup",
        ".modal-overlay",
        ".ad",
        ".advertisement",
        "[id*='cookie']",
        "[class*='banner']",
      ];

      seletoresLixo.forEach((seletor) => {
        try {
          document.querySelectorAll(seletor).forEach((el) => {
            if (el.tagName !== "SCRIPT" && el.tagName !== "STYLE") {
              el.remove();
            }
          });
        } catch (e) {}
      });

      // Prepara o conteúdo principal - procura em vários locais
      let main = document.querySelector(
        "main, article, [role='main'], .main, #main, .content, #content"
      );
      if (!main) {
        main = document.body;
      }

      main.style.margin = "0";
      main.style.padding = "20px";
      main.style.width = "100%";
      main.style.boxSizing = "border-box";
      main.style.fontSize = "14px";
      main.style.lineHeight = "1.6";

      // Garante que imagens tenham tamanho apropriado
      document.querySelectorAll("img").forEach((img) => {
        img.style.maxWidth = "100%";
        img.style.height = "auto";
        img.style.display = "block";
        img.style.margin = "10px 0";
        img.style.pageBreakInside = "avoid";
      });

      // Melhora tabelas
      document.querySelectorAll("table").forEach((table) => {
        table.style.width = "100%";
        table.style.borderCollapse = "collapse";
        table.style.margin = "20px 0";
        table.style.pageBreakInside = "avoid";
      });

      document.querySelectorAll("th, td").forEach((cell) => {
        cell.style.padding = "10px";
        cell.style.border = "1px solid #ddd";
      });

      // Melhora parágrafos
      document.querySelectorAll("p, h1, h2, h3, h4, h5, h6").forEach((el) => {
        el.style.pageBreakInside = "avoid";
        el.style.margin = "10px 0";
      });
    });
    console.log("✅ Conteúdo preparado!\n");

    // 6. Ativa modo de impressão para renderizar melhor
    await page.emulateMedia({ media: "print" });
    await page.waitForTimeout(1000); // Aguarda re-render

    // 7. Gera o PDF
    const nomeArquivo = gerarNomePDF(titulo);
    const caminhoCompleto = path.join(process.cwd(), nomeArquivo);

    console.log("📄 Gerando PDF com alta qualidade...");
    console.log(`   ⏱️  Isto pode levar alguns segundos...\n`);

    await page.pdf({
      path: caminhoCompleto,
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
      timeout: 60000,
      margin: {
        top: "30px",
        bottom: "30px",
        left: "20px",
        right: "20px",
      },
      scale: 1.0,
      displayHeaderFooter: false,
    });

    // Verifica se o arquivo foi criado
    if (fs.existsSync(caminhoCompleto)) {
      const stats = fs.statSync(caminhoCompleto);
      const sizeMB = (stats.size / 1024 / 1024).toFixed(2);

      console.log("\n✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!");
      console.log(`💾 Arquivo salvo: ${nomeArquivo}`);
      console.log(`📏 Tamanho: ${sizeMB} MB`);
      console.log(`📍 Localização: ${caminhoCompleto}\n`);
    } else {
      console.log("\n⚠️  Arquivo PDF não foi criado!");
    }
  } catch (err) {
    console.error("\n❌ ERRO NA EXTRAÇÃO:");
    console.error(`   ${err.message}\n`);

    if (err.message.includes("ECONNREFUSED")) {
      console.log("💡 DICA: Nenhum navegador em modo debug foi encontrado!");
      console.log("   Feche o navegador e abra novamente com:");
      console.log("   - Chrome/Edge: --remote-debugging-port=9222");
      console.log(
        "   - Firefox: --remote-debugging-protocol -start-debugger-server 9223\n"
      );
    }

    console.log("🔧 Dicas para resolver:");
    console.log("   1. Aguarde o site carregar completamente antes de rodar");
    console.log("   2. Se for site com login, faça login antes de rodar o script");
    console.log("   3. Feche popups/modals que estejam abertos");
    console.log("   4. Tente novamente com o navegador em modo debug\n");
  } finally {
    if (browser) {
      await browser.close();
      console.log("👋 Desconectado do navegador. Você pode continuar navegando!");
    }
  }
})();

// ==================== FUNÇÕES AUXILIARES ====================
function gerarNomePDF(titulo) {
  const nomeLimpo = titulo
    .replace(/[<>:"|?*\/\\]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 50);

  const timestamp = new Date().toISOString().slice(0, 10);
  return `${nomeLimpo}_${timestamp}.pdf`;
}

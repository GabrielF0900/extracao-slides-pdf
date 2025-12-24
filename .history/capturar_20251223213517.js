const { chromium, firefox, webkit } = require("playwright");
const fs = require("fs");
const path = require("path");

// ==================== CONFIGURAÇÕES ====================
const PORTS = [9222, 9223, 9224];
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
        // Continua tentando o próximo navegador
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

    // 3. Aguarda carregamento completo
    console.log("⏳ Aguardando carregamento completo da página...");
    await page.waitForLoadState("networkidle");
    console.log("✅ Página carregada!\n");

    // 4. Limpa e prepara o conteúdo
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
      ];

      seletoresLixo.forEach((seletor) => {
        document.querySelectorAll(seletor).forEach((el) => {
          if (el.tagName !== "SCRIPT" && el.tagName !== "STYLE") {
            el.remove();
          }
        });
      });

      // Prepara o conteúdo principal
      const main =
        document.querySelector('main, article, [role="main"]') || document.body;
      main.style.margin = "0";
      main.style.padding = "20px";
      main.style.width = "100%";
      main.style.boxSizing = "border-box";

      // Garante que imagens tenham tamanho apropriado
      document.querySelectorAll("img").forEach((img) => {
        img.style.maxWidth = "100%";
        img.style.height = "auto";
        img.style.display = "block";
        img.style.margin = "10px 0";
      });

      // Melhora tabelas
      document.querySelectorAll("table").forEach((table) => {
        table.style.width = "100%";
        table.style.borderCollapse = "collapse";
        table.style.margin = "20px 0";
      });

      document.querySelectorAll("th, td").forEach((cell) => {
        cell.style.padding = "10px";
        cell.style.border = "1px solid #ddd";
      });
    });
    console.log("✅ Conteúdo preparado!\n");

    // 5. Ativa modo de impressão para renderizar melhor
    await page.emulateMedia({ media: "print" });

    // 6. Gera o PDF
    const nomeArquivo = gerarNomePDF(titulo);
    const caminhoCompleto = path.join(process.cwd(), nomeArquivo);

    console.log("📄 Gerando PDF...");
    await page.pdf({
      path: caminhoCompleto,
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
      margin: {
        top: "30px",
        bottom: "30px",
        left: "20px",
        right: "20px",
      },
      scale: 1.0,
      displayHeaderFooter: true,
      headerTemplate:
        '<div style="font-size: 12px; width: 100%; text-align: center;"></div>',
      footerTemplate:
        '<div style="font-size: 12px; width: 100%; text-align: center;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    });

    console.log("\n✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!");
    console.log(`💾 Arquivo salvo: ${nomeArquivo}`);
    console.log(`📍 Localização: ${caminhoCompleto}\n`);
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
  } finally {
    // Fecha a conexão (sem fechar o navegador)
    if (browser) {
      await browser.close();
      console.log(
        "👋 Desconectado do navegador. Você pode continuar navegando!"
      );
    }
  }
})();

// ==================== FUNÇÕES AUXILIARES ====================
function gerarNomePDF(titulo) {
  // Remove caracteres inválidos e gera nome limpo
  const nomeLimpo = titulo
    .replace(/[<>:"|?*]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 50);

  const timestamp = new Date().toISOString().slice(0, 10);
  return `${nomeLimpo}_${timestamp}.pdf`;
}

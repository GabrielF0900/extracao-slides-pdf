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

    // 5. Aguarda iframes e conteúdo dinâmico
    console.log("🔍 Processando iframes e conteúdo dinâmico...");
    await page.waitForTimeout(2000);
    const frames = page.frames();
    console.log(`   📌 Encontrado ${frames.length} frame(s)`);
    for (const frame of frames) {
      try {
        await frame.waitForLoadState("networkidle").catch(() => {});
      } catch (e) {}
    }
    console.log("✅ Conteúdo processado!\n");

    // 6. Obtém informações
    const titulo = await page.title();
    console.log(`📑 Título: "${titulo}"`);
    console.log(`🌐 URL: ${page.url()}\n`);

    // 7. Prepara o conteúdo para PDF
    console.log("🧹 Preparando conteúdo para PDF...");
    await page.evaluate(() => {
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
        ".navigation-bar",
        '[role="navigation"]',
        '[role="complementary"]',
        ".cookies-banner",
        ".popup",
        ".modal-overlay",
        ".ad",
        ".advertisement",
        "[class*='botao-']",
        "[class*='button-']",
        "[class*='nav-']",
        ".menu",
        "[id*='cookie']",
      ];

      seletoresLixo.forEach((seletor) => {
        try {
          document.querySelectorAll(seletor).forEach((el) => {
            el.remove();
          });
        } catch (e) {}
      });

      // Encontra o melhor container de conteúdo
      let main = document.querySelector(
        "main, article, [role='main'], .main, #main, .content, #content, .page-content, .slide-content, .material, [class*='lesson'], [class*='lesson-content']"
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

      // Ajusta imagens para aparecerem bem no PDF
      document.querySelectorAll("img").forEach((img) => {
        img.style.maxWidth = "100%";
        img.style.height = "auto";
        img.style.display = "block";
        img.style.margin = "15px 0";
        img.style.pageBreakInside = "avoid";
        img.style.borderRadius = "0";

        // Tenta forçar o carregamento da imagem
        if (img.dataset.src) {
          img.src = img.dataset.src;
        }
      });

      // Ajusta tabelas
      document.querySelectorAll("table").forEach((table) => {
        table.style.width = "100%";
        table.style.borderCollapse = "collapse";
        table.style.margin = "20px 0";
        table.style.pageBreakInside = "avoid";
      });

      document.querySelectorAll("th, td").forEach((cell) => {
        cell.style.padding = "12px";
        cell.style.border = "1px solid #ccc";
        cell.style.textAlign = "left";
      });

      // Ajusta títulos e parágrafos
      document
        .querySelectorAll("p, h1, h2, h3, h4, h5, h6, li")
        .forEach((el) => {
          el.style.pageBreakInside = "avoid";
          el.style.margin = "10px 0";
        });

      // Garante que divs com conteúdo fiquem visíveis
      document.querySelectorAll("div, section").forEach((el) => {
        el.style.pageBreakInside = "avoid";
      });
    });
    console.log("✅ Conteúdo preparado!\n");

    // 8. Ativa modo de impressão para renderizar melhor
    await page.emulateMedia({ media: "print" });
    await page.waitForTimeout(1000);

    // 9. Gera o PDF
    const nomeArquivo = gerarNomePDF(titulo);
    const caminhoCompleto = path.join(process.cwd(), nomeArquivo);

    console.log("📄 Gerando PDF com alta qualidade...");
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
        `📏 Tamanho: ${sizeMB > 0 ? sizeMB + " MB" : sizeKB + " KB"}`
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
    console.log("   3. Feche popups/modals que estejam abertos");
    console.log("   4. Tente novamente\n");
  } finally {
    if (browser) {
      await browser.close();
    }
    rl.close();
  }
})();

function gerarNomePDF(titulo) {
  const nomeLimpo = titulo
    .replace(/[<>:"|?*\/\\]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 50);

  const timestamp = new Date().toISOString().slice(0, 10);
  return `${nomeLimpo}_${timestamp}.pdf`;
}

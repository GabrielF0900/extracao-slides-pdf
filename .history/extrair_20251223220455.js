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
    console.log("   📄 EXTRATOR PARA PDF 📄");
    console.log("=".repeat(60) + "\n");

    console.log("Qual navegador?\n");
    console.log("1 - Chrome");
    console.log("2 - Firefox");
    console.log("3 - Safari\n");

    const opcao = await pergunta("Digite (1-3): ");

    let browserType, browserName;

    if (opcao === "1") {
      browserType = chromium;
      browserName = "Chrome";
    } else if (opcao === "2") {
      browserType = firefox;
      browserName = "Firefox";
    } else if (opcao === "3") {
      browserType = webkit;
      browserName = "Safari";
    } else {
      console.log("❌ Inválido!");
      rl.close();
      return;
    }

    console.log(`\n🚀 Abrindo...\n`);
    browser = await browserType.launch({ headless: false });
    page = await browser.newPage();

    await page.goto("about:blank");
    console.log(`✅ ${browserName} aberto!\n`);

    const url = await pergunta("URL (ou ENTER): ");
    console.log();

    if (url.trim()) {
      console.log(`🌐 Carregando...\n`);
      try {
        await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
      } catch (e) {
        console.log("⚠️  Continuando...\n");
      }
    } else {
      console.log("👉 Navegue manualmente\n");
      await pergunta("ENTER quando carregar: ");
      console.log();
    }

    console.log("⏳ Aguardando 3s...");
    await page.waitForTimeout(3000);
    console.log("✅ Página carregada!\n");

    // Aguarda confirmação do usuário para extrair
    console.log("=" + "=".repeat(58) + "=");
    await pergunta("\n🎯 Pressione ENTER para EXTRAIR e gerar PDF: ");
    console.log();

    const titulo = await page.title();
    const nomeArquivo = `${titulo.substring(0, 30)}_${new Date()
      .toISOString()
      .slice(0, 10)}.pdf`;
    const caminhoCompleto = path.join(process.cwd(), nomeArquivo);

    console.log("📄 Gerando PDF...");
    await page.pdf({
      path: caminhoCompleto,
      format: "A4",
      printBackground: true,
      margin: { top: 20, bottom: 20, left: 20, right: 20 },
    });

    if (fs.existsSync(caminhoCompleto)) {
      const stats = fs.statSync(caminhoCompleto);
      const sizeMB = (stats.size / 1024 / 1024).toFixed(2);

      console.log("\n✅ PRONTO!\n");
      console.log(`📄 ${nomeArquivo}`);
      console.log(`📏 ${sizeMB} MB`);
      console.log(`📍 ${caminhoCompleto}\n`);

      const abrir = await pergunta("Abrir? (s/n): ");
      if (abrir.toLowerCase() === "s") {
        const { exec } = require("child_process");
        exec(`start "" "${caminhoCompleto}"`);
      }
    }
  } catch (err) {
    console.error("\n❌ ERRO: " + err.message + "\n");
  } finally {
    if (browser) await browser.close();
    rl.close();
  }
})();

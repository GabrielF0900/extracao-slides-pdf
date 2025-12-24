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
    console.log("   📄 EXTRATOR COMPLETO PARA PDF 📄");
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

    // Detecta número de páginas
    console.log("🔍 Detectando páginas...");
    let totalPaginas = await detectarPaginas(page);
    console.log(`📊 Total detectado: ${totalPaginas} página(s)\n`);

    // Coleta conteúdo de todas as páginas
    console.log("📥 Coletando conteúdo...\n");
    const paginas = [];

    for (let i = 1; i <= totalPaginas; i++) {
      console.log(`   ⏳ Página ${i}/${totalPaginas}...`);

      // Aguarda renderização
      await page.waitForTimeout(1500);

      // Extrai conteúdo (HTML) da página
      const conteudo = await page.evaluate(() => {
        // Remove elementos desnecessários
        const elementos = document.querySelectorAll(
          "header, footer, nav, [class*='nav'], [class*='menu'], [class*='button-next'], [class*='button-prev'], .ads, [id*='cookie']"
        );
        elementos.forEach((el) => {
          el.style.display = "none";
        });

        // Encontra container principal
        const container =
          document.querySelector(
            "main, article, [role='main'], .content, .page, [class*='slide'], [class*='lesson']"
          ) || document.body;

        // Extrai HTML limpo
        return container.innerHTML;
      });

      if (conteudo && conteudo.trim().length > 0) {
        paginas.push(conteudo);
        console.log(`   ✅ Coletada`);
      }

      // Clica próximo
      if (i < totalPaginas) {
        const clicou = await clicarProximo(page);
        if (!clicou) {
          console.log(`   ⚠️  Não consegui avançar. Parando.`);
          totalPaginas = i;
          break;
        }
      }
    }

    console.log();

    // Gera HTML combinado
    console.log("🎨 Montando PDF...");

    const htmlCompleto = gerarHTML(paginas);

    const titulo = await page.title();
    const nomeArquivo = `${titulo.substring(0, 30)}_${new Date()
      .toISOString()
      .slice(0, 10)}.pdf`;
    const caminhoCompleto = path.join(process.cwd(), nomeArquivo);

    // Navega para o HTML gerado
    await page.goto(`data:text/html,${encodeURIComponent(htmlCompleto)}`, {
      waitUntil: "domcontentloaded",
    });

    await page.waitForTimeout(2000);

    // Gera PDF
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
      console.log(`📊 Páginas: ${paginas.length}`);
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

// ==================== FUNÇÕES ====================

async function detectarPaginas(page) {
  try {
    const num = await page.evaluate(() => {
      const texto = document.body.innerText;

      // "página X de Y"
      let match = texto.match(/página\s+(\d+)\s+d[ae]\s+(\d+)/i);
      if (match) return parseInt(match[2]);

      // "page X of Y"
      match = texto.match(/page\s+(\d+)\s+of\s+(\d+)/i);
      if (match) return parseInt(match[2]);

      // "X / Y"
      match = texto.match(/(\d+)\s*\/\s*(\d+)/);
      if (match) {
        const n = parseInt(match[2]);
        if (n > 0 && n < 200) return n;
      }

      return null;
    });

    return num || 1; // Padrão: 1 página
  } catch (err) {
    return 1;
  }
}

async function clicarProximo(page) {
  try {
    const clicou = await page.evaluate(() => {
      const botoes = Array.from(
        document.querySelectorAll("button, a, [role='button']")
      );
      const botao = botoes.find((b) => {
        const texto = b.innerText.toLowerCase().trim();
        return (
          texto.includes("próximo") ||
          texto.includes("next") ||
          texto.includes("avançar") ||
          texto === ">" ||
          texto === "→"
        );
      });

      if (botao && botao.offsetHeight > 0) {
        botao.click();
        return true;
      }
      return false;
    });

    return clicou;
  } catch (err) {
    return false;
  }
}

function gerarHTML(paginas) {
  return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            background: white;
        }
        .pagina { 
            page-break-after: always; 
            padding: 30px;
            min-height: 100vh;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            background: white;
        }
        .pagina:last-child {
            page-break-after: avoid;
        }
        img { 
            max-width: 100%; 
            height: auto; 
            margin: 15px 0;
            display: block;
            border-radius: 4px;
        }
        p { margin: 12px 0; }
        h1 { margin: 25px 0 15px 0; font-size: 28px; }
        h2 { margin: 20px 0 12px 0; font-size: 22px; }
        h3 { margin: 18px 0 10px 0; font-size: 18px; }
        h4, h5, h6 { margin: 15px 0 8px 0; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            border: 1px solid #ddd;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        ul, ol { margin: 12px 0 12px 20px; }
        li { margin: 6px 0; }
        pre {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 12px 0;
        }
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    ${paginas
      .map(
        (html) => `
    <div class="pagina">
        ${html}
    </div>
    `
      )
      .join("")}
</body>
</html>
  `;
}

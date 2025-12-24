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
    console.log("   📄 EXTRATOR SIMPLES - TEXTOS E IMAGENS 📄");
    console.log("=".repeat(60) + "\n");

    // 1. Pergunta qual navegador
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

    browser = await browserType.launch({ headless: false });
    page = await browser.newPage();
    page.setViewportSize({ width: 1920, height: 1080 });

    await page.goto("about:blank");

    console.log(`✅ ${browserName} aberto!\n`);

    // 2. URL
    console.log("=" + "=".repeat(58) + "=");
    const url = await pergunta(
      "\n📌 Digite a URL ou ENTER se já está na página: "
    );
    console.log();

    if (url.trim()) {
      console.log(`🌐 Navegando...\n`);
      try {
        await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
      } catch (err) {
        console.log("⚠️  Continuando mesmo assim...\n");
      }
    } else {
      console.log("📌 Navegue manualmente");
      await pergunta("ENTER quando estiver pronto: ");
      console.log();
    }

    // 3. Aguarda
    console.log("⏳ Carregando...");
    await page.waitForTimeout(2000);
    console.log("✅ Pronto!\n");

    // 4. Detecta número de páginas
    console.log("🔍 Detectando páginas...");
    let numPaginas = await detectarNumPaginas(page);
    console.log(`📊 Páginas detectadas: ${numPaginas}\n`);

    // 5. Coleta conteúdo de cada página
    console.log("📥 Coletando conteúdo...\n");
    const paginas = [];

    for (let i = 1; i <= numPaginas; i++) {
      console.log(`   ⏳ Página ${i}/${numPaginas}...`);

      // Extrai apenas textos e imagens
      const conteudo = await page.evaluate(() => {
        // Encontra o container principal de conteúdo
        const container =
          document.querySelector(
            "[class*='slide'], [class*='page'], [class*='content'], [class*='lesson'], main, article"
          ) || document.body;

        // Extrai HTML limpo
        let html = container.innerHTML;

        // Remove scripts e styles
        html = html.replace(
          /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
          ""
        );
        html = html.replace(
          /<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi,
          ""
        );

        // Remove elementos desnecessários
        const temp = document.createElement("div");
        temp.innerHTML = html;

        const remover = [
          "[class*='nav']",
          "[class*='menu']",
          "[class*='button-next']",
          "[class*='button-prev']",
          "header",
          "footer",
          "nav",
          "aside",
        ];

        remover.forEach((sel) => {
          temp.querySelectorAll(sel).forEach((el) => {
            el.remove();
          });
        });

        return temp.innerHTML;
      });

      if (conteudo && conteudo.trim().length > 0) {
        paginas.push(conteudo);
      }

      // Clica próximo
      if (i < numPaginas) {
        const clicou = await clicarProximo(page);
        if (clicou) {
          await page.waitForTimeout(1500);
        } else {
          console.log(`   ⚠️  Não consegui navegar. Parando aqui.`);
          numPaginas = i;
          break;
        }
      }

      console.log(`   ✅ Coletada`);
    }

    console.log();

    // 6. Monta HTML para PDF
    console.log("🎨 Montando PDF...");

    const htmlFinal = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; }
        .pagina { 
            page-break-after: always; 
            padding: 30px;
            min-height: 100vh;
            font-size: 14px;
            line-height: 1.6;
        }
        img { 
            max-width: 100%; 
            height: auto; 
            margin: 15px 0; 
            display: block;
        }
        p { margin: 10px 0; }
        h1, h2, h3, h4, h5, h6 { margin: 15px 0 10px 0; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    </style>
</head>
<body>
    ${paginas.map((html) => `<div class="pagina">${html}</div>`).join("")}
</body>
</html>
    `;

    // 7. Gera PDF
    const titulo = await page.title();
    const nomeArquivo = gerarNomePDF(titulo);
    const caminhoCompleto = path.join(process.cwd(), nomeArquivo);

    console.log(`📄 Gerando PDF (${paginas.length} páginas)...`);
    await page.goto(`data:text/html,${encodeURIComponent(htmlFinal)}`);
    await page.waitForTimeout(2000);

    await page.pdf({
      path: caminhoCompleto,
      format: "A4",
      printBackground: true,
      margin: { top: 20, bottom: 20, left: 20, right: 20 },
      displayHeaderFooter: false,
    });

    // 8. Resultado
    if (fs.existsSync(caminhoCompleto)) {
      const stats = fs.statSync(caminhoCompleto);
      const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
      const sizeKB = (stats.size / 1024).toFixed(2);

      console.log("\n✅ SUCESSO!\n");
      console.log(`💾 Arquivo: ${nomeArquivo}`);
      console.log(`📊 Páginas: ${paginas.length}`);
      console.log(
        `📏 Tamanho: ${sizeMB > 0.1 ? sizeMB + " MB" : sizeKB + " KB"}`
      );
      console.log(`📍 Local: ${caminhoCompleto}\n`);

      const abrir = await pergunta("Abrir PDF? (s/n): ");
      if (abrir.toLowerCase() === "s" || abrir.toLowerCase() === "y") {
        const { exec } = require("child_process");
        exec(`start "" "${caminhoCompleto}"`);
      }
    } else {
      console.log("❌ Erro ao criar PDF\n");
    }
  } catch (err) {
    console.error("\n❌ ERRO:\n");
    console.error(`${err.message}\n`);
  } finally {
    if (browser) {
      await browser.close();
    }
    rl.close();
  }
})();

// ==================== FUNÇÕES ====================

async function detectarNumPaginas(page) {
  try {
    const num = await page.evaluate(() => {
      // Procura por "X de Y" ou "X / Y"
      const texto = document.body.innerText;

      // Padrão: "página X de Y"
      let match = texto.match(/página\s+(\d+)\s+d[ae]\s+(\d+)/i);
      if (match) return parseInt(match[2]);

      // Padrão: "X / Y"
      match = texto.match(/(\d+)\s*\/\s*(\d+)/);
      if (match) {
        const num1 = parseInt(match[1]);
        const num2 = parseInt(match[2]);
        return num2 > num1 ? num2 : 10;
      }

      // Padrão: "page X of Y"
      match = texto.match(/page\s+(\d+)\s+of\s+(\d+)/i);
      if (match) return parseInt(match[2]);

      // Procura em atributos de dados
      const elements = document.querySelectorAll(
        "[data-page-count], [data-total], [data-pages]"
      );
      for (let el of elements) {
        const num = parseInt(
          el.getAttribute("data-page-count") ||
            el.getAttribute("data-total") ||
            el.getAttribute("data-pages")
        );
        if (num > 0) return num;
      }

      return null;
    });

    return num || 10; // Padrão: 10 páginas se não detectar
  } catch (err) {
    return 10; // Padrão
  }
}

async function clicarProximo(page) {
  try {
    const clicou = await page.evaluate(() => {
      // Procura botão próximo/next/avançar
      const botoes = Array.from(
        document.querySelectorAll("button, a, [role='button']")
      );
      const botao = botoes.find((b) => {
        const texto = b.innerText.toLowerCase();
        return (
          texto.includes("próximo") ||
          texto.includes("next") ||
          texto.includes("avançar") ||
          texto.includes("forward") ||
          texto.includes("continue")
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

function gerarNomePDF(titulo) {
  const nomeLimpo = titulo
    .replace(/[<>:"|?*\/\\]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 50);

  const timestamp = new Date().toISOString().slice(0, 10);
  return `${nomeLimpo}_${timestamp}.pdf`;
}

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
      headless: false, // Abre com interface visual
    });

    // Abre uma página em branco
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

    // 5. Obtém informações
    const titulo = await page.title();
    console.log(`📑 Título: "${titulo}"`);
    console.log(`🌐 URL: ${page.url()}\n`);

    // 6. Detecta quantas páginas tem
    console.log("🔍 Detectando quantidade de páginas...");
    let totalPaginas = await detectarTotalPaginas(page);
    console.log(`📊 Total de páginas detectadas: ${totalPaginas}\n`);

    // 7. Coleta conteúdo de TODAS as páginas
    let conteudoCompleto = [];
    let paginaAtual = 1;

    console.log("📥 Coletando conteúdo de todas as páginas...\n");

    while (paginaAtual <= totalPaginas) {
      console.log(`⏳ Processando página ${paginaAtual}/${totalPaginas}...`);

      // Aguarda iframes carregarem
      await page.waitForTimeout(1000);
      const frames = page.frames();
      for (const frame of frames) {
        try {
          await frame.waitForLoadState("networkidle").catch(() => {});
        } catch (e) {}
      }

      // Extrai conteúdo da página
      const conteudo = await extrairConteudoPagina(page);
      conteudoCompleto.push(conteudo);

      // Se não for última página, clica no botão próximo
      if (paginaAtual < totalPaginas) {
        const proximoClicado = await clicarProximo(page);
        if (!proximoClicado) {
          console.log(
            `   ⚠️  Não consegui encontrar botão próximo. Parando em página ${paginaAtual}.`
          );
          totalPaginas = paginaAtual;
          break;
        }

        // Aguarda página carregar
        await Promise.race([
          page.waitForLoadState("networkidle").catch(() => {}),
          new Promise((resolve) => setTimeout(resolve, 3000)),
        ]);
      }

      console.log(`   ✅ Página ${paginaAtual} coletada!\n`);
      paginaAtual++;
    }

    // 8. Combina todo o conteúdo em uma página
    console.log("🧹 Preparando conteúdo combinado para PDF...\n");
    await page.evaluate((conteudos) => {
      // Cria um container para o conteúdo combinado
      const container = document.createElement("div");
      container.id = "pdf-container-completo";
      container.style.margin = "0";
      container.style.padding = "20px";
      container.style.width = "100%";
      container.style.boxSizing = "border-box";
      container.style.fontSize = "14px";
      container.style.lineHeight = "1.6";

      // Adiciona cada página com quebra de página
      conteudos.forEach((conteudo, index) => {
        const paginaDiv = document.createElement("div");
        paginaDiv.style.pageBreakAfter = "always";
        paginaDiv.style.paddingBottom = "20px";
        paginaDiv.innerHTML = conteudo;
        container.appendChild(paginaDiv);
      });

      // Substitui o body pelo container
      document.body.innerHTML = "";
      document.body.appendChild(container);

      // Remove elementos desnecessários
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
        '[role="navigation"]',
        '[role="complementary"]',
        ".cookies-banner",
        ".popup",
        ".modal-overlay",
        ".ad",
        ".advertisement",
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

      // Ajusta imagens
      document.querySelectorAll("img").forEach((img) => {
        img.style.maxWidth = "100%";
        img.style.height = "auto";
        img.style.display = "block";
        img.style.margin = "10px 0";
        img.style.pageBreakInside = "avoid";
      });

      // Ajusta tabelas
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

      // Ajusta textos
      document.querySelectorAll("p, h1, h2, h3, h4, h5, h6").forEach((el) => {
        el.style.pageBreakInside = "avoid";
        el.style.margin = "10px 0";
      });
    }, conteudoCompleto);

    // 9. Ativa modo de impressão
    await page.emulateMedia({ media: "print" });
    await page.waitForTimeout(1000);

    // 10. Gera PDF com todas as páginas
    const nomeArquivo = gerarNomePDF(titulo);
    const caminhoCompleto = path.join(process.cwd(), nomeArquivo);

    console.log("📄 Gerando PDF com alta qualidade...");
    console.log(`   📊 Páginas: ${totalPaginas}`);
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

    // Verifica
    if (fs.existsSync(caminhoCompleto)) {
      const stats = fs.statSync(caminhoCompleto);
      const sizeMB = (stats.size / 1024 / 1024).toFixed(2);

      console.log("✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!\n");
      console.log(`💾 Arquivo: ${nomeArquivo}`);
      console.log(`📊 Páginas extraídas: ${totalPaginas}`);
      console.log(`📏 Tamanho: ${sizeMB} MB`);
      console.log(`📍 Caminho: ${caminhoCompleto}\n`);

      // Pergunta se quer abrir
      const abrir = await pergunta("Deseja abrir o PDF? (s/n): ");
      if (abrir.toLowerCase() === "s") {
        const { exec } = require("child_process");
        exec(`start "" "${caminhoCompleto}"`);
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
    console.log("   3. Feche popups/banners que estejam abertos");
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

// ==================== FUNÇÕES AUXILIARES ====================

async function detectarTotalPaginas(page) {
  // Tenta encontrar indicadores de paginação
  const indicadores = await page.evaluate(() => {
    // Procura por números de página visíveis
    const possiveisIndicadores = [
      // Texto com "página X de Y"
      () => {
        const text = document.body.innerText;
        const match = text.match(/página\s+(\d+)\s+d[ae]\s+(\d+)/i);
        if (match) return parseInt(match[2]);

        const match2 = text.match(/page\s+(\d+)\s+of\s+(\d+)/i);
        if (match2) return parseInt(match2[2]);

        return null;
      },

      // Contador de slides/páginas em elementos
      () => {
        const elementos = document.querySelectorAll(
          "[data-page-count], [data-total-pages], [data-slides], [class*='total']"
        );
        for (let el of elementos) {
          const text =
            el.getAttribute("data-page-count") ||
            el.getAttribute("data-total-pages") ||
            el.getAttribute("data-slides") ||
            el.innerText;
          const num = parseInt(text);
          if (num > 0) return num;
        }
        return null;
      },

      // Conta botões de navegação
      () => {
        const botoes = document.querySelectorAll(
          "button[aria-label*='next'], button[aria-label*='próximo'], .next-button, [class*='next']"
        );
        if (botoes.length > 0) return 999; // Retorna um número alto se houver botões
        return null;
      },
    ];

    for (let fn of possiveisIndicadores) {
      const resultado = fn();
      if (resultado) return resultado;
    }

    return null;
  });

  // Se não encontrou, assume múltiplas páginas
  return indicadores || 20; // Padrão: 20 páginas
}

async function extrairConteudoPagina(page) {
  // Extrai apenas o conteúdo principal, sem elementos desnecessários
  const conteudo = await page.evaluate(() => {
    // Procura pelo elemento principal de conteúdo
    let main = document.querySelector(
      "main, article, [role='main'], .main, #main, .content, #content, .page-content, .slide-content"
    );

    if (!main) {
      main = document.body;
    }

    // Clona para não modificar o original
    const clone = main.cloneNode(true);

    // Remove elementos desnecessários da cópia
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
      "[class*='button-next']",
      "[class*='button-prev']",
      "[class*='pagination']",
    ];

    seletoresLixo.forEach((seletor) => {
      clone.querySelectorAll(seletor).forEach((el) => {
        el.remove();
      });
    });

    // Garante que imagens e tabelas estejam formatadas
    clone.querySelectorAll("img").forEach((img) => {
      img.style.maxWidth = "100%";
      img.style.height = "auto";
      img.style.display = "block";
      img.style.margin = "10px 0";
    });

    clone.querySelectorAll("table").forEach((table) => {
      table.style.width = "100%";
      table.style.borderCollapse = "collapse";
      table.style.margin = "20px 0";
    });

    clone.querySelectorAll("th, td").forEach((cell) => {
      cell.style.padding = "10px";
      cell.style.border = "1px solid #ddd";
    });

    return clone.innerHTML;
  });

  return conteudo;
}

async function clicarProximo(page) {
  // Tenta clicar em botão próximo/next/avançar
  const seletoresProximo = [
    // Atributos aria-label
    'button[aria-label*="próximo"], button[aria-label*="next"], button[aria-label*="forward"]',

    // Classes comuns
    ".next-button, .btn-next, .button-next, .nav-next, [class*='next-btn']",

    // IDs comuns
    "#next, #btn-next, #next-page, #advance",

    // Text content
    'button:has-text("Próximo"), button:has-text("Next"), button:has-text("Avançar")',

    // Role = button
    'button[role="button"]:contains("Próximo")',

    // Qualquer botão com ícone de seta para direita
    'button svg[class*="arrow-right"]',
    'a[class*="next"], a[class*="forward"]',
  ];

  for (const seletor of seletoresProximo) {
    try {
      const elemento = await page.$(seletor);
      if (elemento) {
        await elemento.click();
        return true;
      }
    } catch (e) {}
  }

  // Tenta alternativa: procura por qualquer botão com texto "próximo" em qualquer lugar
  try {
    const clicou = await page.evaluate(() => {
      const botoes = Array.from(
        document.querySelectorAll("button, a, [role='button']")
      );
      const botao = botoes.find((b) => {
        const texto = b.innerText.toLowerCase();
        return (
          texto.includes("próximo") ||
          texto.includes("next") ||
          texto.includes("avançar") ||
          texto.includes("forward")
        );
      });

      if (botao) {
        botao.click();
        return true;
      }
      return false;
    });

    return clicou;
  } catch (e) {
    return false;
  }
}

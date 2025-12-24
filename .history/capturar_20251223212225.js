const { chromium } = require('playwright');
const readline = require('readline');

// Função para pausar e esperar seu comando no terminal
const waitForKey = () => {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question('Navegue até a aula e pressione ENTER para gerar o PDF...', () => {
    rl.close();
    resolve();
  }));
};

(async () => {
  // 1. Lança o navegador visível para você logar
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('--- AUTOMAÇÃO ESCOLA DA NUVEM ---');
  await page.goto('https://escoladanuvem.org.br/'); // Altere para a URL de login se for diferente

  // 2. Espera você fazer o login e chegar na aula
  await waitForKey();

  // 3. MAPEAMENTO E LIMPEZA (O "pulo do gato")
  // Aqui removemos elementos que poluem o PDF (menus, rodapés, botões)
  // IMPORTANTE: Ajuste os seletores (ex: .sidebar, header) conforme o site
  await page.evaluate(() => {
    const seletoresParaRemover = [
      'header', 'footer', 'nav', '.sidebar', '.navigation-buttons', '.menu-lateral'
    ];
    seletoresParaRemover.forEach(selector => {
      const element = document.querySelector(selector);
      if (element) element.style.display = 'none';
    });

    // Garante que o container principal ocupe 100% da largura para o PDF
    const mainContent = document.querySelector('main') || document.body;
    mainContent.style.margin = '0';
    mainContent.style.padding = '20px';
  });

  // 4. GERAR O PDF
  const tituloAula = await page.title();
  const fileName = `${tituloAula.replace(/[/\\?%*:|"<>]/g, '-')}.pdf`;

  await page.pdf({
    path: fileName,
    format: 'A4',
    printBackground: true, // Garante que as cores e imagens de fundo apareçam
    margin: { top: '20px', right: '20px', bottom: '20px', left: '20px' }
  });

  console.log(`✅ Sucesso! Material salvo como: ${fileName}`);

  // Pergunta se quer fechar ou capturar outra
  console.log('Deseja capturar outra aula? (Navegue e aperte ENTER ou feche o terminal)');
  await waitForKey();

  await browser.close();
})();
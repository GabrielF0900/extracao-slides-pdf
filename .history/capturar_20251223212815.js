const { chromium } = require('playwright');
const readline = require('readline');

/**
 * Função para pausar a execução e esperar o usuário navegar até a aula.
 */
const esperarComando = (mensagem) => {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(mensagem, () => {
    rl.close();
    resolve();
  }));
};

(async () => {
  console.log('🚀 Iniciando automação de extração...');

  // 1. Lança o navegador (visível para que você possa fazer o login)
  const browser = await chromium.launch({ headless: false });

  // 2. Cria o contexto ignorando erros de HTTPS/Certificado
  const context = await browser.newContext({
    ignoreHTTPSErrors: true, // CORREÇÃO DO ERRO ANTERIOR
    viewport: { width: 1280, height: 800 }
  });

  const page = await context.newPage();

  // 3. Navega para a página inicial
  try {
    await page.goto('https://www.escoladanuvem.org.br/', { waitUntil: 'networkidle' });
  } catch (err) {
    console.log('⚠️ Aviso: O site demorou a responder, mas vamos continuar...');
  }

  console.log('\n--- PASSO A PASSO ---');
  console.log('1. Faça o login manualmente no navegador que abriu.');
  console.log('2. Navegue até a aula que você deseja salvar.');
  console.log('3. Quando a aula estiver carregada na tela, volte aqui e aperte ENTER.');

  while (true) {
    await esperarComando('\n👉 Pressione ENTER para capturar a página atual ou CTRL+C para sair...');

    console.log('⏳ Mapeando conteúdo e gerando PDF...');

    // 4. Limpeza do DOM (Remove elementos que atrapalham o PDF)
    // DICA: Adicione aqui as classes ou IDs que você quer esconder
    await page.evaluate(() => {
      const seletoresParaEsconder = [
        'header', 'footer', '.sidebar', 'nav', 
        '.menu', '.botoes-navegacao', '#barra-lateral'
      ];
      
      seletoresParaEsconder.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => el.style.display = 'none');
      });

      // Expande o conteúdo principal para ocupar a tela toda no PDF
      const main = document.querySelector('main') || document.body;
      if (main) {
        main.style.width = '100%';
        main.style.margin = '0';
        main.style.padding = '10px';
      }
    });

    // 5. Emula o modo de impressão (carrega o CSS otimizado para PDF)
    await page.emulateMedia({ media: 'print' });

    // 6. Define o nome do arquivo baseado no título da página
    const tituloRaw = await page.title();
    const tituloLimpo = tituloRaw.replace(/[/\\?%*:|"<>]/g, '-').substring(0, 50);
    const nomeArquivo = `AWS_Aula_${tituloLimpo}_${Date.now()}.pdf`;

    // 7. Gera o PDF com imagens e fundo coloridos
    await page.pdf({
      path: nomeArquivo,
      format: 'A4',
      printBackground: true, // Mantém as cores e imagens
      margin: { top: '40px', bottom: '40px', left: '20px', right: '20px' },
      displayHeaderFooter: false
    });

    console.log(`✅ PDF gerado com sucesso: ${nomeArquivo}`);
    console.log('Navegue para a próxima aula no navegador e repita o processo.');
  }
})();
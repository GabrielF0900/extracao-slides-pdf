const { chromium } = require('playwright');

(async () => {
  try {
    console.log('🔗 Tentando conectar ao seu Chrome aberto...');

    // Conecta ao navegador que você abriu manualmente na porta 9222
    const browser = await chromium.connectOverCDP('http://localhost:9222');
    
    // Pega todas as abas abertas e foca na que você está visualizando (a ativa)
    const defaultContext = browser.contexts()[0];
    const pages = defaultContext.pages();
    const page = pages[0]; // Pega a primeira aba encontrada

    if (!page) {
      console.error('❌ Nenhuma aba aberta encontrada no Chrome.');
      return;
    }

    console.log(`📍 Aba encontrada: "${await page.title()}"`);
    console.log('⏳ Mapeando conteúdo e gerando PDF...');

    // --- LOGICA DE MAPEAMENTO E LIMPEZA ---
    await page.evaluate(() => {
      // Remove elementos de interface para o PDF ficar limpo
      const lixo = ['header', 'footer', '.sidebar', 'nav', 'aside', '.buttons'];
      lixo.forEach(s => {
        document.querySelectorAll(s).forEach(el => el.style.display = 'none');
      });

      // Garante que o conteúdo principal use o espaço todo
      const content = document.querySelector('main') || document.body;
      content.style.padding = '20px';
    });

    // Emula modo de impressão para capturar imagens e CSS corretamente
    await page.emulateMedia({ media: 'print' });

    const nomeArquivo = `Captura_AWS_${Date.now()}.pdf`;

    // Gera o PDF da página que VOCÊ escolheu
    await page.pdf({
      path: nomeArquivo,
      format: 'A4',
      printBackground: true,
      margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' }
    });

    console.log(`✅ Concluído! O arquivo "${nomeArquivo}" foi gerado.`);
    
    // Desconecta do navegador sem fechá-lo
    await browser.close();

  } catch (err) {
    console.error('❌ Erro ao conectar: Verifique se o Chrome foi aberto com a porta 9222.');
    console.error(err);
  }
})();
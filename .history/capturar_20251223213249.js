const { chromium } = require('playwright');

(async () => {
  try {
    console.log('🔍 Iniciando mapeamento da página ativa...');

    // 1. Conecta ao Edge que já está aberto na porta 9222
    const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
    
    // 2. Pega todas as abas e foca na última que você interagiu
    const context = browser.contexts()[0];
    const pages = context.pages();
    const page = pages[pages.length - 1]; 

    if (!page) {
      console.log('❌ Erro: Não encontrei nenhuma aba aberta no Edge.');
      return;
    }

    const titulo = await page.title();
    console.log(`📑 Mapeando conteúdo de: "${titulo}"`);

    // 3. O ALGORITMO DE MAPEAMENTO (Injetado na página)
    await page.evaluate(() => {
      // Remove elementos que atrapalham o PDF (ajuste os nomes se necessário)
      const seletoresLixo = [
        'header', 'footer', 'nav', 'aside', 
        '.sidebar', '.menu-lateral', '.navigation-bar', 
        '.botoes-proximo-anterior', '#barra-progresso'
      ];
      
      seletoresLixo.forEach(s => {
        document.querySelectorAll(s).forEach(el => el.style.display = 'none');
      });

      // Mapeia o container principal e remove margens desnecessárias
      const main = document.querySelector('main') || document.body;
      main.style.margin = '0';
      main.style.padding = '20px';
      main.style.width = '100%';
    });

    // 4. Garante que o modo de impressão seja ativado para o PDF ficar bonito
    await page.emulateMedia({ media: 'print' });

    // 5. Gera o PDF com o nome da aula
    const nomeArquivo = `AWS_Material_${Date.now()}.pdf`;
    
    await page.pdf({
      path: nomeArquivo,
      format: 'A4',
      printBackground: true, // Crucial para as fotos do material aparecerem
      margin: { top: '30px', bottom: '30px', left: '20px', right: '20px' }
    });

    console.log(`✅ MAPEAMENTO CONCLUÍDO!`);
    console.log(`💾 Arquivo salvo: ${nomeArquivo}`);
    
    // Desconecta o script para você continuar navegando
    await browser.close();

  } catch (err) {
    console.error('❌ Erro ao mapear: Verifique se você abriu o Edge pelo atalho .bat');
    console.error('Detalhe do erro:', err.message);
  }
})();
# 📘 Guia de Uso - Extração de Conteúdo para PDF

## 🚀 Como Usar (Qualquer Navegador)

### 1️⃣ **Abra seu navegador em Modo Debug**

#### Para **Chrome/Edge**:
```powershell
# Feche completamente o navegador primeiro
# Depois abra no terminal:
chrome --remote-debugging-port=9222

# ou para Edge:
msedge --remote-debugging-port=9222
```

#### Para **Firefox**:
```powershell
firefox --remote-debugging-protocol -start-debugger-server 9223
```

### 2️⃣ **Navegue até o site desejado**
- Abra qualquer URL no seu navegador
- Posicione-se no conteúdo que quer extrair

### 3️⃣ **Execute o script**
```powershell
# No terminal, na pasta do projeto
node capturar.js
```

## 📋 O que o Script Faz

✅ **Detecta automaticamente qual navegador está aberto**
- Chrome/Edge (porta 9222)
- Firefox (porta 9223)  
- Safari/Webkit (porta 9224)

✅ **Extrai o conteúdo:**
- Textos e parágrafos
- Imagens (preserva tamanho e qualidade)
- Tabelas (com bordas e formatação)
- Títulos e estrutura

✅ **Remove elementos desnecessários:**
- Headers e footers
- Menus e navegação
- Banners de cookies
- Popups e modais

✅ **Gera PDF profissional:**
- Formato A4
- Com numeração de páginas
- Margem apropriada
- Imagens em alta qualidade

## 📁 Saída

O PDF será salvo na mesma pasta do script com nome como:
```
Nome_da_Pagina_2025-12-23.pdf
```

## 💡 Dicas Importantes

1. **Feche o navegador completamente** antes de abrir em modo debug
2. **A aba precisa estar ativa** quando você rodou o script
3. Se houver erro de conexão, verifique se a porta está correta
4. Você pode continuar navegando após o script terminar

## 🔧 Personalizações (Opcional)

Se quiser remover mais elementos específicos, edite a linha que começa com `const seletoresLixo`:

```javascript
const seletoresLixo = [
  'header', 'footer', 'nav', // elementos HTML
  '.classe-css', // classes CSS
  '#id-elemento' // IDs HTML
];
```

## ❌ Resolvendo Problemas

**Erro: "ECONNREFUSED"**
- Navegador não está em modo debug
- Porta 9222 está bloqueada
- Tente fechar tudo e abrir novamente

**PDF com conteúdo incompleto**
- Aguarde o site carregar completamente antes de rodar o script
- Aumente o timeout se necessário

**Imagens não aparecem no PDF**
- Verifique se `printBackground: true` está ativado
- Algumas imagens lazy-loaded podem não ser capturadas

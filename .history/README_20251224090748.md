# Extração Slides PDF 📄

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Uma ferramenta de automação (RPA) desenvolvida em Python para capturar slides de apresentações web (cursos online, EAD, vídeos) e convertê-los automaticamente em um arquivo PDF limpo, removendo bordas, abas e menus do navegador.

## 🚀 Funcionalidades

- **Detecção Automática:** Identifica e foca na janela ativa do navegador.
- **Corte Inteligente (Crop):** Remove automaticamente a barra de endereço, abas, favoritos e rodapé (configurável).
- **Nomeação Segura:** Sanitização automática do nome do arquivo (remove caracteres inválidos do Windows).
- **Backup de Emergência:** Salva o trabalho mesmo se houver erro ao salvar o arquivo final.
- **Conversão Direta:** Transforma a sequência de prints diretamente em PDF sem perda de qualidade.

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **PyAutoGUI:** Automação de mouse e teclado.
- **PyGetWindow:** Gerenciamento e detecção de janelas ativas.
- **Img2Pdf:** Conversão otimizada de imagens para PDF.
- **Keyboard:** Detecção de atalhos globais.

## 📦 Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/gabrielfalcao/extracao-slides-pdf.git
   cd extracao-slides-pdf
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuração (Calibragem)

Cada monitor e navegador possui tamanhos diferentes de barras. Antes de usar oficialmente, abra o script `extrair.py` e ajuste as variáveis de corte no topo do arquivo se necessário:

```python
# Ajuste fino em Pixels
CORTE_TOPO = 160   # Remove abas, barra de endereço e favoritos
CORTE_BAIXO = 20   # Remove barra de status/rodapé
CORTE_LADOS = 10   # Remove bordas laterais do Windows
```

> **Dica:** Faça um teste capturando 1 slide. Se o PDF cortar o título, diminua o `CORTE_TOPO`. Se aparecer a barra de endereço, aumente o valor.

## 🖱️ Como Usar

1. Execute o script:
   ```bash
   python extrair.py
   ```

2. O terminal pedirá o **nome do arquivo**. Digite o nome desejado (ex: `Aula_Historia`).
3. O script iniciará uma contagem de 3 segundos. **Clique na janela do navegador/slide** imediatamente para torná-la ativa.
4. **Controles:**
   - `ENTER`: Captura o slide atual.
   - `ESC`: Finaliza a captura e gera o arquivo PDF na pasta do projeto.

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Desenvolvido por Gabriel Falcão

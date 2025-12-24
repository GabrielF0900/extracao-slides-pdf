# ⚡ Guia Rápido - Como Usar o Script

## 🚀 PASSO 1: Execute o Script

### Opção A: Windows (Fácil) 🖱️
Clique 2 vezes em: **`extrair_python.bat`**

### Opção B: Terminal/PowerShell
```powershell
python extrair.py
```

---

## 📝 PASSO 2: Digite o Nome do Arquivo

O script perguntará:
```
>> Digite o NOME do arquivo:
```

**Exemplos:**
```
Aula_Historia_Slide_01
Matematica_Cap3
Informatica_2025
```

- Deixe em branco para nome padrão automático
- Não precisa digitar `.pdf` (é adicionado automaticamente)
- Caracteres especiais (/, \, :, ?, ") são removidos

---

## 📂 PASSO 3: Escolha a Pasta de Destino

O script perguntará:
```
Onde deseja salvar? (Deixe em branco para salvar na pasta atual)
>> Cole o CAMINHO da pasta:
```

**Exemplos:**
```
C:\Users\seu_usuario\Desktop\Material
C:\Users\seu_usuario\Documents\PDFs
D:\Backup\Slides
```

- Deixe **em branco** para salvar na pasta do script
- Se a pasta não existir, salva na pasta atual automaticamente

---

## ⏱️ PASSO 4: Aguarde 3 Segundos e Clique

O script mostrará:
```
Calibrando em 3...
Calibrando em 2...
Calibrando em 1...
```

**Durante essa contagem:**
- ⚠️ Clique na janela do navegador com seus slides
- O script detectará automaticamente qual janela ativou

---

## 📸 PASSO 5: Capture os Slides

O terminal mostrará:
```
--- COMANDOS ---
 [ENTER] -> Capturar Slide
 [ESC]   -> Finalizar e Gerar PDF
```

### Para Capturar:
1. Visualize o slide no navegador
2. Pressione **`ENTER`** para capturar
3. Você verá: `[SUCESSO] Slide 1 salvo em temp_Aula_Historia_Slide_01`
4. Navegue para o próximo slide (use setas, scroll, clique, etc)
5. Pressione **`ENTER`** novamente
6. Repita até o último slide

### Exemplo de Captura:
```
[SUCESSO] Slide 1 salvo em temp_Aula_Historia_Slide_01
[SUCESSO] Slide 2 salvo em temp_Aula_Historia_Slide_01
[SUCESSO] Slide 3 salvo em temp_Aula_Historia_Slide_01
[SUCESSO] Slide 4 salvo em temp_Aula_Historia_Slide_01
```

---

## 📄 PASSO 6: Gere o PDF

Quando terminar de capturar:

**Pressione: `ESC`**

O script fará:
```
Encerrando captura...
Gerando PDF em: C:\... ✅

✅ SUCESSO! Arquivo criado:
C:\Users\seu_usuario\Desktop\Material\Aula_Historia_Slide_01.pdf
```

---

## ✅ PRONTO!

Seu PDF está gerado e pronto para usar! 🎉

- Todas as imagens capturadas estão em: `temp_Aula_Historia_Slide_01/`
- PDF final em: `Aula_Historia_Slide_01.pdf`

---

## 🔧 Se der erro?

| Erro | O que fazer |
|------|------------|
| Nada acontece ao pressionar ENTER | Clique no navegador e tente novamente |
| PDF vazio/preto | O crop está errado. Veja GUIA_USO.md para ajustar |
| "ModuleNotFoundError" | Execute: `pip install -r requirements.txt` |
| Pasta não encontrada | Deixe em branco ou use caminho válido |

---

## 📚 Precisa de mais detalhes?

Leia: **`GUIA_USO.md`** para configurações avançadas, personalizações e troubleshooting completo!

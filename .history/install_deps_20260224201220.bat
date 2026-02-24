@echo off
echo Instalando dependências do projeto (requirements.txt)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Concluído. Pressione qualquer tecla para sair.
pause>nul
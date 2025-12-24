@echo off
REM Script para abrir navegadores em modo debug automaticamente

echo.
echo ========================================
echo    Extrator de Conteudo para PDF
echo ========================================
echo.
echo Escolha seu navegador:
echo.
echo 1 - Chrome/Edge
echo 2 - Firefox
echo 3 - Executar script (detecta automaticamente)
echo.

set /p opcao="Digite a opcao (1-3): "

if "%opcao%"=="1" (
    echo.
    echo Abrindo Chrome/Edge em modo debug...
    echo Porta: 9222
    echo.
    taskkill /F /IM chrome.exe 2>nul
    taskkill /F /IM msedge.exe 2>nul
    timeout /t 2 /nobreak
    
    REM Tenta abrir Chrome primeiro, depois Edge
    if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
        start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
    ) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
        start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
    ) else (
        echo Erro: Chrome ou Edge nao encontrados!
        pause
        exit /b 1
    )
    
    echo.
    echo Navegador aberto! Aguarde 3 segundos...
    timeout /t 3 /nobreak
    echo.
    echo Agora navegue ate o site desejado e pressione ENTER
    pause
    echo.
    echo Executando script de extracao...
    node capturar.js
    
) else if "%opcao%"=="2" (
    echo.
    echo Abrindo Firefox em modo debug...
    echo Porta: 9223
    echo.
    taskkill /F /IM firefox.exe 2>nul
    timeout /t 2 /nobreak
    
    if exist "C:\Program Files\Mozilla Firefox\firefox.exe" (
        start "" "C:\Program Files\Mozilla Firefox\firefox.exe" --remote-debugging-protocol -start-debugger-server 9223
    ) else (
        echo Erro: Firefox nao encontrado!
        pause
        exit /b 1
    )
    
    echo.
    echo Firefox aberto! Aguarde 3 segundos...
    timeout /t 3 /nobreak
    echo.
    echo Agora navegue ate o site desejado e pressione ENTER
    pause
    echo.
    echo Executando script de extracao...
    node capturar.js
    
) else if "%opcao%"=="3" (
    echo.
    echo Executando script (detecta navegador automaticamente)...
    echo.
    node capturar.js
    
) else (
    echo Opcao invalida!
    pause
    exit /b 1
)

echo.
pause

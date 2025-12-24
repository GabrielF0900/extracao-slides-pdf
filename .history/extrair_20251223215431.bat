@echo off
REM Script para extrair TODAS as páginas do conteúdo para PDF

cd /d "%~dp0"
node extrair_completo.js
pause
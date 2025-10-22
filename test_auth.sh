#!/bin/bash

# Script de teste do sistema de autenticação
# Execute após iniciar o container com autenticação habilitada

set -e

BASE_URL="http://localhost:8102"
COOKIE_FILE="/tmp/pm2_cookies.txt"

echo "=========================================="
echo "Testando Sistema de Autenticação"
echo "=========================================="
echo ""

# Limpar cookies anteriores
rm -f "$COOKIE_FILE"

echo "1. Testando acesso sem autenticação..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$RESPONSE" = "302" ]; then
    echo "   ✓ Redirecionamento funcionando (302)"
else
    echo "   ✗ Erro: Esperado 302, recebido $RESPONSE"
fi
echo ""

echo "2. Testando status de autenticação..."
AUTH_STATUS=$(curl -s "$BASE_URL/api/auth-status")
echo "   $AUTH_STATUS"
echo ""

echo "3. Testando login com credenciais inválidas..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"wrong"}' \
    -w "%{http_code}" \
    -o /dev/null)
if [ "$RESPONSE" = "401" ]; then
    echo "   ✓ Rejeição de senha inválida (401)"
else
    echo "   ✗ Erro: Esperado 401, recebido $RESPONSE"
fi
echo ""

echo "4. Testando login com credenciais válidas..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"changeme"}' \
    -c "$COOKIE_FILE" \
    -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✓ Login bem-sucedido (200)"
else
    echo "   ✗ Erro: Esperado 200, recebido $HTTP_CODE"
fi
echo ""

echo "5. Testando acesso autenticado..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/")
if [ "$RESPONSE" = "200" ]; then
    echo "   ✓ Acesso autenticado funcionando (200)"
else
    echo "   ✗ Erro: Esperado 200, recebido $RESPONSE"
fi
echo ""

echo "6. Testando endpoint /files autenticado..."
RESPONSE=$(curl -s -w "%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/files")
if echo "$RESPONSE" | grep -q "200"; then
    echo "   ✓ Endpoint /files acessível (200)"
else
    echo "   ✗ Erro ao acessar /files"
fi
echo ""

echo "7. Testando logout..."
LOGOUT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/logout" \
    -b "$COOKIE_FILE" \
    -w "%{http_code}" \
    -o /dev/null)
if [ "$LOGOUT_RESPONSE" = "200" ]; then
    echo "   ✓ Logout bem-sucedido (200)"
else
    echo "   ✗ Erro: Esperado 200, recebido $LOGOUT_RESPONSE"
fi
echo ""

echo "8. Testando acesso após logout..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/")
if [ "$RESPONSE" = "302" ]; then
    echo "   ✓ Redirecionamento após logout (302)"
else
    echo "   ✗ Erro: Esperado 302, recebido $RESPONSE"
fi
echo ""

# Limpar
rm -f "$COOKIE_FILE"

echo "=========================================="
echo "Testes Concluídos!"
echo "=========================================="
echo ""
echo "Para testar manualmente:"
echo "1. Acesse: $BASE_URL"
echo "2. Login: admin / changeme"
echo "3. Altere a senha após o primeiro login!"
echo ""

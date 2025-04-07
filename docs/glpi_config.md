# Configuração do GLPI para uso com MCP

Este guia demonstra como configurar sua instância GLPI para permitir a integração com o MCP (Management Control Protocol).

## Pré-requisitos

- GLPI instalado (versão 9.5 ou superior)
- Acesso administrativo ao GLPI

## Passo 1: Ativar a API REST do GLPI

1. Acesse sua instância GLPI com um usuário administrativo
2. Navegue até **Configuração** > **Geral**
3. Clique na aba **API**
4. Certifique-se de que a opção **API REST** esteja ativada (Sim)
5. Salve as alterações

![Ativação da API REST](images/glpi_api_activate.png)

## Passo 2: Criar um token de API (App-Token)

1. Ainda na página de configuração da API, clique em **Token de API**
2. Clique no botão **+** para adicionar um novo token
3. Preencha os campos:
   - **Nome**: MCP Integration
   - **Comentário**: Token para integração com MCP Server
4. Clique em **Adicionar**
5. Anote o token gerado (você precisará dele para configurar o MCP)

![Criação de App-Token](images/glpi_app_token.png)

## Passo 3: Criar um token de usuário (User-Token)

1. Navegue até **Administração** > **Usuários**
2. Selecione o usuário que será usado para a integração (ou crie um novo)
3. Na aba **API Tokens**, clique no botão **+**
4. Preencha os campos:
   - **Nome**: MCP API User Token
   - **Comentário**: Token para autenticação do MCP
5. Clique em **Adicionar**
6. Anote o token gerado (você precisará dele para configurar o MCP)

![Criação de User-Token](images/glpi_user_token.png)

## Passo 4: Permissões necessárias para o usuário

O usuário associado ao token deve ter as seguintes permissões mínimas:

1. Navegue até **Administração** > **Perfis**
2. Edite o perfil associado ao usuário da API
3. Certifique-se de que as seguintes permissões estejam configuradas:
   - **Tickets**: Leitura, Escrita e Atribuição (mínimo)
   - **Categorias de Tickets**: Leitura
   - **API**: Sim

![Permissões do Perfil](images/glpi_permissions.png)

## Passo 5: Configuração no MCP

Após obter os tokens e configurar as permissões, você precisará configurar o arquivo `.env` do MCP com as seguintes informações:

```env
GLPI_URL=http://seu-servidor-glpi
GLPI_APP_TOKEN=seu-app-token-gerado-no-passo-2
GLPI_USER_TOKEN=seu-user-token-gerado-no-passo-3
GLPI_DEFAULT_ENTITY_ID=0  # ID da entidade padrão, normalmente 0 para Root Entity
```

## Testando a configuração

Após configurar o GLPI e o MCP, você pode verificar se a integração está funcionando corretamente usando o endpoint de verificação de saúde:

```bash
curl http://localhost:8000/api/v1/health
```

A resposta deve incluir o status "ok" se a conexão com o GLPI estiver funcionando.

## Solução de problemas

### Erros de autenticação

- Verifique se os tokens foram digitados corretamente no arquivo `.env`
- Confirme se o usuário associado ao token está ativo
- Verifique se a API REST está realmente ativada

### Erros de permissão

- Verifique se o usuário tem permissões suficientes no GLPI
- Confira se o usuário tem acesso à entidade especificada em `GLPI_DEFAULT_ENTITY_ID`

### Erros de conexão

- Confirme se a URL do GLPI está correta e acessível do servidor onde o MCP está rodando
- Verifique se não há firewalls bloqueando a comunicação entre o MCP e o GLPI
``` 
</rewritten_file>
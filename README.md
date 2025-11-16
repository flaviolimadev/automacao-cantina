# Projeto de Conexão com Supabase

Este projeto demonstra como conectar-se ao Supabase usando Python e gerenciar credenciais através de um arquivo `.env`.

## Pré-requisitos

- Python 3.7 ou superior
- Uma conta no Supabase
- Projeto criado no Supabase

## Instalação

1. Clone ou baixe este projeto
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração

1. Renomeie o arquivo `env_example.txt` para `.env`
2. Edite o arquivo `.env` com suas credenciais do Supabase:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key
DATABASE_URL=postgresql://postgres:senha@db.seu-projeto.supabase.co:5432/postgres
```

### Como obter as credenciais do Supabase:

1. Acesse o [dashboard do Supabase](https://app.supabase.com)
2. Selecione seu projeto
3. Vá em **Settings** > **API**
4. Copie:
   - **URL**: para `SUPABASE_URL`
   - **anon public**: para `SUPABASE_KEY`
   - **service_role**: para `SUPABASE_SERVICE_ROLE_KEY`

### Para a URL do banco de dados:

1. Vá em **Settings** > **Database**
2. Copie a **Connection string** e cole em `DATABASE_URL`
3. Substitua `[YOUR-PASSWORD]` pela senha do seu banco

## Uso

Execute o arquivo principal:
```bash
python main.py
```

O programa irá:
- Testar a conexão com o Supabase
- Mostrar exemplos de uso (comentados)

## Funcionalidades

A classe `SupabaseConnection` oferece os seguintes métodos:

### Conexão e Teste
- `test_connection()`: Testa se a conexão está funcionando
- `get_database_connection()`: Retorna conexão direta com PostgreSQL

### Operações CRUD
- `insert_data(table_name, data)`: Insere dados em uma tabela
- `select_data(table_name, columns, filters)`: Seleciona dados de uma tabela
- `update_data(table_name, data, filters)`: Atualiza dados em uma tabela
- `delete_data(table_name, filters)`: Deleta dados de uma tabela

## Exemplos de Uso

### Inserir dados:
```python
supabase_conn = SupabaseConnection()
data = {"nome": "João", "email": "joao@email.com"}
supabase_conn.insert_data('usuarios', data)
```

### Selecionar dados:
```python
usuarios = supabase_conn.select_data('usuarios')
print(usuarios)
```

### Atualizar dados:
```python
supabase_conn.update_data('usuarios', {"nome": "João Silva"}, {"id": 1})
```

### Deletar dados:
```python
supabase_conn.delete_data('usuarios', {"id": 1})
```

## Scripts Específicos para Responsáveis e Alunos

### Sistema completo com menu interativo:
```bash
python responsaveis_requests.py
```
**Opções disponíveis:**
- Listar responsáveis (simples)
- Listar responsáveis com alunos relacionados (completo)
- 🎯 **Listar apenas relações NÍVEL 1** (filtrado)
- Listar relações (resumido)
- Inserir novo responsável
- Exibir em formato JSON

### Scripts individuais:

#### Exibir responsáveis com alunos:
```bash
python listar_relacoes.py
```

#### 🎯 Exibir APENAS relações de nível 1:
```bash
python nivel_1_apenas.py
```

#### Exibir tabela responsaveis (simples):
```bash
python listar_responsaveis_simples.py
```

#### Script original (biblioteca supabase):
```bash
python exibir_responsaveis.py --simples  # Apenas listagem
python exibir_responsaveis.py --json     # Formato JSON
```

### Funcionalidades das Relações:
- ✅ **Responsáveis com alunos**: Mostra cada responsável e seus alunos
- ✅ **Dados completos**: Nome, contato, série, escola
- ✅ **Nível de relação**: Identifica o tipo de parentesco
- 🎯 **Filtro por nível**: Exibe apenas relações de nível específico (ex: nível 1)
- ✅ **Estatísticas**: Resumo com totais e distribuição
- ✅ **Formatação de datas**: Datas legíveis em português

## Estrutura do Projeto

```
automaçao-cantina/
├── main.py                      # Classe principal SupabaseConnection
├── exemplos_uso.py              # Exemplos completos de uso
├── responsaveis_requests.py     # 🆕 Sistema completo com menu (RECOMENDADO)
├── listar_relacoes.py          # 🆕 Exibe relações responsáveis ↔ alunos
├── nivel_1_apenas.py           # 🎯 Apenas relações de nível 1
├── exibir_responsaveis.py       # Script original (biblioteca supabase)
├── listar_responsaveis_simples.py # Versão simples para listar responsaveis
├── teste_conexao.py            # Teste com biblioteca supabase
├── teste_conexao_simples.py    # Teste com requests direto
├── requirements.txt             # Dependências
├── env_example.txt              # Exemplo de arquivo .env
├── README.md                   # Este arquivo
├── INICIO_RAPIDO.md            # Guia rápido
├── .gitignore                  # Arquivos a ignorar no Git
└── .env                        # Suas credenciais (criar manualmente)
```

## Dependências

- `supabase`: Cliente oficial do Supabase para Python
- `python-dotenv`: Para carregar variáveis de ambiente
- `psycopg2-binary`: Para conexão direta com PostgreSQL

## Tratamento de Erros

O projeto inclui tratamento de erros para:
- Credenciais ausentes no arquivo `.env`
- Falhas de conexão
- Operações de banco de dados

## Segurança

⚠️ **Importante**: Nunca commite o arquivo `.env` no seu repositório Git. Adicione-o ao `.gitignore` para manter suas credenciais seguras.

## Suporte

Se encontrar problemas:
1. Verifique se suas credenciais estão corretas
2. Confirme se o projeto no Supabase está ativo
3. Teste a conexão com a internet 
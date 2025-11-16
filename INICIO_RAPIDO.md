# 🚀 Início Rápido - Supabase Python

## Passos para usar em 5 minutos:

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

#### Se der erro de 'proxy':
```bash
pip uninstall supabase -y
pip install supabase==2.7.4
```

### 2. Configurar credenciais
1. Renomeie `env_example.txt` para `.env`
2. Edite o arquivo `.env` com suas credenciais do Supabase:
   - URL do projeto
   - Chave anon
   - Chave service_role
   - URL do banco de dados

### 3. Testar conexão
```bash
python teste_conexao.py
```

#### Se funcionar, teste o script principal:
```bash
python main.py
```

### 4. Usar o sistema completo (RECOMENDADO)
```bash
python responsaveis_requests.py
```

### 5. Ver apenas relações de NÍVEL 1 🎯
```bash
python nivel_1_apenas.py
```

### 6. Ou ver todas as relações
```bash
python listar_relacoes.py
```

### 7. Outros exemplos
```bash
python exemplos_uso.py
```

---

## 🔧 Como obter credenciais do Supabase:

1. **Acesse:** https://app.supabase.com
2. **Selecione seu projeto**
3. **Vá em Settings > API**
4. **Copie:**
   - URL → `SUPABASE_URL`
   - anon public → `SUPABASE_KEY`
   - service_role → `SUPABASE_SERVICE_ROLE_KEY`

5. **Para DATABASE_URL:**
   - Vá em Settings > Database
   - Copie a Connection string
   - Substitua `[YOUR-PASSWORD]` pela senha do seu banco

---

## 📁 Scripts principais:
- `responsaveis_requests.py` - Sistema completo com menu 🌟
- `nivel_1_apenas.py` - Apenas relações de nível 1 🎯
- `listar_relacoes.py` - Todas as relações responsáveis ↔ alunos
- `main.py` - Classe principal SupabaseConnection
- `.env` - Suas credenciais (criar)

---

## ⚡ Pronto para usar!
Se tiver dúvidas, consulte o `README.md` completo. 
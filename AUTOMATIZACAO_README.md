# 🤖 Automatizador de Cobranças - Infinite Pay

Sistema completo para automatizar a criação de cobranças no Infinite Pay a partir dos dados de responsáveis com dívidas na cantina.

## 📋 Pré-requisitos

### 1. Dependências Python
```bash
pip install -r requirements.txt
```

### 2. Chrome Driver
- Baixe o ChromeDriver compatível com sua versão do Chrome
- Adicione ao PATH do sistema ou na pasta do projeto
- Link: https://chromedriver.chromium.org/

### 3. Configuração do banco
- Arquivo `.env` configurado com credenciais do Supabase
- Tabelas: `responsaveis`, `alunos`, `relacao`, `compras`

## 🚀 Como usar

### Passo 1: Gerar CSV de responsáveis com dívidas
```bash
python dividas_nivel1.py
```
Este comando irá:
- Buscar responsáveis nível 1 com alunos devendo
- Gerar arquivo CSV no formato: `responsaveis_com_dividas_YYYYMMDD_HHMMSS.csv`

### Passo 2: Fazer login no Infinite Pay
1. Acesse https://app.infinitepay.io
2. Faça seu login normalmente
3. **MANTENHA a aba aberta** (o script usará a sessão logada)

### Passo 3: Testar a automação (RECOMENDADO)
```bash
python teste_automatizacao.py
```
Este script:
- Verifica se consegue acessar o Infinite Pay
- Confirma se você está logado
- Testa os seletores principais

### Passo 4: Executar automação completa
```bash
python automatizar_cobrancas.py
```

## 📝 Processo automatizado

O script executa os seguintes passos para cada responsável:

1. **Verificação**: Filtra responsáveis que estão no CSV e têm dívidas
2. **Acesso**: Navega para https://app.infinitepay.io/invoices
3. **Nova cobrança**: Clica no botão "Nova cobrança"
4. **Dados do cliente**: Insere nome do responsável
5. **Valor**: Insere valor total da dívida
6. **Descrição**: Adiciona descrição "Cobrança cantina - X aluno(s)"
7. **Continuar**: Avança para próxima etapa
8. **Configurações**: Ativa opções necessárias
9. **Data**: Define data de vencimento (dia atual)
10. **Envio**: Envia a cobrança

## 📊 Monitoramento

### Logs em tempo real
- Console: Mostra progresso em tempo real
- Arquivo: `cobrancas_automatizadas.log`

### Relatório final
```
📊 RELATÓRIO FINAL:
✅ Cobranças criadas: 150
❌ Cobranças com erro: 3
📋 Total processado: 153
```

## ⚠️ Importante

### Segurança
- **NÃO** compartilhe suas credenciais do Infinite Pay
- Execute apenas em ambiente seguro
- Mantenha os logs confidenciais

### Performance
- O script aguarda 5 segundos entre cobranças
- Não sobrecarrega o sistema do Infinite Pay
- Timeouts configurados para evitar travamentos

### Controle
- Pressione `Ctrl+C` para interromper a qualquer momento
- O script pode ser pausado e retomado
- Progresso é salvo em logs

## 🔧 Configurações avançadas

### Modificar timeouts
No arquivo `automatizar_cobrancas.py`, altere:
```python
self.wait = WebDriverWait(self.driver, 20)  # Timeout geral
time.sleep(5)  # Delay entre cobranças
```

### Executar em modo headless (sem interface)
Descomente no arquivo:
```python
# self.chrome_options.add_argument("--headless")
```

### Filtrar responsáveis específicos
Edite o CSV manualmente antes de executar, mantendo apenas os responsáveis desejados.

## 🛠️ Solução de problemas

### "Chrome driver not found"
- Baixe ChromeDriver compatível
- Adicione ao PATH ou pasta do projeto

### "Botão não encontrado"
- Verifique se está logado no Infinite Pay
- Execute `teste_automatizacao.py` primeiro
- Verifique se a interface mudou

### "Timeout" frequentes
- Aumente o timeout: `WebDriverWait(self.driver, 30)`
- Verifique conexão com internet
- Infinite Pay pode estar lento

### Cobranças não criadas
- Verifique se os dados estão corretos
- Confirme se há saldo/limite na conta
- Verifique logs para detalhes do erro

## 📁 Estrutura de arquivos

```
automaçao-cantina/
├── automatizar_cobrancas.py      # Script principal
├── teste_automatizacao.py        # Teste de conectividade  
├── dividas_nivel1.py             # Gerador de CSV
├── responsaveis_requests.py      # Conexão com banco
├── requirements.txt              # Dependências
├── cobrancas_automatizadas.log   # Logs (gerado)
└── responsaveis_com_dividas_*.csv # CSVs (gerados)
```

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs** em `cobrancas_automatizadas.log`
2. **Execute o teste** com `teste_automatizacao.py`
3. **Confirme dependências** com `pip list | grep selenium`
4. **Verifique ChromeDriver** com `chromedriver --version`

## 📈 Próximas melhorias

- [ ] Interface gráfica (GUI)
- [ ] Agendamento automático
- [ ] Integração com WhatsApp
- [ ] Dashboard de acompanhamento
- [ ] Exportação de relatórios
- [ ] Notificações por email

---

**⚡ Sistema otimizado e testado para máxima eficiência!** 
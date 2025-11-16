#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def teste_simples():
    """Teste básico de conexão sem usar a classe"""
    try:
        print("🔄 Carregando variáveis de ambiente...")
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("❌ Erro: Variáveis SUPABASE_URL ou SUPABASE_KEY não encontradas no .env")
            print("📝 Verifique se o arquivo .env existe e contém:")
            print("   SUPABASE_URL=https://seu-projeto.supabase.co")
            print("   SUPABASE_KEY=sua-chave-anon")
            return False
        
        print(f"✅ URL carregada: {url[:30]}...")
        print(f"✅ Key carregada: {key[:20]}...")
        
        print("\n🔄 Importando Supabase...")
        from supabase import create_client
        
        print("🔄 Criando cliente...")
        supabase = create_client(url, key)
        
        print("🔄 Testando conexão com tabela responsaveis...")
        response = supabase.table('responsaveis').select('*').limit(1).execute()
        
        print("✅ Conexão realizada com sucesso!")
        print(f"📊 Tipo de resposta: {type(response)}")
        
        if hasattr(response, 'data') and response.data:
            print(f"📋 Dados encontrados: {len(response.data)} registro(s)")
            print(f"🔍 Primeiro registro: {response.data[0] if response.data else 'Nenhum'}")
        else:
            print("⚠️ Tabela vazia ou sem dados")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Solução: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n🔧 Possíveis soluções:")
        print("1. Reinstalar dependências: pip uninstall supabase && pip install supabase")
        print("2. Verificar credenciais no arquivo .env")
        print("3. Confirmar se a tabela 'responsaveis' existe")
        return False

def verificar_env():
    """Verifica se o arquivo .env existe e está configurado"""
    print("🔍 Verificando arquivo .env...")
    
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        print("📝 Renomeie env_example.txt para .env e configure suas credenciais")
        return False
    
    with open('.env', 'r') as f:
        conteudo = f.read()
    
    variaveis_necessarias = ['SUPABASE_URL', 'SUPABASE_KEY']
    
    for var in variaveis_necessarias:
        if var not in conteudo:
            print(f"❌ Variável {var} não encontrada no .env")
            return False
        
        # Verificar se não está vazia
        valor = os.getenv(var)
        if not valor or valor.strip() == '' or 'seu-projeto' in valor:
            print(f"❌ Variável {var} não está configurada corretamente")
            print(f"   Valor atual: {valor}")
            return False
    
    print("✅ Arquivo .env configurado corretamente")
    return True

def main():
    """Função principal de teste"""
    print("🧪 TESTE DE CONEXÃO SUPABASE")
    print("=" * 40)
    
    # Verificar .env
    if not verificar_env():
        return
    
    print("\n" + "-" * 40)
    
    # Testar conexão
    if teste_simples():
        print("\n🎉 Teste concluído com sucesso!")
        print("✅ Agora você pode usar os scripts normalmente")
    else:
        print("\n💔 Teste falhou")
        print("🔧 Siga as soluções sugeridas acima")

if __name__ == "__main__":
    main() 
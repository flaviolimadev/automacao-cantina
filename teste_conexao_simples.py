#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

def teste_com_requests():
    """Testa conexão usando apenas requests (sem biblioteca supabase)"""
    try:
        print("🔄 Carregando credenciais...")
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("❌ Credenciais não encontradas no .env")
            return False
            
        print(f"✅ URL: {url[:30]}...")
        print(f"✅ Key: {key[:20]}...")
        
        # Fazer requisição HTTP direta
        api_url = f"{url}/rest/v1/responsaveis"
        
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        print("\n🔄 Fazendo requisição HTTP direta...")
        response = requests.get(api_url, headers=headers, params={'limit': 5})
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Conexão HTTP realizada com sucesso!")
            
            data = response.json()
            print(f"📋 Registros encontrados: {len(data)}")
            
            if data:
                print("\n🔍 Primeiros registros:")
                for i, item in enumerate(data[:3], 1):
                    print(f"  {i}. Nome: {item.get('nome', 'N/A')} {item.get('sobrenome', 'N/A')}")
                    print(f"     Contato: {item.get('contato', 'N/A')}")
                    print(f"     ID: {item.get('id', 'N/A')[:8]}...")
                    print()
            else:
                print("⚠️ Tabela vazia")
                
            return True
            
        elif response.status_code == 401:
            print("❌ Erro 401: Credenciais inválidas")
            print("🔧 Verifique suas chaves no arquivo .env")
            return False
            
        elif response.status_code == 404:
            print("❌ Erro 404: Tabela 'responsaveis' não encontrada")
            print("🔧 Verifique se a tabela existe no seu banco")
            return False
            
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: Não foi possível conectar ao Supabase")
        print("🔧 Verifique sua conexão com a internet")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def listar_responsaveis():
    """Lista todos os responsáveis usando requests"""
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("❌ Credenciais não encontradas")
            return
            
        api_url = f"{url}/rest/v1/responsaveis"
        
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                print("⚠️ Nenhum responsável encontrado")
                return
                
            print(f"✅ {len(data)} responsáveis encontrados:")
            print("=" * 60)
            
            for i, resp in enumerate(data, 1):
                print(f"{i:2d}. {resp.get('nome', 'N/A')} {resp.get('sobrenome', 'N/A')}")
                print(f"    📞 Contato: {resp.get('contato', 'N/A')}")
                print(f"    🆔 ID: {resp.get('id', 'N/A')}")
                
                # Datas
                if resp.get('created_at'):
                    print(f"    📅 Criado: {resp['created_at'][:10]}")
                    
                print("-" * 40)
                
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🧪 TESTE DE CONEXÃO SIMPLES (SEM BIBLIOTECA SUPABASE)")
    print("=" * 60)
    
    # Teste básico
    if teste_com_requests():
        print("\n🎉 Teste básico passou!")
        print("\n" + "=" * 60)
        print("📋 LISTANDO RESPONSÁVEIS:")
        print("=" * 60)
        listar_responsaveis()
        
        print("\n✅ Conexão funcionando perfeitamente!")
        print("💡 Agora é só resolver o problema da biblioteca supabase")
        
    else:
        print("\n💔 Teste falhou")
        print("🔧 Verifique as credenciais no arquivo .env")

if __name__ == "__main__":
    main() 
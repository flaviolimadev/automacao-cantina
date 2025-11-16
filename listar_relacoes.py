#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Script para listar relações entre responsáveis e alunos"""
    try:
        # Configurar conexão
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("❌ Credenciais não encontradas no arquivo .env")
            return
        
        base_url = f"{url}/rest/v1"
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        print("🔄 Buscando relações entre responsáveis e alunos...")
        
        # Buscar todas as relações
        response = requests.get(f"{base_url}/relacao", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao buscar relações: {response.status_code}")
            return
        
        relacoes = response.json()
        
        if not relacoes:
            print("⚠️ Nenhuma relação encontrada")
            return
        
        print(f"✅ {len(relacoes)} relação(ões) encontrada(s)")
        print("\n" + "=" * 100)
        
        # Para cada relação, buscar dados do responsável e aluno
        for i, relacao in enumerate(relacoes, 1):
            responsavel_id = relacao.get('responsavel_id')
            aluno_id = relacao.get('aluno_id')
            nivel = relacao.get('nivel', 'N/A')
            
            # Buscar dados do responsável
            resp_response = requests.get(
                f"{base_url}/responsaveis?id=eq.{responsavel_id}",
                headers=headers
            )
            
            # Buscar dados do aluno
            aluno_response = requests.get(
                f"{base_url}/alunos?id=eq.{aluno_id}",
                headers=headers
            )
            
            if resp_response.status_code == 200 and aluno_response.status_code == 200:
                responsavel = resp_response.json()[0] if resp_response.json() else {}
                aluno = aluno_response.json()[0] if aluno_response.json() else {}
                
                print(f"\n{i}. 🔗 RELAÇÃO:")
                print(f"   👤 Responsável: {responsavel.get('nome', 'N/A')} {responsavel.get('sobrenome', 'N/A')}")
                print(f"      📞 Contato: {responsavel.get('contato', 'N/A')}")
                print(f"      🆔 ID: {responsavel.get('id', 'N/A')}")
                
                print(f"   🎓 Aluno: {aluno.get('nome', 'N/A')} {aluno.get('sobrenome', 'N/A')}")
                print(f"      📚 Série ID: {aluno.get('serie_id', 'N/A')}")
                print(f"      🏫 Escola ID: {aluno.get('escola_id', 'N/A')}")
                print(f"      🆔 ID: {aluno.get('id', 'N/A')}")
                
                print(f"   🔗 Nível da Relação: {nivel}")
                
                # Data da relação
                if relacao.get('created_at'):
                    try:
                        data_relacao = datetime.fromisoformat(relacao['created_at'].replace('Z', '+00:00'))
                        print(f"   📅 Relação criada: {data_relacao.strftime('%d/%m/%Y às %H:%M:%S')}")
                    except:
                        print(f"   📅 Relação criada: {relacao.get('created_at', 'N/A')}")
                
                if i < len(relacoes):
                    print("\n" + "-" * 80)
        
        print("\n" + "=" * 100)
        print(f"📊 RESUMO: {len(relacoes)} relações encontradas")
        
        # Contar quantos responsáveis e alunos únicos
        responsaveis_unicos = set()
        alunos_unicos = set()
        
        for relacao in relacoes:
            responsaveis_unicos.add(relacao.get('responsavel_id'))
            alunos_unicos.add(relacao.get('aluno_id'))
        
        print(f"   👥 Responsáveis únicos: {len(responsaveis_unicos)}")
        print(f"   🎓 Alunos únicos: {len(alunos_unicos)}")
        
        # Agrupar por nível se disponível
        niveis = {}
        for relacao in relacoes:
            nivel = relacao.get('nivel', 'N/A')
            niveis[nivel] = niveis.get(nivel, 0) + 1
        
        if niveis:
            print(f"   📊 Distribuição por nível:")
            for nivel, quantidade in niveis.items():
                print(f"      Nível {nivel}: {quantidade} relações")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main() 
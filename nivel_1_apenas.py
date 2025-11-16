#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Script para exibir apenas responsáveis com relações de nível 1"""
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
        
        print("🎯 Buscando apenas relações de NÍVEL 1...")
        print("=" * 60)
        
        # Buscar relações apenas de nível 1
        response = requests.get(f"{base_url}/relacao?nivel=eq.1", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao buscar relações: {response.status_code}")
            return
        
        relacoes = response.json()
        
        if not relacoes:
            print("⚠️ Nenhuma relação de nível 1 encontrada")
            return
        
        print(f"✅ {len(relacoes)} relação(ões) de NÍVEL 1 encontrada(s)")
        print("\n" + "=" * 80)
        
        # Agrupar por responsável
        responsaveis_map = {}
        
        for relacao in relacoes:
            responsavel_id = relacao.get('responsavel_id')
            aluno_id = relacao.get('aluno_id')
            
            if responsavel_id not in responsaveis_map:
                # Buscar dados do responsável
                resp_response = requests.get(
                    f"{base_url}/responsaveis?id=eq.{responsavel_id}",
                    headers=headers
                )
                
                if resp_response.status_code == 200 and resp_response.json():
                    responsaveis_map[responsavel_id] = {
                        'dados': resp_response.json()[0],
                        'alunos': []
                    }
                else:
                    continue
            
            # Buscar dados do aluno
            aluno_response = requests.get(
                f"{base_url}/alunos?id=eq.{aluno_id}",
                headers=headers
            )
            
            if aluno_response.status_code == 200 and aluno_response.json():
                aluno = aluno_response.json()[0]
                aluno['relacao_criada'] = relacao.get('created_at')
                responsaveis_map[responsavel_id]['alunos'].append(aluno)
        
        if not responsaveis_map:
            print("⚠️ Nenhum responsável encontrado para as relações de nível 1")
            return
        
        # Exibir resultados
        total_alunos = 0
        
        for i, (resp_id, dados) in enumerate(responsaveis_map.items(), 1):
            responsavel = dados['dados']
            alunos = dados['alunos']
            
            print(f"\n{i}. 👤 RESPONSÁVEL:")
            print(f"   📛 Nome: {responsavel.get('nome', 'N/A')} {responsavel.get('sobrenome', 'N/A')}")
            print(f"   📞 Contato: {responsavel.get('contato', 'N/A')}")
            print(f"   🆔 ID: {responsavel.get('id', 'N/A')}")
            
            # Data de criação do responsável
            if responsavel.get('created_at'):
                try:
                    data_resp = datetime.fromisoformat(responsavel['created_at'].replace('Z', '+00:00'))
                    print(f"   📅 Criado: {data_resp.strftime('%d/%m/%Y às %H:%M:%S')}")
                except:
                    print(f"   📅 Criado: {responsavel.get('created_at', 'N/A')}")
            
            print(f"\n   🎯 ALUNOS DE NÍVEL 1 ({len(alunos)}):")
            
            for j, aluno in enumerate(alunos, 1):
                print(f"      {j}. 🎓 {aluno.get('nome', 'N/A')} {aluno.get('sobrenome', 'N/A')}")
                print(f"         🆔 ID: {aluno.get('id', 'N/A')}")
                print(f"         📚 Série ID: {aluno.get('serie_id', 'N/A')}")
                print(f"         🏫 Escola ID: {aluno.get('escola_id', 'N/A')}")
                
                # Foto se disponível
                if aluno.get('foto_url'):
                    print(f"         📸 Foto: {aluno.get('foto_url', 'N/A')}")
                
                # Data da relação
                if aluno.get('relacao_criada'):
                    try:
                        data_relacao = datetime.fromisoformat(aluno['relacao_criada'].replace('Z', '+00:00'))
                        print(f"         🔗 Relação criada: {data_relacao.strftime('%d/%m/%Y às %H:%M:%S')}")
                    except:
                        print(f"         🔗 Relação criada: {aluno.get('relacao_criada', 'N/A')}")
                
                # Data de criação do aluno
                if aluno.get('created_at'):
                    try:
                        data_aluno = datetime.fromisoformat(aluno['created_at'].replace('Z', '+00:00'))
                        print(f"         📅 Aluno criado: {data_aluno.strftime('%d/%m/%Y')}")
                    except:
                        print(f"         📅 Aluno criado: {aluno.get('created_at', 'N/A')}")
                
                if j < len(alunos):
                    print("         " + "- " * 20)
            
            total_alunos += len(alunos)
            
            if i < len(responsaveis_map):
                print("\n" + "=" * 80)
        
        # Resumo final
        print("\n" + "=" * 80)
        print(f"📊 RESUMO - RELAÇÕES NÍVEL 1:")
        print(f"   🎯 Filtro: Apenas nível 1")
        print(f"   👥 Responsáveis com nível 1: {len(responsaveis_map)}")
        print(f"   🎓 Total de alunos de nível 1: {total_alunos}")
        print(f"   📈 Média de alunos por responsável: {total_alunos/len(responsaveis_map):.1f}")
        print(f"   🔗 Total de relações de nível 1: {len(relacoes)}")
        
        # Informação adicional
        print(f"\n💡 INFORMAÇÃO:")
        print(f"   Este script mostra apenas relações com nível = 1")
        print(f"   Para ver todas as relações, use: python responsaveis_requests.py")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main() 
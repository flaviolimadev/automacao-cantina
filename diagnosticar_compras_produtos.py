#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar produtos por compra individual
Analisa cada compra e busca seus produtos específicos
"""

import os
import requests
from dotenv import load_dotenv
from responsaveis_requests import SupabaseRequests

# Carregar variáveis de ambiente
load_dotenv()

def analisar_compras_com_produtos():
    """Analisar cada compra e buscar seus produtos específicos"""
    
    print("🔍 ANÁLISE DE COMPRAS → PRODUTOS")
    print("=" * 60)
    
    try:
        supabase = SupabaseRequests()
        
        # 1. Buscar compras pendentes (status = false)
        print("1️⃣ Buscando compras pendentes...")
        compras_response = requests.get(
            f"{supabase.base_url}/compras?status=eq.false&limit=10",
            headers=supabase.headers
        )
        
        if compras_response.status_code != 200:
            print(f"❌ Erro ao buscar compras: {compras_response.text}")
            return
        
        compras = compras_response.json()
        print(f"✅ {len(compras)} compras pendentes encontradas")
        
        # 2. Buscar todos os produtos para referência
        print("\n2️⃣ Carregando produtos...")
        produtos_response = requests.get(
            f"{supabase.base_url}/produtos",
            headers=supabase.headers
        )
        
        if produtos_response.status_code != 200:
            print(f"❌ Erro ao buscar produtos: {produtos_response.text}")
            return
        
        produtos = produtos_response.json()
        produtos_dict = {p['id']: p for p in produtos}
        print(f"✅ {len(produtos)} produtos carregados")
        
        # 3. Analisar cada compra individualmente
        print("\n3️⃣ Analisando cada compra...")
        print("-" * 60)
        
        compras_com_produtos = 0
        compras_sem_produtos = 0
        total_produtos_encontrados = 0
        
        for i, compra in enumerate(compras[:10]):  # Primeiras 10 compras
            compra_id = compra['id']
            valor = compra.get('value', 0)
            observacoes = compra.get('observacoes') or 'Sem observações'
            data_compra = compra.get('created_at', '')[:10]  # Apenas a data
            
            print(f"\n📋 COMPRA #{i+1}")
            print(f"   ID: {compra_id}")
            print(f"   Data: {data_compra}")
            print(f"   Valor: R$ {valor}")
            print(f"   Observações: {observacoes}")
            
            # Buscar produtos desta compra específica
            produtos_compra_response = requests.get(
                f"{supabase.base_url}/produtos_comprados?compra_id=eq.{compra_id}",
                headers=supabase.headers
            )
            
            if produtos_compra_response.status_code == 200:
                produtos_compra = produtos_compra_response.json()
                
                if produtos_compra:
                    compras_com_produtos += 1
                    total_produtos_encontrados += len(produtos_compra)
                    print(f"   ✅ {len(produtos_compra)} produto(s) encontrado(s):")
                    
                    produtos_descritos = []
                    for pc in produtos_compra:
                        produto_id = pc['produto_id']
                        quantidade = pc['quantidade']
                        
                        if produto_id in produtos_dict:
                            produto = produtos_dict[produto_id]
                            nome = produto.get('nome', 'Nome não encontrado')
                            valor_unit = produto.get('valor', 0)
                            
                            if quantidade > 1:
                                desc = f"{quantidade}x {nome}"
                            else:
                                desc = nome
                                
                            produtos_descritos.append(desc)
                            print(f"      • {desc} (R$ {valor_unit} cada)")
                        else:
                            produtos_descritos.append(f"{quantidade}x [Produto ID não encontrado]")
                            print(f"      • {quantidade}x [Produto ID {produto_id} não encontrado]")
                    
                    # Criar descrição final
                    descricao_final = " + ".join(produtos_descritos)
                    print(f"   📝 Descrição final: {descricao_final}")
                    
                else:
                    compras_sem_produtos += 1
                    print("   ⚠️ Nenhum produto encontrado")
                    print(f"   📝 Fallback: {observacoes}")
            else:
                compras_sem_produtos += 1
                print(f"   ❌ Erro ao buscar produtos: {produtos_compra_response.status_code}")
        
        # 4. Resumo da análise
        print("\n" + "=" * 60)
        print("📊 RESUMO DA ANÁLISE")
        print("=" * 60)
        print(f"Total de compras analisadas: {len(compras[:10])}")
        print(f"Compras COM produtos: {compras_com_produtos}")
        print(f"Compras SEM produtos: {compras_sem_produtos}")
        print(f"Total de produtos encontrados: {total_produtos_encontrados}")
        print(f"Taxa de sucesso: {(compras_com_produtos/len(compras[:10]))*100:.1f}%")
        
        # 5. Testar uma busca completa de responsáveis
        print(f"\n4️⃣ Testando busca de responsáveis com dívidas...")
        responsaveis = supabase.select_responsaveis_nivel1_com_dividas()
        
        if responsaveis:
            print(f"✅ {len(responsaveis)} responsáveis com dívidas encontrados")
            
            # Analisar primeiro responsável
            primeiro = responsaveis[0]
            nome_resp = f"{primeiro.get('nome', '')} {primeiro.get('sobrenome', '')}".strip()
            print(f"\n📋 Exemplo - Responsável: {nome_resp}")
            
            if 'alunos' in primeiro:
                for aluno in primeiro['alunos'][:1]:  # Primeiro aluno
                    nome_aluno = f"{aluno.get('nome', '')} {aluno.get('sobrenome', '')}".strip()
                    print(f"   👦 Aluno: {nome_aluno}")
                    
                    if 'compras_pendentes' in aluno:
                        print(f"   💰 {len(aluno['compras_pendentes'])} compras pendentes")
                        
                        for compra in aluno['compras_pendentes'][:3]:  # Primeiras 3 compras
                            compra_id = compra['id']
                            valor = compra.get('value', 0)
                            
                            # Buscar produtos desta compra
                            produtos_resp = requests.get(
                                f"{supabase.base_url}/produtos_comprados?compra_id=eq.{compra_id}",
                                headers=supabase.headers
                            )
                            
                            if produtos_resp.status_code == 200:
                                produtos_compra = produtos_resp.json()
                                if produtos_compra:
                                    produtos_nomes = []
                                    for pc in produtos_compra:
                                        if pc['produto_id'] in produtos_dict:
                                            nome = produtos_dict[pc['produto_id']]['nome']
                                            if pc['quantidade'] > 1:
                                                produtos_nomes.append(f"{pc['quantidade']}x {nome}")
                                            else:
                                                produtos_nomes.append(nome)
                                    
                                    descricao = " + ".join(produtos_nomes)
                                    print(f"      • R$ {valor} - {descricao}")
                                else:
                                    print(f"      • R$ {valor} - Produto não especificado")
                            else:
                                print(f"      • R$ {valor} - Erro ao buscar produtos")
        else:
            print("❌ Nenhum responsável encontrado")
        
        print("\n" + "=" * 60)
        print("🎯 ANÁLISE CONCLUÍDA")
        
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analisar_compras_com_produtos() 
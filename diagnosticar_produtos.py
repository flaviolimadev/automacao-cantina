#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problemas na busca de produtos
"""

import os
import requests
from dotenv import load_dotenv
from responsaveis_requests import SupabaseRequests

# Carregar variáveis de ambiente
load_dotenv()

def diagnosticar_produtos():
    """Diagnosticar problemas na busca de produtos"""
    
    print("🔍 DIAGNÓSTICO DE PRODUTOS")
    print("=" * 50)
    
    try:
        supabase = SupabaseRequests()
        
        # 1. Testar conexão básica
        print("1️⃣ Testando conexão com Supabase...")
        print(f"   URL: {supabase.base_url}")
        
        # 2. Buscar produtos
        print("\n2️⃣ Buscando tabela 'produtos'...")
        produtos_response = requests.get(
            f"{supabase.base_url}/produtos",
            headers=supabase.headers
        )
        
        print(f"   Status: {produtos_response.status_code}")
        if produtos_response.status_code == 200:
            produtos = produtos_response.json()
            print(f"   ✅ {len(produtos)} produtos encontrados")
            
            # Mostrar alguns exemplos
            print("\n   📋 Primeiros 3 produtos:")
            for i, produto in enumerate(produtos[:3]):
                print(f"      {i+1}. ID: {produto.get('id')} | Nome: {produto.get('nome')} | Valor: R$ {produto.get('valor', 0)}")
        else:
            print(f"   ❌ Erro: {produtos_response.text}")
            return
        
        # 3. Buscar produtos_comprados
        print("\n3️⃣ Buscando tabela 'produtos_comprados'...")
        produtos_comprados_response = requests.get(
            f"{supabase.base_url}/produtos_comprados",
            headers=supabase.headers
        )
        
        print(f"   Status: {produtos_comprados_response.status_code}")
        if produtos_comprados_response.status_code == 200:
            produtos_comprados = produtos_comprados_response.json()
            print(f"   ✅ {len(produtos_comprados)} relações produtos-comprados encontradas")
            
            # Mostrar alguns exemplos
            print("\n   📋 Primeiras 3 relações:")
            for i, pc in enumerate(produtos_comprados[:3]):
                print(f"      {i+1}. Compra ID: {pc.get('compra_id')} | Produto ID: {pc.get('produto_id')} | Quantidade: {pc.get('quantidade')}")
        else:
            print(f"   ❌ Erro: {produtos_comprados_response.text}")
            return
        
        # 4. Buscar algumas compras para verificar
        print("\n4️⃣ Buscando tabela 'compras' (primeiras 5)...")
        compras_response = requests.get(
            f"{supabase.base_url}/compras?limit=5",
            headers=supabase.headers
        )
        
        print(f"   Status: {compras_response.status_code}")
        if compras_response.status_code == 200:
            compras = compras_response.json()
            print(f"   ✅ {len(compras)} compras encontradas")
            
            # Verificar se há produtos_comprados para essas compras
            produtos_dict = {p['id']: p for p in produtos}
            produtos_por_compra = {}
            for pc in produtos_comprados:
                compra_id = pc['compra_id']
                if compra_id not in produtos_por_compra:
                    produtos_por_compra[compra_id] = []
                produtos_por_compra[compra_id].append(pc)
            
            print("\n   📋 Análise das primeiras compras:")
            for i, compra in enumerate(compras):
                compra_id = compra['id']
                observacoes = compra.get('observacoes', 'Sem observações')
                valor = compra.get('value', 0)
                
                print(f"\n      Compra {i+1}:")
                print(f"        ID: {compra_id}")
                print(f"        Valor: R$ {valor}")
                print(f"        Observações: {observacoes}")
                
                # Verificar se há produtos para esta compra
                if compra_id in produtos_por_compra:
                    print(f"        ✅ {len(produtos_por_compra[compra_id])} produto(s) encontrado(s):")
                    for pc in produtos_por_compra[compra_id]:
                        produto_id = pc['produto_id']
                        quantidade = pc['quantidade']
                        if produto_id in produtos_dict:
                            produto = produtos_dict[produto_id]
                            nome_produto = produto.get('nome', 'Nome não encontrado')
                            print(f"           - {quantidade}x {nome_produto}")
                        else:
                            print(f"           - {quantidade}x [Produto ID {produto_id} não encontrado]")
                else:
                    print("        ⚠️ Nenhum produto encontrado para esta compra")
                    
        else:
            print(f"   ❌ Erro: {compras_response.text}")
        
        print("\n" + "=" * 50)
        print("🎯 DIAGNÓSTICO CONCLUÍDO")
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")

if __name__ == "__main__":
    diagnosticar_produtos() 
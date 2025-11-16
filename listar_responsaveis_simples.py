#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from main import SupabaseConnection

def main():
    """Script simples para listar todos os responsáveis"""
    try:
        # Conectar
        conn = SupabaseConnection()
        
        # Buscar dados
        dados = conn.select_data('responsaveis')
        
        if not dados:
            print("Nenhum responsável encontrado.")
            return
        
        # Exibir
        print(f"Total: {len(dados)} responsáveis\n")
        
        for i, resp in enumerate(dados, 1):
            print(f"{i}. {resp.get('nome', '')} {resp.get('sobrenome', '')}")
            print(f"   Contato: {resp.get('contato', 'N/A')}")
            print(f"   ID: {resp.get('id', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main() 
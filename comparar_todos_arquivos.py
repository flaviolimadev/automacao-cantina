#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar os 41 responsáveis novos (03/08) com todos os outros arquivos CSV
e identificar quais são realmente novos (não aparecem em nenhum arquivo anterior)
"""

import csv
import re
from datetime import datetime

def normalizar_nome(nome):
    """
    Normaliza o nome para comparação, removendo espaços extras e padronizando
    """
    if not nome:
        return ""
    
    # Remove espaços extras e converte para maiúsculas
    nome_normalizado = re.sub(r'\s+', ' ', nome.strip()).upper()
    
    # Remove acentos e caracteres especiais para comparação mais flexível
    nome_sem_acentos = nome_normalizado
    nome_sem_acentos = nome_sem_acentos.replace('Á', 'A').replace('À', 'A').replace('Â', 'A').replace('Ã', 'A')
    nome_sem_acentos = nome_sem_acentos.replace('É', 'E').replace('Ê', 'E')
    nome_sem_acentos = nome_sem_acentos.replace('Í', 'I')
    nome_sem_acentos = nome_sem_acentos.replace('Ó', 'O').replace('Ô', 'O').replace('Õ', 'O')
    nome_sem_acentos = nome_sem_acentos.replace('Ú', 'U')
    nome_sem_acentos = nome_sem_acentos.replace('Ç', 'C')
    
    return nome_sem_acentos

def carregar_responsaveis_arquivo(arquivo):
    """
    Carrega responsáveis de um arquivo CSV (formato flexível)
    """
    responsaveis = set()
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Tenta diferentes nomes de coluna
                nome = (row.get('Nome', '') or 
                       row.get('NOME_COMPLETO', '') or 
                       row.get('nome', '')).strip()
                
                if nome:
                    nome_normalizado = normalizar_nome(nome)
                    responsaveis.add(nome_normalizado)
        
        print(f"✅ Carregados {len(responsaveis)} responsáveis de {arquivo}")
        return responsaveis
        
    except Exception as e:
        print(f"❌ Erro ao carregar {arquivo}: {e}")
        return set()

def carregar_todos_arquivos_anteriores():
    """
    Carrega responsáveis de todos os arquivos anteriores
    """
    arquivos = [
        "responsaveis_com_dividas_20250702_214842.csv",
        "responsaveis_com_dividas_20250702_214717.csv", 
        "responsaveis_com_dividas_20250702_215730.csv",
        "responsaveis_com_dividas_20250702_233812.csv",
        "responsaveis_com_dividas_20250719_151304.csv",
        "responsaveis_com_dividas_20250727_135730.csv",
        "responsaveis_com_dividas_20250727_141835.csv",
        "responsaveis_com_dividas_20250727_140853.csv",
        "responsaveis_com_dividas_20250727_141044.csv"
    ]
    
    todos_responsaveis = set()
    
    for arquivo in arquivos:
        responsaveis = carregar_responsaveis_arquivo(arquivo)
        todos_responsaveis.update(responsaveis)
    
    return todos_responsaveis

def obter_responsaveis_novos_03agosto():
    """
    Obtém os 41 responsáveis que estão no arquivo de 03/08 mas não no de 27/07
    """
    arquivo_27julho = "responsaveis_com_dividas_20250727_144957.csv"
    arquivo_03agosto = "responsaveis_com_dividas_20250803_130614.csv"
    
    responsaveis_27julho = carregar_responsaveis_arquivo(arquivo_27julho)
    responsaveis_03agosto = carregar_responsaveis_arquivo(arquivo_03agosto)
    
    # Responsáveis novos (03/08 - 27/07)
    responsaveis_novos = responsaveis_03agosto - responsaveis_27julho
    
    # Obter dados completos dos responsáveis novos
    dados_completos = []
    
    try:
        with open(arquivo_03agosto, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nome = row.get('Nome', '').strip()
                if nome:
                    nome_normalizado = normalizar_nome(nome)
                    if nome_normalizado in responsaveis_novos:
                        dados_completos.append({
                            'nome': nome,
                            'telefone': row.get('Telefone', ''),
                            'cpf_cnpj': row.get('CPF/CNPJ', ''),
                            'email': row.get('e-mail', ''),
                            'nome_normalizado': nome_normalizado
                        })
        
        return dados_completos
        
    except Exception as e:
        print(f"❌ Erro ao obter dados completos: {e}")
        return []

def main():
    """
    Função principal para comparar todos os arquivos
    """
    print("🔍 COMPARADOR COMPLETO - RESPONSÁVEIS NOVOS vs TODOS OS ARQUIVOS")
    print("=" * 80)
    
    # Carregar responsáveis novos de 03/08
    print("\n📋 Carregando responsáveis novos de 03/08...")
    responsaveis_novos_03agosto = obter_responsaveis_novos_03agosto()
    
    if not responsaveis_novos_03agosto:
        print("❌ Não foi possível carregar os responsáveis novos de 03/08")
        return
    
    print(f"✅ Encontrados {len(responsaveis_novos_03agosto)} responsáveis novos em 03/08")
    
    # Carregar todos os arquivos anteriores
    print("\n📋 Carregando todos os arquivos anteriores...")
    todos_responsaveis_anteriores = carregar_todos_arquivos_anteriores()
    
    print(f"✅ Total de responsáveis em todos os arquivos anteriores: {len(todos_responsaveis_anteriores)}")
    
    # Encontrar responsáveis realmente novos
    nomes_novos_normalizados = {r['nome_normalizado'] for r in responsaveis_novos_03agosto}
    responsaveis_realmente_novos = nomes_novos_normalizados - todos_responsaveis_anteriores
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   • Responsáveis novos em 03/08: {len(responsaveis_novos_03agosto)}")
    print(f"   • Total em arquivos anteriores: {len(todos_responsaveis_anteriores)}")
    print(f"   • Responsáveis REALMENTE novos: {len(responsaveis_realmente_novos)}")
    
    if responsaveis_realmente_novos:
        print(f"\n🆕 RESPONSÁVEIS REALMENTE NOVOS (não aparecem em nenhum arquivo anterior):")
        print("=" * 80)
        
        # Filtrar dados completos dos responsáveis realmente novos
        dados_realmente_novos = [
            r for r in responsaveis_novos_03agosto 
            if r['nome_normalizado'] in responsaveis_realmente_novos
        ]
        
        # Ordenar por nome
        dados_realmente_novos.sort(key=lambda x: x['nome'])
        
        for i, responsavel in enumerate(dados_realmente_novos, 1):
            print(f"{i:2d}. {responsavel['nome']}")
            print(f"    📞 {responsavel['telefone']}")
            if responsavel['cpf_cnpj']:
                print(f"    🆔 {responsavel['cpf_cnpj']}")
            if responsavel['email']:
                print(f"    📧 {responsavel['email']}")
            print()
        
        # Gerar arquivo CSV com os responsáveis realmente novos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = f"responsaveis_realmente_novos_{timestamp}.csv"
        
        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nome', 'Telefone', 'CPF/CNPJ', 'e-mail'])
            
            for responsavel in dados_realmente_novos:
                writer.writerow([
                    responsavel['nome'],
                    responsavel['telefone'],
                    responsavel['cpf_cnpj'],
                    responsavel['email']
                ])
        
        print(f"💾 Arquivo CSV com responsáveis realmente novos gerado: {arquivo_saida}")
        
    else:
        print("\n✅ Nenhum responsável realmente novo encontrado!")
        print("   Todos os responsáveis novos de 03/08 já apareciam em algum arquivo anterior.")
    
    # Mostrar responsáveis que aparecem em arquivos anteriores
    responsaveis_que_aparecem_anteriores = nomes_novos_normalizados & todos_responsaveis_anteriores
    
    if responsaveis_que_aparecem_anteriores:
        print(f"\n📋 RESPONSÁVEIS QUE APARECEM EM ARQUIVOS ANTERIORES ({len(responsaveis_que_aparecem_anteriores)}):")
        print("=" * 80)
        
        dados_que_aparecem = [
            r for r in responsaveis_novos_03agosto 
            if r['nome_normalizado'] in responsaveis_que_aparecem_anteriores
        ]
        
        dados_que_aparecem.sort(key=lambda x: x['nome'])
        
        for i, responsavel in enumerate(dados_que_aparecem, 1):
            print(f"{i:2d}. {responsavel['nome']}")
            print(f"    📞 {responsavel['telefone']}")
            print()
    
    print("\n" + "=" * 80)
    print("🏁 Análise completa concluída!")

if __name__ == "__main__":
    main() 
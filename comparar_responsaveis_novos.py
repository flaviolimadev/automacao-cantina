#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar responsáveis do arquivo responsaveis_novos_03vs27_20250803_130839.csv
com todos os outros arquivos CSV listados e identificar quais são realmente novos.
"""

import csv
import os
from typing import Set, List, Dict

def carregar_responsaveis_arquivo(arquivo: str) -> Set[str]:
    """
    Carrega os nomes dos responsáveis de um arquivo CSV.
    
    Args:
        arquivo: Caminho do arquivo CSV
        
    Returns:
        Conjunto com os nomes dos responsáveis
    """
    responsaveis = set()
    
    if not os.path.exists(arquivo):
        print(f"⚠️ Arquivo não encontrado: {arquivo}")
        return responsaveis
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nome = row.get('Nome', '').strip()
                if nome:
                    responsaveis.add(nome)
        
        print(f"✅ Carregados {len(responsaveis)} responsáveis de {arquivo}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar {arquivo}: {str(e)}")
    
    return responsaveis

def main():
    """Função principal"""
    print("🔍 ANÁLISE DE RESPONSÁVEIS NOVOS")
    print("=" * 60)
    
    # Arquivo principal (responsáveis novos)
    arquivo_principal = "responsaveis_novos_03vs27_20250803_130839.csv"
    
    # Lista de arquivos para comparação
    arquivos_comparacao = [
        "responsaveis_com_dividas_20250702_214717.csv",
        "responsaveis_com_dividas_20250702_214842.csv",
        "responsaveis_com_dividas_20250702_215730.csv",
        "responsaveis_com_dividas_20250702_233812.csv",
        "responsaveis_com_dividas_20250719_151304.csv",
        "responsaveis_com_dividas_20250727_135730.csv",
        "responsaveis_com_dividas_20250727_140853.csv",
        "responsaveis_com_dividas_20250727_141044.csv",
        "responsaveis_com_dividas_20250727_141835.csv",
        "responsaveis_com_dividas_20250727_144957.csv",
        "responsaveis_com_dividas_20250803_130253.csv",
        "responsaveis_com_dividas_20250803_130614.csv",
        "responsaveis_com_dividas_20250810_163926.csv",
        "responsaveis_com_dividas_20250810_164006.csv",
        "responsaveis_com_dividas_20250810_164144.csv",
        "responsaveis_com_dividas_20250817_213203.csv"
    ]
    
    # Carregar responsáveis do arquivo principal
    print(f"📋 Carregando arquivo principal: {arquivo_principal}")
    responsaveis_principais = carregar_responsaveis_arquivo(arquivo_principal)
    
    if not responsaveis_principais:
        print("❌ Nenhum responsável encontrado no arquivo principal")
        return
    
    print(f"\n📊 Total de responsáveis no arquivo principal: {len(responsaveis_principais)}")
    
    # Conjunto para armazenar todos os responsáveis dos arquivos de comparação
    todos_responsaveis_comparacao = set()
    
    # Carregar responsáveis de cada arquivo de comparação
    print(f"\n🔍 Carregando {len(arquivos_comparacao)} arquivos de comparação...")
    
    for arquivo in arquivos_comparacao:
        responsaveis_arquivo = carregar_responsaveis_arquivo(arquivo)
        todos_responsaveis_comparacao.update(responsaveis_arquivo)
    
    print(f"\n📊 Total de responsáveis únicos nos arquivos de comparação: {len(todos_responsaveis_comparacao)}")
    
    # Encontrar responsáveis que estão no arquivo principal mas NÃO estão nos arquivos de comparação
    responsaveis_realmente_novos = responsaveis_principais - todos_responsaveis_comparacao
    
    print(f"\n🎯 RESPONSÁVEIS REALMENTE NOVOS (não encontrados em nenhum arquivo de comparação):")
    print("=" * 60)
    
    if responsaveis_realmente_novos:
        print(f"✅ Encontrados {len(responsaveis_realmente_novos)} responsáveis realmente novos:")
        
        # Ordenar por nome para facilitar a leitura
        for i, nome in enumerate(sorted(responsaveis_realmente_novos), 1):
            print(f"  {i:2d}. {nome}")
        
        # Salvar em arquivo CSV
        arquivo_saida = "responsaveis_realmente_novos_final.csv"
        try:
            with open(arquivo_saida, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Nome', 'Status'])
                for nome in sorted(responsaveis_realmente_novos):
                    writer.writerow([nome, 'REALMENTE NOVO'])
            
            print(f"\n💾 Lista salva em: {arquivo_saida}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {str(e)}")
            
    else:
        print("ℹ️ Nenhum responsável realmente novo encontrado.")
        print("Todos os responsáveis do arquivo principal já existem em pelo menos um arquivo de comparação.")
    
    # Mostrar responsáveis que estão em ambos (para verificação)
    responsaveis_em_ambos = responsaveis_principais & todos_responsaveis_comparacao
    
    if responsaveis_em_ambos:
        print(f"\n📋 RESPONSÁVEIS QUE JÁ EXISTEM (encontrados em pelo menos um arquivo de comparação):")
        print("=" * 60)
        print(f"ℹ️ Encontrados {len(responsaveis_em_ambos)} responsáveis que já existem:")
        
        for i, nome in enumerate(sorted(responsaveis_em_ambos), 1):
            print(f"  {i:2d}. {nome}")
    
    # Estatísticas finais
    print(f"\n📊 RESUMO FINAL:")
    print("=" * 60)
    print(f"📋 Total no arquivo principal: {len(responsaveis_principais)}")
    print(f"🔄 Já existem em outros arquivos: {len(responsaveis_em_ambos)}")
    print(f"🆕 Realmente novos: {len(responsaveis_realmente_novos)}")
    
    if responsaveis_realmente_novos:
        percentual_novos = (len(responsaveis_realmente_novos) / len(responsaveis_principais)) * 100
        print(f"📊 Percentual de responsáveis novos: {percentual_novos:.1f}%")
    
    print("\n✅ Análise concluída!")

if __name__ == "__main__":
    main() 
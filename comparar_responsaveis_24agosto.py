#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar responsáveis do arquivo 24/08/2025 com todos os arquivos anteriores
Identifica responsáveis que são verdadeiramente novos (não aparecem em nenhum arquivo anterior)
"""

import csv
import os
from datetime import datetime

def extrair_nomes_csv(arquivo_csv):
    """Extrai os nomes dos responsáveis de um arquivo CSV"""
    nomes = set()
    
    if not os.path.exists(arquivo_csv):
        print(f"⚠️ Arquivo não encontrado: {arquivo_csv}")
        return nomes
    
    try:
        with open(arquivo_csv, 'r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            
            # Detectar automaticamente a coluna de nome
            colunas = leitor.fieldnames
            coluna_nome = None
            
            for col in colunas:
                if any(palavra in col.upper() for palavra in ['NOME', 'NAME']):
                    coluna_nome = col
                    break
            
            if not coluna_nome:
                print(f"⚠️ Coluna de nome não encontrada em {arquivo_csv}")
                return nomes
            
            for linha in leitor:
                nome = linha.get(coluna_nome, '').strip()
                if nome:
                    nomes.add(nome.upper())  # Normalizar para maiúsculas
                    
        print(f"✅ {arquivo_csv}: {len(nomes)} responsáveis carregados")
        
    except Exception as e:
        print(f"❌ Erro ao ler {arquivo_csv}: {str(e)}")
    
    return nomes

def main():
    print("🔍 COMPARAÇÃO DE RESPONSÁVEIS - 24 DE AGOSTO vs ARQUIVOS ANTERIORES")
    print("=" * 80)
    
    # Arquivo mais recente (24/08)
    arquivo_recente = "responsaveis_com_dividas_20250824_124910.csv"
    
    # Lista de todos os arquivos anteriores
    arquivos_anteriores = [
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
        "responsaveis_com_dividas_20250817_213203.csv",
        "responsaveis_com_dividas_20250810_164006.csv",
        "responsaveis_com_dividas_20250810_164144.csv",
        "responsaveis_com_dividas_20250817_213203_backup.csv",
        "responsaveis_com_dividas_20250817_214620.csv"
    ]
    
    # Carregar responsáveis do arquivo mais recente
    print(f"📥 Carregando arquivo mais recente: {arquivo_recente}")
    responsaveis_recentes = extrair_nomes_csv(arquivo_recente)
    
    if not responsaveis_recentes:
        print("❌ Não foi possível carregar o arquivo mais recente!")
        return
    
    print(f"📊 Total de responsáveis no arquivo de 24/08: {len(responsaveis_recentes)}")
    print()
    
    # Carregar todos os responsáveis dos arquivos anteriores
    print("📥 Carregando arquivos anteriores...")
    responsaveis_historicos = set()
    
    for arquivo in arquivos_anteriores:
        nomes_arquivo = extrair_nomes_csv(arquivo)
        responsaveis_historicos.update(nomes_arquivo)
    
    print(f"📊 Total de responsáveis únicos nos arquivos anteriores: {len(responsaveis_historicos)}")
    print()
    
    # Encontrar responsáveis verdadeiramente novos
    responsaveis_novos = responsaveis_recentes - responsaveis_historicos
    
    print("🔍 RESULTADOS DA ANÁLISE:")
    print("=" * 50)
    print(f"📊 Responsáveis no arquivo 24/08: {len(responsaveis_recentes)}")
    print(f"📊 Responsáveis em arquivos anteriores: {len(responsaveis_historicos)}")
    print(f"🆕 Responsáveis verdadeiramente NOVOS: {len(responsaveis_novos)}")
    print()
    
    if responsaveis_novos:
        print("📋 LISTA DOS RESPONSÁVEIS NOVOS:")
        print("-" * 40)
        for i, nome in enumerate(sorted(responsaveis_novos), 1):
            print(f"{i:2d}. {nome}")
        
        # Salvar em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = f"responsaveis_novos_24agosto_{timestamp}.csv"
        
        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['Nome'])
            for nome in sorted(responsaveis_novos):
                escritor.writerow([nome])
        
        print()
        print(f"💾 Lista dos novos responsáveis salva em: {arquivo_saida}")
        
    else:
        print("✅ Nenhum responsável verdadeiramente novo encontrado!")
        print("   Todos os responsáveis do arquivo 24/08 já apareceram em arquivos anteriores.")
    
    print()
    print("🎉 Análise concluída!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar dois arquivos CSV de responsáveis com dívidas
e identificar quais estão no arquivo mais recente mas não no anterior
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

def carregar_responsaveis_antigo(arquivo):
    """
    Carrega responsáveis do arquivo antigo (formato com TOTAL_DEVIDO)
    """
    responsaveis = set()
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nome = row.get('NOME_COMPLETO', '').strip()
                if nome:
                    nome_normalizado = normalizar_nome(nome)
                    responsaveis.add(nome_normalizado)
        
        print(f"✅ Carregados {len(responsaveis)} responsáveis do arquivo antigo")
        return responsaveis
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo antigo: {e}")
        return set()

def carregar_responsaveis_novo(arquivo):
    """
    Carrega responsáveis do arquivo novo (formato simplificado)
    """
    responsaveis = set()
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nome = row.get('Nome', '').strip()
                if nome:
                    nome_normalizado = normalizar_nome(nome)
                    responsaveis.add(nome_normalizado)
        
        print(f"✅ Carregados {len(responsaveis)} responsáveis do arquivo novo")
        return responsaveis
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo novo: {e}")
        return set()

def encontrar_novos_responsaveis(responsaveis_novo, responsaveis_antigo):
    """
    Encontra responsáveis que estão no arquivo novo mas não no antigo
    """
    novos = responsaveis_novo - responsaveis_antigo
    return novos

def obter_dados_completos_novos(arquivo_novo, nomes_novos):
    """
    Obtém os dados completos dos responsáveis novos
    """
    dados_completos = []
    
    try:
        with open(arquivo_novo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nome = row.get('Nome', '').strip()
                if nome:
                    nome_normalizado = normalizar_nome(nome)
                    if nome_normalizado in nomes_novos:
                        dados_completos.append({
                            'nome': nome,
                            'telefone': row.get('Telefone', ''),
                            'cpf_cnpj': row.get('CPF/CNPJ', ''),
                            'email': row.get('e-mail', '')
                        })
        
        return dados_completos
        
    except Exception as e:
        print(f"❌ Erro ao obter dados completos: {e}")
        return []

def main():
    """
    Função principal para comparar os arquivos
    """
    print("🔍 COMPARADOR DE ARQUIVOS CSV - RESPONSÁVEIS COM DÍVIDAS")
    print("=" * 70)
    
    # Arquivos a comparar
    arquivo_antigo = "responsaveis_com_dividas_20250702_214717.csv"
    arquivo_novo = "responsaveis_com_dividas_20250719_151304.csv"
    
    print(f"📁 Arquivo antigo: {arquivo_antigo}")
    print(f"📁 Arquivo novo: {arquivo_novo}")
    print("=" * 70)
    
    # Carregar responsáveis dos dois arquivos
    responsaveis_antigo = carregar_responsaveis_antigo(arquivo_antigo)
    responsaveis_novo = carregar_responsaveis_novo(arquivo_novo)
    
    if not responsaveis_antigo or not responsaveis_novo:
        print("❌ Não foi possível carregar um dos arquivos")
        return
    
    # Encontrar responsáveis novos
    responsaveis_novos = encontrar_novos_responsaveis(responsaveis_novo, responsaveis_antigo)
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   • Total no arquivo antigo: {len(responsaveis_antigo)}")
    print(f"   • Total no arquivo novo: {len(responsaveis_novo)}")
    print(f"   • Responsáveis novos: {len(responsaveis_novos)}")
    
    if responsaveis_novos:
        print(f"\n🆕 RESPONSÁVEIS NOVOS (estão no arquivo novo mas não no antigo):")
        print("=" * 70)
        
        # Obter dados completos dos responsáveis novos
        dados_novos = obter_dados_completos_novos(arquivo_novo, responsaveis_novos)
        
        # Ordenar por nome
        dados_novos.sort(key=lambda x: x['nome'])
        
        for i, responsavel in enumerate(dados_novos, 1):
            print(f"{i:2d}. {responsavel['nome']}")
            print(f"    📞 {responsavel['telefone']}")
            if responsavel['cpf_cnpj']:
                print(f"    🆔 {responsavel['cpf_cnpj']}")
            if responsavel['email']:
                print(f"    📧 {responsavel['email']}")
            print()
        
        # Gerar arquivo CSV com os novos responsáveis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = f"responsaveis_novos_{timestamp}.csv"
        
        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nome', 'Telefone', 'CPF/CNPJ', 'e-mail'])
            
            for responsavel in dados_novos:
                writer.writerow([
                    responsavel['nome'],
                    responsavel['telefone'],
                    responsavel['cpf_cnpj'],
                    responsavel['email']
                ])
        
        print(f"💾 Arquivo CSV com responsáveis novos gerado: {arquivo_saida}")
        
    else:
        print("\n✅ Nenhum responsável novo encontrado!")
        print("   Todos os responsáveis do arquivo novo já estavam no arquivo antigo.")
    
    print("\n" + "=" * 70)
    print("🏁 Análise concluída!")

if __name__ == "__main__":
    main() 
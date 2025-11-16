#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar dois arquivos CSV de responsáveis com dívidas
e identificar quais estão no arquivo mais recente (27/07 144957) mas não no anterior (19/07)
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

def carregar_responsaveis_19julho(arquivo):
    """
    Carrega responsáveis do arquivo de 19/07
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
        
        print(f"✅ Carregados {len(responsaveis)} responsáveis do arquivo de 19/07")
        return responsaveis
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo de 19/07: {e}")
        return set()

def carregar_responsaveis_27julho(arquivo):
    """
    Carrega responsáveis do arquivo de 27/07 (144957)
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
        
        print(f"✅ Carregados {len(responsaveis)} responsáveis do arquivo de 27/07 (144957)")
        return responsaveis
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo de 27/07: {e}")
        return set()

def encontrar_novos_responsaveis(responsaveis_27julho, responsaveis_19julho):
    """
    Encontra responsáveis que estão no arquivo de 27/07 mas não no de 19/07
    """
    novos = responsaveis_27julho - responsaveis_19julho
    return novos

def obter_dados_completos_novos(arquivo_27julho, nomes_novos):
    """
    Obtém os dados completos dos responsáveis novos
    """
    dados_completos = []
    
    try:
        with open(arquivo_27julho, 'r', encoding='utf-8') as file:
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

def criar_arquivo_novos(dados_novos):
    """
    Cria arquivo CSV apenas com os responsáveis novos
    """
    try:
        nome_arquivo = "responsaveis_novos_27julho_144957.csv"
        
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nome', 'Telefone', 'CPF/CNPJ', 'e-mail'])
            
            for responsavel in dados_novos:
                writer.writerow([
                    responsavel['nome'],
                    responsavel['telefone'],
                    responsavel['cpf_cnpj'],
                    responsavel['email']
                ])
        
        print(f"💾 Arquivo criado: {nome_arquivo}")
        return nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")
        return None

def main():
    """
    Função principal para comparar os arquivos
    """
    print("🔍 COMPARADOR DE ARQUIVOS CSV - RESPONSÁVEIS COM DÍVIDAS")
    print("=" * 70)
    
    # Arquivos a comparar
    arquivo_19julho = "responsaveis_com_dividas_20250719_151304.csv"
    arquivo_27julho = "responsaveis_com_dividas_20250727_144957.csv"
    
    print(f"📁 Arquivo 19/07: {arquivo_19julho}")
    print(f"📁 Arquivo 27/07: {arquivo_27julho}")
    print("=" * 70)
    
    # Carregar responsáveis dos dois arquivos
    responsaveis_19julho = carregar_responsaveis_19julho(arquivo_19julho)
    responsaveis_27julho = carregar_responsaveis_27julho(arquivo_27julho)
    
    if not responsaveis_19julho or not responsaveis_27julho:
        print("❌ Não foi possível carregar um dos arquivos")
        return
    
    # Encontrar responsáveis novos
    responsaveis_novos = encontrar_novos_responsaveis(responsaveis_27julho, responsaveis_19julho)
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   • Total no arquivo 19/07: {len(responsaveis_19julho)}")
    print(f"   • Total no arquivo 27/07: {len(responsaveis_27julho)}")
    print(f"   • Responsáveis novos (27/07): {len(responsaveis_novos)}")
    
    if responsaveis_novos:
        print(f"\n🆕 RESPONSÁVEIS NOVOS (estão no arquivo 27/07 mas não no 19/07):")
        print("=" * 70)
        
        # Obter dados completos dos responsáveis novos
        dados_novos = obter_dados_completos_novos(arquivo_27julho, responsaveis_novos)
        
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
        
        # Criar arquivo CSV com os novos responsáveis
        arquivo_criado = criar_arquivo_novos(dados_novos)
        
        if arquivo_criado:
            print(f"✅ Arquivo criado com sucesso: {arquivo_criado}")
            print(f"📊 {len(dados_novos)} responsáveis novos incluídos")
        
    else:
        print("\n✅ Nenhum responsável novo encontrado!")
        print("   Todos os responsáveis do arquivo 27/07 já estavam no arquivo 19/07.")
    
    print("\n" + "=" * 70)
    print("🏁 Análise concluída!")

if __name__ == "__main__":
    main() 
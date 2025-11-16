#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar responsaveis_com_dividas_20250803_130614.csv vs responsaveis_com_dividas_20250727_144957.csv
e identificar quais responsáveis estão no arquivo de 03/08 mas não no de 27/07
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

def carregar_responsaveis_27julho(arquivo):
    """
    Carrega responsáveis do arquivo de 27/07
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
        
        print(f"✅ Carregados {len(responsaveis)} responsáveis do arquivo de 27/07")
        return responsaveis
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo de 27/07: {e}")
        return set()

def carregar_responsaveis_03agosto(arquivo):
    """
    Carrega responsáveis do arquivo de 03/08
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
        
        print(f"✅ Carregados {len(responsaveis)} responsáveis do arquivo de 03/08")
        return responsaveis
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo de 03/08: {e}")
        return set()

def encontrar_novos_responsaveis(responsaveis_03agosto, responsaveis_27julho):
    """
    Encontra responsáveis que estão no arquivo de 03/08 mas não no de 27/07
    """
    novos = responsaveis_03agosto - responsaveis_27julho
    return novos

def obter_dados_completos_novos(arquivo_03agosto, nomes_novos):
    """
    Obtém os dados completos dos responsáveis novos
    """
    dados_completos = []
    
    try:
        with open(arquivo_03agosto, 'r', encoding='utf-8') as file:
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
    print("🔍 COMPARADOR: 27/07 vs 03/08 - RESPONSÁVEIS COM DÍVIDAS")
    print("=" * 70)
    
    # Arquivos a comparar
    arquivo_27julho = "responsaveis_com_dividas_20250727_144957.csv"
    arquivo_03agosto = "responsaveis_com_dividas_20250803_130614.csv"
    
    print(f"📁 Arquivo de 27/07: {arquivo_27julho}")
    print(f"📁 Arquivo de 03/08: {arquivo_03agosto}")
    print("=" * 70)
    
    # Carregar responsáveis dos dois arquivos
    responsaveis_27julho = carregar_responsaveis_27julho(arquivo_27julho)
    responsaveis_03agosto = carregar_responsaveis_03agosto(arquivo_03agosto)
    
    if not responsaveis_27julho or not responsaveis_03agosto:
        print("❌ Não foi possível carregar um dos arquivos")
        return
    
    # Encontrar responsáveis novos
    responsaveis_novos = encontrar_novos_responsaveis(responsaveis_03agosto, responsaveis_27julho)
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   • Total no arquivo de 27/07: {len(responsaveis_27julho)}")
    print(f"   • Total no arquivo de 03/08: {len(responsaveis_03agosto)}")
    print(f"   • Responsáveis novos (03/08): {len(responsaveis_novos)}")
    
    if responsaveis_novos:
        print(f"\n🆕 RESPONSÁVEIS NOVOS (estão em 03/08 mas não em 27/07):")
        print("=" * 70)
        
        # Obter dados completos dos responsáveis novos
        dados_novos = obter_dados_completos_novos(arquivo_03agosto, responsaveis_novos)
        
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
        arquivo_saida = f"responsaveis_novos_03vs27_{timestamp}.csv"
        
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
        print("   Todos os responsáveis do arquivo de 03/08 já estavam no arquivo de 27/07.")
    
    print("\n" + "=" * 70)
    print("🏁 Análise concluída!")

if __name__ == "__main__":
    main() 
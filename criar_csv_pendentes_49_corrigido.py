#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar CSV apenas com responsáveis pendentes (VERSÃO CORRIGIDA)
Baseado na comparação com relatório do Infinite Pay
"""

import csv
from typing import List, Dict

def normalizar_nome(nome: str) -> str:
    """
    Normaliza nome removendo espaços extras e convertendo para maiúsculas
    """
    return ' '.join(nome.split()).upper()

def criar_csv_pendentes():
    """
    Cria CSV apenas com os 49 responsáveis pendentes
    """
    
    # Lista dos 49 responsáveis que estão faltando no relatório
    responsaveis_pendentes = [
        "ADRIANA SANTOS LEÔNCIO BRANDÃO",
        "ADRIANO ELISMAEL MACÊDO DE PAIVA",
        "ALEXANDRA LIMA BEZERRA",
        "ALINE MANETTI LOPES BARANSKI",
        "ANA CLEIDE DE AGUIAR FERREIRA",
        "ANA LUIZA DOS SANTOS CRUZ",
        "ASENATE DAMARIS CAETANO DA ROCHA",
        "AURICEA MARIA DE MEDEIROS",
        "BERENICE DE CARVALHO SOUSA",
        "CARLA PAVONE SANTISTEBAN",
        "CARLA SONEIDE DA SILVA OLIVEIRA BATISTA",
        "CASSIA CASTILHO MAROTTI",
        "CHRISTIELLE DE LIMA CONRADO",
        "CLEBER PEDRO DE OLIVEIRA",
        "DIUANA NUNES DA SILVA",
        "ELIANDERSON OLIVEIRA DOS SANTOS",
        "ELIZANDRO HEBERT RENOVATO DE MIRANDA",
        "EMILIANE FRANCISCA DA SILVA LUCENA",
        "FLAVIA DE OLIVEIRA GOMES DE ARAÚJO",
        "GIULLIANE ROCHA BOTARELI DANTAS",
        "HAGAR MARIA DE ANDRADE PINHEIRO",
        "IRANIR RIBEIRO DA SILVA BATISTA",
        "JAMILE MARQUES BARROS DA SILVA",
        "JANAINA ATALIBA DE MELO SOUZA",
        "JANAÍNA CORDULA DO LAGO",
        "JAZIA AMARILES DA SILVA OLIVEIRA",
        "JEFFERSON WLLISSES NASCIMENTO DE SOUZA",
        "JESSICA KAROLINE CAMPOS COSTA",
        "KENNYA AMORIM DE LIMA GRALHA",
        "LAURIANO DA SILVA COUTO",
        "LUCAS RAMATIS",
        "LUCIANA MONTEIRO MARQUES",
        "MARCIA TALITA",
        "MARCOS AURELIO PEREIRA DE AZEVEDO",
        "MARCOS DELGADO DA SILVA",
        "MARCOS SANT'ANNA DA SILVA JUNIOR",
        "MARIA DE FATIMA DA SILVA FARIAS SOARES",
        "MARIA DE FATIMA DA SILVA LIMA",
        "MARIA JOSENY",
        "MARIA MARILENE DE OLIVEIRA",
        "MARIANA SILVA",
        "MARIANGELA MOTA DE OLIVEIRA NUNES",
        "MARILIA DE MOURA CAFÉ FREIRE",
        "O'HARA DANIELE SOARES COUTINHO",
        "PAULA LILIANE MEDEIROS DA CONCEIÇÃO",
        "ROSINARA DA SILVA BORGES SANTANA",
        "RUTE MEDEIROS DE ALBUQUERQUE",
        "SUELY ALESSANDRA DA SILVA ALVES",
        "VERANA SIMÃO DE HOLANDA MOURA"
    ]
    
    # Normalizar nomes da lista
    responsaveis_pendentes_normalizados = [normalizar_nome(nome) for nome in responsaveis_pendentes]
    
    # Ler dados completos do CSV original
    dados_completos = {}
    nomes_encontrados = 0
    
    try:
        with open("responsaveis_com_dividas_20250831_170501.csv", 'r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                nome_original = linha['Nome'].strip()
                nome_normalizado = normalizar_nome(nome_original)
                
                # Verificar se este nome está na lista de pendentes
                if nome_normalizado in responsaveis_pendentes_normalizados:
                    dados_completos[nome_normalizado] = linha
                    nomes_encontrados += 1
                    
    except FileNotFoundError:
        print("❌ Arquivo responsaveis_com_dividas_20250831_170501.csv não encontrado")
        return
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {str(e)}")
        return
    
    print(f"✅ Encontrados {nomes_encontrados} responsáveis no CSV original")
    
    # Criar CSV apenas com os pendentes
    arquivo_saida = "responsaveis_pendentes_49_corrigido.csv"
    
    try:
        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as arquivo:
            # Cabeçalho
            writer = csv.writer(arquivo)
            writer.writerow(['Nome', 'Telefone', 'CPF/CNPJ', 'e-mail'])
            
            # Dados dos responsáveis pendentes
            for nome_normalizado in responsaveis_pendentes_normalizados:
                if nome_normalizado in dados_completos:
                    linha = dados_completos[nome_normalizado]
                    writer.writerow([
                        linha['Nome'],
                        linha['Telefone'],
                        linha['CPF/CNPJ'],
                        linha['e-mail']
                    ])
                else:
                    print(f"⚠️ Nome não encontrado no CSV original: {nome_normalizado}")
        
        print(f"✅ CSV criado com sucesso: {arquivo_saida}")
        print(f"📊 Total de responsáveis: {len(responsaveis_pendentes)}")
        
        # Verificar se todos foram incluídos
        with open(arquivo_saida, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()
            total_linhas = len(linhas) - 1  # -1 para excluir cabeçalho
            print(f"📝 Linhas no arquivo (excluindo cabeçalho): {total_linhas}")
            
            if total_linhas == len(responsaveis_pendentes):
                print("✅ Todos os responsáveis foram incluídos corretamente")
            else:
                print(f"⚠️ Diferença encontrada: {len(responsaveis_pendentes)} esperados vs {total_linhas} incluídos")
                
    except Exception as e:
        print(f"❌ Erro ao criar CSV: {str(e)}")

def main():
    print("📝 CRIADOR DE CSV PENDENTES (VERSÃO CORRIGIDA)")
    print("=" * 50)
    print("🎯 Criando CSV apenas com responsáveis pendentes...")
    print("🔧 Normalizando nomes para lidar com espaços extras")
    
    criar_csv_pendentes()
    
    print("\n" + "=" * 50)
    print("🎯 PRÓXIMOS PASSOS:")
    print("=" * 50)
    print("1. ✅ CSV responsaveis_pendentes_49_corrigido.csv criado")
    print("2. 🔄 Atualizar automatizar_cobrancas.py")
    print("3. 🚀 Executar automação com lista completa")
    
    print("\n✨ Processo concluído!")

if __name__ == "__main__":
    main()

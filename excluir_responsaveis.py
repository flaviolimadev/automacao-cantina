#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para excluir responsáveis específicos do arquivo CSV.
"""

import csv
import os
from typing import Set, List

def excluir_responsaveis():
    """Exclui os responsáveis especificados do arquivo CSV"""
    
    # Arquivo original
    arquivo_original = "responsaveis_com_dividas_20250817_213203.csv"
    
    # Arquivo de backup
    arquivo_backup = "responsaveis_com_dividas_20250817_213203_backup.csv"
    
    # Lista de responsáveis a serem excluídos
    responsaveis_excluir = {
        "MARIA EDUARDA DANTAS TAVARES DA SILVA",
        "LUCAS GABRIEL NUNES DOS SANTOS SÉTIMO B",
        "JULIENE ANGELICA RODRIGUES MASCARENHAS MOURA",
        "BETANIA SILVA DE ARAUJO MEDEIROS",
        "JAQUELINE WANDERLEI",
        "TALIANE SUERDA DE MORA SILVA",
        "AGOSTINHO JUSTINO DE ANDRADE NETO",
        "YASMIN MEDEIROS SILVA",
        "JOSEFA JEOVANIA TEIXEIRA DE OLIVEIRA DIAS",
        "KALINE RODRIGUES DE FREITAS PAIVA",
        "DIÓGENES PEREIRA DA SILVA",
        "IRANIR RIBEIRO DA SILVA BATISTA",
        "MARTA DE HOLLANDA FRANCO ALBUQUERQUE",
        "ANA CLEIDE DE AGUIAR FERREIRA",
        "FRANCIDALVA PEDRO DOS SANTOS",
        "JULLIETE GONÇALVES DE OLIVEIRA PIMENTA",
        "ADRIANO ELISMAEL MACÊDO DE PAIVA",
        "O'HARA DANIELE SOARES COUTINHO",
        "MARIA MICARLA DE FREITAS",
        "ANA CAROLINA MAIA DE SÁ",
        "MARCOS AURELIO PEREIRA DE AZEVEDO",
        "MARIA IVANILDA BERNADINO DA SILVA SEGUNDO",
        "LIGIA ANDERSON DA SILVA COSTA ARAUJO",
        "ARQUIMEDES JOSE EPIFANIO DA SILVA",
        "NAIRA CAROLINE DE OLIVEIRA BRITO",
        "ELIANA CARLA GOMES DE ALBUQUERQUE MONTEIRO",
        "TALITTA SANTOS NEVES",
        "JUCIARA MARIA SILVA DO NASCIMENTO",
        "KARLA DANIELLA VIEIRA E SILVA ARAUJO",
        "JOELMA MATIAS",
        "VANESSA GOSSON GADELHA DE FREITAS FORTES",
        "ANA CAROLINA NOVAES FERNANDES",
        "PRISCILA GOMES DE OLIVEIRA",
        "SAMARA LOPES DE QUEIROZ",
        "ADRIANA DA SILVA FERNANDES CAMBERLIN",
        "BETANIA CARDOSO",
        "MIKAELY LISIANE DIAS DE AQUINO OLIVEIRA",
        "MARCOS SANT'ANNA DA SILVA JUNIOR",
        "FERNANDA EDIKA DE SOUZA LOPES",
        "CARLA PAVONE SANTISTEBAN",
        "CASSIA CASTILHO MAROTTI",
        "REBECA DA ROCHA MARQUES LOPES",
        "MARIA JOSENY",
        "PATRICIA TORRES",
        "NEUSSANA KELLEN DE ARAUJO MEDEIROS TORREÃO",
        "MICARLA GOMES DE PONTES",
        "VIVIANE ARNAUD LOPES DIAS",
        "DIUANA NUNES DA SILVA",
        "SUELY ALESSANDRA DA SILVA ALVES",
        "EMILIANE FRANCISCA DA SILVA LUCENA",
        "LÚCIO CARLOS DE OLIVEIRA BARBOSA",
        "MISSERINE DEL VALLE CARVALHO VICUNA",
        "SUZETE L OP ES GALVÃO",
        "LUCIANA MONTEIRO MARQUES",
        "ERIKA PRISCILLA",
        "MACLI IRVING DA SILVA",
        "KENNYA AMORIM DE LIMA GRALHA",
        "PRISCILA GABRIELA SOUZA DA SILVA MUNHOZ",
        "KRYSSIA ALEIXO DE SOUZA CAROLINO DE MELO",
        "ELIANDERSON OLIVEIRA DOS SANTOS",
        "TASSIA CAMILA DA SILVA",
        "JEANE DOS SANTOS LIMA",
        "ISABELLY THUANY DE FREITAS CARVALHO",
        "SARA RUANA",
        "AURICEA MARIA DE MEDEIROS",
        "VERANA SIMÃO DE HOLANDA MOURA",
        "PAULO CESAR DE LIMA",
        "MARCUS VINICIUS DOS SANTOS COSTA",
        "EDUARDO LIMA DE SANTANA",
        "FLAVIO FIGUEREDO SEGUNDO",
        "CHARLENE GABRIEL SOARES DE MELO",
        "ANDREZZA SIMOES DA SILVA",
        "DANIELLY CRISTINA BEZERRA DE SOUZA ALMEIDA",
        "MIRIÃ KELLY CHAGAS DO NASCIMENTO OLIVEIRA",
        "LAYANE ORRICO",
        "GABRIELA ARAUJO SARAIVA NERY"
    }
    
    print(f"🔍 ANÁLISE DE EXCLUSÃO DE RESPONSÁVEIS")
    print("=" * 60)
    print(f"📄 Arquivo original: {arquivo_original}")
    print(f"📄 Arquivo de backup: {arquivo_backup}")
    print(f"🗑️ Responsáveis a excluir: {len(responsaveis_excluir)}")
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_original):
        print(f"❌ Arquivo não encontrado: {arquivo_original}")
        return
    
    # Ler arquivo original
    responsaveis_originais = []
    responsaveis_mantidos = []
    responsaveis_encontrados = set()
    
    try:
        with open(arquivo_original, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            responsaveis_originais = list(reader)
            
        print(f"✅ Arquivo lido com sucesso")
        print(f"📊 Total de responsáveis originais: {len(responsaveis_originais)}")
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {str(e)}")
        return
    
    # Criar backup
    try:
        with open(arquivo_backup, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=responsaveis_originais[0].keys())
            writer.writeheader()
            writer.writerows(responsaveis_originais)
        
        print(f"✅ Backup criado: {arquivo_backup}")
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {str(e)}")
        return
    
    # Filtrar responsáveis
    for responsavel in responsaveis_originais:
        nome = responsavel.get('Nome', '').strip()
        if nome in responsaveis_excluir:
            responsaveis_encontrados.add(nome)
            print(f"🗑️ Excluindo: {nome}")
        else:
            responsaveis_mantidos.append(responsavel)
    
    # Verificar responsáveis não encontrados
    responsaveis_nao_encontrados = responsaveis_excluir - responsaveis_encontrados
    if responsaveis_nao_encontrados:
        print(f"\n⚠️ RESPONSÁVEIS NÃO ENCONTRADOS NO ARQUIVO:")
        for nome in sorted(responsaveis_nao_encontrados):
            print(f"   - {nome}")
    
    # Salvar arquivo filtrado
    try:
        with open(arquivo_original, 'w', newline='', encoding='utf-8') as file:
            if responsaveis_mantidos:
                writer = csv.DictWriter(file, fieldnames=responsaveis_mantidos[0].keys())
                writer.writeheader()
                writer.writerows(responsaveis_mantidos)
        
        print(f"\n✅ Arquivo atualizado com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {str(e)}")
        return
    
    # Estatísticas finais
    print(f"\n📊 RESUMO FINAL:")
    print("=" * 60)
    print(f"📋 Total original: {len(responsaveis_originais)}")
    print(f"🗑️ Excluídos: {len(responsaveis_encontrados)}")
    print(f"✅ Mantidos: {len(responsaveis_mantidos)}")
    print(f"📄 Backup salvo em: {arquivo_backup}")
    
    if responsaveis_nao_encontrados:
        print(f"⚠️ Responsáveis não encontrados: {len(responsaveis_nao_encontrados)}")
    
    print(f"\n✅ Processo concluído!")

if __name__ == "__main__":
    excluir_responsaveis() 
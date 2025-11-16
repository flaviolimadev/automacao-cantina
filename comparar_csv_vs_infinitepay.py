#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar responsáveis do CSV com o relatório de cobranças do Infinite Pay
Identifica quais responsáveis estão no CSV mas não aparecem no relatório
"""

import csv
import re
from datetime import datetime

def extrair_nomes_csv(arquivo_csv):
    """Extrai os nomes dos responsáveis do arquivo CSV"""
    nomes = set()
    
    try:
        with open(arquivo_csv, 'r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            
            for linha in leitor:
                nome = linha.get('Nome', '').strip()
                if nome:
                    # Normalizar nome (maiúsculas e remover espaços extras)
                    nome_normalizado = ' '.join(nome.upper().split())
                    nomes.add(nome_normalizado)
                    
        print(f"✅ CSV: {len(nomes)} responsáveis carregados")
        
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {str(e)}")
    
    return nomes

def extrair_nomes_relatorio():
    """Extrai os nomes dos responsáveis do relatório do Infinite Pay"""
    
    # Lista dos nomes que aparecem no relatório (extraído do texto fornecido)
    nomes_relatorio = [
        "ANDREZA KARINA ALVES PAIVA DUARTE",
        "ANDREZZA DE FATIMA", 
        "KRISTIANE GLACIENE NUNES FILGUEIRA CAMARA",
        "AURICEA MARIA DE MEDEIROS",
        "MARCOS SANT'ANNA DA SILVA JUNIOR",
        "LIDNADJA CRISTINA SILVEIRA DE SOUZA",
        "BETANIA SILVA DE ARAUJO MEDEIROS",
        "DEBORAH VICTÓRIA MARQUES DE FREIRAS",
        "TATIANA LARISSA DE MOURA ALVES",
        "ELAINNE VANESSA DE ANDRADE CLEMENTINO",
        "MARIANGELA MOTA DE OLIVEIRA NUNES",
        "TATIANA DE CARVALHO MACHADO",
        "MARIA EDUARDA DANTAS TAVARES DA SILVA",
        "ALDENISE RAMOS CARNEIRO DA CUNHA",
        "VIVIANE ARNAUD LOPES DIAS",
        "EMILIANE FRANCISCA DA SILVA LUCENA",
        "ANDREZA CARVALHO DE LIMA TELLES",
        "GENIFFER LIMA DE BRITO MELO",
        "O'HARA DANIELE SOARES COUTINHO",
        "EMILVA DANTAS DA SILVA MENDONÇA",
        "CLEBER PEDRO DE OLIVEIRA",
        "JULIANA GONÇALO",
        "TASSIA CAMILA DA SILVA",
        "NILMA CRISTINA",
        "ANDREZZA SIMOES DA SILVA",
        "ADRIANO ELISMAEL MACÊDO DE PAIVA",
        "AMANDA AMANDA",
        "KAYNIELLE VANELE",
        "VERANA SIMÃO DE HOLANDA MOURA",
        "CRISTIANNE MARCELLE MEDEIROS DOS SANTOS MELO",
        "JAQUELINE WANDERLEI",
        "ELIANE DA SILVA RODRIGUES",
        "RITA HELAINE ABREU DE ALMEIDA PAIVA",
        "MARIANA DE LIMA SOUZA DELGADO",
        "MARIA ISABEL RAMALHO GONCALVES",
        "PONCIO PABLO BERTOLDO DA COSTA",
        "MARIA ORLANDA MARTINS DAS NEVES",
        "VANESSA DA SILVA CRUZ COSTA",
        "KATIA FERNANDES",
        "JANAÍNA CORDULA DO LAGO",
        "SAMARA LOPES DE QUEIROZ",
        "MARIA DE FATIMA ARAUJO",
        "DAYANNY DUARTE DE MOURA FERREIRA",
        "GLADYS NUNES VIEIRA",
        "RAYANE PONTES",
        "PAULO CESAR DE LIMA",
        "HAGAR MARIA DE ANDRADE PINHEIRO",
        "LISANDRA ALMEIDA DE OLIVEIRA",
        "KARLA DANIELLA VIEIRA E SILVA ARAUJO",
        "SUZETE L OP ES GALVÃO",
        "LIGIA ANDERSON DA SILVA COSTA ARAUJO",
        "TALIANE SUERDA DE MORA SILVA",
        "TALITTA SANTOS NEVES",
        "LAYANE ORRICO",
        "CRISTIANO DE ARAUJO CASTRO",
        "FRANCIDALVA PEDRO DOS SANTOS",
        "ANDRÉA KALINE COSTA DA SILVA",
        "MIKAELY LISIANE DIAS DE AQUINO OLIVEIRA",
        "FERNANDA EDIKA DE SOUZA LOPES",
        "RODRIGO REGLY CARVAL HO",
        "JULIENNE DANTAS DE CARVALHO NUNES",
        "KELLYANE CRISTINE PRATA DE LUCENA RIBEIRO",
        "ELOIZA DOS SANTOS RAIMUNDO",
        "SARAH SASKYA SERAFIM DE ARAÚJO",
        "MARIA JOSENY",
        "KATIA ALVES MALHEIROS",
        "JULIETE SANTOS",
        "MARIA IVANILDA BERNADINO DA SILVA SEGUNDO",
        "MARUSK MIKAELLY ALVES DE LIMA",
        "ERIKACIA DA SILVA BATISTA DOURADO",
        "JUCIARA MARIA SILVA DO NASCIMENTO",
        "LÚCIO CARLOS DE OLIVEIRA BARBOSA",
        "BETANIA CARDOSO",
        "YANNE BARRETO",
        "ANA CAROLINA MAIA DE SÁ",
        "MARIA MICARLA DE FREITAS",
        "ANDREZA LIMA DE OLIVEIRA",
        "MACLI IRVING DA SILVA",
        "KALINE RODRIGUES DE FREITAS PAIVA",
        "JULIENE ANGELICA RODRIGUES MASCARENHAS MOURA",
        "ARQUIMEDES JOSE EPIFANIO DA SILVA",
        "CHARLENE GABRIEL SOARES DE MELO",
        "VANIA CLEIDE DE MORAIS SILVA LIRA",
        "MONICA PATRICIA LINHARES",
        "GABRIELA ARAUJO SARAIVA NERY",
        "ANA RAPHAELLA BARROCA FRANCO",
        "KENNYA AMORIM DE LIMA GRALHA",
        "LUCAS GABRIEL NUNES DOS SANTOS SÉTIMO B",
        "GIULLIANE ROCHA BOTARELI DANTAS",
        "SUELY ALESSANDRA DA SILVA ALVES",
        "JACQUELINE EVANGELISTA DE SOUSA",
        "ROSINARA DA SILVA BORGES SANTANA",
        "FLAVIO FIGUEREDO SEGUNDO",
        "GISLAINE TCHARLIANE CARDOSO PEREIRA DA COSTA",
        "PRISCILA GABRIELA SOUZA DA SILVA MUNHOZ",
        "ROBERTA MONTEIRO DE SOUZA VIEIRA",
        "DAYSE SOARES DOS SANTOS",
        "ADRIANA SANTOS LEÔNCIO BRANDÃO",
        "MARCUS VINICIUS DOS SANTOS COSTA",
        "MISSERINE DEL VALLE CARVAJAL VICUNA",
        "ANDRE MARCOS DA CUNHA VARELA",
        "JAQUELINE GOMES GOMES DA SILVA",
        "JESSICA KAROLINE CAMPOS COSTA",
        "CARLA SONEIDE DA SILVA OLIVEIRA BATISTA",
        "SARA RUANA",
        "NATHALLYA KARELLYNE INACIO DUARTE DE MELO OLIVEIRA",
        "VALDICE BERNADO DA SILVA PEREIRA",
        "ROBEILTON AZEVED O DA SILVA GOMES",
        "FRANCISCA VANESSA ARAÚJO DE SOUZA",
        "PATRICIA TORRES",
        "MARCOS DELGADO DA SILVA",
        "ANA CAROLINA NOVAES FERNANDES",
        "ANDREZA CABRAL CÂMARA NUNES",
        "SUERDA MEDEIROS DE SOUZA SANTOS",
        "MÔNICA REJANE",
        "HELENA LEITE DA SILVA ALENCAR",
        "YARA ANGELICA ALVES FERNANDES",
        "ASENATE DAMARIS CAETANO DA ROCHA",
        "MIGUEL CAMILO PENA",
        "MAGNOLIA FAGUNDES ALVES BARBOSA",
        "ELISANDRA MARIA DA SILVA ANTAS",
        "DIÓGENES PEREIRA DA SILVA",
        "PATRICIA LOPES DA SILVA",
        "MARTA DE HOLLANDA FRANCO ALBUQUERQUE",
        "ALESSANDRA BELLAGUARDA",
        "RAFAELY PRISCILLA DA SILVA FÉLIX",
        "EDUARDO LIMA DE SANTANA",
        "NEUSSANA KELLEN DE ARAUJO MEDEIROS TORREÃO",
        "FELIPE LANDEIRA",
        "LUCIANA MONTEIRO MARQUES",
        "ELIZANDRO HEBERT RENOVATO DE MIRANDA",
        "EDIONE MENDONÇA MACARIO",
        "DANIELE DUARTE MENDONÇA BARBOSA",
        "DIUANA NUNES DA SILVA",
        "FABIANA FREIRE RODRIGUES DE MEDEIROS",
        "FERNANDA CRISTINA DA SILVA MEDEIROS",
        "FLAVIANA BEZERRA LEAO FONSECA",
        "KATIA PATRICIA DE OLIVEIRA AQUINO",
        "KRYSSIA ALEIXO DE SOUZA CAROLINO DE MELO",
        "MARIA MARILENE DE OLIVEIRA",
        "JEANE DOS SANTOS LIMA",
        "JACIANE FERREIRA DE LIMA VIDAL",
        "ALINE MANETTI LOPES BARANSKI",
        "JANE KELLY DOS SANTO S CANINDE GOMES",
        "PAULA LILIANE MEDEIROS DA CONCEIÇÃO",
        "ERIKA HERONILDES COSTA DA SILVA",
        "DANIELE ROSEGLEI DA SILVA",
        "MARCOS AURELIO PEREIRA DE AZEVEDO",
        "ANNA PAULA ALCANTRA DA SILVA",
        "MICARLA GOMES DE PONTES",
        "JULLIETE GONÇALVES DE OLIVEIRA PIMENTA",
        "MIRIÃ KELLY CHAGAS DO NASCIMENTO OLIVEIRA",
        "CASSIA CASTILHO MAROTTI",
        "PATRICIA DA SILVA ROCHA",
        "MELICIA PEREIRA DO NASCIMENTO MEDEIROS",
        "ELIANDERSON OLIVEIRA DOS SANTOS",
        "MARIA SELMA INACIO DE OLIVEIRA",
        "NAIRA CAROLINE DE OLIVEIRA BRITO",
        "ELIANA CARLA GOMES DE ALBUQUERQUE MONTEIRO",
        "LICIA DE CASTRO REGO",
        "CIBELE DE CASTRO REGO HERONILDES",
        "ERIKA PRISCILLA",
        "PAULO RANGEL",
        "PRISCILA GOMES DE OLIVEIRA",
        "ANA PAULA",
        "MARIANA SILVA",
        "FERNANDA THEMES SILVA NASCIMENTO FERNANDES",
        "JOELMA MATIAS",
        "VANESSA GOSSON GADELHA DE FREITAS FORTES",
        "LUISE BEATRIZ DA CUNHA SILVA",
        "CARLA PAVONE SANTISTEBAN",
        "KEYLANE MARQUES DA SILVA RAMOS",
        "IRANIR RIBEIRO DA SILVA BATISTA",
        "DANIELLY CRISTINA BEZERRA DE SOUZA ALMEIDA",
        "REBECA DA ROCHA MARQUES LOPES",
        "PAULO ROMMEL RODRIGUES DA SILVA",
        "ISABELLY THUANY DE FREITAS CARVALHO",
        "JANAINA ATALIBA DE MELO SOUZA",
        "ALIADNE CRISTINA DOS SANTOS BARBOSA"
    ]
    
    # Normalizar nomes do relatório
    nomes_normalizados = set()
    for nome in nomes_relatorio:
        nome_normalizado = ' '.join(nome.upper().split())
        nomes_normalizados.add(nome_normalizado)
    
    print(f"✅ Relatório: {len(nomes_normalizados)} responsáveis processados")
    
    return nomes_normalizados

def main():
    print("🔍 COMPARAÇÃO: CSV vs RELATÓRIO INFINITE PAY")
    print("=" * 60)
    
    # Carregar responsáveis do CSV
    arquivo_csv = "responsaveis_com_dividas_20250824_131824.csv"
    nomes_csv = extrair_nomes_csv(arquivo_csv)
    
    # Carregar responsáveis do relatório
    nomes_relatorio = extrair_nomes_relatorio()
    
    if not nomes_csv:
        print("❌ Nenhum responsável carregado do CSV")
        return
    
    if not nomes_relatorio:
        print("❌ Nenhum responsável carregado do relatório")
        return
    
    print()
    print("📊 ESTATÍSTICAS:")
    print(f"📋 Responsáveis no CSV: {len(nomes_csv)}")
    print(f"📄 Responsáveis no relatório: {len(nomes_relatorio)}")
    
    # Encontrar responsáveis que estão no CSV mas não no relatório
    faltando_no_relatorio = nomes_csv - nomes_relatorio
    
    # Encontrar responsáveis que estão no relatório mas não no CSV
    faltando_no_csv = nomes_relatorio - nomes_csv
    
    # Responsáveis que aparecem em ambos
    em_ambos = nomes_csv & nomes_relatorio
    
    print()
    print("🔍 RESULTADOS DA ANÁLISE:")
    print("=" * 50)
    print(f"✅ Responsáveis processados (em ambos): {len(em_ambos)}")
    print(f"❌ Responsáveis do CSV que NÃO foram processados: {len(faltando_no_relatorio)}")
    print(f"⚠️ Responsáveis no relatório que não estão no CSV: {len(faltando_no_csv)}")
    
    if faltando_no_relatorio:
        print()
        print("❌ RESPONSÁVEIS DO CSV QUE NÃO FORAM PROCESSADOS:")
        print("-" * 50)
        for i, nome in enumerate(sorted(faltando_no_relatorio), 1):
            print(f"{i:2d}. {nome}")
        
        # Salvar em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = f"responsaveis_nao_processados_{timestamp}.csv"
        
        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['Nome'])
            for nome in sorted(faltando_no_relatorio):
                escritor.writerow([nome])
        
        print()
        print(f"💾 Lista dos não processados salva em: {arquivo_saida}")
    
    if faltando_no_csv:
        print()
        print("⚠️ RESPONSÁVEIS NO RELATÓRIO QUE NÃO ESTÃO NO CSV:")
        print("-" * 50)
        for i, nome in enumerate(sorted(faltando_no_csv), 1):
            print(f"{i:2d}. {nome}")
    
    # Calcular taxa de processamento
    if nomes_csv:
        taxa_processamento = (len(em_ambos) / len(nomes_csv)) * 100
        print()
        print(f"📊 Taxa de processamento: {taxa_processamento:.1f}% ({len(em_ambos)}/{len(nomes_csv)})")
    
    print()
    print("🎉 Análise concluída!")

if __name__ == "__main__":
    main() 
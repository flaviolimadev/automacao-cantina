#!/usr/bin/env python3
"""
Script para listar responsáveis nível 1 com alunos que possuem dívidas
"""

import os
import csv
import re
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar nossa classe
from responsaveis_requests import SupabaseRequests, exibir_responsaveis_nivel1_com_dividas

def formatar_contato(contato):
    """Formatar contato para o padrão (84) 99695-2876"""
    if not contato:
        return "N/A"
    
    # Remover tudo que não é número
    apenas_numeros = re.sub(r'[^0-9]', '', contato)
    
    # Se tem 11 dígitos (padrão brasileiro com DDD)
    if len(apenas_numeros) == 11:
        ddd = apenas_numeros[:2]
        parte1 = apenas_numeros[2:7]
        parte2 = apenas_numeros[7:11]
        return f"({ddd}) {parte1}-{parte2}"
    
    # Se tem 10 dígitos (sem o 9)
    elif len(apenas_numeros) == 10:
        ddd = apenas_numeros[:2]
        parte1 = apenas_numeros[2:6]
        parte2 = apenas_numeros[6:10]
        return f"({ddd}) {parte1}-{parte2}"
    
    # Se não conseguir formatar, retornar original
    else:
        return contato

def gerar_csv_responsaveis_com_dividas():
    """Gerar CSV com responsáveis que têm dívidas"""
    try:
        supabase = SupabaseRequests()
        
        print("📊 Coletando dados dos responsáveis com dívidas...")
        responsaveis_com_dividas = supabase.select_responsaveis_nivel1_com_dividas()
        
        if not responsaveis_com_dividas:
            print("⚠️ Nenhum responsável com dívidas encontrado para exportar")
            return
        
        # Nome do arquivo CSV com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"responsaveis_com_dividas_{timestamp}.csv"
        
        # Criar arquivo CSV
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
            escritor = csv.writer(arquivo_csv)
            
            # Cabeçalho - seguindo modelo exato
            escritor.writerow(['Nome', 'Telefone', 'CPF/CNPJ', 'e-mail'])
            
            # Dados dos responsáveis - seguindo modelo exato
            for responsavel in responsaveis_com_dividas:
                nome_completo = f"{responsavel.get('nome', 'N/A')} {responsavel.get('sobrenome', 'N/A')}"
                telefone_formatado = formatar_contato(responsavel.get('contato', ''))
                cpf_cnpj = ""  # Campo vazio - não temos essa informação
                email = ""     # Campo vazio - não temos essa informação
                
                escritor.writerow([nome_completo, telefone_formatado, cpf_cnpj, email])
        
        print(f"✅ Arquivo CSV gerado: {nome_arquivo}")
        print(f"📊 {len(responsaveis_com_dividas)} responsáveis exportados")
        
        # Estatísticas do arquivo
        total_geral = sum(resp.get('total_geral_devido', 0) for resp in responsaveis_com_dividas)
        print(f"💰 Total geral das dívidas: R$ {total_geral:.2f}")
        
        return nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao gerar CSV: {e}")
        return None

def main():
    """Executar busca de responsáveis nível 1 com dívidas"""
    print("🏢 SISTEMA DE CONTROLE DE DÍVIDAS")
    print("=" * 50)
    print("📋 Buscando responsáveis nível 1 com alunos devendo...")
    print("=" * 50)
    
    try:
        # Executar busca e exibir resultados
        exibir_responsaveis_nivel1_com_dividas()
        
        print("\n" + "=" * 60)
        print("📄 GERANDO ARQUIVO CSV...")
        print("=" * 60)
        
        # Gerar CSV
        arquivo_gerado = gerar_csv_responsaveis_com_dividas()
        
        if arquivo_gerado:
            print(f"\n🎉 Sucesso! Arquivo CSV gerado: {arquivo_gerado}")
            print("📋 Formato: Nome, Telefone, CPF/CNPJ, e-mail (seguindo modelo exato)")
            print("📞 Telefones formatados: (84) 99695-2876")
            print("📝 CPF/CNPJ e e-mail ficam vazios (dados não disponíveis)")
            print("💡 Use este arquivo para importar em planilhas ou sistemas de cobrança")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("🔧 Verifique se o arquivo .env está configurado corretamente")

if __name__ == "__main__":
    main() 
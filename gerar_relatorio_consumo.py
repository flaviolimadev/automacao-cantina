#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar relatório de consumo formatado para PDF
Organiza os dados em formato de nota de consumo legível
"""

import csv
import os
from datetime import datetime
from collections import defaultdict

def gerar_relatorio_formatado(arquivo_entrada):
    """
    Gera um relatório formatado a partir do CSV detalhado
    """
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        return
    
    # Estrutura para organizar os dados
    dados_responsaveis = defaultdict(lambda: {
        'telefone': '',
        'total_geral': 0.0,
        'alunos': defaultdict(lambda: {
            'total_aluno': 0.0,
            'compras': []
        })
    })
    
    # Ler o arquivo CSV
    print("📊 Processando dados do CSV...")
    
    # Variáveis para manter o contexto das linhas anteriores
    ultimo_responsavel = ""
    ultimo_telefone = ""
    ultimo_aluno = ""
    ultimo_total_aluno = 0.0
    ultimo_total_responsavel = 0.0
    
    with open(arquivo_entrada, 'r', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        
        for linha in leitor:
            responsavel = linha['Responsável'].strip()
            telefone = linha['Telefone'].strip()
            aluno = linha['Aluno'].strip()
            data_compra = linha['Data Compra'].strip()
            valor_str = linha['Valor Item (R$)'].strip()
            descricao = linha['Descrição/Observações'].strip()
            total_aluno_str = linha['Total Aluno (R$)'].strip()
            total_responsavel_str = linha['Total Responsável (R$)'].strip()
            
            # Se os campos principais estão vazios, usar os últimos valores conhecidos
            if not responsavel and ultimo_responsavel:
                responsavel = ultimo_responsavel
            if not telefone and ultimo_telefone:
                telefone = ultimo_telefone
            if not aluno and ultimo_aluno:
                aluno = ultimo_aluno
            if not total_aluno_str and ultimo_total_aluno > 0:
                total_aluno_str = f"R$ {ultimo_total_aluno:.2f}".replace('.', ',')
            if not total_responsavel_str and ultimo_total_responsavel > 0:
                total_responsavel_str = f"R$ {ultimo_total_responsavel:.2f}".replace('.', ',')
            
            # Atualizar últimos valores conhecidos quando não estão vazios
            if responsavel:
                ultimo_responsavel = responsavel
            if telefone:
                ultimo_telefone = telefone
            if aluno:
                ultimo_aluno = aluno
                
            # Pular linhas completamente vazias
            if not responsavel or not aluno or not data_compra:
                continue
            
            # Extrair valor numérico
            try:
                valor = float(valor_str.replace('R$', '').replace(',', '.').strip())
            except:
                valor = 0.0
            
            # Extrair total do aluno
            try:
                total_aluno = float(total_aluno_str.replace('R$', '').replace(',', '.').strip())
                if total_aluno > 0:
                    ultimo_total_aluno = total_aluno
            except:
                total_aluno = ultimo_total_aluno
            
            # Extrair total do responsável
            try:
                total_responsavel = float(total_responsavel_str.replace('R$', '').replace(',', '.').strip())
                if total_responsavel > 0:
                    ultimo_total_responsavel = total_responsavel
            except:
                total_responsavel = ultimo_total_responsavel
            
            # Organizar dados
            dados_responsaveis[responsavel]['telefone'] = telefone
            dados_responsaveis[responsavel]['total_geral'] = total_responsavel
            dados_responsaveis[responsavel]['alunos'][aluno]['total_aluno'] = total_aluno
            
            # Adicionar compra se tiver dados válidos
            if data_compra and valor > 0:
                dados_responsaveis[responsavel]['alunos'][aluno]['compras'].append({
                    'data': data_compra,
                    'valor': valor,
                    'descricao': descricao or 'Não especificado'
                })
    
    # Gerar relatório formatado
    nome_arquivo = f"relatorio_consumo_formatado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    print(f"📄 Gerando relatório formatado: {nome_arquivo}")
    
    with open(nome_arquivo, 'w', encoding='utf-8', newline='') as arquivo:
        writer = csv.writer(arquivo)
        
        # Cabeçalho principal
        writer.writerow([])
        writer.writerow(['=' * 80])
        writer.writerow(['                    RELATÓRIO DE CONSUMO - CANTINA ESCOLAR'])
        writer.writerow(['                    Data de Geração:', datetime.now().strftime('%d/%m/%Y às %H:%M')])
        writer.writerow(['=' * 80])
        writer.writerow([])
        
        total_geral_cantina = 0.0
        contador_responsaveis = 0
        
        # Processar cada responsável
        for responsavel, dados in sorted(dados_responsaveis.items()):
            if not responsavel:
                continue
                
            contador_responsaveis += 1
            total_geral_cantina += dados['total_geral']
            
            # Cabeçalho do responsável
            writer.writerow(['-' * 80])
            writer.writerow([f"RESPONSÁVEL #{contador_responsaveis:03d}"])
            writer.writerow(['-' * 80])
            writer.writerow([f"Nome: {responsavel}"])
            writer.writerow([f"Telefone: {dados['telefone'] or 'Não informado'}"])
            writer.writerow([f"Total Geral: R$ {dados['total_geral']:.2f}".replace('.', ',')])
            writer.writerow([])
            
            # Processar cada aluno
            for aluno, dados_aluno in sorted(dados['alunos'].items()):
                if not aluno:
                    continue
                    
                writer.writerow([f"  📚 ALUNO: {aluno}"])
                writer.writerow([f"  💰 Total do Aluno: R$ {dados_aluno['total_aluno']:.2f}".replace('.', ',')])
                writer.writerow([])
                
                # Cabeçalho das compras
                writer.writerow(['    Data', 'Valor (R$)', 'Descrição do Consumo'])
                writer.writerow(['    ' + '-' * 10, '-' * 12, '-' * 40])
                
                # Listar compras ordenadas por data
                compras_ordenadas = sorted(
                    dados_aluno['compras'], 
                    key=lambda x: x['data'], 
                    reverse=True
                )
                
                if compras_ordenadas:
                    for compra in compras_ordenadas:
                        valor_formatado = f"R$ {compra['valor']:.2f}".replace('.', ',')
                        writer.writerow([
                            f"    {compra['data']}", 
                            valor_formatado, 
                            compra['descricao']
                        ])
                else:
                    writer.writerow(['    -', '-', 'Nenhuma compra registrada'])
                
                writer.writerow([])
            
            writer.writerow([])
        
        # Resumo final
        writer.writerow(['=' * 80])
        writer.writerow(['                              RESUMO GERAL'])
        writer.writerow(['=' * 80])
        writer.writerow([f"Total de Responsáveis: {contador_responsaveis}"])
        writer.writerow([f"Total de Alunos: {sum(len(dados['alunos']) for dados in dados_responsaveis.values())}"])
        writer.writerow([f"VALOR TOTAL GERAL: R$ {total_geral_cantina:.2f}".replace('.', ',')])
        writer.writerow([])
        writer.writerow(['Relatório gerado automaticamente pelo Sistema de Gestão da Cantina'])
        writer.writerow(['=' * 80])
    
    print(f"✅ Relatório gerado com sucesso!")
    print(f"📁 Arquivo: {nome_arquivo}")
    print(f"📊 Total de responsáveis: {contador_responsaveis}")
    print(f"💰 Valor total: R$ {total_geral_cantina:.2f}".replace('.', ','))

def main():
    """Função principal"""
    print("🏢 GERADOR DE RELATÓRIO DE CONSUMO FORMATADO")
    print("=" * 60)
    
    # Arquivo de entrada
    arquivo_entrada = "consumo_detalhado_20250914_140701.csv"
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        print("📝 Certifique-se de que o arquivo existe no diretório atual")
        return
    
    print(f"📄 Processando arquivo: {arquivo_entrada}")
    
    # Gerar relatório
    gerar_relatorio_formatado(arquivo_entrada)
    
    print("=" * 60)
    print("🎉 Processamento concluído!")

if __name__ == "__main__":
    main() 
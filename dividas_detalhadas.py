#!/usr/bin/env python3
"""
Script para gerar CSV detalhado com responsáveis, alunos e consumo individual
Inclui detalhes de cada compra/consumo realizado pelos alunos
"""

import os
import csv
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar nossa classe
from responsaveis_requests import SupabaseRequests

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

def formatar_data(data_str):
    """Formatar data para formato brasileiro dd/mm/yyyy"""
    if not data_str:
        return "N/A"
    
    try:
        # Converter string ISO para datetime e depois para formato brasileiro
        data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
        return data_obj.strftime("%d/%m/%Y")
    except:
        return data_str

def buscar_detalhes_consumo():
    """Buscar detalhes completos do consumo por responsável e aluno, incluindo produtos"""
    try:
        supabase = SupabaseRequests()
        
        print("📊 Coletando dados detalhados de consumo...")
        
        # Usar o método existente que já faz toda a lógica necessária
        responsaveis_com_dividas = supabase.select_responsaveis_nivel1_com_dividas()
        
        if not responsaveis_com_dividas:
            print("⚠️ Nenhum responsável com dívidas encontrado")
            return {}
        
        # Buscar todos os produtos para fazer o join
        print("🛒 Buscando informações dos produtos...")
        produtos_response = requests.get(
            f"{supabase.base_url}/produtos",
            headers=supabase.headers
        )
        
        if produtos_response.status_code == 200:
            produtos = produtos_response.json()
            produtos_dict = {p['id']: p for p in produtos}
            print(f"✅ {len(produtos)} produtos carregados")
        else:
            print(f"⚠️ Erro ao buscar produtos: {produtos_response.status_code}")
            produtos_dict = {}
        
        # Buscar tabela produtos_comprados para fazer join (OTIMIZADO)
        print("🔗 Buscando relações produtos-comprados...")
        produtos_comprados_response = requests.get(
            f"{supabase.base_url}/produtos_comprados",
            headers=supabase.headers
        )
        
        if produtos_comprados_response.status_code == 200:
            produtos_comprados = produtos_comprados_response.json()
            # Mapear por compra_id para facilitar busca (OTIMIZADO)
            produtos_por_compra = {}
            for pc in produtos_comprados:
                compra_id = pc['compra_id']
                if compra_id not in produtos_por_compra:
                    produtos_por_compra[compra_id] = []
                produtos_por_compra[compra_id].append(pc)
            print(f"✅ {len(produtos_comprados)} relações produtos-comprados carregadas")
        else:
            print(f"⚠️ Erro ao buscar produtos_comprados: {produtos_comprados_response.status_code}")
            produtos_por_compra = {}
        
        # Reorganizar dados no formato esperado pelo resto do código
        dados_responsaveis = {}
        
        for responsavel in responsaveis_com_dividas:
            responsavel_id = responsavel['id']
            dados_responsaveis[responsavel_id] = {
                'responsavel': {
                    'id': responsavel_id,
                    'nome': responsavel.get('nome', ''),
                    'sobrenome': responsavel.get('sobrenome', ''),
                    'contato': responsavel.get('contato', '')
                },
                'alunos': {}
            }
            
            # Processar cada aluno com dívidas
            for aluno in responsavel.get('alunos', []):
                aluno_id = aluno['id']
                
                # Enriquecer compras com informações de produtos (OTIMIZADO)
                compras_enriquecidas = []
                for compra in aluno.get('compras_pendentes', []):
                    compra_enriquecida = compra.copy()
                    
                    # Buscar produtos desta compra usando dados já carregados (OTIMIZADO)
                    compra_id = compra['id']
                    produtos_da_compra = []
                    
                    # Usar o mapeamento já carregado em vez de fazer nova requisição
                    if compra_id in produtos_por_compra:
                        for pc in produtos_por_compra[compra_id]:
                            produto_id = pc['produto_id']
                            quantidade = pc['quantidade']
                            
                            if produto_id in produtos_dict:
                                produto = produtos_dict[produto_id]
                                produto_info = {
                                    'nome': produto.get('nome', 'Produto sem nome'),
                                    'quantidade': quantidade,
                                    'valor_unitario': produto.get('valor', 0)
                                }
                                produtos_da_compra.append(produto_info)
                    
                    # Criar descrição detalhada
                    if produtos_da_compra:
                        descricoes = []
                        for p in produtos_da_compra:
                            if p['quantidade'] > 1:
                                descricoes.append(f"{p['quantidade']}x {p['nome']}")
                            else:
                                descricoes.append(p['nome'])
                        compra_enriquecida['descricao_produtos'] = " + ".join(descricoes)
                    else:
                        # Usar observações da compra como fallback
                        compra_enriquecida['descricao_produtos'] = compra.get('observacoes') or 'Produto não especificado'
                    
                    compras_enriquecidas.append(compra_enriquecida)
                
                dados_responsaveis[responsavel_id]['alunos'][aluno_id] = {
                    'dados_aluno': {
                        'id': aluno_id,
                        'nome': aluno.get('nome', ''),
                        'sobrenome': aluno.get('sobrenome', '')
                    },
                    'compras': compras_enriquecidas,
                    'total_devido': aluno.get('total_devido', 0.0)
                }
        
        return dados_responsaveis
        
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes do consumo: {e}")
        return {}

def gerar_csv_detalhado():
    """Gerar CSV com detalhes completos do consumo"""
    try:
        dados_responsaveis = buscar_detalhes_consumo()
        
        if not dados_responsaveis:
            print("⚠️ Nenhum dado encontrado para exportar")
            return None
        
        # Nome do arquivo CSV com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"consumo_detalhado_{timestamp}.csv"
        
        # Criar arquivo CSV
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
            escritor = csv.writer(arquivo_csv)
            
            # Cabeçalho detalhado
            escritor.writerow([
                'Responsável', 
                'Telefone', 
                'Aluno', 
                'Data Compra', 
                'Valor Item (R$)', 
                'Descrição/Observações', 
                'Total Aluno (R$)',
                'Total Responsável (R$)'
            ])
            
            total_geral = 0.0
            contador_responsaveis = 0
            contador_alunos = 0
            contador_compras = 0
            
            # Processar cada responsável
            for responsavel_id, dados in dados_responsaveis.items():
                responsavel = dados['responsavel']
                nome_responsavel = f"{responsavel.get('nome', 'N/A')} {responsavel.get('sobrenome', 'N/A')}"
                telefone_responsavel = formatar_contato(responsavel.get('contato', ''))
                
                # Calcular total do responsável
                total_responsavel = sum(
                    dados_aluno['total_devido'] 
                    for dados_aluno in dados['alunos'].values()
                )
                total_geral += total_responsavel
                contador_responsaveis += 1
                
                primeira_linha_responsavel = True
                
                # Processar cada aluno do responsável
                for aluno_id, dados_aluno in dados['alunos'].items():
                    aluno = dados_aluno['dados_aluno']
                    nome_aluno = f"{aluno.get('nome', 'N/A')} {aluno.get('sobrenome', 'N/A')}"
                    total_aluno = dados_aluno['total_devido']
                    contador_alunos += 1
                    
                    primeira_linha_aluno = True
                    
                    # Processar cada compra do aluno
                    compras_ordenadas = sorted(
                        dados_aluno['compras'], 
                        key=lambda x: x.get('created_at', ''), 
                        reverse=True
                    )
                    
                    for compra in compras_ordenadas:
                        data_compra = formatar_data(compra.get('created_at', ''))
                        valor_item = float(compra['value'])
                        # Usar a descrição dos produtos enriquecida
                        observacoes = compra.get('descricao_produtos', compra.get('observacoes', 'Produto não identificado'))
                        contador_compras += 1
                        
                        # Escrever linha no CSV
                        escritor.writerow([
                            nome_responsavel if primeira_linha_responsavel else '',
                            telefone_responsavel if primeira_linha_responsavel else '',
                            nome_aluno if primeira_linha_aluno else '',
                            data_compra,
                            f"R$ {valor_item:.2f}",
                            observacoes,
                            f"R$ {total_aluno:.2f}" if primeira_linha_aluno else '',
                            f"R$ {total_responsavel:.2f}" if primeira_linha_responsavel else ''
                        ])
                        
                        primeira_linha_responsavel = False
                        primeira_linha_aluno = False
                    
                    # Se aluno não tem compras, adicionar linha vazia
                    if not compras_ordenadas:
                        escritor.writerow([
                            nome_responsavel if primeira_linha_responsavel else '',
                            telefone_responsavel if primeira_linha_responsavel else '',
                            nome_aluno,
                            'Sem compras',
                            'R$ 0,00',
                            'Nenhuma compra registrada',
                            f"R$ {total_aluno:.2f}",
                            f"R$ {total_responsavel:.2f}" if primeira_linha_responsavel else ''
                        ])
                        primeira_linha_responsavel = False
        
        print(f"✅ Arquivo CSV detalhado gerado: {nome_arquivo}")
        print(f"📊 Estatísticas:")
        print(f"   👥 Responsáveis: {contador_responsaveis}")
        print(f"   🎓 Alunos: {contador_alunos}")
        print(f"   🛒 Compras: {contador_compras}")
        print(f"   💰 Total geral: R$ {total_geral:.2f}")
        
        return nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao gerar CSV detalhado: {e}")
        return None

def gerar_relatorio_resumido():
    """Gerar relatório resumido na tela"""
    try:
        dados_responsaveis = buscar_detalhes_consumo()
        
        if not dados_responsaveis:
            print("⚠️ Nenhum dado encontrado")
            return
        
        print("\n📊 RELATÓRIO RESUMIDO:")
        print("=" * 80)
        
        for responsavel_id, dados in dados_responsaveis.items():
            responsavel = dados['responsavel']
            nome_responsavel = f"{responsavel.get('nome', 'N/A')} {responsavel.get('sobrenome', 'N/A')}"
            telefone = formatar_contato(responsavel.get('contato', ''))
            
            total_responsavel = sum(
                dados_aluno['total_devido'] 
                for dados_aluno in dados['alunos'].values()
            )
            
            print(f"\n👤 {nome_responsavel}")
            print(f"📞 {telefone}")
            print(f"💰 Total devido: R$ {total_responsavel:.2f}")
            print(f"👥 Alunos: {len(dados['alunos'])}")
            
            for aluno_id, dados_aluno in dados['alunos'].items():
                aluno = dados_aluno['dados_aluno']
                nome_aluno = f"{aluno.get('nome', 'N/A')} {aluno.get('sobrenome', 'N/A')}"
                total_aluno = dados_aluno['total_devido']
                qtd_compras = len(dados_aluno['compras'])
                
                print(f"   🎓 {nome_aluno}: R$ {total_aluno:.2f} ({qtd_compras} compras)")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Executar geração de relatório detalhado de consumo"""
    print("🏢 SISTEMA DE RELATÓRIO DETALHADO DE CONSUMO")
    print("=" * 60)
    print("📋 Gerando relatório com detalhes de consumo por aluno...")
    print("=" * 60)
    
    try:
        # Gerar relatório resumido na tela
        gerar_relatorio_resumido()
        
        print("\n" + "=" * 60)
        print("📄 GERANDO ARQUIVO CSV DETALHADO...")
        print("=" * 60)
        
        # Gerar CSV detalhado
        arquivo_gerado = gerar_csv_detalhado()
        
        if arquivo_gerado:
            print(f"\n🎉 Sucesso! Arquivo CSV detalhado gerado: {arquivo_gerado}")
            print("📋 Formato: Responsável, Telefone, Aluno, Data, Valor, Descrição, Total Aluno, Total Responsável")
            print("📞 Telefones formatados: (84) 99695-2876")
            print("📅 Datas formatadas: dd/mm/yyyy")
            print("💰 Valores formatados: R$ 15,00")
            print("📝 Inclui descrição/observações de cada compra")
            print("💡 Use este arquivo para análise detalhada de consumo")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("🔧 Verifique se o arquivo .env está configurado corretamente")

if __name__ == "__main__":
    main() 
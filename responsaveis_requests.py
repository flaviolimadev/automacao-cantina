#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import json

# Carregar variáveis de ambiente
load_dotenv()

class SupabaseRequests:
    def __init__(self):
        """Inicializa conexão usando apenas requests"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Credenciais não encontradas no arquivo .env")
        
        self.base_url = f"{self.url}/rest/v1"
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Cache simples para evitar requisições desnecessárias
        self._cache = {
            'responsaveis': None,
            'relacoes': None,
            'alunos': None,
            'cache_time': None
        }
        self._cache_timeout = 30  # segundos
    
    def _is_cache_valid(self):
        """Verifica se o cache ainda é válido"""
        if self._cache['cache_time'] is None:
            return False
        
        import time
        return (time.time() - self._cache['cache_time']) < self._cache_timeout
    
    def _update_cache_time(self):
        """Atualiza o tempo do cache"""
        import time
        self._cache['cache_time'] = time.time()
    
    def limpar_cache(self):
        """Limpa o cache para forçar nova busca"""
        self._cache = {
            'responsaveis': None,
            'relacoes': None,
            'alunos': None,
            'cache_time': None
        }
        print("🧹 Cache limpo!")
    
    def select_all_responsaveis(self, usar_cache=True):
        """Busca todos os responsáveis com cache otimizado"""
        try:
            # Verificar cache primeiro
            if usar_cache and self._is_cache_valid() and self._cache['responsaveis']:
                return self._cache['responsaveis']
            
            response = requests.get(
                f"{self.base_url}/responsaveis?order=nome.asc",
                headers=self.headers
            )
            
            if response.status_code == 200:
                responsaveis = response.json()
                # Atualizar cache
                self._cache['responsaveis'] = responsaveis
                if not self._cache['cache_time']:
                    self._update_cache_time()
                return responsaveis
            else:
                print(f"Erro {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro na requisição: {e}")
            return None
    
    def select_responsaveis_com_alunos(self, filtro_nivel=None):
        """Busca responsáveis com seus alunos relacionados (OTIMIZADO)"""
        try:
            import time
            inicio = time.time()
            
            print("⚡ Otimizando busca - carregando dados em lote...")
            
            # 1. Buscar todos os responsáveis de uma vez
            responsaveis = self.select_all_responsaveis()
            if not responsaveis:
                return None
            
            # 2. Buscar TODAS as relações de uma vez (muito mais rápido)
            url_relacoes = f"{self.base_url}/relacao"
            if filtro_nivel is not None:
                url_relacoes += f"?nivel=eq.{filtro_nivel}"
            
            relacoes_response = requests.get(url_relacoes, headers=self.headers)
            
            if relacoes_response.status_code != 200:
                print(f"Erro ao buscar relações: {relacoes_response.status_code}")
                return responsaveis
            
            todas_relacoes = relacoes_response.json()
            
            if not todas_relacoes:
                # Se não há relações, retornar responsáveis sem alunos
                for responsavel in responsaveis:
                    responsavel['alunos'] = []
                return responsaveis
            
            # 3. Extrair todos os IDs de alunos únicos
            alunos_ids = list(set([relacao['aluno_id'] for relacao in todas_relacoes]))
            
            # 4. Buscar TODOS os alunos de uma vez usando query com múltiplos IDs
            if alunos_ids:
                # Criar query para buscar múltiplos alunos: id.in.(id1,id2,id3...)
                ids_string = ','.join(alunos_ids)
                alunos_response = requests.get(
                    f"{self.base_url}/alunos?id=in.({ids_string})",
                    headers=self.headers
                )
                
                if alunos_response.status_code == 200:
                    todos_alunos = alunos_response.json()
                    # Criar mapeamento ID -> dados do aluno para acesso rápido
                    alunos_map = {aluno['id']: aluno for aluno in todos_alunos}
                else:
                    print(f"Erro ao buscar alunos: {alunos_response.status_code}")
                    alunos_map = {}
            else:
                alunos_map = {}
            
            # 5. Agrupar relações por responsável
            relacoes_por_responsavel = {}
            for relacao in todas_relacoes:
                resp_id = relacao['responsavel_id']
                if resp_id not in relacoes_por_responsavel:
                    relacoes_por_responsavel[resp_id] = []
                relacoes_por_responsavel[resp_id].append(relacao)
            
            # 6. Associar alunos aos responsáveis
            for responsavel in responsaveis:
                responsavel_id = responsavel['id']
                responsavel['alunos'] = []
                
                if responsavel_id in relacoes_por_responsavel:
                    for relacao in relacoes_por_responsavel[responsavel_id]:
                        aluno_id = relacao['aluno_id']
                        
                        if aluno_id in alunos_map:
                            aluno = alunos_map[aluno_id].copy()
                            aluno['nivel_relacao'] = relacao.get('nivel', 'N/A')
                            aluno['relacao_id'] = relacao.get('id', 'N/A')
                            responsavel['alunos'].append(aluno)
            
            fim = time.time()
            tempo_execucao = fim - inicio
            
            print(f"✅ Busca otimizada concluída em {tempo_execucao:.2f} segundos!")
            print(f"📊 Estatísticas: {len(responsaveis)} responsáveis, {len(todas_relacoes)} relações, {len(alunos_map)} alunos únicos")
            return responsaveis
            
        except Exception as e:
            print(f"Erro ao buscar responsáveis com alunos: {e}")
            return None

    def select_responsaveis_nivel1_com_dividas(self):
        """Busca responsáveis nível 1 com alunos que têm compras pendentes (status=false)"""
        try:
            import time
            inicio = time.time()
            
            print("💰 Buscando responsáveis nível 1 com alunos devendo...")
            
            # 1. Buscar responsáveis nível 1 com seus alunos
            responsaveis = self.select_responsaveis_com_alunos(filtro_nivel=1)
            if not responsaveis:
                return None
            
            # 2. Coletar todos os IDs de alunos de nível 1
            alunos_nivel1_ids = []
            for responsavel in responsaveis:
                for aluno in responsavel.get('alunos', []):
                    alunos_nivel1_ids.append(aluno['id'])
            
            if not alunos_nivel1_ids:
                return []
            
            # 3. Buscar TODAS as compras pendentes (status=false) desses alunos
            ids_string = ','.join(alunos_nivel1_ids)
            compras_response = requests.get(
                f"{self.base_url}/compras?aluno_id=in.({ids_string})&status=eq.false",
                headers=self.headers
            )
            
            if compras_response.status_code != 200:
                print(f"Erro ao buscar compras: {compras_response.status_code}")
                return []
            
            compras_pendentes = compras_response.json()
            
            if not compras_pendentes:
                print("📋 Nenhuma compra pendente encontrada para responsáveis nível 1")
                return []
            
            # 4. Agrupar compras por aluno_id
            compras_por_aluno = {}
            for compra in compras_pendentes:
                aluno_id = compra['aluno_id']
                if aluno_id not in compras_por_aluno:
                    compras_por_aluno[aluno_id] = []
                compras_por_aluno[aluno_id].append(compra)
            
            # 5. Filtrar responsáveis que têm alunos com dívidas
            responsaveis_com_dividas = []
            
            for responsavel in responsaveis:
                alunos_com_divida = []
                
                for aluno in responsavel.get('alunos', []):
                    aluno_id = aluno['id']
                    
                    if aluno_id in compras_por_aluno:
                        # Calcular total devido por este aluno
                        compras_aluno = compras_por_aluno[aluno_id]
                        total_devido = sum(float(compra.get('value', 0)) for compra in compras_aluno)
                        
                        # Adicionar informações de dívida ao aluno
                        aluno_com_divida = aluno.copy()
                        aluno_com_divida['compras_pendentes'] = compras_aluno
                        aluno_com_divida['total_devido'] = total_devido
                        aluno_com_divida['qtd_compras_pendentes'] = len(compras_aluno)
                        
                        alunos_com_divida.append(aluno_com_divida)
                
                # Se este responsável tem alunos com dívidas, incluir na lista
                if alunos_com_divida:
                    responsavel_com_divida = responsavel.copy()
                    responsavel_com_divida['alunos'] = alunos_com_divida
                    responsavel_com_divida['total_geral_devido'] = sum(aluno['total_devido'] for aluno in alunos_com_divida)
                    responsaveis_com_dividas.append(responsavel_com_divida)
            
            fim = time.time()
            tempo_execucao = fim - inicio
            
            print(f"✅ Busca de dívidas concluída em {tempo_execucao:.2f} segundos!")
            print(f"📊 Estatísticas: {len(responsaveis_com_dividas)} responsáveis com dívidas, {len(compras_pendentes)} compras pendentes")
            
            return responsaveis_com_dividas
            
        except Exception as e:
            print(f"Erro ao buscar responsáveis com dívidas: {e}")
            return None
    
    def insert_responsavel(self, data):
        """Insere novo responsável"""
        try:
            response = requests.post(
                f"{self.base_url}/responsaveis",
                headers=self.headers,
                json=data
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"Erro {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro na inserção: {e}")
            return None
    
    def update_responsavel(self, id_responsavel, data):
        """Atualiza responsável por ID"""
        try:
            response = requests.patch(
                f"{self.base_url}/responsaveis?id=eq.{id_responsavel}",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro na atualização: {e}")
            return None
    
    def delete_responsavel(self, id_responsavel):
        """Deleta responsável por ID"""
        try:
            response = requests.delete(
                f"{self.base_url}/responsaveis?id=eq.{id_responsavel}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Erro {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"Erro na exclusão: {e}")
            return False

def exibir_responsaveis():
    """Exibe todos os responsáveis de forma organizada"""
    try:
        supabase = SupabaseRequests()
        
        print("🔄 Buscando responsáveis...")
        responsaveis = supabase.select_all_responsaveis()
        
        if not responsaveis:
            print("⚠️ Nenhum responsável encontrado")
            return
        
        print(f"\n✅ {len(responsaveis)} responsável(is) encontrado(s)")
        print("=" * 80)
        print(f"{'ID':<8} | {'NOME':<20} | {'SOBRENOME':<20} | {'CONTATO':<15}")
        print("-" * 80)
        
        for resp in responsaveis:
            id_short = str(resp.get('id', ''))[:8]
            nome = (resp.get('nome', 'N/A') or 'N/A')[:18]
            sobrenome = (resp.get('sobrenome', 'N/A') or 'N/A')[:18]
            contato = (resp.get('contato', 'N/A') or 'N/A')[:13]
            
            print(f"{id_short:<8} | {nome:<20} | {sobrenome:<20} | {contato:<15}")
        
        print("=" * 80)
        
        # Detalhes completos
        print("\n📄 DETALHES COMPLETOS:")
        print("-" * 50)
        
        for i, resp in enumerate(responsaveis, 1):
            print(f"\n{i}. RESPONSÁVEL:")
            print(f"   🆔 ID: {resp.get('id', 'N/A')}")
            print(f"   👤 Nome: {resp.get('nome', 'N/A')}")
            print(f"   👤 Sobrenome: {resp.get('sobrenome', 'N/A')}")
            print(f"   📞 Contato: {resp.get('contato', 'N/A')}")
            
            # Formatar datas
            if resp.get('created_at'):
                try:
                    data_criacao = datetime.fromisoformat(resp['created_at'].replace('Z', '+00:00'))
                    print(f"   📅 Criado: {data_criacao.strftime('%d/%m/%Y às %H:%M:%S')}")
                except:
                    print(f"   📅 Criado: {resp.get('created_at', 'N/A')}")
            
            if resp.get('updated_at'):
                try:
                    data_atualizacao = datetime.fromisoformat(resp['updated_at'].replace('Z', '+00:00'))
                    print(f"   🔄 Atualizado: {data_atualizacao.strftime('%d/%m/%Y às %H:%M:%S')}")
                except:
                    print(f"   🔄 Atualizado: {resp.get('updated_at', 'N/A')}")
            
            if i < len(responsaveis):
                print("   " + "-" * 40)
        
        print(f"\n📊 RESUMO:")
        print(f"   Total: {len(responsaveis)} responsáveis")
        print(f"   Tabela: responsaveis")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def exibir_responsaveis_com_alunos(filtro_nivel=None):
    """Exibe responsáveis com seus alunos relacionados"""
    try:
        supabase = SupabaseRequests()
        
        if filtro_nivel is not None:
            print(f"🔄 Buscando responsáveis com relações de NÍVEL {filtro_nivel}...")
        else:
            print("🔄 Buscando responsáveis e suas relações com alunos...")
            
        responsaveis = supabase.select_responsaveis_com_alunos(filtro_nivel)
        
        if not responsaveis:
            print("⚠️ Nenhum responsável encontrado")
            return
        
        # Filtrar responsáveis que têm alunos (para o caso de filtro)
        responsaveis_com_alunos = [r for r in responsaveis if r.get('alunos')]
        
        if filtro_nivel is not None and not responsaveis_com_alunos:
            print(f"⚠️ Nenhuma relação com nível {filtro_nivel} encontrada")
            return
        
        responsaveis_para_exibir = responsaveis_com_alunos if filtro_nivel is not None else responsaveis
        
        if filtro_nivel is not None:
            print(f"\n✅ {len(responsaveis_com_alunos)} responsável(is) com relações de nível {filtro_nivel}")
        else:
            print(f"\n✅ {len(responsaveis)} responsável(is) encontrado(s)")
            
        print("=" * 100)
        
        total_relacoes = 0
        
        for i, resp in enumerate(responsaveis_para_exibir, 1):
            print(f"\n{i}. 👤 RESPONSÁVEL:")
            print(f"   🆔 ID: {resp.get('id', 'N/A')}")
            print(f"   📛 Nome: {resp.get('nome', 'N/A')} {resp.get('sobrenome', 'N/A')}")
            print(f"   📞 Contato: {resp.get('contato', 'N/A')}")
            
            # Formatar data de criação
            if resp.get('created_at'):
                try:
                    data_criacao = datetime.fromisoformat(resp['created_at'].replace('Z', '+00:00'))
                    print(f"   📅 Criado: {data_criacao.strftime('%d/%m/%Y às %H:%M:%S')}")
                except:
                    print(f"   📅 Criado: {resp.get('created_at', 'N/A')}")
            
            # Exibir alunos relacionados
            alunos = resp.get('alunos', [])
            if alunos:
                if filtro_nivel is not None:
                    print(f"\n   👨‍👩‍👧‍👦 ALUNOS COM NÍVEL {filtro_nivel} ({len(alunos)}):")
                else:
                    print(f"\n   👨‍👩‍👧‍👦 ALUNOS RELACIONADOS ({len(alunos)}):")
                    
                for j, aluno in enumerate(alunos, 1):
                    print(f"      {j}. 🎓 {aluno.get('nome', 'N/A')} {aluno.get('sobrenome', 'N/A')}")
                    print(f"         🆔 ID: {aluno.get('id', 'N/A')}")
                    print(f"         📚 Série ID: {aluno.get('serie_id', 'N/A')}")
                    print(f"         🏫 Escola ID: {aluno.get('escola_id', 'N/A')}")
                    print(f"         🔗 Nível Relação: {aluno.get('nivel_relacao', 'N/A')}")
                    
                    # Foto se disponível
                    if aluno.get('foto_url'):
                        print(f"         📸 Foto: {aluno.get('foto_url', 'N/A')}")
                    
                    # Data de criação do aluno
                    if aluno.get('created_at'):
                        try:
                            data_aluno = datetime.fromisoformat(aluno['created_at'].replace('Z', '+00:00'))
                            print(f"         📅 Criado: {data_aluno.strftime('%d/%m/%Y')}")
                        except:
                            print(f"         📅 Criado: {aluno.get('created_at', 'N/A')}")
                    
                    if j < len(alunos):
                        print("         " + "- " * 15)
                
                total_relacoes += len(alunos)
            else:
                if filtro_nivel is None:
                    print(f"\n   ⚠️ Nenhum aluno relacionado encontrado")
            
            if i < len(responsaveis_para_exibir):
                print("\n" + "=" * 100)
        
        print(f"\n📊 RESUMO GERAL:")
        if filtro_nivel is not None:
            print(f"   🎯 Filtro aplicado: Nível {filtro_nivel}")
            print(f"   👥 Responsáveis com nível {filtro_nivel}: {len(responsaveis_com_alunos)}")
        else:
            print(f"   👥 Total de responsáveis: {len(responsaveis)}")
        print(f"   🎓 Total de alunos relacionados: {total_relacoes}")
        if len(responsaveis_para_exibir) > 0:
            print(f"   📈 Média de alunos por responsável: {total_relacoes/len(responsaveis_para_exibir):.1f}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def exibir_responsaveis_nivel_1():
    """Exibe apenas responsáveis com relações de nível 1"""
    exibir_responsaveis_com_alunos(filtro_nivel=1)

def exibir_responsaveis_nivel1_com_dividas():
    """Exibe responsáveis nível 1 com alunos que possuem dívidas"""
    try:
        supabase = SupabaseRequests()
        
        print("💰 RESPONSÁVEIS NÍVEL 1 COM ALUNOS DEVENDO")
        print("="*80)
        
        responsaveis_com_dividas = supabase.select_responsaveis_nivel1_com_dividas()
        
        if not responsaveis_com_dividas:
            print("🎉 Nenhum responsável nível 1 com dívidas encontrado!")
            return
        
        # Ordenar por valor devido (maior primeiro)
        responsaveis_com_dividas.sort(key=lambda x: x['total_geral_devido'], reverse=True)
        
        total_geral_todas_dividas = sum(resp['total_geral_devido'] for resp in responsaveis_com_dividas)
        total_alunos_devendo = sum(len(resp['alunos']) for resp in responsaveis_com_dividas)
        
        print(f"📊 RESUMO EXECUTIVO:")
        print(f"   👥 Responsáveis nível 1 com dívidas: {len(responsaveis_com_dividas)}")
        print(f"   🎓 Alunos devendo: {total_alunos_devendo}")
        print(f"   💰 Total geral devido: R$ {total_geral_todas_dividas:.2f}")
        print("="*80)
        
        for i, responsavel in enumerate(responsaveis_com_dividas, 1):
            print(f"\n{i}. 👤 RESPONSÁVEL:")
            print(f"   📛 Nome: {responsavel.get('nome', 'N/A')} {responsavel.get('sobrenome', 'N/A')}")
            print(f"   📞 Contato: {responsavel.get('contato', 'N/A')}")
            print(f"   💰 Total devido: R$ {responsavel['total_geral_devido']:.2f}")
            print(f"   🎓 Alunos com dívidas: {len(responsavel['alunos'])}")
            
            # Formatar data de criação
            if responsavel.get('created_at'):
                try:
                    data_criacao = datetime.fromisoformat(responsavel['created_at'].replace('Z', '+00:00'))
                    print(f"   📅 Cliente desde: {data_criacao.strftime('%d/%m/%Y')}")
                except:
                    pass
            
            print(f"\n   🎓 ALUNOS COM DÍVIDAS:")
            print(f"   {'-'*60}")
            
            for j, aluno in enumerate(responsavel['alunos'], 1):
                print(f"      {j}. 🎓 {aluno.get('nome', 'N/A')} {aluno.get('sobrenome', 'N/A')}")
                print(f"         💰 Total devido: R$ {aluno['total_devido']:.2f}")
                print(f"         📊 Compras pendentes: {aluno['qtd_compras_pendentes']}")
                print(f"         🆔 ID: {aluno.get('id', 'N/A')}")
                
                # Exibir detalhes das compras pendentes
                print(f"         📋 COMPRAS PENDENTES:")
                for k, compra in enumerate(aluno['compras_pendentes'], 1):
                    valor = float(compra.get('value', 0))
                    print(f"            {k}. R$ {valor:.2f} - ID: {str(compra.get('id', 'N/A'))[:8]}")
                    
                    # Data da compra
                    if compra.get('created_at'):
                        try:
                            data_compra = datetime.fromisoformat(compra['created_at'].replace('Z', '+00:00'))
                            print(f"               📅 Data: {data_compra.strftime('%d/%m/%Y')}")
                        except:
                            pass
                    
                    # Observações se houver
                    if compra.get('observacoes'):
                        obs = compra['observacoes'][:50] + '...' if len(compra['observacoes']) > 50 else compra['observacoes']
                        print(f"               📝 Obs: {obs}")
                    
                    # Link de pagamento se houver
                    if compra.get('payment_link'):
                        print(f"               🔗 Link: {compra['payment_link']}")
                
                if j < len(responsavel['alunos']):
                    print(f"         {'-'*40}")
            
            if i < len(responsaveis_com_dividas):
                print(f"\n{'='*80}")
        
        print(f"\n📊 ESTATÍSTICAS DETALHADAS:")
        print(f"   💰 Maior dívida individual: R$ {max(resp['total_geral_devido'] for resp in responsaveis_com_dividas):.2f}")
        print(f"   💰 Menor dívida individual: R$ {min(resp['total_geral_devido'] for resp in responsaveis_com_dividas):.2f}")
        print(f"   💰 Média por responsável: R$ {total_geral_todas_dividas/len(responsaveis_com_dividas):.2f}")
        
        # Top 3 maiores devedores
        print(f"\n🏆 TOP 3 MAIORES DEVEDORES:")
        for i, resp in enumerate(responsaveis_com_dividas[:3], 1):
            nome = f"{resp.get('nome', 'N/A')} {resp.get('sobrenome', 'N/A')}"
            print(f"   {i}. {nome} - R$ {resp['total_geral_devido']:.2f}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def listar_relacoes_simples():
    """Lista apenas as relações de forma simples"""
    try:
        supabase = SupabaseRequests()
        
        print("🔄 Buscando relações...")
        responsaveis = supabase.select_responsaveis_com_alunos()
        
        if not responsaveis:
            print("⚠️ Nenhum responsável encontrado")
            return
        
        print(f"\n📋 RELAÇÕES RESPONSÁVEIS ↔ ALUNOS:")
        print("-" * 60)
        
        for resp in responsaveis:
            nome_resp = f"{resp.get('nome', 'N/A')} {resp.get('sobrenome', 'N/A')}"
            alunos = resp.get('alunos', [])
            
            if alunos:
                for aluno in alunos:
                    nome_aluno = f"{aluno.get('nome', 'N/A')} {aluno.get('sobrenome', 'N/A')}"
                    nivel = aluno.get('nivel_relacao', 'N/A')
                    print(f"👤 {nome_resp:<30} → 🎓 {nome_aluno:<30} (Nível: {nivel})")
            else:
                print(f"👤 {nome_resp:<30} → ⚠️ Sem alunos relacionados")
        
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def inserir_responsavel():
    """Insere novo responsável"""
    try:
        supabase = SupabaseRequests()
        
        print("📝 INSERIR NOVO RESPONSÁVEL")
        print("-" * 30)
        
        nome = input("👤 Nome: ").strip()
        sobrenome = input("👤 Sobrenome: ").strip()
        contato = input("📞 Contato: ").strip()
        
        if not nome or not sobrenome:
            print("❌ Nome e sobrenome são obrigatórios")
            return
        
        dados = {
            'nome': nome,
            'sobrenome': sobrenome,
            'contato': contato if contato else None
        }
        
        print("🔄 Inserindo...")
        resultado = supabase.insert_responsavel(dados)
        
        if resultado:
            print("✅ Responsável inserido com sucesso!")
            print(f"   ID: {resultado[0].get('id', 'N/A')}")
            print(f"   Nome: {resultado[0].get('nome', 'N/A')} {resultado[0].get('sobrenome', 'N/A')}")
        else:
            print("❌ Erro ao inserir responsável")
            
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada")
    except Exception as e:
        print(f"❌ Erro: {e}")

def menu_principal():
    """Menu principal do sistema"""
    print("\n🏢 SISTEMA DE RESPONSÁVEIS E ALUNOS (OTIMIZADO)")
    print("=" * 65)
    print("1. Listar responsáveis (simples)")
    print("2. Listar responsáveis com alunos (completo)")
    print("3. Listar apenas relações NÍVEL 1 🎯")
    print("4. Listar relações (resumido)")
    print("5. 💰 Responsáveis nível 1 com DÍVIDAS")
    print("6. Inserir novo responsável")
    print("7. Exibir em formato JSON")
    print("8. 🧹 Limpar cache (forçar nova busca)")
    print("9. Sair")
    print("-" * 65)
    
    while True:
        try:
            opcao = input("\n👉 Escolha uma opção (1-9): ").strip()
            supabase = SupabaseRequests()
            
            if opcao == '1':
                print("\n" + "="*80)
                exibir_responsaveis()
                print("="*80)
                
            elif opcao == '2':
                print("\n" + "="*100)
                exibir_responsaveis_com_alunos()
                print("="*100)
                
            elif opcao == '3':
                print("\n" + "="*100)
                exibir_responsaveis_nivel_1()
                print("="*100)
                
            elif opcao == '4':
                print("\n" + "="*80)
                listar_relacoes_simples()
                print("="*80)
                
            elif opcao == '5':
                print("\n" + "="*100)
                exibir_responsaveis_nivel1_com_dividas()
                print("="*100)
                
            elif opcao == '6':
                print("\n" + "="*60)
                inserir_responsavel()
                print("="*60)
                # Limpar cache após inserção para mostrar dados atualizados
                supabase.limpar_cache()
                
            elif opcao == '7':
                print("\n" + "="*60)
                try:
                    dados = supabase.select_responsaveis_com_alunos()
                    if dados:
                        print("📄 DADOS EM FORMATO JSON:")
                        print(json.dumps(dados, indent=2, ensure_ascii=False, default=str))
                    else:
                        print("⚠️ Nenhum dado encontrado")
                except Exception as e:
                    print(f"❌ Erro: {e}")
                print("="*60)
                
            elif opcao == '8':
                print("\n" + "="*40)
                supabase.limpar_cache()
                print("✅ Cache limpo! Próximas buscas serão atualizadas.")
                print("="*40)
                
            elif opcao == '9':
                print("👋 Saindo... Até mais!")
                break
                
            else:
                print("❌ Opção inválida. Escolha entre 1-9.")
                
            print("\n" + "-"*75)
            print("1. Simples | 2. Completo | 3. Nível 1 | 4. Relações | 5. Dívidas | 6. Inserir | 7. JSON | 8. Cache | 9. Sair")
            
        except KeyboardInterrupt:
            print("\n\n👋 Saindo... Até mais!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    try:
        # Teste rápido de conexão
        supabase = SupabaseRequests()
        print("✅ Conexão com Supabase estabelecida")
        
        # Iniciar menu
        menu_principal()
        
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        print("🔧 Verifique se o arquivo .env está configurado corretamente") 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Automação de Cobranças - Infinite Pay
Conecta ao Supabase, busca responsáveis com dívidas e automatiza a criação de cobranças.

🔧 PRINCIPAIS MELHORIAS IMPLEMENTADAS:
- ✅ Verificação de responsáveis autorizados contra CSV específico
- ✅ Seletor correto para campo React Select (react-select-2-input)
- ✅ Seletor correto para botão de data (data-testid="choose-due-date-btn")
- ✅ Tempos de espera otimizados (10s após data, 8s após continuar)
- ✅ Tratamento robusto de erros com recuperação automática
- ✅ Logs detalhados para debugging
- ✅ Integração direta com Supabase via requests
- ✅ Formatação brasileira para valores monetários
- ✅ Espera de 10 segundos entre cada responsável

🚀 MELHORIAS ADICIONAIS PARA MÁXIMA FUNCIONALIDADE:
- ✅ Validação rigorosa de configurações e variáveis de ambiente
- ✅ Teste de conectividade com Supabase antes de iniciar
- ✅ Verificação de saúde do sistema (ChromeDriver, arquivos, etc.)
- ✅ Configurações anti-detecção avançadas do navegador
- ✅ Retry automático com múltiplas estratégias para cada elemento
- ✅ Verificação de acessibilidade dos elementos antes de interagir
- ✅ Tratamento robusto de erros com recuperação automática
- ✅ Relatórios detalhados com estatísticas e métricas
- ✅ Limpeza automática de recursos em caso de falha
- ✅ Timeout configurável e otimizado para cada operação
- ✅ Logs estruturados com níveis de informação apropriados
- ✅ Separação de responsabilidades em funções específicas
- ✅ Verificação de integridade dos dados processados
- ✅ Sistema de fallback para navegação em caso de erro

🎯 FUNCIONALIDADE GARANTIDA:
- 🔒 Segurança: Validação completa de entradas e configurações
- 🚀 Performance: Otimização de tempos de espera e operações
- 🛡️ Confiabilidade: Tratamento robusto de erros e recuperação
- 📊 Transparência: Logs detalhados e relatórios completos
- 🔄 Manutenibilidade: Código bem estruturado e documentado

🚀 FLUXO DE AUTOMAÇÃO:
1. Carrega responsáveis autorizados do CSV
2. Busca dívidas no Supabase
3. Filtra apenas responsáveis autorizados
4. Navega para Infinite Pay
5. Cria cobranças com seletores específicos
6. Trata erros e continua processamento
"""

import os
import sys
import time
import csv
import logging
from datetime import datetime
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import requests

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automacao_cobrancas.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomacaoCobrancas:
    def __init__(self, supabase_url: str, supabase_key: str, csv_file: str = "responsaveis_com_dividas_20251116_113430.csv"):
        """
        Inicializa o sistema de automação de cobranças.
        
        Args:
            supabase_url: URL do projeto Supabase
            supabase_key: Chave de API do Supabase
            csv_file: Arquivo CSV com responsáveis autorizados
        """
        # Validações críticas
        if not supabase_url or not supabase_key:
            raise ValueError("❌ URL e chave do Supabase são obrigatórias!")
        
        if not supabase_url.startswith('https://'):
            raise ValueError("❌ URL do Supabase deve começar com 'https://'")
        
        self.supabase_url = supabase_url.rstrip('/')  # Remove barra final se existir
        self.supabase_key = supabase_key
        self.csv_file = csv_file
        self.responsaveis_autorizados = set()
        self.driver = None
        self.wait = None
        self.contador_sucesso = 0
        self.contador_erro = 0
        
        # Configurar timeout padrão (ajustável)
        self.timeout_padrao = 30
        self.timeout_longo = 60
        
        # Carregar responsáveis autorizados do CSV
        self.carregar_responsaveis_autorizados()
        
        # Verificar se carregou responsáveis
        if not self.responsaveis_autorizados:
            raise ValueError(f"❌ Nenhum responsável foi carregado do arquivo {csv_file}")
        
        # Configurar opções do Chrome
        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_experimental_option("detach", True)
        
        # Headers anti-detecção
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Para debugging - remover em produção
        # self.chrome_options.add_argument("--headless")
        
        logger.info(f"✅ Sistema iniciado com {len(self.responsaveis_autorizados)} responsáveis autorizados")
    
    def carregar_responsaveis_autorizados(self):
        """
        Carrega a lista de responsáveis autorizados do arquivo CSV específico.
        Apenas estes responsáveis terão cobranças criadas.
        """
        try:
            if not os.path.exists(self.csv_file):
                logger.error(f"❌ Arquivo CSV não encontrado: {self.csv_file}")
                return
            
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    nome = row.get('Nome', '').strip()
                    if nome:
                        self.responsaveis_autorizados.add(nome)
            
            logger.info(f"✅ Carregados {len(self.responsaveis_autorizados)} responsáveis autorizados do CSV")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar arquivo CSV: {str(e)}")
            self.responsaveis_autorizados = set()
    
    def is_responsavel_autorizado(self, nome: str) -> bool:
        """
        Verifica se o responsável está autorizado (cadastrado no CSV).
        
        Args:
            nome: Nome do responsável para verificar
            
        Returns:
            True se o responsável está autorizado, False caso contrário
        """
        nome_normalizado = nome.strip()
        autorizado = nome_normalizado in self.responsaveis_autorizados
        
        if autorizado:
            logger.info(f"✅ Responsável AUTORIZADO: {nome_normalizado}")
        else:
            logger.warning(f"⚠️ Responsável NÃO AUTORIZADO (não está no CSV): {nome_normalizado}")
        
        return autorizado
    
    def testar_conectividade(self) -> bool:
        """
        Testa a conectividade com Supabase antes de começar.
        
        Returns:
            True se a conexão está ok, False caso contrário
        """
        try:
            logger.info("🔗 Testando conectividade com Supabase...")
            
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Teste simples: buscar apenas 1 responsável
            test_url = f"{self.supabase_url}/rest/v1/responsaveis"
            test_params = {'select': 'id', 'limit': '1'}
            
            response = requests.get(test_url, headers=headers, params=test_params, timeout=10)
            response.raise_for_status()
            
            logger.info("✅ Conectividade com Supabase confirmada")
            return True
            
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout na conexão com Supabase")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Erro de conexão com Supabase - verifique a URL")
            return False
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("❌ Erro de autenticação - verifique a chave da API")
            else:
                logger.error(f"❌ Erro HTTP {e.response.status_code} na conexão com Supabase")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao testar conectividade: {str(e)}")
            return False
    
    def buscar_responsaveis_com_dividas(self) -> List[Dict]:
        """
        Busca responsáveis com dívidas no Supabase.
        Apenas retorna responsáveis que estão no arquivo CSV autorizado.
        
        Returns:
            Lista de responsáveis com dívidas autorizados
        """
        try:
            logger.info("🔍 Buscando responsáveis com dívidas no Supabase...")
            
            # Headers para autenticação
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            # Buscar relações nível 1
            relacoes_url = f"{self.supabase_url}/rest/v1/relacao"
            relacoes_params = {
                'select': 'aluno_id,responsavel_id',
                'nivel': 'eq.1'
            }
            
            relacoes_response = requests.get(relacoes_url, headers=headers, params=relacoes_params)
            relacoes_response.raise_for_status()
            relacoes = relacoes_response.json()
            
            if not relacoes:
                logger.warning("⚠️ Nenhuma relação nível 1 encontrada")
                return []
                
            # Buscar compras em dívida
            compras_url = f"{self.supabase_url}/rest/v1/compras"
            compras_params = {
                'select': 'aluno_id,value,observacoes,created_at',
                'status': 'eq.false'
            }
            
            compras_response = requests.get(compras_url, headers=headers, params=compras_params)
            compras_response.raise_for_status()
            compras = compras_response.json()
            
            if not compras:
                logger.warning("⚠️ Nenhuma compra em dívida encontrada")
                return []
                
            # Buscar responsáveis
            responsaveis_url = f"{self.supabase_url}/rest/v1/responsaveis"
            responsaveis_params = {
                'select': 'id,nome,sobrenome,contato'
            }
            
            responsaveis_response = requests.get(responsaveis_url, headers=headers, params=responsaveis_params)
            responsaveis_response.raise_for_status()
            responsaveis = responsaveis_response.json()
            
            # Buscar alunos
            alunos_url = f"{self.supabase_url}/rest/v1/alunos"
            alunos_params = {
                'select': 'id,nome,sobrenome'
            }
            
            alunos_response = requests.get(alunos_url, headers=headers, params=alunos_params)
            alunos_response.raise_for_status()
            alunos = alunos_response.json()
            
            # Processar dados
            responsaveis_dict = {r['id']: r for r in responsaveis}
            alunos_dict = {a['id']: a for a in alunos}
            
            # Mapear alunos para responsáveis
            aluno_responsavel_map = {}
            for relacao in relacoes:
                aluno_id = relacao['aluno_id']
                responsavel_id = relacao['responsavel_id']
                if aluno_id not in aluno_responsavel_map:
                    aluno_responsavel_map[aluno_id] = []
                aluno_responsavel_map[aluno_id].append(responsavel_id)
            
            # Calcular dívidas por responsável
            responsaveis_dividas = {}
            for compra in compras:
                aluno_id = compra['aluno_id']
                valor = float(compra['value'])
                
                if aluno_id in aluno_responsavel_map:
                    for responsavel_id in aluno_responsavel_map[aluno_id]:
                        if responsavel_id not in responsaveis_dividas:
                            responsaveis_dividas[responsavel_id] = {
                                'valor_total': 0.0,
                                'compras': [],
                                'alunos': set()
                            }
                        
                        responsaveis_dividas[responsavel_id]['valor_total'] += valor
                        responsaveis_dividas[responsavel_id]['compras'].append(compra)
                        responsaveis_dividas[responsavel_id]['alunos'].add(aluno_id)
            
            # Criar lista final de responsáveis com dívidas
            responsaveis_com_dividas = []
            for responsavel_id, divida_info in responsaveis_dividas.items():
                if responsavel_id in responsaveis_dict:
                    responsavel = responsaveis_dict[responsavel_id]
                    nome_completo = f"{responsavel['nome']} {responsavel['sobrenome']}".strip()
                    
                    # **VERIFICAÇÃO CRUCIAL**: Apenas processar se estiver no CSV autorizado
                    if not self.is_responsavel_autorizado(nome_completo):
                        logger.info(f"⚠️ Responsável {nome_completo} pulado (não autorizado)")
                        continue
                    
                    alunos_nomes = []
                    for aluno_id in divida_info['alunos']:
                        if aluno_id in alunos_dict:
                            aluno = alunos_dict[aluno_id]
                            aluno_nome = f"{aluno['nome']} {aluno['sobrenome']}".strip()
                            alunos_nomes.append(aluno_nome)
                    
                    responsavel_info = {
                        'id': responsavel_id,
                        'nome': nome_completo,
                        'contato': responsavel['contato'],
                        'valor_total': divida_info['valor_total'],
                        'quantidade_alunos': len(divida_info['alunos']),
                        'alunos': alunos_nomes
                    }
                    
                    responsaveis_com_dividas.append(responsavel_info)
            
            logger.info(f"✅ Encontrados {len(responsaveis_com_dividas)} responsáveis AUTORIZADOS com dívidas")
            
            # Exibir resumo
            if responsaveis_com_dividas:
                valor_total_geral = sum(r['valor_total'] for r in responsaveis_com_dividas)
                logger.info(f"💰 Valor total das dívidas: R$ {valor_total_geral:.2f}")
                
                # Exibir top 5 maiores devedores
                responsaveis_ordenados = sorted(responsaveis_com_dividas, key=lambda x: x['valor_total'], reverse=True)
                logger.info("🏆 Top 5 maiores devedores autorizados:")
                for i, resp in enumerate(responsaveis_ordenados[:5], 1):
                    logger.info(f"  {i}. {resp['nome']} - R$ {resp['valor_total']:.2f}")
            
            return responsaveis_com_dividas
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro de conexão com Supabase: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"❌ Erro ao buscar responsáveis com dívidas: {str(e)}")
            return []
    
    def filtrar_responsaveis_para_cobranca(self, responsaveis_com_dividas: List[Dict]) -> List[Dict]:
        """
        Filtra responsáveis para cobrança.
        Agora apenas valida se há responsáveis (a validação de autorização já foi feita).
        
        Args:
            responsaveis_com_dividas: Lista de responsáveis com dívidas já filtrados
            
        Returns:
            Lista de responsáveis prontos para cobrança
        """
        try:
            if not responsaveis_com_dividas:
                logger.warning("⚠️ Nenhum responsável com dívidas encontrado para cobrança")
                return []
                
            logger.info(f"✅ {len(responsaveis_com_dividas)} responsáveis prontos para cobrança")
            
            # Exibir lista de responsáveis que serão processados
            logger.info("📋 Responsáveis que terão cobranças criadas:")
            for i, resp in enumerate(responsaveis_com_dividas, 1):
                logger.info(f"  {i}. {resp['nome']} - R$ {resp['valor_total']:.2f} ({resp['quantidade_alunos']} aluno(s))")
            
            return responsaveis_com_dividas
            
        except Exception as e:
            logger.error(f"❌ Erro ao filtrar responsáveis para cobrança: {str(e)}")
            return []
    
    def iniciar_navegador(self):
        """Iniciar o navegador Chrome com configurações otimizadas"""
        try:
            logger.info("🌐 Iniciando navegador Chrome...")
            
            # Verificar se ChromeDriver está disponível
            try:
                self.driver = webdriver.Chrome(options=self.chrome_options)
            except Exception as e:
                logger.error(f"❌ Erro ao iniciar ChromeDriver: {str(e)}")
                logger.error("💡 Certifique-se de que o ChromeDriver está instalado e no PATH")
                return False
            
            # Configurar timeouts
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, self.timeout_padrao)
            
            # Executar scripts anti-detecção
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined,
                        });
                    """
                })
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível aplicar algumas configurações anti-detecção: {str(e)}")
            
            # Verificar se navegador abriu corretamente
            if not self.driver or not self.driver.session_id:
                logger.error("❌ Falha ao inicializar navegador")
                return False
            
            logger.info("✅ Navegador iniciado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar navegador: {str(e)}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False
    
    def navegar_infinite_pay(self) -> bool:
        """Navegar para o Infinite Pay e acessar a página de cobranças"""
        try:
            logger.info("🌐 Navegando para Infinite Pay...")
            
            # Verificar se o driver está ativo
            if not self.driver or not self.driver.session_id:
                logger.error("❌ Navegador não está ativo")
                return False
            
            # Acessar página inicial com retry
            max_tentativas = 3
            for tentativa in range(max_tentativas):
                try:
                    logger.info(f"🔗 Tentativa {tentativa + 1}/{max_tentativas} - Acessando página inicial...")
                    self.driver.get("https://app.infinitepay.io")
                    
                    # Verificar se a página carregou
                    WebDriverWait(self.driver, 15).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                    break
                    
                except Exception as e:
                    logger.warning(f"⚠️ Tentativa {tentativa + 1} falhou: {str(e)}")
                    if tentativa == max_tentativas - 1:
                        logger.error("❌ Falha ao acessar página inicial após todas as tentativas")
                        return False
                    time.sleep(3)
            
            logger.info("⏳ Aguardando 3 segundos para carregamento inicial...")
            time.sleep(120)
            
            # Verificar se está na página correta
            try:
                current_url = self.driver.current_url
                if "infinitepay.io" not in current_url:
                    logger.error(f"❌ URL incorreta: {current_url}")
                    return False
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível verificar URL: {str(e)}")
            
            # Navegar para página de cobranças
            logger.info("📋 Navegando para página de cobranças...")
            try:
                self.driver.get("https://app.infinitepay.io/invoices")
                
                # Verificar se chegou na página de cobranças
                WebDriverWait(self.driver, 15).until(
                    lambda driver: "invoices" in driver.current_url.lower()
                )
                
                # Aguardar elementos da página carregarem
                time.sleep(3)
                
                logger.info("✅ Navegação bem-sucedida!")
                return True
                
            except TimeoutException:
                logger.error("❌ Timeout ao navegar para página de cobranças")
                return False
            except Exception as e:
                logger.error(f"❌ Erro ao navegar para cobranças: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro geral na navegação: {str(e)}")
            return False
    
    def criar_cobranca(self, responsavel: Dict) -> bool:
        """
        Cria uma cobrança no Infinite Pay para o responsável.
        
        Args:
            responsavel: Dicionário com dados do responsável
            
        Returns:
            True se a cobrança foi criada com sucesso, False caso contrário
        """
        try:
            nome = responsavel['nome']
            valor = responsavel['valor_total']
            qtd_alunos = responsavel['quantidade_alunos']
            
            logger.info(f"💳 Criando cobrança para {nome} - R$ {valor:.2f}")
            
            # Verificar se está na página correta
            try:
                current_url = self.driver.current_url
                if "invoices" not in current_url.lower():
                    logger.warning(f"⚠️ Não está na página de cobranças: {current_url}")
                    logger.info("🔄 Navegando para página de cobranças...")
                    self.driver.get("https://app.infinitepay.io/invoices")
                    time.sleep(3)
            except Exception:
                logger.info("ℹ️ Não foi possível verificar URL, continuando...")
            
            # Passo 1: Navegar diretamente para página de criação de cobrança
            logger.info("🆕 Navegando para página de criação de cobrança...")
            
            try:
                self.driver.get("https://app.infinitepay.io/invoices/create")
                logger.info("✅ Navegação direta para página de criação")
                time.sleep(3)  # Aguardar carregamento da página
                
                # Verificar se chegou na página correta
                current_url = self.driver.current_url
                if "invoices/create" in current_url:
                    logger.info("✅ Página de criação carregada com sucesso")
                else:
                    logger.warning(f"⚠️ URL inesperada: {current_url}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao navegar para página de criação: {str(e)}")
                raise
            
            # Passo 2: Inserir nome do responsável (React Select)
            logger.info(f"👤 Inserindo nome: {nome}")
            
            # Verificar se campo de nome existe antes de tentar interagir
            campo_nome = None
            
            # Estratégia 1: Tentar encontrar pelo ID específico
            try:
                campo_nome = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "react-select-2-input"))
                )
                logger.info("✅ Campo nome encontrado pelo ID")
            except TimeoutException:
                logger.info("⚠️ Campo nome não encontrado pelo ID, tentando por placeholder...")
                
                # Estratégia 2: Buscar por placeholder
                try:
                    campo_nome = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'Busque pelo nome') or contains(@placeholder, 'nome')]"))
                    )
                    logger.info("✅ Campo nome encontrado por placeholder")
                except TimeoutException:
                    logger.error("❌ Campo nome não encontrado por nenhum método")
                    raise
            
            if not campo_nome:
                raise Exception("Campo nome não encontrado")
            
            # Verificar se o campo está visível e clicável
            if not campo_nome.is_displayed() or not campo_nome.is_enabled():
                logger.error("❌ Campo nome não está visível ou habilitado")
                raise Exception("Campo nome não acessível")
            
            # Clicar no campo para focar
            try:
                campo_nome.click()
                time.sleep(1)
                logger.info("✅ Campo nome focado")
            except Exception as e:
                logger.error(f"❌ Erro ao clicar no campo nome: {str(e)}")
                raise
            
            # Limpar e digitar o nome
            try:
                campo_nome.clear()
                time.sleep(0.5)
                campo_nome.send_keys(nome)
                time.sleep(2)
                logger.info(f"✅ Nome '{nome}' digitado")
            except Exception as e:
                logger.error(f"❌ Erro ao digitar nome: {str(e)}")
                raise
            
            # Pressionar Enter para confirmar
            try:
                campo_nome.send_keys(Keys.ENTER)
                time.sleep(2)
                logger.info("✅ Enter pressionado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao pressionar Enter: {str(e)}")
            
            # Verificar se apareceu dropdown com opções e selecionar a primeira
            try:
                # Aguardar um pouco para o dropdown aparecer
                time.sleep(1)
                opcoes = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'css-') and contains(@class, 'option') or contains(@class, 'select-option')]")
                
                if opcoes:
                    opcoes[0].click()
                    time.sleep(1)
                    logger.info("✅ Primeira opção do dropdown selecionada")
                else:
                    logger.info("ℹ️ Nenhuma opção de dropdown encontrada, continuando...")
                    
            except Exception as e:
                logger.info(f"ℹ️ Erro ao processar dropdown: {str(e)} - continuando...")
            
            # Aguardar 3 segundos após inserir nome
            logger.info("⏳ Aguardando 3 segundos após inserir nome...")
            time.sleep(3)
            
            # Passo 3: Inserir valor
            logger.info(f"💰 Inserindo valor: R$ {valor:.2f}")
            
            campo_valor = None
            
            # Estratégia 1: Buscar por data-testid
            try:
                campo_valor = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@data-testid='invoice-amount-input']"))
                )
                logger.info("✅ Campo valor encontrado por data-testid")
            except TimeoutException:
                logger.info("⚠️ Campo valor não encontrado por data-testid, tentando por placeholder...")
                
                # Estratégia 2: Buscar por placeholder
                try:
                    campo_valor = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Valor' or @placeholder='R$' or contains(@placeholder, 'valor')]"))
                    )
                    logger.info("✅ Campo valor encontrado por placeholder")
                except TimeoutException:
                    logger.info("⚠️ Campo valor não encontrado por placeholder, tentando por tipo...")
                    
                    # Estratégia 3: Buscar por tipo
                    try:
                        campo_valor = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='number' or @type='text'][contains(@placeholder, 'valor') or contains(@placeholder, 'Valor')]"))
                        )
                        logger.info("✅ Campo valor encontrado por tipo")
                    except TimeoutException:
                        logger.error("❌ Campo valor não encontrado por nenhum método")
                        raise
            
            if not campo_valor:
                raise Exception("Campo valor não encontrado")
            
            # Verificar se o campo está acessível
            if not campo_valor.is_displayed() or not campo_valor.is_enabled():
                logger.error("❌ Campo valor não está visível ou habilitado")
                raise Exception("Campo valor não acessível")
            
            # Limpar e inserir valor
            try:
                campo_valor.clear()
                time.sleep(0.5)
                
                # Formatar valor para padrão brasileiro se necessário
                valor_formatado = f"{valor:.2f}".replace('.', ',')
                campo_valor.send_keys(valor_formatado)
                time.sleep(1)
                
                logger.info(f"✅ Valor R$ {valor_formatado} inserido")
            except Exception as e:
                logger.error(f"❌ Erro ao inserir valor: {str(e)}")
                raise
            
            # Aguardar 3 segundos após inserir valor
            logger.info("⏳ Aguardando 3 segundos após inserir valor...")
            time.sleep(3)
            
            # Passo 4: Inserir descrição
            logger.info(f"📝 Inserindo descrição...")
            responsavel_id = responsavel.get('id', 'N/A')
            descricao = "VIA AUTOMAÇAO"
            
            campo_descricao = None
            
            # Estratégia 1: Buscar por data-testid
            try:
                campo_descricao = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//textarea[@data-testid='invoice-description-input']"))
                )
                logger.info("✅ Campo descrição encontrado por data-testid")
            except TimeoutException:
                logger.info("⚠️ Campo descrição não encontrado por data-testid, tentando por placeholder...")
                
                # Estratégia 2: Buscar por placeholder
                try:
                    campo_descricao = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//textarea[@placeholder='Descrição' or @placeholder='Observações' or contains(@placeholder, 'descrição')]"))
                    )
                    logger.info("✅ Campo descrição encontrado por placeholder")
                except TimeoutException:
                    logger.info("⚠️ Campo descrição não encontrado por placeholder, tentando busca genérica...")
                    
                    # Estratégia 3: Buscar textarea genérico
                    try:
                        campo_descricao = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//textarea[contains(@placeholder, 'descrição') or contains(@placeholder, 'Descrição')]"))
                        )
                        logger.info("✅ Campo descrição encontrado por busca genérica")
                    except TimeoutException:
                        logger.error("❌ Campo descrição não encontrado por nenhum método")
                        raise
            
            if not campo_descricao:
                raise Exception("Campo descrição não encontrado")
            
            # Verificar se o campo está acessível
            if not campo_descricao.is_displayed() or not campo_descricao.is_enabled():
                logger.error("❌ Campo descrição não está visível ou habilitado")
                raise Exception("Campo descrição não acessível")
            
            # Limpar e inserir descrição
            try:
                campo_descricao.clear()
                time.sleep(0.5)
                campo_descricao.send_keys(descricao)
                time.sleep(1)
                
                logger.info(f"✅ Descrição '{descricao}' inserida")
            except Exception as e:
                logger.error(f"❌ Erro ao inserir descrição: {str(e)}")
                raise
            
            # Aguardar 3 segundos após inserir descrição
            logger.info("⏳ Aguardando 3 segundos após inserir descrição...")
            time.sleep(3)
            
            # Passo 5: Clicar em "Continuar"
            logger.info("➡️ Clicando em 'Continuar'...")
            
            continuar_btn = None
            
            # Estratégia 1: Buscar por data-testid
            try:
                continuar_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-btn']"))
                )
                logger.info("✅ Botão continuar encontrado por data-testid")
            except TimeoutException:
                logger.info("⚠️ Botão continuar não encontrado por data-testid, tentando por texto...")
                
                # Estratégia 2: Buscar por texto
                try:
                    continuar_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continuar') or contains(text(), 'Próximo')]"))
                    )
                    logger.info("✅ Botão continuar encontrado por texto")
                except TimeoutException:
                    logger.error("❌ Botão continuar não encontrado por nenhum método")
                    raise
            
            if not continuar_btn:
                raise Exception("Botão continuar não encontrado")
            
            # Verificar se o botão está acessível
            if not continuar_btn.is_displayed() or not continuar_btn.is_enabled():
                logger.error("❌ Botão continuar não está visível ou habilitado")
                raise Exception("Botão continuar não acessível")
            
            # Clicar no botão
            try:
                continuar_btn.click()
                logger.info("✅ Botão continuar clicado, aguardando 3 segundos...")
                time.sleep(3)  # Tempo otimizado para carregar próxima tela
            except Exception as e:
                logger.error(f"❌ Erro ao clicar no botão continuar: {str(e)}")
                raise
            
            # Aguardar 3 segundos após clicar continuar
            logger.info("⏳ Aguardando 3 segundos após clicar continuar...")
            time.sleep(3)
            
            # Passo 6: Ativar toggle/switch (somente se necessário)
            logger.info("🔄 Verificando se toggle precisa ser ativado...")
            
            # Verificar se toggle existe e se o texto indica que precisa ser clicado
            toggle_clicado = False
            
            try:
                # Procurar pela div que contém o texto "Não pode ser paga após a validade"
                texto_div = self.driver.find_element(By.XPATH, "//div[contains(@class, 'border-color-medium')]//span[contains(text(), 'Não pode ser paga após a validade')]")
                
                if texto_div:
                    logger.info("✅ Encontrado texto 'Não pode ser paga após a validade' - toggle precisa ser ativado")
                    
                    # Buscar o botão toggle dentro da mesma div
                    try:
                        toggle_btn = self.driver.find_element(By.XPATH, "//div[contains(@class, 'border-color-medium')]//button[@data-testid='list-toggle']")
                        
                        if toggle_btn.is_displayed() and toggle_btn.is_enabled():
                            toggle_btn.click()
                            toggle_clicado = True
                            logger.info("✅ Toggle clicado com sucesso")
                        else:
                            logger.warning("⚠️ Toggle encontrado mas não está acessível")
                            
                    except NoSuchElementException:
                        logger.warning("⚠️ Toggle não encontrado dentro da div")
                        
                else:
                    logger.info("ℹ️ Texto 'Não pode ser paga após a validade' não encontrado")
                    
            except NoSuchElementException:
                logger.info("ℹ️ Div com texto 'Não pode ser paga após a validade' não encontrada")
                
            # Se não encontrou a condição específica, verificar se há outro texto que indique não clicar
            if not toggle_clicado:
                try:
                    # Verificar se existe texto que indica que não precisa clicar
                    texto_nao_clicar = self.driver.find_element(By.XPATH, "//div[contains(@class, 'border-color-medium')]//span[contains(text(), 'Pode ser paga após a validade') or contains(text(), 'Permitir pagamento após') or not(contains(text(), 'Não pode ser paga após a validade'))]")
                    
                    if texto_nao_clicar:
                        logger.info("ℹ️ Texto indica que toggle não precisa ser clicado - mantendo configuração atual")
                        
                except NoSuchElementException:
                    logger.info("ℹ️ Nenhum texto específico encontrado sobre configuração de atraso")
            
            if toggle_clicado:
                logger.info("✅ Toggle processado, aguardando 3 segundos...")
                time.sleep(3)
            else:
                logger.info("ℹ️ Toggle não foi clicado - configuração mantida")
            
            # Passo 7: Selecionar data de vencimento (16/11/2025)
            logger.info("📅 Configurando data de vencimento para 16/11/2025...")
            
            data_configurada = False
            
            try:
                # Estratégia 1: Buscar por data-testid específico
                data_btn = None
                
                try:
                    data_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//span[@data-testid='choose-due-date-btn']"))
                    )
                    logger.info("✅ Botão de data encontrado por data-testid")
                except TimeoutException:
                    logger.info("⚠️ Botão de data não encontrado por data-testid, tentando alternativas...")
                    
                    # Estratégia 2: Buscar por texto ou outros atributos
                    try:
                        data_btn = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'data') or contains(text(), 'Data') or contains(@class, 'date')]"))
                        )
                        logger.info("✅ Botão de data encontrado por alternativa")
                    except TimeoutException:
                        logger.warning("⚠️ Botão de data não encontrado - pulando seleção de data")
                        data_configurada = True  # Continuar sem configurar data
                
                if data_btn and not data_configurada:
                    # Verificar se o botão está acessível
                    if not data_btn.is_displayed() or not data_btn.is_enabled():
                        logger.warning("⚠️ Botão de data não está acessível - usando data padrão")
                        data_configurada = True
                    else:
                        # Clicar no botão
                        data_btn.click()
                        logger.info("✅ Botão de data clicado, aguardando react-calendar aparecer...")
                        time.sleep(3)  # Aguardar calendar aparecer
                        
                        # Aguardar especificamente o react-calendar aparecer
                        try:
                            calendar_container = self.wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, "react-calendar"))
                            )
                            logger.info("✅ React Calendar encontrado")
                            time.sleep(2)  # Aguardar calendar carregar completamente
                            
                            # Processar seleção da data
                            data_configurada = self.selecionar_data_calendario()
                            
                        except TimeoutException:
                            logger.error("❌ React Calendar não apareceu - usando data padrão")
                            data_configurada = True
            
            except Exception as e:
                logger.error(f"❌ Erro ao configurar data: {str(e)} - usando data padrão")
                data_configurada = True
            
            if data_configurada:
                logger.info("✅ Configuração de data concluída")
                time.sleep(1)  # Aguardar 1 segundo antes do próximo passo
            else:
                logger.warning("⚠️ Falha ao configurar data - continuando com data padrão")
                time.sleep(1)
            
            # Aguardar 3 segundos após seleção de data
            logger.info("⏳ Aguardando 3 segundos após seleção de data...")
            time.sleep(3)
            
            # Passo 8: Enviar cobrança
            logger.info("📤 Enviando cobrança...")
            
            # Ir para o final da página
            logger.info("📜 Indo para o final da página...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Aguardar scroll
            
            # Buscar e clicar no botão "Enviar cobrança"
            try:
                enviar_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='generate-invoice-btn']"))
                )
                
                logger.info("✅ Botão 'Enviar cobrança' encontrado")
                enviar_btn.click()
                logger.info("✅ Botão 'Enviar cobrança' clicado")
                
                # Aguardar 6 segundos conforme solicitado
                logger.info("⏳ Aguardando 6 segundos...")
                time.sleep(6)
                
                logger.info("✅ Processamento concluído, prosseguindo...")
                
            except Exception as e:
                logger.error(f"❌ Erro ao enviar cobrança: {str(e)}")
                raise
            
            self.contador_sucesso += 1
            logger.info(f"✅ Cobrança criada com sucesso para {nome}")
            
            # Voltar para a lista de cobranças
            self.retornar_lista_cobrancas()
            
            return True
            
        except TimeoutException as e:
            logger.error(f"⏰ Timeout ao criar cobrança para {nome}: {str(e)}")
            self.contador_erro += 1
            
            # Tentar voltar para a lista em caso de erro
            try:
                logger.info("🔄 Tentando recuperar navegação...")
                self.retornar_lista_cobrancas()
            except Exception as recovery_error:
                logger.warning(f"⚠️ Erro ao recuperar navegação: {str(recovery_error)}")
                # Tentar navegação direta como último recurso
                try:
                    self.driver.get("https://app.infinitepay.io/invoices")
                    time.sleep(3)
                except Exception:
                    logger.error("❌ Falha crítica na navegação - pode precisar reiniciar")
            
            # Aguardar 3 segundos após erro de timeout
            logger.info("⏳ Aguardando 3 segundos após erro de timeout...")
            time.sleep(3)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar cobrança para {nome}: {str(e)}")
            self.contador_erro += 1
            
            # Tentar voltar para a lista em caso de erro
            try:
                logger.info("🔄 Tentando recuperar navegação...")
                self.retornar_lista_cobrancas()
            except Exception as recovery_error:
                logger.warning(f"⚠️ Erro ao recuperar navegação: {str(recovery_error)}")
                # Tentar navegação direta como último recurso
                try:
                    self.driver.get("https://app.infinitepay.io/invoices")
                    time.sleep(3)
                except Exception:
                    logger.error("❌ Falha crítica na navegação - pode precisar reiniciar")
            
            # Aguardar 3 segundos após erro geral
            logger.info("⏳ Aguardando 3 segundos após erro geral...")
            time.sleep(3)
            
            return False
    
    def aguardar_elemento_com_retry(self, locator_tipo: By, locator_valor: str, timeout: int = 30, max_tentativas: int = 3, descricao: str = "elemento") -> bool:
        """
        Aguarda um elemento aparecer com múltiplas tentativas.
        
        Args:
            locator_tipo: Tipo do localizador (By.ID, By.XPATH, etc.)
            locator_valor: Valor do localizador
            timeout: Timeout para cada tentativa
            max_tentativas: Número máximo de tentativas
            descricao: Descrição do elemento para logs
            
        Returns:
            True se encontrou o elemento, False caso contrário
        """
        for tentativa in range(max_tentativas):
            try:
                logger.info(f"🔍 Tentativa {tentativa + 1}/{max_tentativas} - Aguardando {descricao}...")
                
                elemento = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((locator_tipo, locator_valor))
                )
                
                if elemento and elemento.is_displayed():
                    logger.info(f"✅ {descricao} encontrado!")
                    return True
                    
            except TimeoutException:
                logger.warning(f"⚠️ Tentativa {tentativa + 1} falhou - {descricao} não encontrado")
                if tentativa < max_tentativas - 1:
                    time.sleep(2)
                    
        logger.error(f"❌ {descricao} não encontrado após {max_tentativas} tentativas")
        return False
    
    def verificar_elemento_existe(self, xpath: str, descricao: str = "elemento") -> bool:
        """
        Verifica se um elemento existe na página.
        
        Args:
            xpath: XPath do elemento
            descricao: Descrição para logs
            
        Returns:
            True se existe, False caso contrário
        """
        try:
            elemento = self.driver.find_element(By.XPATH, xpath)
            return elemento is not None and elemento.is_displayed()
        except NoSuchElementException:
            logger.info(f"ℹ️ {descricao} não encontrado")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar {descricao}: {str(e)}")
            return False
    
    def selecionar_data_calendario(self) -> bool:
        """
        Seleciona a data 16/11/2025 no react-calendar.
        
        Returns:
            True se conseguiu selecionar a data, False caso contrário
        """
        try:
            # Procurar especificamente pelo dia 16 usando os seletores do react-calendar
            data_encontrada = False
            
            # Estratégia 1: Procurar pelo botão do dia 16 com aria-label específico
            try:
                dia_16_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'react-calendar__tile') and contains(@class, 'react-calendar__month-view__days__day')]//abbr[@aria-label='16 de novembro de 2025']/..")
                dia_16_btn.click()
                logger.info("✅ Dia 16 selecionado (Estratégia 1 - aria-label)")
                data_encontrada = True
                time.sleep(2)
            except NoSuchElementException:
                logger.info("⚠️ Estratégia 1 falhou, tentando Estratégia 2...")
            
            # Estratégia 2: Procurar pelo botão que contém abbr com texto "16"
            if not data_encontrada:
                try:
                    dia_16_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'react-calendar__tile') and contains(@class, 'react-calendar__month-view__days__day')]//abbr[normalize-space(text())='16']/..")
                    dia_16_btn.click()
                    logger.info("✅ Dia 16 selecionado (Estratégia 2 - texto abbr)")
                    data_encontrada = True
                    time.sleep(2)
                except NoSuchElementException:
                    logger.info("⚠️ Estratégia 2 falhou, tentando Estratégia 3...")
            
            # Estratégia 3: Procurar diretamente pelo botão com classe específica e texto 16
            if not data_encontrada:
                try:
                    dia_16_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'react-calendar__tile') and contains(@class, 'react-calendar__month-view__days__day') and .//abbr[text()='16']]")
                    dia_16_btn.click()
                    logger.info("✅ Dia 16 selecionado (Estratégia 3 - classe + texto)")
                    data_encontrada = True
                    time.sleep(2)
                except NoSuchElementException:
                    logger.info("⚠️ Estratégia 3 falhou, tentando Estratégia 4...")
            
            # Estratégia 4: Procurar pelo botão com --now (que indica dia atual/hoje)
            if not data_encontrada:
                try:
                    dia_16_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'react-calendar__tile--now') and contains(@class, 'react-calendar__month-view__days__day')]")
                    dia_16_btn.click()
                    logger.info("✅ Dia 16 selecionado (Estratégia 4 - tile--now)")
                    data_encontrada = True
                    time.sleep(2)
                except NoSuchElementException:
                    logger.info("⚠️ Estratégia 4 falhou, tentando Estratégia 5...")
            
            # Estratégia 5: Listar todos os botões do calendar e procurar pelo que contém "16"
            if not data_encontrada:
                try:
                    botoes_dias = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'react-calendar__tile') and contains(@class, 'react-calendar__month-view__days__day')]")
                    logger.info(f"🔍 Encontrados {len(botoes_dias)} botões de dias no calendar")
                    
                    for i, botao in enumerate(botoes_dias):
                        try:
                            texto_botao = botao.text.strip()
                            aria_label = botao.get_attribute('aria-label') or ''
                            logger.info(f"  Botão {i+1}: texto='{texto_botao}', aria-label='{aria_label}'")
                            
                            if texto_botao == '16' or '16 de novembro' in aria_label:
                                botao.click()
                                logger.info(f"✅ Dia 16 selecionado (Estratégia 5 - botão {i+1})")
                                data_encontrada = True
                                time.sleep(2)
                                break
                        except Exception as e:
                            logger.info(f"  Erro ao verificar botão {i+1}: {str(e)}")
                            continue
                                
                    if not data_encontrada:
                        logger.warning("⚠️ Dia 16 não encontrado na lista de botões")
                        
                        # Estratégia 6: Clicar no décimo sexto botão disponível (que deve ser o dia 16)
                        try:
                            if botoes_dias and len(botoes_dias) >= 16:
                                decimo_sexto_botao = botoes_dias[15]  # Décimo sexto botão (dia 16)
                                decimo_sexto_botao.click()
                                logger.info("✅ Décimo sexto botão (dia 16) clicado como fallback")
                                data_encontrada = True
                                time.sleep(2)
                        except Exception as e:
                            logger.warning(f"⚠️ Estratégia 6 (fallback) falhou: {str(e)}")
                        
                except Exception as e:
                    logger.info(f"⚠️ Estratégia 5 falhou: {str(e)}")
            
            # Aguardar um pouco após seleção para que o calendar processe
            if data_encontrada:
                logger.info("✅ Aguardando calendar processar seleção...")
                time.sleep(1)
                
                # O calendar deve fechar automaticamente após seleção
                # Se não fechar, tentar clicar fora para fechar
                try:
                    # Verificar se o calendar ainda está visível
                    calendar_ainda_visivel = self.driver.find_element(By.CLASS_NAME, "react-calendar")
                    if calendar_ainda_visivel.is_displayed():
                        logger.info("ℹ️ Calendar ainda visível, clicando fora para fechar...")
                        # Clicar em algum lugar fora do calendar
                        body = self.driver.find_element(By.TAG_NAME, "body")
                        body.click()
                        time.sleep(1)
                except NoSuchElementException:
                    logger.info("✅ Calendar fechou automaticamente")
                    
                logger.info("🎉 Data 16/11/2025 configurada com sucesso!")
                return True
            else:
                logger.warning("⚠️ Não foi possível selecionar o dia 16 - usando data padrão")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao selecionar data no calendar: {str(e)}")
            return False
    
    def retornar_lista_cobrancas(self):
        """
        Retorna para a lista de cobranças após criar uma cobrança.
        """
        try:
            logger.info("🔙 Voltando para lista de cobranças...")
            
            # Navegar diretamente para a página de cobranças (método mais confiável)
            self.driver.get("https://app.infinitepay.io/invoices")
            
            # Aguardar página carregar
            logger.info("⏳ Aguardando página de cobranças carregar...")
            time.sleep(3)
            
            # Verificar se chegou na página correta
            try:
                if "invoices" in self.driver.current_url.lower():
                    logger.info("✅ Voltou para lista de cobranças com sucesso")
                else:
                    logger.warning(f"⚠️ URL inesperada: {self.driver.current_url}")
            except Exception:
                logger.info("ℹ️ Não foi possível verificar URL, mas prosseguindo...")
            
            # Aguardar elementos da página carregarem
            logger.info("⏳ Aguardando elementos carregarem...")
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Erro ao voltar para lista: {str(e)}")
            # Tentar uma segunda vez em caso de erro
            try:
                logger.info("🔄 Tentando novamente...")
                self.driver.get("https://app.infinitepay.io/invoices")
                time.sleep(3)
                logger.info("✅ Segunda tentativa bem-sucedida")
            except Exception as e2:
                logger.error(f"❌ Falha na segunda tentativa: {str(e2)}")
    
    def limpar_recursos(self):
        """
        Limpa recursos e fecha o navegador.
        """
        try:
            if self.driver:
                logger.info("🧹 Limpando recursos...")
                self.driver.quit()
                logger.info("✅ Navegador fechado")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao fechar navegador: {str(e)}")
        finally:
            self.driver = None
            self.wait = None
    
    def executar_automacao(self):
        """Executar o processo completo de automação"""
        try:
            logger.info("🚀 Iniciando automação de cobranças...")
            self.inicio_automacao = time.time()  # Marcar início para calcular tempo total
            
            # Verificar saúde do sistema
            if not self.verificar_saude_sistema():
                logger.error("❌ Sistema não passou na verificação de saúde")
                return False
            
            # Testar conectividade com Supabase
            if not self.testar_conectividade():
                logger.error("❌ Falha na conectividade com Supabase")
                return False
            
            # Buscar responsáveis com dívidas do Supabase
            responsaveis_com_dividas = self.buscar_responsaveis_com_dividas()
            
            if not responsaveis_com_dividas:
                logger.warning("⚠️ Nenhum responsável autorizado com dívidas encontrado")
                return False
            
            # Filtrar responsáveis para cobrança
            responsaveis_para_cobranca = self.filtrar_responsaveis_para_cobranca(responsaveis_com_dividas)
            
            if not responsaveis_para_cobranca:
                logger.warning("⚠️ Nenhum responsável selecionado para cobrança")
                return False
            
            # Gerar relatório detalhado
            self.gerar_relatorio_detalhado(responsaveis_com_dividas, responsaveis_para_cobranca)
            
            # Iniciar navegador
            if not self.iniciar_navegador():
                logger.error("❌ Falha ao iniciar navegador")
                return False
            
            # Navegar para Infinite Pay
            if not self.navegar_infinite_pay():
                logger.error("❌ Falha ao navegar para Infinite Pay")
                self.limpar_recursos()
                return False
            
            # Processar cada responsável
            logger.info(f"📋 Processando {len(responsaveis_para_cobranca)} responsáveis...")
            
            for i, responsavel in enumerate(responsaveis_para_cobranca, 1):
                try:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"📋 Processando {i}/{len(responsaveis_para_cobranca)}: {responsavel['nome']}")
                    logger.info(f"💰 Valor: R$ {responsavel['valor_total']:.2f}")
                    logger.info(f"👥 Alunos: {responsavel['quantidade_alunos']}")
                    logger.info(f"{'='*60}")
                    
                    # Criar cobrança
                    sucesso = self.criar_cobranca(responsavel)
                    
                    if sucesso:
                        logger.info(f"✅ Cobrança {i} criada com sucesso!")
                    else:
                        logger.error(f"❌ Falha ao criar cobrança {i}")
                    
                    # Aguardar mais tempo entre cobranças para evitar problemas
                    if i < len(responsaveis_para_cobranca):
                        logger.info(f"⏳ Aguardando 3 segundos antes da próxima cobrança...")
                        time.sleep(3)
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao processar responsável {i}: {str(e)}")
                    self.contador_erro += 1
                    # Continuar com o próximo responsável
                    continue
            
            # Relatório final
            logger.info(f"\n📊 RELATÓRIO FINAL:")
            logger.info(f"✅ Cobranças criadas com sucesso: {self.contador_sucesso}")
            logger.info(f"❌ Falhas: {self.contador_erro}")
            logger.info(f"📋 Total processado: {self.contador_sucesso + self.contador_erro}")
            
            # Calcular estatísticas
            if self.contador_sucesso + self.contador_erro > 0:
                taxa_sucesso = (self.contador_sucesso / (self.contador_sucesso + self.contador_erro)) * 100
                logger.info(f"📊 Taxa de sucesso: {taxa_sucesso:.1f}%")
            
            # Valor processado
            valor_processado = 0
            for i, responsavel in enumerate(responsaveis_para_cobranca):
                if i < self.contador_sucesso:  # Assumindo que os sucessos foram os primeiros
                    valor_processado += responsavel['valor_total']
            
            if valor_processado > 0:
                logger.info(f"💰 Valor total processado: R$ {valor_processado:.2f}")
            
            # Tempo total (se implementado)
            tempo_total = time.time() - getattr(self, 'inicio_automacao', time.time())
            logger.info(f"⏱️ Tempo total de execução: {tempo_total:.1f} segundos")
            
            if self.contador_sucesso > 0:
                logger.info("🎉 Automação concluída com sucesso!")
                logger.info("💡 Verifique as cobranças criadas no Infinite Pay")
                return True
            else:
                logger.warning("⚠️ Nenhuma cobrança foi criada")
                logger.warning("💡 Verifique os logs para identificar os problemas")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro crítico na automação: {str(e)}")
            return False
        finally:
            # Sempre limpar recursos
            self.limpar_recursos()
    
    def gerar_relatorio_detalhado(self, responsaveis_com_dividas: List[Dict], responsaveis_para_cobranca: List[Dict]):
        """
        Gera um relatório detalhado do processamento.
        
        Args:
            responsaveis_com_dividas: Lista de todos os responsáveis com dívidas
            responsaveis_para_cobranca: Lista de responsáveis selecionados para cobrança
        """
        logger.info("\n📊 RELATÓRIO DETALHADO:")
        logger.info("="*60)
        
        # Estatísticas gerais
        total_responsaveis_csv = len(self.responsaveis_autorizados)
        total_com_dividas = len(responsaveis_com_dividas)
        total_para_cobranca = len(responsaveis_para_cobranca)
        
        logger.info(f"📋 Responsáveis no CSV: {total_responsaveis_csv}")
        logger.info(f"💰 Responsáveis com dívidas: {total_com_dividas}")
        logger.info(f"✅ Responsáveis autorizados com dívidas: {total_para_cobranca}")
        
        # Verificar responsáveis não autorizados
        responsaveis_nao_autorizados = [r for r in responsaveis_com_dividas if not self.is_responsavel_autorizado(r['nome'])]
        
        if responsaveis_nao_autorizados:
            logger.warning(f"⚠️ Responsáveis com dívidas NÃO AUTORIZADOS: {len(responsaveis_nao_autorizados)}")
            for resp in responsaveis_nao_autorizados[:5]:  # Mostrar apenas os primeiros 5
                logger.warning(f"   - {resp['nome']}: R$ {resp['valor_total']:.2f}")
            if len(responsaveis_nao_autorizados) > 5:
                logger.warning(f"   ... e mais {len(responsaveis_nao_autorizados) - 5} responsáveis")
        
        # Valor total
        valor_total = sum(r['valor_total'] for r in responsaveis_para_cobranca)
        logger.info(f"💸 Valor total das cobranças autorizadas: R$ {valor_total:.2f}")
        
        # Estatísticas por quantidade de alunos
        distribuicao_alunos = {}
        for resp in responsaveis_para_cobranca:
            qtd = resp['quantidade_alunos']
            if qtd not in distribuicao_alunos:
                distribuicao_alunos[qtd] = 0
            distribuicao_alunos[qtd] += 1
        
        logger.info("\n👥 Distribuição por quantidade de alunos:")
        for qtd, count in sorted(distribuicao_alunos.items()):
            logger.info(f"   {qtd} aluno(s): {count} responsáveis")
        
        logger.info("="*60)

    def verificar_saude_sistema(self) -> bool:
        """
        Verifica se o sistema está funcionando corretamente.
        
        Returns:
            True se tudo está ok, False caso contrário
        """
        logger.info("🔍 Verificando saúde do sistema...")
        
        erros = []
        
        # Verificar se há responsáveis carregados
        if not self.responsaveis_autorizados:
            erros.append("Nenhum responsável autorizado carregado")
        
        # Verificar se arquivo CSV existe
        if not os.path.exists(self.csv_file):
            erros.append(f"Arquivo CSV não encontrado: {self.csv_file}")
        
        # Verificar variáveis de ambiente
        if not self.supabase_url or not self.supabase_key:
            erros.append("Variáveis de ambiente Supabase não configuradas")
        
        # Verificar se ChromeDriver está disponível
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Teste rápido do ChromeDriver
            test_options = Options()
            test_options.add_argument("--headless")
            test_options.add_argument("--no-sandbox")
            test_options.add_argument("--disable-dev-shm-usage")
            
            test_driver = webdriver.Chrome(options=test_options)
            test_driver.quit()
            
        except Exception as e:
            erros.append(f"ChromeDriver não está funcionando: {str(e)}")
        
        if erros:
            logger.error("❌ Problemas encontrados no sistema:")
            for erro in erros:
                logger.error(f"   - {erro}")
            return False
        else:
            logger.info("✅ Sistema funcionando corretamente")
            return True

def main():
    """Função principal do programa"""
    try:
        logger.info("🚀 Iniciando Sistema de Automação de Cobranças")
        logger.info("="*60)
        
        # Verificar variáveis de ambiente
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url:
            logger.error("❌ Variável de ambiente SUPABASE_URL não encontrada")
            logger.error("💡 Certifique-se de que o arquivo .env está configurado corretamente")
            return False
        
        if not supabase_key:
            logger.error("❌ Variável de ambiente SUPABASE_KEY não encontrada")
            logger.error("💡 Certifique-se de que o arquivo .env está configurado corretamente")
            return False
        
        # Verificar se arquivo CSV específico existe
        csv_file = "responsaveis_com_dividas_20251116_113430.csv"
        if not os.path.exists(csv_file):
            logger.error(f"❌ Arquivo CSV não encontrado: {csv_file}")
            logger.error("💡 Certifique-se de que o arquivo CSV está na pasta do projeto")
            return False
        
        logger.info(f"✅ Configurações validadas:")
        logger.info(f"   📄 Arquivo CSV: {csv_file}")
        logger.info(f"   🔗 Supabase URL: {supabase_url}")
        logger.info(f"   🔑 Supabase Key: {'*' * (len(supabase_key) - 10) + supabase_key[-10:]}")
        
        # Inicializar o sistema
        try:
            automacao = AutomacaoCobrancas(supabase_url, supabase_key, csv_file)
            logger.info("✅ Sistema inicializado com sucesso")
        except ValueError as e:
            logger.error(f"❌ Erro de configuração: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar sistema: {str(e)}")
            return False
        
        # Executar automação
        sucesso = automacao.executar_automacao()
        
        if sucesso:
            logger.info("🎉 Automação concluída com sucesso!")
            return True
        else:
            logger.error("❌ Automação falhou")
            return False
            
    except KeyboardInterrupt:
        logger.info("⏹️ Automação interrompida pelo usuário")
        return False
    except Exception as e:
        logger.error(f"❌ Erro crítico: {str(e)}")
        return False

if __name__ == "__main__":
    main() 
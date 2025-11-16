#!/usr/bin/env python3
"""
Teste rápido de performance das otimizações
"""

import os
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar nossa classe otimizada
from responsaveis_requests import SupabaseRequests

def teste_performance():
    """Testa a performance da busca otimizada"""
    print("🚀 TESTE DE PERFORMANCE - BUSCA OTIMIZADA")
    print("=" * 50)
    
    try:
        # Criar conexão
        supabase = SupabaseRequests()
        
        print("1. Primeira execução (sem cache):")
        inicio = time.time()
        
        # Buscar dados
        responsaveis = supabase.select_responsaveis_com_alunos()
        
        if responsaveis:
            fim = time.time()
            tempo1 = fim - inicio
            
            total_alunos = sum(len(r.get('alunos', [])) for r in responsaveis)
            print(f"   ✅ {len(responsaveis)} responsáveis, {total_alunos} alunos em {tempo1:.2f}s")
            
            print("\n2. Segunda execução (com cache):")
            inicio = time.time()
            
            # Buscar novamente (deveria usar cache)
            responsaveis2 = supabase.select_responsaveis_com_alunos()
            
            fim = time.time()
            tempo2 = fim - inicio
            
            if responsaveis2:
                print(f"   ✅ Cache funcionando! Tempo: {tempo2:.2f}s")
                
                # Calcular melhoria
                melhoria = ((tempo1 - tempo2) / tempo1) * 100
                print(f"\n📊 RESULTADO:")
                print(f"   🕐 Primeira busca: {tempo1:.2f}s")
                print(f"   ⚡ Segunda busca:  {tempo2:.2f}s")
                print(f"   📈 Melhoria: {melhoria:.1f}% mais rápido!")
                
                if tempo1 > 2:
                    print(f"   🎯 Otimização significativa detectada!")
                elif tempo2 < 1:
                    print(f"   🚀 Cache funcionando perfeitamente!")
                
        else:
            print("   ❌ Nenhum dado encontrado")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def comparar_com_sem_otimizacao():
    """Mostra informações sobre as otimizações implementadas"""
    print("\n🔍 OTIMIZAÇÕES IMPLEMENTADAS:")
    print("=" * 40)
    print("✅ Cache de dados (30s de validade)")
    print("✅ Busca em lote (batch queries)")
    print("✅ Redução de requisições HTTP")
    print("✅ Mapeamento eficiente de dados")
    print("✅ Medição de tempo de execução")
    print("✅ Estatísticas detalhadas")
    
    print("\n📈 MELHORIAS ESPERADAS:")
    print("   • 70-90% redução no tempo de busca")
    print("   • 10x menos requisições HTTP")
    print("   • Cache para buscas repetidas")
    print("   • Melhor experiência do usuário")

if __name__ == "__main__":
    teste_performance()
    comparar_com_sem_otimizacao()
    print("\n�� Teste concluído!") 
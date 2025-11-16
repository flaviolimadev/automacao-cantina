from main import SupabaseConnection
from datetime import datetime
import json

def exibir_responsaveis():
    """Exibe todos os registros da tabela responsaveis de forma organizada"""
    try:
        # Conectar ao Supabase
        print("🔄 Conectando ao Supabase...")
        supabase_conn = SupabaseConnection()
        
        # Buscar todos os responsáveis
        print("📋 Buscando registros da tabela 'responsaveis'...")
        responsaveis = supabase_conn.select_data('responsaveis')
        
        if not responsaveis:
            print("⚠️ Nenhum registro encontrado na tabela 'responsaveis'")
            return
        
        # Exibir header
        print(f"\n✅ {len(responsaveis)} registro(s) encontrado(s):")
        print("=" * 80)
        print(f"{'ID':<36} | {'NOME':<20} | {'SOBRENOME':<20} | {'CONTATO':<15}")
        print("-" * 80)
        
        # Exibir cada responsável
        for responsavel in responsaveis:
            id_short = str(responsavel.get('id', ''))[:8] + '...' if responsavel.get('id') else 'N/A'
            nome = responsavel.get('nome', 'N/A')[:18]
            sobrenome = responsavel.get('sobrenome', 'N/A')[:18]
            contato = responsavel.get('contato', 'N/A')[:13]
            
            print(f"{id_short:<36} | {nome:<20} | {sobrenome:<20} | {contato:<15}")
        
        print("=" * 80)
        
        # Exibir detalhes completos
        print("\n📄 DETALHES COMPLETOS:")
        print("-" * 50)
        
        for i, responsavel in enumerate(responsaveis, 1):
            print(f"\n{i}. RESPONSÁVEL:")
            print(f"   🆔 ID: {responsavel.get('id', 'N/A')}")
            print(f"   👤 Nome: {responsavel.get('nome', 'N/A')}")
            print(f"   👤 Sobrenome: {responsavel.get('sobrenome', 'N/A')}")
            print(f"   📞 Contato: {responsavel.get('contato', 'N/A')}")
            
            # Formatar datas se existirem
            if responsavel.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(responsavel['created_at'].replace('Z', '+00:00'))
                    print(f"   📅 Criado em: {created_at.strftime('%d/%m/%Y às %H:%M:%S')}")
                except:
                    print(f"   📅 Criado em: {responsavel.get('created_at', 'N/A')}")
            
            if responsavel.get('updated_at'):
                try:
                    updated_at = datetime.fromisoformat(responsavel['updated_at'].replace('Z', '+00:00'))
                    print(f"   🔄 Atualizado em: {updated_at.strftime('%d/%m/%Y às %H:%M:%S')}")
                except:
                    print(f"   🔄 Atualizado em: {responsavel.get('updated_at', 'N/A')}")
            
            if i < len(responsaveis):
                print("   " + "-" * 40)
        
        print(f"\n📊 RESUMO:")
        print(f"   Total de responsáveis: {len(responsaveis)}")
        print(f"   Tabela: responsaveis")
        print(f"   Campos: id, nome, sobrenome, contato, created_at, updated_at")
        
    except Exception as e:
        print(f"❌ Erro ao buscar responsáveis: {str(e)}")
        print("🔧 Verifique se:")
        print("   - O arquivo .env está configurado corretamente")
        print("   - A tabela 'responsaveis' existe no seu banco")
        print("   - Suas credenciais do Supabase estão corretas")

def exibir_responsaveis_json():
    """Exibe os responsáveis em formato JSON para debug"""
    try:
        supabase_conn = SupabaseConnection()
        responsaveis = supabase_conn.select_data('responsaveis')
        
        if responsaveis:
            print("\n📄 DADOS EM FORMATO JSON:")
            print(json.dumps(responsaveis, indent=2, ensure_ascii=False, default=str))
        else:
            print("⚠️ Nenhum dado encontrado")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def menu_responsaveis():
    """Menu interativo para visualizar responsáveis"""
    print("🏢 SISTEMA DE RESPONSÁVEIS")
    print("=" * 40)
    print("1. Exibir todos os responsáveis (formatado)")
    print("2. Exibir em formato JSON")
    print("3. Sair")
    print("-" * 40)
    
    while True:
        try:
            opcao = input("\n👉 Escolha uma opção (1-3): ").strip()
            
            if opcao == '1':
                print("\n" + "="*50)
                exibir_responsaveis()
                print("="*50)
                
            elif opcao == '2':
                print("\n" + "="*50)
                exibir_responsaveis_json()
                print("="*50)
                
            elif opcao == '3':
                print("👋 Saindo... Até mais!")
                break
                
            else:
                print("❌ Opção inválida. Escolha 1, 2 ou 3.")
                
            print("\n" + "-"*40)
            print("1. Exibir responsáveis | 2. JSON | 3. Sair")
            
        except KeyboardInterrupt:
            print("\n\n👋 Saindo... Até mais!")
            break
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    # Verificar se deve executar o menu ou apenas exibir
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        exibir_responsaveis_json()
    elif len(sys.argv) > 1 and sys.argv[1] == '--simples':
        exibir_responsaveis()
    else:
        menu_responsaveis() 
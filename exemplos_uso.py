from main import SupabaseConnection
from datetime import datetime
import json

def exemplo_crud_usuarios():
    """Exemplo completo de operações CRUD com tabela de usuários"""
    try:
        # Conectar ao Supabase
        supabase_conn = SupabaseConnection()
        
        # 1. Inserir um novo usuário
        print("🔄 Inserindo novo usuário...")
        novo_usuario = {
            "nome": "Maria Silva",
            "email": "maria@email.com",
            "idade": 28,
            "ativo": True,
            "criado_em": datetime.now().isoformat()
        }
        
        resultado_insert = supabase_conn.insert_data('usuarios', novo_usuario)
        if resultado_insert:
            print(f"✅ Usuário inserido: {json.dumps(resultado_insert.data, indent=2)}")
        
        # 2. Buscar usuários
        print("\n🔍 Buscando usuários...")
        usuarios = supabase_conn.select_data('usuarios', columns='id, nome, email, idade')
        if usuarios:
            print(f"📋 Usuários encontrados: {len(usuarios)}")
            for usuario in usuarios:
                print(f"   - ID: {usuario['id']}, Nome: {usuario['nome']}, Email: {usuario['email']}")
        
        # 3. Buscar usuário específico
        print("\n🎯 Buscando usuário específico...")
        usuario_especifico = supabase_conn.select_data(
            'usuarios', 
            filters={'email': 'maria@email.com'}
        )
        if usuario_especifico:
            print(f"👤 Usuário encontrado: {usuario_especifico[0]['nome']}")
        
        # 4. Atualizar usuário
        print("\n✏️ Atualizando usuário...")
        dados_atualizacao = {
            "nome": "Maria Silva Santos",
            "idade": 29,
            "atualizado_em": datetime.now().isoformat()
        }
        
        resultado_update = supabase_conn.update_data(
            'usuarios', 
            dados_atualizacao, 
            {'email': 'maria@email.com'}
        )
        
        # 5. Confirmar atualização
        if resultado_update:
            print("✅ Usuário atualizado com sucesso!")
            usuario_atualizado = supabase_conn.select_data(
                'usuarios', 
                filters={'email': 'maria@email.com'}
            )
            if usuario_atualizado:
                print(f"👤 Nome atualizado: {usuario_atualizado[0]['nome']}")
        
        # 6. Deletar usuário (descomente para usar)
        # print("\n🗑️ Deletando usuário...")
        # resultado_delete = supabase_conn.delete_data('usuarios', {'email': 'maria@email.com'})
        # if resultado_delete:
        #     print("✅ Usuário deletado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo CRUD: {str(e)}")

def exemplo_consultas_avancadas():
    """Exemplos de consultas mais avançadas"""
    try:
        supabase_conn = SupabaseConnection()
        
        print("🔍 Executando consultas avançadas...")
        
        # Buscar usuários ativos com idade maior que 25
        print("\n📊 Buscando usuários ativos com idade > 25...")
        usuarios_ativos = supabase_conn.client.table('usuarios')\
            .select('nome, email, idade')\
            .eq('ativo', True)\
            .gt('idade', 25)\
            .order('idade')\
            .execute()
        
        if usuarios_ativos.data:
            print(f"👥 {len(usuarios_ativos.data)} usuários encontrados:")
            for usuario in usuarios_ativos.data:
                print(f"   - {usuario['nome']}: {usuario['idade']} anos")
        
        # Contar total de usuários
        print("\n📈 Contando usuários...")
        total_usuarios = supabase_conn.client.table('usuarios')\
            .select('id', count='exact')\
            .execute()
        
        print(f"👥 Total de usuários: {total_usuarios.count}")
        
        # Buscar usuários com paginação
        print("\n📄 Buscando usuários com paginação...")
        usuarios_paginados = supabase_conn.client.table('usuarios')\
            .select('nome, email')\
            .range(0, 4)\
            .execute()
        
        if usuarios_paginados.data:
            print(f"📋 Primeiros 5 usuários:")
            for usuario in usuarios_paginados.data:
                print(f"   - {usuario['nome']}: {usuario['email']}")
        
    except Exception as e:
        print(f"❌ Erro nas consultas avançadas: {str(e)}")

def exemplo_conexao_direta():
    """Exemplo de conexão direta com PostgreSQL"""
    try:
        supabase_conn = SupabaseConnection()
        
        print("🔗 Testando conexão direta com PostgreSQL...")
        
        # Obter conexão direta
        conn = supabase_conn.get_database_connection()
        if conn:
            cursor = conn.cursor()
            
            # Consultar versão do banco
            cursor.execute("SELECT version();")
            versao = cursor.fetchone()
            print(f"📊 Versão do PostgreSQL: {versao['version']}")
            
            # Consultar tabelas existentes
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tabelas = cursor.fetchall()
            print(f"📋 Tabelas encontradas: {len(tabelas)}")
            for tabela in tabelas:
                print(f"   - {tabela['table_name']}")
            
            # Fechar conexão
            cursor.close()
            conn.close()
            print("✅ Conexão direta finalizada")
        
    except Exception as e:
        print(f"❌ Erro na conexão direta: {str(e)}")

def exemplo_autenticacao():
    """Exemplo de autenticação de usuário"""
    try:
        supabase_conn = SupabaseConnection()
        
        print("🔐 Exemplos de autenticação...")
        
        # Exemplo de cadastro (descomente para usar)
        # email = "teste@email.com"
        # senha = "senha123"
        # 
        # print(f"📝 Cadastrando usuário: {email}")
        # resultado = supabase_conn.client.auth.sign_up({
        #     "email": email,
        #     "password": senha
        # })
        # print(f"✅ Usuário cadastrado: {resultado}")
        
        # Exemplo de login (descomente para usar)
        # print(f"🔑 Fazendo login: {email}")
        # resultado = supabase_conn.client.auth.sign_in_with_password({
        #     "email": email,
        #     "password": senha
        # })
        # print(f"✅ Login realizado: {resultado}")
        
        # Verificar usuário atual
        usuario_atual = supabase_conn.client.auth.get_user()
        if usuario_atual:
            print(f"👤 Usuário atual: {usuario_atual}")
        else:
            print("🚫 Nenhum usuário logado")
        
    except Exception as e:
        print(f"❌ Erro na autenticação: {str(e)}")

def main():
    """Função principal para executar todos os exemplos"""
    print("🚀 Iniciando exemplos de uso do Supabase")
    print("=" * 50)
    
    # Exemplo 1: CRUD básico
    print("\n1️⃣ EXEMPLO: Operações CRUD")
    print("-" * 30)
    exemplo_crud_usuarios()
    
    # Exemplo 2: Consultas avançadas
    print("\n2️⃣ EXEMPLO: Consultas Avançadas")
    print("-" * 30)
    exemplo_consultas_avancadas()
    
    # Exemplo 3: Conexão direta
    print("\n3️⃣ EXEMPLO: Conexão Direta PostgreSQL")
    print("-" * 30)
    exemplo_conexao_direta()
    
    # Exemplo 4: Autenticação
    print("\n4️⃣ EXEMPLO: Autenticação")
    print("-" * 30)
    exemplo_autenticacao()
    
    print("\n" + "=" * 50)
    print("✨ Exemplos finalizados!")

if __name__ == "__main__":
    main() 
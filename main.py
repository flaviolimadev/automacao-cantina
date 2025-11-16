import os
from dotenv import load_dotenv
from supabase import create_client, Client
import psycopg2
from psycopg2.extras import RealDictCursor

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class SupabaseConnection:
    def __init__(self):
        """Inicializa a conexão com o Supabase"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.database_url = os.getenv('DATABASE_URL')
        
        # Verificar se as credenciais estão carregadas
        if not self.url or not self.key:
            raise ValueError("As credenciais do Supabase não foram encontradas no arquivo .env")
        
        # Criar cliente do Supabase
        self.client: Client = create_client(self.url, self.key)
        
    def test_connection(self):
        """Testa a conexão com o Supabase"""
        try:
            # Fazer uma consulta simples para testar
            response = self.client.table('users').select('*').limit(1).execute()
            print("✅ Conexão com Supabase realizada com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro na conexão com Supabase: {str(e)}")
            return False
    
    def get_database_connection(self):
        """Retorna uma conexão direta com o banco PostgreSQL"""
        if not self.database_url:
            raise ValueError("DATABASE_URL não foi definida no arquivo .env")
        
        try:
            conn = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            print(f"❌ Erro na conexão direta com o banco: {str(e)}")
            return None
    
    def insert_data(self, table_name: str, data: dict):
        """Insere dados em uma tabela"""
        try:
            response = self.client.table(table_name).insert(data).execute()
            print(f"✅ Dados inseridos com sucesso na tabela {table_name}")
            return response
        except Exception as e:
            print(f"❌ Erro ao inserir dados: {str(e)}")
            return None
    
    def select_data(self, table_name: str, columns: str = '*', filters: dict = None):
        """Seleciona dados de uma tabela"""
        try:
            query = self.client.table(table_name).select(columns)
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"❌ Erro ao selecionar dados: {str(e)}")
            return None
    
    def update_data(self, table_name: str, data: dict, filters: dict):
        """Atualiza dados em uma tabela"""
        try:
            query = self.client.table(table_name).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            print(f"✅ Dados atualizados com sucesso na tabela {table_name}")
            return response
        except Exception as e:
            print(f"❌ Erro ao atualizar dados: {str(e)}")
            return None
    
    def delete_data(self, table_name: str, filters: dict):
        """Deleta dados de uma tabela"""
        try:
            query = self.client.table(table_name).delete()
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            print(f"✅ Dados deletados com sucesso da tabela {table_name}")
            return response
        except Exception as e:
            print(f"❌ Erro ao deletar dados: {str(e)}")
            return None


def main():
    """Função principal para demonstrar o uso"""
    try:
        # Conectar ao Supabase
        supabase_conn = SupabaseConnection()
        
        # Testar conexão
        if supabase_conn.test_connection():
            print("🎉 Pronto para usar o Supabase!")
        
        # Exemplo de uso das funções
        print("\n--- Exemplos de uso ---")
        
        # Exemplo 1: Inserir dados (descomente para usar)
        # data = {"nome": "João", "email": "joao@email.com"}
        # supabase_conn.insert_data('usuarios', data)
        
        # Exemplo 2: Selecionar dados (descomente para usar)
        # usuarios = supabase_conn.select_data('usuarios')
        # print(f"Usuários encontrados: {usuarios}")
        
        # Exemplo 3: Atualizar dados (descomente para usar)
        # supabase_conn.update_data('usuarios', {"nome": "João Silva"}, {"id": 1})
        
        # Exemplo 4: Deletar dados (descomente para usar)
        # supabase_conn.delete_data('usuarios', {"id": 1})
        
        # Exemplo 5: Conexão direta com PostgreSQL (descomente para usar)
        # conn = supabase_conn.get_database_connection()
        # if conn:
        #     cursor = conn.cursor()
        #     cursor.execute("SELECT version();")
        #     print(f"Versão do PostgreSQL: {cursor.fetchone()}")
        #     conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        print("Verifique se o arquivo .env está configurado corretamente")


if __name__ == "__main__":
    main() 
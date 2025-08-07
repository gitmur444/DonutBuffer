"""
SafeSQLTool - Secure SQL execution wrapper for AI Test Planner
Smart SQL capabilities - generates SQL from natural language intent only
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional

from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from rich.console import Console

from tools.openai_config import OpenAIConfig

console = Console()

# Global schema cache to avoid Pydantic field issues
SCHEMA_CACHE = {
    'fingerprint': None,
    'analysis': None,
    'timestamp': None,
    'ttl': 300  # 5 minutes cache
}


class SafeSQLTool(QuerySQLDatabaseTool):
    """Secure SQL tool with Smart SQL capabilities - generates SQL from natural language intent only"""
    
    def __init__(self, db: SQLDatabase):
        """Initialize with SQLDatabase instance"""
        super().__init__(db=db)
        # Don't initialize openai_config here to avoid Pydantic issues
        self._openai_config = None
    
    @property
    def openai_config(self):
        """Lazy initialization of OpenAI config to avoid Pydantic field issues"""
        if self._openai_config is None:
            self._openai_config = OpenAIConfig()
        return self._openai_config
    
    def validate_sql(self, sql: str) -> bool:
        """Validate SQL is read-only"""
        sql_upper = sql.upper().strip()
        dangerous_keywords = ['UPDATE', 'DELETE', 'INSERT', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', ';']
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
                
        if not sql_upper.startswith('SELECT'):
            return False
            
        return True
    
    def get_schema_fingerprint(self) -> str:
        """Generate fingerprint of database schema for caching"""
        try:
            # Get table structures
            schema_query = """
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
            result = self.db.run(schema_query)
            
            # Get record counts
            tables_query = """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """
            tables = self.db.run(tables_query)
            
            counts = {}
            for table_row in tables.split('\n')[1:]:  # Skip header
                if table_row.strip():
                    table_name = table_row.strip().split('|')[0].strip()
                    try:
                        count_result = self.db.run(f"SELECT COUNT(*) FROM {table_name}")
                        counts[table_name] = count_result
                    except:
                        counts[table_name] = "unknown"
            
            fingerprint_data = f"{result}|{counts}"
            return hashlib.md5(fingerprint_data.encode()).hexdigest()
            
        except Exception as e:
            console.print(f"❌ Schema fingerprint failed: {e}")
            return "error"
    
    def analyze_database_schema(self) -> str:
        """Analyze current database schema and provide context"""
        try:
            # Get table structures with constraints
            schema_info = []
            
            # Tables and columns
            columns_query = """
                SELECT 
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    tc.constraint_type
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
                LEFT JOIN information_schema.key_column_usage kcu ON c.table_name = kcu.table_name 
                    AND c.column_name = kcu.column_name
                LEFT JOIN information_schema.table_constraints tc ON kcu.constraint_name = tc.constraint_name
                WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name, c.ordinal_position
            """
            
            schema_result = self.db.run(columns_query)
            
            # Get record counts and sample data
            tables_query = """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """
            tables_result = self.db.run(tables_query)
            
            table_stats = {}
            for table_line in tables_result.split('\n')[1:]:  # Skip header
                if table_line.strip():
                    table_name = table_line.strip().split('|')[0].strip()
                    try:
                        # Count records
                        count_result = self.db.run(f"SELECT COUNT(*) FROM {table_name}")
                        count = count_result.split('\n')[1].strip() if '\n' in count_result else count_result.strip()
                        
                        # Get sample data
                        sample_result = self.db.run(f"SELECT * FROM {table_name} LIMIT 2")
                        
                        table_stats[table_name] = {
                            'count': count,
                            'sample': sample_result[:200] + '...' if len(sample_result) > 200 else sample_result
                        }
                    except Exception as e:
                        table_stats[table_name] = {'count': 'error', 'sample': f'Error: {e}'}
            
            analysis = f"""
                DATABASE SCHEMA ANALYSIS:

                STRUCTURE:
                {schema_result}

                TABLE STATISTICS:
                {json.dumps(table_stats, indent=2)}

                IMPORTANT NOTES:
                - actual_tests table: unique by (test_suite, test_name) pair
                - Always include test_suite when querying actual_tests to avoid confusion
                - Use proper JOINs when relating test_results and actual_tests
            """
            
            return analysis
            
        except Exception as e:
            return f"Schema analysis failed: {e}"
    
    def get_fresh_schema_context(self) -> str:
        """Get fresh schema context with caching"""
        global SCHEMA_CACHE
        current_time = time.time()
        current_fingerprint = self.get_schema_fingerprint()
        
        # Check if cache is valid
        if (SCHEMA_CACHE['fingerprint'] == current_fingerprint and 
            SCHEMA_CACHE['timestamp'] and 
            current_time - SCHEMA_CACHE['timestamp'] < SCHEMA_CACHE['ttl']):
            return SCHEMA_CACHE['analysis']
        
        # Generate fresh analysis
        analysis = self.analyze_database_schema()
        
        # Update cache
        SCHEMA_CACHE.update({
            'fingerprint': current_fingerprint,
            'analysis': analysis,
            'timestamp': current_time
        })
        
        return analysis
    
    def generate_sql_from_intent(self, intent: str, context: str = "") -> str:
        """Generate SQL query from natural language intent"""
        schema_context = self.get_fresh_schema_context()
        
        prompt = f"""
            You are a SQL expert. Generate ONLY a valid SELECT query based on the user's intent.

            DATABASE CONTEXT:
            {schema_context}

            USER INTENT: {intent}
            ADDITIONAL CONTEXT: {context}

            RESPONSE:
            Only the SQL query, without explanations or formatting:
        """
        
        try:
            response = OpenAIConfig.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                use_case="planning"
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the response (remove ```sql blocks if present)
            if sql_query.startswith('```'):
                sql_query = sql_query.split('\n', 1)[1] if '\n' in sql_query else sql_query[3:]
            if sql_query.endswith('```'):
                sql_query = sql_query.rsplit('\n', 1)[0] if '\n' in sql_query else sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            console.print(f"�� Generated SQL from intent: {sql_query}")
            return sql_query
            
        except Exception as e:
            raise RuntimeError(f"SQL generation failed: {e}")
    
    def run(self, query: str) -> str:
        """Execute read-only SQL query with safety validation"""
        if not self.validate_sql(query):
            raise ValueError(f"Unsafe SQL query rejected: {query}")
            
        try:
            result = super()._run(query)
            console.print("✔ SQL query executed successfully")
            return result
                
        except Exception as e:
            raise RuntimeError(f"Database query failed: {str(e)}")
    
    def execute(self, params: Dict[str, Any]) -> str:
        """Execute SQL query - only supports intent-based generation (no direct SQL)"""
        
        if 'intent' in params:
            # Smart SQL - generate SQL from intent
            intent = params.get('intent', '')
            context = params.get('context', '')
            
            console.print(f"🧠 [SmartSQLTool] Processing intent: {intent}")
            if context:
                console.print(f"📝 [SmartSQLTool] Context: {context}")
            
            # Generate SQL from intent
            sql_query = self.generate_sql_from_intent(intent, context)
            
            # Execute generated SQL
            return self._run(sql_query)
        
        else:
            raise ValueError("'intent' parameter required. Direct SQL execution is disabled - use natural language instead.") 
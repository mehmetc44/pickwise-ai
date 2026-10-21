from context.DBContext import DBContext
from psycopg2.extras import RealDictCursor

class ProductRepository:
    def get_all(self, limit: int = 100):
        conn = DBContext.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM products LIMIT %s", (limit,))
                return cursor.fetchall()
        finally:
            DBContext.release_connection(conn)

    def get_by_id(self, product_id: int):
        conn = DBContext.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT p.*, c.full_path 
                    FROM products p
                    LEFT JOIN categories c ON p.category_id = c.id
                    WHERE p.id = %s
                """, (product_id,))
                return cursor.fetchone()
        finally:
            DBContext.release_connection(conn)

    def get_by_category_id(self, category_id: int, limit: int = 100):
        conn = DBContext.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM products WHERE category_id = %s LIMIT %s", (category_id, limit))
                return cursor.fetchall()
        finally:
            DBContext.release_connection(conn)

    def get_by_main_category(self, main_category_path: str, limit: int = 100):
        conn = DBContext.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Append '%' to the path for LIKE clause to fetch all taxonomy under this category
                like_pattern = f"{main_category_path}%"
                query = """
                    SELECT p.* 
                    FROM products p
                    JOIN categories c ON p.category_id = c.id
                    WHERE c.full_path LIKE %s
                    LIMIT %s
                """
                cursor.execute(query, (like_pattern, limit))
                return cursor.fetchall()
        finally:
            DBContext.release_connection(conn)

    def get_closest(self, vector: list[float], limit: int = 10, category_id: int = None):
        conn = DBContext.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                vector_str = "[" + ",".join(map(str, vector)) + "]"
                if category_id:
                    query = """
                    SELECT p.*, c.full_path,
                           1 - (p.text_embedding <=> %s::vector) AS similarity
                    FROM products p
                    LEFT JOIN categories c ON p.category_id = c.id
                    WHERE p.text_embedding IS NOT NULL AND p.category_id = %s
                    ORDER BY p.text_embedding <=> %s::vector
                    LIMIT %s
                    """
                    cursor.execute(query, (vector_str, category_id, vector_str, limit))
                else:
                    query = """
                    SELECT p.*, c.full_path,
                           1 - (p.text_embedding <=> %s::vector) AS similarity
                    FROM products p
                    LEFT JOIN categories c ON p.category_id = c.id
                    WHERE p.text_embedding IS NOT NULL
                    ORDER BY p.text_embedding <=> %s::vector
                    LIMIT %s
                    """
                    cursor.execute(query, (vector_str, vector_str, limit))
                return cursor.fetchall()
        finally:
            DBContext.release_connection(conn)


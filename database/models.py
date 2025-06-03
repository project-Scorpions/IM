from database.db_connector import DatabaseConnection
import logging
from datetime import datetime, date

class BaseModel:
    """Base model class for database operations"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def _format_value(self, value):
        """Format value for SQL query"""
        if value is None:
            return "NULL"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (datetime, date)):
            return f"'{value.isoformat()}'"
        else:
            escaped_value = str(value).replace("'", "''")
            return f"'{escaped_value}'"


class ProductModel(BaseModel):
    """Model for product-related database operations"""
    
    def get_all_products(self):
        """Get all products"""
        try:
            query = """
                SELECT p.product_id, p.product_name, c.name as category_name, 
                       p.description, p.unit_price, p.cost_price, p.stock_quantity, 
                       p.expiry_date, p.reorder_level, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                ORDER BY p.product_name
            """
            return self.db.execute_query(query, fetchall=True)
        except Exception as e:
            logging.error(f"Error getting products: {e}")
            raise
    
    def get_product_by_id(self, product_id):
        """Get product by ID"""
        try:
            query = """
                SELECT p.product_id, p.product_name, p.category_id, c.name as category_name, 
                       p.description, p.unit_price, p.cost_price, p.stock_quantity, 
                       p.expiry_date, p.reorder_level, p.supplier_id, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                WHERE p.product_id = %s
            """
            return self.db.execute_query(query, (product_id,), fetchone=True)
        except Exception as e:
            logging.error(f"Error getting product {product_id}: {e}")
            raise
    
    def create_product(self, data):
        """Create a new product"""
        try:
            query = """
                INSERT INTO products
                (product_name, category_id, description, unit_price, cost_price,
                 stock_quantity, expiry_date, reorder_level, supplier_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING product_id
            """
            params = (
                data.get('product_name'),
                data.get('category_id'),
                data.get('description'),
                data.get('unit_price'),
                data.get('cost_price'),
                data.get('stock_quantity', 0),
                data.get('expiry_date'),
                data.get('reorder_level', 10),
                data.get('supplier_id')
            )
            return self.db.execute_query(query, params, fetchone=True)[0]
        except Exception as e:
            logging.error(f"Error creating product: {e}")
            raise
    
    def update_product(self, product_id, data):
        """Update an existing product"""
        try:
            query = """
                UPDATE products
                SET product_name = %s, category_id = %s, description = %s,
                    unit_price = %s, cost_price = %s, stock_quantity = %s,
                    expiry_date = %s, reorder_level = %s, supplier_id = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE product_id = %s
            """
            params = (
                data.get('product_name'),
                data.get('category_id'),
                data.get('description'),
                data.get('unit_price'),
                data.get('cost_price'),
                data.get('stock_quantity'),
                data.get('expiry_date'),
                data.get('reorder_level'),
                data.get('supplier_id'),
                product_id
            )
            return self.db.execute_query(query, params)
        except Exception as e:
            logging.error(f"Error updating product {product_id}: {e}")
            raise
    
    def delete_product(self, product_id):
        """Delete a product"""
        try:
            query = "DELETE FROM products WHERE product_id = %s"
            return self.db.execute_query(query, (product_id,))
        except Exception as e:
            logging.error(f"Error deleting product {product_id}: {e}")
            raise
    
    def update_stock(self, product_id, quantity_change):
        """Update product stock quantity"""
        try:
            query = """
                UPDATE products
                SET stock_quantity = stock_quantity + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE product_id = %s
            """
            return self.db.execute_query(query, (quantity_change, product_id))
        except Exception as e:
            logging.error(f"Error updating stock for product {product_id}: {e}")
            raise
    
    def get_low_stock_products(self):
        """Get products with stock below reorder level"""
        try:
            query = """
                SELECT p.product_id, p.product_name, c.name as category_name, 
                       p.unit_price, p.stock_quantity, p.reorder_level
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.stock_quantity <= p.reorder_level
                ORDER BY (p.reorder_level - p.stock_quantity) DESC, p.product_name
            """
            return self.db.execute_query(query, fetchall=True)
        except Exception as e:
            logging.error(f"Error getting low stock products: {e}")
            raise
    
    def get_expiring_products(self, days=30):
        """Get products expiring within a number of days"""
        try:
            query = """
                SELECT p.product_id, p.product_name, c.name as category_name, 
                       p.unit_price, p.stock_quantity, p.expiry_date
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.expiry_date IS NOT NULL 
                AND p.expiry_date <= CURRENT_DATE + INTERVAL '%s days'
                ORDER BY p.expiry_date, p.product_name
            """
            return self.db.execute_query(query, (days,), fetchall=True)
        except Exception as e:
            logging.error(f"Error getting expiring products: {e}")
            raise


class CategoryModel(BaseModel):
    """Model for category-related database operations"""
    
    def get_all_categories(self):
        """Get all categories"""
        try:
            query = "SELECT category_id, name, description FROM categories ORDER BY name"
            return self.db.execute_query(query, fetchall=True)
        except Exception as e:
            logging.error(f"Error getting categories: {e}")
            raise
    
    def get_categories_with_product_count(self):
        """Get all categories with product count"""
        try:
            query = """
                SELECT c.category_id, c.name, c.description, COUNT(p.product_id) AS product_count
                FROM categories c
                LEFT JOIN products p ON c.category_id = p.category_id
                GROUP BY c.category_id, c.name, c.description
                ORDER BY c.name
            """
            return self.db.execute_query(query, fetchall=True)
        except Exception as e:
            logging.error(f"Error getting categories with product count: {e}")
            raise
    
    def get_category_by_id(self, category_id):
        """Get category by ID"""
        try:
            query = "SELECT category_id, name, description FROM categories WHERE category_id = %s"
            return self.db.execute_query(query, (category_id,), fetchone=True)
        except Exception as e:
            logging.error(f"Error getting category {category_id}: {e}")
            raise
    
    def create_category(self, name, description=None):
        """Create a new category"""
        try:
            query = """
                INSERT INTO categories (name, description)
                VALUES (%s, %s)
                RETURNING category_id
            """
            return self.db.execute_query(query, (name, description), fetchone=True)[0]
        except Exception as e:
            logging.error(f"Error creating category: {e}")
            raise
    
    def update_category(self, category_id, name, description=None):
        """Update an existing category"""
        try:
            query = """
                UPDATE categories
                SET name = %s, description = %s, updated_at = CURRENT_TIMESTAMP
                WHERE category_id = %s
            """
            return self.db.execute_query(query, (name, description, category_id))
        except Exception as e:
            logging.error(f"Error updating category {category_id}: {e}")
            raise
    
    def delete_category(self, category_id):
        """Delete a category"""
        try:
            query = "DELETE FROM categories WHERE category_id = %s"
            return self.db.execute_query(query, (category_id,))
        except Exception as e:
            logging.error(f"Error deleting category {category_id}: {e}")
            raise


class SaleModel(BaseModel):
    """Model for sale-related database operations"""
    
    def create_sale(self, user_id, total_amount, payment_method, notes=None):
        """Create a new sale"""
        try:
            # Generate invoice number (format: INV-YYYYMMDD-XXXX)
            today = datetime.now()
            date_part = today.strftime("%Y%m%d")
            
            # Get latest invoice number
            query = """
                SELECT invoice_number FROM sales 
                WHERE invoice_number LIKE %s 
                ORDER BY invoice_number DESC LIMIT 1
            """
            result = self.db.execute_query(query, (f"INV-{date_part}-%",), fetchone=True)
            
            if result:
                last_number = int(result[0].split('-')[-1])
                invoice_number = f"INV-{date_part}-{last_number + 1:04d}"
            else:
                invoice_number = f"INV-{date_part}-0001"
            
            # Insert sale
            query = """
                INSERT INTO sales 
                (invoice_number, user_id, total_amount, payment_method, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING sale_id
            """
            return self.db.execute_query(
                query, 
                (invoice_number, user_id, total_amount, payment_method, notes),
                fetchone=True
            )[0]
        except Exception as e:
            logging.error(f"Error creating sale: {e}")
            raise
    
    def add_sale_item(self, sale_id, product_id, quantity, unit_price, discount=0):
        """Add an item to a sale"""
        try:
            subtotal = quantity * unit_price - discount
            
            query = """
                INSERT INTO sale_items
                (sale_id, product_id, quantity, unit_price, discount, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING item_id
            """
            return self.db.execute_query(
                query, 
                (sale_id, product_id, quantity, unit_price, discount, subtotal),
                fetchone=True
            )[0]
        except Exception as e:
            logging.error(f"Error adding sale item: {e}")
            raise
    
    def get_sale_by_id(self, sale_id):
        """Get sale by ID"""
        try:
            query = """
                SELECT s.sale_id, s.invoice_number, s.sale_date, s.total_amount, 
                       s.payment_method, s.notes, u.username, u.full_name
                FROM sales s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.sale_id = %s
            """
            return self.db.execute_query(query, (sale_id,), fetchone=True)
        except Exception as e:
            logging.error(f"Error getting sale {sale_id}: {e}")
            raise
    
    def get_sale_items(self, sale_id):
        """Get items for a sale"""
        try:
            query = """
                SELECT si.item_id, si.product_id, p.product_name, si.quantity, 
                       si.unit_price, si.discount, si.subtotal
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = %s
                ORDER BY si.item_id
            """
            return self.db.execute_query(query, (sale_id,), fetchall=True)
        except Exception as e:
            logging.error(f"Error getting items for sale {sale_id}: {e}")
            raise
    
    def get_sales_by_date_range(self, start_date, end_date, payment_method=None):
        """Get sales within a date range"""
        try:
            query = """
                SELECT s.sale_id, s.invoice_number, s.sale_date, s.total_amount, 
                       s.payment_method, u.full_name, COUNT(si.item_id) as item_count
                FROM sales s
                JOIN users u ON s.user_id = u.user_id
                JOIN sale_items si ON s.sale_id = si.sale_id
                WHERE s.sale_date::date BETWEEN %s AND %s
            """
            
            params = [start_date, end_date]
            
            if payment_method:
                query += " AND s.payment_method = %s"
                params.append(payment_method)
            
            query += " GROUP BY s.sale_id, s.invoice_number, s.sale_date, s.total_amount, s.payment_method, u.full_name"
            query += " ORDER BY s.sale_date DESC"
            
            return self.db.execute_query(query, params, fetchall=True)
        except Exception as e:
            logging.error(f"Error getting sales by date range: {e}")
            raise
    
    def get_daily_sales_totals(self, start_date, end_date, payment_method=None):
        """Get daily sales totals within a date range"""
        try:
            query = """
                SELECT DATE(s.sale_date) as sale_day, SUM(s.total_amount) as daily_total
                FROM sales s
                WHERE s.sale_date::date BETWEEN %s AND %s
            """
            
            params = [start_date, end_date]
            
            if payment_method:
                query += " AND s.payment_method = %s"
                params.append(payment_method)
            
            query += " GROUP BY sale_day ORDER BY sale_day"
            
            return self.db.execute_query(query, params, fetchall=True)
        except Exception as e:
            logging.error(f"Error getting daily sales totals: {e}")
            raise
    
    def get_payment_method_totals(self, start_date, end_date):
        """Get sales totals by payment method within a date range"""
        try:
            query = """
                SELECT s.payment_method, SUM(s.total_amount) as total
                FROM sales s
                WHERE s.sale_date::date BETWEEN %s AND %s
                GROUP BY s.payment_method
                ORDER BY total DESC
            """
            
            return self.db.execute_query(query, (start_date, end_date), fetchall=True)
        except Exception as e:
            logging.error(f"Error getting payment method totals: {e}")
            raise


class UserModel(BaseModel):
    """Model for user-related database operations"""
    
    def get_all_users(self):
        """Get all users"""
        try:
            query = """
                SELECT user_id, username, full_name, email, role, is_active, last_login
                FROM users
                ORDER BY username
            """
            return self.db.execute_query(query, fetchall=True)
        except Exception as e:
            logging.error(f"Error getting users: {e}")
            raise
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            query = """
                SELECT user_id, username, full_name, email, role, is_active, last_login
                FROM users
                WHERE user_id = %s
            """
            return self.db.execute_query(query, (user_id,), fetchone=True)
        except Exception as e:
            logging.error(f"Error getting user {user_id}: {e}")
            raise
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            query = """
                SELECT user_id, username, full_name, email, role, is_active, last_login
                FROM users
                WHERE username = %s
            """
            return self.db.execute_query(query, (username,), fetchone=True)
        except Exception as e:
            logging.error(f"Error getting user by username {username}: {e}")
            raise
    
    def create_user(self, username, password_hash, full_name, role, email=None):
        """Create a new user"""
        try:
            query = """
                INSERT INTO users
                (username, password, full_name, role, email, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                RETURNING user_id
            """
            return self.db.execute_query(
                query, 
                (username, password_hash, full_name, role, email),
                fetchone=True
            )[0]
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            raise
    
    def update_user(self, user_id, data):
        """Update an existing user"""
        try:
            # Determine which fields to update
            update_fields = []
            params = []
            
            if 'username' in data:
                update_fields.append("username = %s")
                params.append(data['username'])
            
            if 'full_name' in data:
                update_fields.append("full_name = %s")
                params.append(data['full_name'])
            
            if 'email' in data:
                update_fields.append("email = %s")
                params.append(data['email'])
            
            if 'role' in data:
                update_fields.append("role = %s")
                params.append(data['role'])
            
            if 'is_active' in data:
                update_fields.append("is_active = %s")
                params.append(data['is_active'])
            
            if 'password' in data:
                update_fields.append("password = %s")
                params.append(data['password'])
            
            if not update_fields:
                return 0  # No fields to update
            
            # Build and execute query
            query = f"""
                UPDATE users
                SET {', '.join(update_fields)}
                WHERE user_id = %s
            """
            params.append(user_id)
            
            return self.db.execute_query(query, params)
        except Exception as e:
            logging.error(f"Error updating user {user_id}: {e}")
            raise
    
    def delete_user(self, user_id):
        """Delete a user"""
        try:
            query = "DELETE FROM users WHERE user_id = %s"
            return self.db.execute_query(query, (user_id,))
        except Exception as e:
            logging.error(f"Error deleting user {user_id}: {e}")
            raise
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        try:
            query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s"
            return self.db.execute_query(query, (user_id,))
        except Exception as e:
            logging.error(f"Error updating last login for user {user_id}: {e}")
            raise


class SupplierModel(BaseModel):
    """Model for supplier-related database operations"""
    
    def get_all_suppliers(self):
        """Get all suppliers"""
        try:
            query = """
                SELECT supplier_id, name, contact_person, phone, email, address
                FROM suppliers
                ORDER BY name
            """
            return self.db.execute_query(query, fetchall=True)
        except Exception as e:
            logging.error(f"Error getting suppliers: {e}")
            raise
    
    def get_supplier_by_id(self, supplier_id):
        """Get supplier by ID"""
        try:
            query = """
                SELECT supplier_id, name, contact_person, phone, email, address
                FROM suppliers
                WHERE supplier_id = %s
            """
            return self.db.execute_query(query, (supplier_id,), fetchone=True)
        except Exception as e:
            logging.error(f"Error getting supplier {supplier_id}: {e}")
            raise
    
    def create_supplier(self, name, contact_person=None, phone=None, email=None, address=None):
        """Create a new supplier"""
        try:
            query = """
                INSERT INTO suppliers
                (name, contact_person, phone, email, address)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING supplier_id
            """
            return self.db.execute_query(
                query, 
                (name, contact_person, phone, email, address),
                fetchone=True
            )[0]
        except Exception as e:
            logging.error(f"Error creating supplier: {e}")
            raise
    
    def update_supplier(self, supplier_id, data):
        """Update an existing supplier"""
        try:
            query = """
                UPDATE suppliers
                SET name = %s, contact_person = %s, phone = %s, email = %s, 
                    address = %s, updated_at = CURRENT_TIMESTAMP
                WHERE supplier_id = %s
            """
            params = (
                data.get('name'),
                data.get('contact_person'),
                data.get('phone'),
                data.get('email'),
                data.get('address'),
                supplier_id
            )
            return self.db.execute_query(query, params)
        except Exception as e:
            logging.error(f"Error updating supplier {supplier_id}: {e}")
            raise
    
    def delete_supplier(self, supplier_id):
        """Delete a supplier"""
        try:
            query = "DELETE FROM suppliers WHERE supplier_id = %s"
            return self.db.execute_query(query, (supplier_id,))
        except Exception as e:
            logging.error(f"Error deleting supplier {supplier_id}: {e}")
            raise
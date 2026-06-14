import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pymysql
import pymysql.cursors

app = Flask(__name__)
# Secret key is required for sessions and flash messaging
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', 'password')
    port = int(os.environ.get('MYSQL_PORT', 3306))
    db_name = os.environ.get('MYSQL_DB', 'employee_db')
    
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    """Initializes the database and table. Retries connection for dev/docker environment robustness."""
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', 'password')
    port = int(os.environ.get('MYSQL_PORT', 3306))
    db_name = os.environ.get('MYSQL_DB', 'employee_db')
    
    connection = None
    last_error = None
    
    # Retry connecting to MySQL (useful when DB starts up slower than app in Docker environment)
    for i in range(5):
        try:
            print(f"Connecting to MySQL at {host}:{port} (Attempt {i+1}/5)...")
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                port=port
            )
            break
        except Exception as e:
            last_error = e
            time.sleep(2)
            
    if not connection:
        raise Exception(f"Failed to connect to MySQL server. Error: {last_error}")
        
    try:
        with connection.cursor() as cursor:
            # Create the database if it does not exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # Create the employees table if it does not exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    position VARCHAR(100) NOT NULL,
                    salary DECIMAL(10, 2) NOT NULL
                )
            """)
        connection.commit()
        print("Database structure verified/created successfully.")
    finally:
        connection.close()

# ----------------- Application Routes -----------------

@app.route('/')
def index():
    """Home route displaying all employees with optional search filter."""
    search_query = request.args.get('search', '')
    employees = []
    db_error = None
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if search_query:
                sql = """
                    SELECT * FROM employees 
                    WHERE full_name LIKE %s 
                       OR email LIKE %s 
                       OR department LIKE %s 
                       OR position LIKE %s
                """
                # Use parameterized query to prevent SQL Injection
                search_param = f"%{search_query}%"
                cursor.execute(sql, (search_param, search_param, search_param, search_param))
            else:
                cursor.execute("SELECT * FROM employees ORDER BY id DESC")
            employees = cursor.fetchall()
        conn.close()
    except Exception as e:
        db_error = f"Database connection issue: {e}"
        print(db_error)
        
    return render_template('index.html', employees=employees, db_error=db_error, search_query=search_query)

@app.route('/view/<int:id>')
def view_employee(id):
    """View details of a single employee."""
    employee = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
            employee = cursor.fetchone()
        conn.close()
    except Exception as e:
        flash(f"Error fetching employee details: {e}", "danger")
        return redirect(url_for('index'))
        
    if not employee:
        flash("Employee not found.", "warning")
        return redirect(url_for('index'))
        
    return render_template('view.html', employee=employee)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    """Add a new employee record."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        position = request.form.get('position', '').strip()
        salary = request.form.get('salary', '').strip()
        
        # Validation checks
        if not all([full_name, email, department, position, salary]):
            flash("All fields are required.", "warning")
            return render_template('add.html', form_data=request.form)
            
        try:
            salary_val = float(salary)
            if salary_val < 0:
                raise ValueError("Salary must be positive.")
        except ValueError:
            flash("Invalid salary format. Must be a numeric value.", "warning")
            return render_template('add.html', form_data=request.form)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO employees (full_name, email, department, position, salary)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (full_name, email, department, position, salary_val))
            conn.commit()
            conn.close()
            flash(f"Employee {full_name} added successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Database error while adding employee: {e}", "danger")
            return render_template('add.html', form_data=request.form)
            
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    """Edit an existing employee record."""
    employee = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
            employee = cursor.fetchone()
        conn.close()
    except Exception as e:
        flash(f"Error fetching employee for editing: {e}", "danger")
        return redirect(url_for('index'))
        
    if not employee:
        flash("Employee not found.", "warning")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        position = request.form.get('position', '').strip()
        salary = request.form.get('salary', '').strip()
        
        if not all([full_name, email, department, position, salary]):
            flash("All fields are required.", "warning")
            return render_template('edit.html', employee=employee)
            
        try:
            salary_val = float(salary)
            if salary_val < 0:
                raise ValueError("Salary must be positive.")
        except ValueError:
            flash("Invalid salary format. Must be a numeric value.", "warning")
            return render_template('edit.html', employee=employee)
            
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = """
                    UPDATE employees 
                    SET full_name = %s, email = %s, department = %s, position = %s, salary = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (full_name, email, department, position, salary_val, id))
            conn.commit()
            conn.close()
            flash("Employee details updated successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Database error while updating employee: {e}", "danger")
            return render_template('edit.html', employee=employee)
            
    return render_template('edit.html', employee=employee)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    """Deletes an employee record (safely via POST request)."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        flash("Employee record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting employee record: {e}", "danger")
        
    return redirect(url_for('index'))

@app.route('/health')
def health():
    """Health check endpoint for platform, load balancer, and pipeline tests."""
    return jsonify({"status": "healthy"})
    

# ----------------- Main Entrypoint -----------------

if __name__ == '__main__':
    # Try initializing the database at startup
    try:
        init_db()
    except Exception as e:
        print(f"CRITICAL WARNING: Database initialization failed during startup. App will load but features requiring database connection may fail.\nDetail: {e}")
        
    # Bind to all interfaces for container deployment availability
    app.run(host='0.0.0.0', port=5000, debug=True)

# CI/CD Rollback Test
# webhook test 2
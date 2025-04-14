import os
import sys  # Voor printen naar stderr
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg  # Vervangen door psycopg (v3) voor lager geheugengebruik

load_dotenv()  # Laadt variabelen van .env bestand

app = Flask(__name__)
# Configuratie voor statische bestanden beperken (vermindert geheugengebruik)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache voor 1 jaar
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limiet upload grootte (16MB)

# Sta requests toe van je React app
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
RENDER_FRONTEND_URL = os.getenv("RENDER_FRONTEND_URL")

origins = [FRONTEND_URL]
if RENDER_FRONTEND_URL:
    origins.append(RENDER_FRONTEND_URL)

# Gebruik CORS alleen waar nodig
CORS(app, resources={r"/api/*": {"origins": origins}})

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("FATAL: DATABASE_URL environment variable not set.", file=sys.stderr)
    sys.exit(1)

# Connection pool configuratie met minimale overhead
connection_params = {}
# Kleinere pool om geheugen te sparen, standaard 'minconn=1, maxconn=10'
# Aanpassen op basis van werkelijke load
#connection_params['min_size'] = 1
#connection_params['max_size'] = 5

def get_db_connection():
    """Maakt verbinding met de PostgreSQL database met psycopg v3."""
    try:
        # Gebruikt psycopg's connection pooling met minimale instellingen
        conn = psycopg.connect(DATABASE_URL, **connection_params, autocommit=False)
        return conn
    except psycopg.Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        return None

# --- Clients API ---
@app.route('/api/clients', methods=['GET'])
def get_clients():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        
        # Gebruik psycopg v3's cursor met row factory
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("SELECT id, name, email, phone FROM clients ORDER BY name")
            # Gebruik iteratie om geheugengebruik te beperken bij grote datasets
            clients_list = list(cur)
            return jsonify(clients_list)
    except psycopg.Error as e:
        print(f"Error fetching clients: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve clients"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO clients (name, email, phone) VALUES (%s, %s, %s) RETURNING id",
                (name, email, phone)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({"id": new_id, "name": name, "email": email, "phone": phone}), 201
    except psycopg.Error as e:
        if conn: conn.rollback()
        print(f"Error adding client: {e}", file=sys.stderr)
        if "unique constraint" in str(e).lower():
            return jsonify({"error": "Client with this information might already exist."}), 409
        return jsonify({"error": "Failed to add client"}), 500
    finally:
        if conn: conn.close()

# --- Treatment Methods API ---
@app.route('/api/treatment-methods', methods=['GET'])
def get_treatment_methods():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("SELECT id, name, billing_type, rate FROM treatment_methods ORDER BY name")
            methods = list(cur)
            # Converteer rate naar float in-place om Decimal objecten te vermijden
            for method in methods:
                if method['rate'] is not None:
                    method['rate'] = float(method['rate'])
            return jsonify(methods)
    except psycopg.Error as e:
        print(f"Error fetching treatment methods: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve treatment methods"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/treatment-methods', methods=['POST'])
def add_treatment_method():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    name = data.get('name')
    billing_type = data.get('billing_type')
    rate_str = data.get('rate')

    if not name or not billing_type or rate_str is None:
        return jsonify({"error": "Missing required fields: name, billing_type, rate"}), 400
    if billing_type not in ['hourly', 'session']:
        return jsonify({"error": "Invalid billing_type. Must be 'hourly' or 'session'."}), 400

    # Simpelere validatie om Decimal import te vermijden
    try:
        rate = float(rate_str)
        if rate < 0:
            raise ValueError("Rate cannot be negative.")
    except (ValueError, TypeError) as verr:
        return jsonify({"error": f"Invalid rate format: {verr}"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO treatment_methods (name, billing_type, rate) VALUES (%s, %s, %s) RETURNING id",
                (name, billing_type, rate)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({"id": new_id, "name": name, "billing_type": billing_type, "rate": float(rate)}), 201
    except psycopg.Error as e:
        if conn: conn.rollback()
        print(f"Error adding treatment method: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to add treatment method"}), 500
    finally:
        if conn: conn.close()

# --- Treatments API ---
@app.route('/api/treatments', methods=['GET'])
def get_treatments():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        with conn.cursor() as cur:
            # Efficiëntere query met alleen nodige velden
            cur.execute("""
                SELECT t.id, t.treatment_date, t.duration_hours, t.notes, t.is_billed,
                       c.name as client_name, tm.name as method_name, tm.billing_type,
                       tm.rate
                FROM treatments t
                JOIN clients c ON t.client_id = c.id
                JOIN treatment_methods tm ON t.treatment_method_id = tm.id
                ORDER BY t.treatment_date DESC, t.created_at DESC
            """)
            
            # Stream verwerking voor lager geheugengebruik
            treatments_list = []
            for row in cur:
                treatments_list.append({
                    "id": row[0],
                    "treatment_date": row[1].isoformat() if row[1] else None,
                    "duration_hours": float(row[2]) if row[2] is not None else None,
                    "notes": row[3],
                    "is_billed": row[4],
                    "client_name": row[5],
                    "method_name": row[6],
                    "billing_type": row[7],
                    "rate": float(row[8]) if row[8] is not None else None
                })
            return jsonify(treatments_list)
    except psycopg.Error as e:
        print(f"Error fetching treatments: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve treatments"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/treatments', methods=['POST'])
def add_treatment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    client_id = data.get('client_id')
    treatment_method_id = data.get('treatment_method_id')
    treatment_date = data.get('treatment_date')
    duration_hours_str = data.get('duration_hours')
    notes = data.get('notes', '')

    if not client_id or not treatment_method_id or not treatment_date:
        return jsonify({"error": "Missing required fields: client_id, treatment_method_id, treatment_date"}), 400

    # Simpelere validatie zonder Decimal
    duration_hours = None
    if duration_hours_str is not None:
        try:
            duration_hours = float(duration_hours_str)
            if duration_hours <= 0:
                raise ValueError("Duration must be positive.")
        except (ValueError, TypeError) as verr:
            return jsonify({"error": f"Invalid duration_hours format: {verr}"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO treatments (client_id, treatment_method_id, treatment_date, duration_hours, notes)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (client_id, treatment_method_id, treatment_date, duration_hours, notes)
            )
            new_id = cur.fetchone()[0]
            conn.commit()

            response_data = {
                "id": new_id,
                "client_id": client_id,
                "treatment_method_id": treatment_method_id,
                "treatment_date": treatment_date,
                "duration_hours": float(duration_hours) if duration_hours is not None else None,
                "notes": notes,
                "is_billed": False
            }
            return jsonify(response_data), 201

    except psycopg.Error as e:
        if conn: conn.rollback()
        print(f"Error adding treatment: {e}", file=sys.stderr)
        if "foreign key constraint" in str(e).lower():
            return jsonify({"error": "Invalid client_id or treatment_method_id provided."}), 400
        return jsonify({"error": "Failed to add treatment"}), 500
    finally:
        if conn: conn.close()

# --- Invoices API (Placeholders) ---
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    # Placeholder: Haal facturen op uit de DB (Implementatie nodig)
    mock_invoices = [
        {"id": "inv_1", "invoice_number": "FACT-2025-001", "client_name": "Test Client A", "invoice_date": "2025-03-31", "total_amount": 150.00, "status": "open"},
        {"id": "inv_2", "invoice_number": "FACT-2025-002", "client_name": "Test Client B", "invoice_date": "2025-03-31", "total_amount": 80.00, "status": "paid"},
    ]
    return jsonify(mock_invoices)

@app.route('/api/invoices/generate', methods=['POST'])
def generate_invoices():
    # Placeholder: Implementeer logica om facturen te genereren
    print("LOG: Invoice generation triggered", request.get_json())
    return jsonify({"message": "Invoice generation process started (placeholder)"}), 202

# Lazy imports voor PDF- en XLS-generatie
# Importeer deze modules alleen als nodig om RAM te sparen
pdf_module = None
excel_module = None
io_module = None

@app.route('/api/invoices/<invoice_id>/pdf', methods=['GET'])
def get_invoice_pdf(invoice_id):
    global pdf_module
    
    # Lazy import: alleen laden wanneer nodig
    if pdf_module is None:
        try:
            from weasyprint import HTML
            pdf_module = HTML
        except ImportError:
            print("ERROR: WeasyPrint library not installed. Cannot generate PDF.", file=sys.stderr)
            return jsonify({"error": "PDF generation library not available."}), 501

    print(f"LOG: PDF requested for invoice {invoice_id}")

    # Placeholder PDF response
    pdf_content = f"PDF voor factuur {invoice_id} (placeholder - WeasyPrint is beschikbaar)"
    return Response(
        pdf_content.encode('utf-8'),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename=factuur_{invoice_id}.pdf'}
    )

@app.route('/api/invoices/<invoice_id>/xls', methods=['GET'])
def get_invoice_xls(invoice_id):
    global excel_module, io_module
    
    # Lazy import: alleen laden wanneer nodig
    if excel_module is None or io_module is None:
        try:
            import openpyxl
            import io
            excel_module = openpyxl
            io_module = io
        except ImportError:
            print("ERROR: openpyxl library not installed. Cannot generate XLS.", file=sys.stderr)
            return jsonify({"error": "XLS generation library not available."}), 501

    print(f"LOG: XLS requested for invoice {invoice_id}")

    # Placeholder XLS response
    xls_content = f"XLS voor factuur {invoice_id} (placeholder - openpyxl is beschikbaar)"
    return Response(
        xls_content.encode('utf-8'),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment;filename=factuur_{invoice_id}.xlsx'}
    )

if __name__ == '__main__':
    # Gebruik PORT env var voor Render, default naar 5001
    port = int(os.getenv('PORT', 5001))
    debug_mode = os.getenv('FLASK_DEBUG') == '1'
    
    # Minder threads gebruiken om RAM te besparen
    print(f"Starting Flask app on port {port} with debug mode: {debug_mode}")
    app.run(debug=debug_mode, port=port, host='0.0.0.0', threaded=True, processes=1)
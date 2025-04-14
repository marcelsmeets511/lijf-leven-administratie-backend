import os
import psycopg2
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import sys # Goede gewoonte om te gebruiken voor printen naar stderr

load_dotenv() # Laadt variabelen van .env bestand

app = Flask(__name__)
# Sta requests toe van je React app (pas eventueel de origin aan)
# Haal de frontend URL op uit de environment variabelen voor flexibiliteit
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000") # Default naar localhost:3000
RENDER_FRONTEND_URL = os.getenv("RENDER_FRONTEND_URL") # Specifieke Render URL (optioneel)

origins = [FRONTEND_URL]
if RENDER_FRONTEND_URL:
    origins.append(RENDER_FRONTEND_URL)

CORS(app, resources={r"/api/*": {"origins": origins}})

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("FATAL: DATABASE_URL environment variable not set.", file=sys.stderr)
    sys.exit(1) # Stop de applicatie als de DB URL mist

def get_db_connection():
    """Maakt verbinding met de PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        # Gebruik stderr voor foutmeldingen
        print(f"Database connection error: {e}", file=sys.stderr)
        return None

# --- Clients API ---
@app.route('/api/clients', methods=['GET'])
def get_clients():
    conn = None # Initialiseer conn
    try:
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        with conn.cursor() as cur:
            # Gebruik psycopg2's dict cursor voor direct dictionary resultaat (optioneel, kan iets meer geheugen gebruiken dan tuples)
            # from psycopg2.extras import RealDictCursor
            # with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, email, phone FROM clients ORDER BY name")
            clients = cur.fetchall()
            # Converteer naar list of dicts (nodig als je geen RealDictCursor gebruikt)
            clients_list = [{"id": row[0], "name": row[1], "email": row[2], "phone": row[3]} for row in clients]
            return jsonify(clients_list)
    except psycopg2.Error as e:
        print(f"Error fetching clients: {e}", file=sys.stderr) # Log de error server-side
        return jsonify({"error": "Failed to retrieve clients"}), 500 # Generic error for client
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
    except psycopg2.Error as e:
        if conn: conn.rollback() # Ensure rollback happens if conn exists
        print(f"Error adding client: {e}", file=sys.stderr)
        # Check for specific errors if needed, e.g., unique constraint violation
        if "unique constraint" in str(e).lower():
             return jsonify({"error": "Client with this information might already exist."}), 409 # Conflict
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
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, billing_type, rate FROM treatment_methods ORDER BY name")
            methods = cur.fetchall()
            # Converteer rate naar float tijdens de list comprehension
            methods_list = [{"id": row[0], "name": row[1], "billing_type": row[2], "rate": float(row[3]) if row[3] is not None else None} for row in methods]
            return jsonify(methods_list)
    except psycopg2.Error as e:
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
    rate_str = data.get('rate') # Ontvang als string of number

    if not name or not billing_type or rate_str is None:
        return jsonify({"error": "Missing required fields: name, billing_type, rate"}), 400
    if billing_type not in ['hourly', 'session']:
         return jsonify({"error": "Invalid billing_type. Must be 'hourly' or 'session'."}), 400

    try:
        # Valideer en converteer rate naar numeriek type (Decimal aanbevolen voor geld)
        from decimal import Decimal, InvalidOperation
        try:
            rate = Decimal(rate_str)
            if rate < 0:
                 raise ValueError("Rate cannot be negative.")
        except (InvalidOperation, ValueError) as verr:
            return jsonify({"error": f"Invalid rate format: {verr}"}), 400
    except ImportError:
        # Fallback to float if Decimal is not available (minder precies)
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
                (name, billing_type, rate) # Stuur Decimal of float naar DB
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            # Converteer rate terug naar float voor JSON (JSON ondersteunt geen Decimal)
            return jsonify({"id": new_id, "name": name, "billing_type": billing_type, "rate": float(rate)}), 201
    except psycopg2.Error as e:
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
            # Join met clients en methods om namen op te halen
            cur.execute("""
                SELECT t.id, t.treatment_date, t.duration_hours, t.notes, t.is_billed,
                       c.name as client_name, tm.name as method_name, tm.billing_type,
                       tm.rate -- Haal rate ook op voor eventuele berekeningen
                FROM treatments t
                JOIN clients c ON t.client_id = c.id
                JOIN treatment_methods tm ON t.treatment_method_id = tm.id
                ORDER BY t.treatment_date DESC, t.created_at DESC
            """)
            treatments = cur.fetchall()
            treatments_list = []
            for row in treatments:
                # Converteer Decimal/numeric types correct naar float voor JSON
                duration = float(row[2]) if row[2] is not None else None
                rate = float(row[8]) if row[8] is not None else None # Rate van treatment_method

                treatments_list.append({
                    "id": row[0],
                    "treatment_date": row[1].isoformat() if row[1] else None, # Check if date exists
                    "duration_hours": duration,
                    "notes": row[3],
                    "is_billed": row[4],
                    "client_name": row[5],
                    "method_name": row[6],
                    "billing_type": row[7],
                    "rate": rate # Voeg rate toe aan de response indien nuttig
                })
            return jsonify(treatments_list)
    except psycopg2.Error as e:
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
    treatment_date = data.get('treatment_date') # Moet ISO format zijn (YYYY-MM-DD)
    duration_hours_str = data.get('duration_hours')
    notes = data.get('notes', '') # Default naar lege string

    if not client_id or not treatment_method_id or not treatment_date:
         return jsonify({"error": "Missing required fields: client_id, treatment_method_id, treatment_date"}), 400

    # Validatie en conversie voor duration_hours (optioneel veld, maar moet numeriek zijn indien aanwezig)
    duration_hours = None
    if duration_hours_str is not None:
        try:
            # Gebruik Decimal voor precisie indien nodig, anders float
            from decimal import Decimal, InvalidOperation
            try:
                duration_hours = Decimal(duration_hours_str)
                if duration_hours <= 0:
                     raise ValueError("Duration must be positive.")
            except (InvalidOperation, ValueError) as verr:
                 return jsonify({"error": f"Invalid duration_hours format: {verr}"}), 400
        except ImportError:
             # Fallback float
            try:
                duration_hours = float(duration_hours_str)
                if duration_hours <= 0:
                    raise ValueError("Duration must be positive.")
            except (ValueError, TypeError) as verr:
                return jsonify({"error": f"Invalid duration_hours format: {verr}"}), 400

    # Hier zou je een check kunnen toevoegen of duration_hours verplicht is
    # gebaseerd op de billing_type van de treatment_method_id (vereist extra query).
    # Voor nu laten we het zoals het was.

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

            # Creëer response data (converteer Decimal terug naar float voor JSON)
            response_data = {
                "id": new_id,
                "client_id": client_id,
                "treatment_method_id": treatment_method_id,
                "treatment_date": treatment_date,
                "duration_hours": float(duration_hours) if duration_hours is not None else None,
                "notes": notes,
                "is_billed": False # Nieuwe treatments zijn niet gefactureerd
            }
            # Optioneel: Haal client/method namen op voor een completere response (extra query nodig)
            return jsonify(response_data), 201

    except psycopg2.Error as e:
        if conn: conn.rollback()
        print(f"Error adding treatment: {e}", file=sys.stderr)
        # Check bv. foreign key constraint error
        if "foreign key constraint" in str(e).lower():
            return jsonify({"error": "Invalid client_id or treatment_method_id provided."}), 400
        return jsonify({"error": "Failed to add treatment"}), 500
    finally:
        if conn: conn.close()

# --- Invoices API (Placeholders) ---
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    # Placeholder: Haal facturen op uit de DB (Implementatie nodig)
    # Voeg joins toe om client naam etc. op te halen
    mock_invoices = [
        {"id": "inv_1", "invoice_number": "FACT-2025-001", "client_name": "Test Client A", "invoice_date": "2025-03-31", "total_amount": 150.00, "status": "open"},
        {"id": "inv_2", "invoice_number": "FACT-2025-002", "client_name": "Test Client B", "invoice_date": "2025-03-31", "total_amount": 80.00, "status": "paid"},
    ]
    # In een echte implementatie haal je dit uit de database
    return jsonify(mock_invoices)

@app.route('/api/invoices/generate', methods=['POST'])
def generate_invoices():
    # Placeholder: Implementeer logica om facturen te genereren
    # (vereist DB queries, berekeningen, updates)
    print("LOG: Invoice generation triggered", request.get_json())
    # Echte implementatie zou hier starten
    return jsonify({"message": "Invoice generation process started (placeholder)"}), 202 # Accepted

@app.route('/api/invoices/<invoice_id>/pdf', methods=['GET'])
def get_invoice_pdf(invoice_id):
    # **Importeer WeasyPrint alleen wanneer deze functie wordt aangeroepen**
    try:
        from weasyprint import HTML
    except ImportError:
        print("ERROR: WeasyPrint library not installed. Cannot generate PDF.", file=sys.stderr)
        return jsonify({"error": "PDF generation library not available."}), 501 # Not Implemented

    print(f"LOG: PDF requested for invoice {invoice_id}")

    # Placeholder: Implementeer PDF generatie
    # 1. Haal factuur data + bijbehorende behandelingen op uit DB
    # 2. Render HTML template (bv. met Jinja2 - importeer die hier ook)
    # 3. Converteer HTML -> PDF
    # Voorbeeld (vereist echte data en template):
    # html_content = render_template('invoice_template.html', invoice_data=data)
    # pdf_bytes = HTML(string=html_content).write_pdf()
    # return Response(pdf_bytes, ...)

    # Huidige placeholder response:
    pdf_content = f"PDF voor factuur {invoice_id} (placeholder - WeasyPrint is beschikbaar)"
    return Response(
        pdf_content.encode('utf-8'), # Stuur bytes
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename=factuur_{invoice_id}.pdf'}
    )

@app.route('/api/invoices/<invoice_id>/xls', methods=['GET'])
def get_invoice_xls(invoice_id):
    # **Importeer openpyxl en io alleen wanneer deze functie wordt aangeroepen**
    try:
        import openpyxl
        import io
    except ImportError:
        print("ERROR: openpyxl library not installed. Cannot generate XLS.", file=sys.stderr)
        return jsonify({"error": "XLS generation library not available."}), 501 # Not Implemented

    print(f"LOG: XLS requested for invoice {invoice_id}")

    # Placeholder: Implementeer XLS generatie
    # 1. Haal factuur data op
    # 2. Creëer workbook en sheet met openpyxl
    # 3. Vul sheet met data
    # 4. Sla op naar een byte stream (io.BytesIO)

    # Voorbeeld (vereist echte data):
    # workbook = openpyxl.Workbook()
    # sheet = workbook.active
    # sheet['A1'] = f"Factuur {invoice_id}"
    # ... voeg meer data toe ...
    #
    # virtual_workbook = io.BytesIO()
    # workbook.save(virtual_workbook)
    # virtual_workbook.seek(0) # Ga terug naar begin van stream
    # return Response(virtual_workbook, ...)

    # Huidige placeholder response:
    xls_content = f"XLS voor factuur {invoice_id} (placeholder - openpyxl is beschikbaar)"
    return Response(
        xls_content.encode('utf-8'), # Stuur bytes (dit is geen echte XLS)
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment;filename=factuur_{invoice_id}.xlsx'}
    )


if __name__ == '__main__':
    # Gebruik PORT env var voor Render, default naar 5001 om conflicten met React dev server (vaak 5000) te voorkomen
    port = int(os.getenv('PORT', 5001))
    # Debug mode alleen aan als FLASK_DEBUG=1 is ingesteld in environment (veiliger voor productie)
    debug_mode = os.getenv('FLASK_DEBUG') == '1'
    print(f"Starting Flask app on port {port} with debug mode: {debug_mode}")
    app.run(debug=debug_mode, port=port, host='0.0.0.0') # host='0.0.0.0' is vaak nodig voor Docker/Render

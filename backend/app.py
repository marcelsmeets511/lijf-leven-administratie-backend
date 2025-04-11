import os
import psycopg2
from flask import Flask, request, jsonify, Response # Added Response
from flask_cors import CORS
from dotenv import load_dotenv
# from weasyprint import HTML # Placeholder for PDF generation
# import openpyxl # Placeholder for XLS generation
# import io # Placeholder for XLS generation

load_dotenv() # Laadt variabelen van .env bestand

app = Flask(__name__)
# Sta requests toe van je React app (pas eventueel de origin aan)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "YOUR_RENDER_FRONTEND_URL"]}}) # Vul je Render frontend URL in

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Maakt verbinding met de PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

# --- Clients API ---
@app.route('/api/clients', methods=['GET'])
def get_clients():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, phone FROM clients ORDER BY name")
            clients = cur.fetchall()
            # Converteer naar list of dicts
            clients_list = [{"id": row[0], "name": row[1], "email": row[2], "phone": row[3]} for row in clients]
            return jsonify(clients_list)
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@app.route('/api/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone') # Voeg andere velden toe indien nodig

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO clients (name, email, phone) VALUES (%s, %s, %s) RETURNING id",
                (name, email, phone)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({"id": new_id, "name": name, "email": email, "phone": phone}), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- Treatment Methods API ---
@app.route('/api/treatment-methods', methods=['GET'])
def get_treatment_methods():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, billing_type, rate FROM treatment_methods ORDER BY name")
            methods = cur.fetchall()
            methods_list = [{"id": row[0], "name": row[1], "billing_type": row[2], "rate": float(row[3])} for row in methods]
            return jsonify(methods_list)
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()


@app.route('/api/treatment-methods', methods=['POST'])
def add_treatment_method():
    data = request.get_json()
    name = data.get('name')
    billing_type = data.get('billing_type')
    rate = data.get('rate')

    if not name or not billing_type or rate is None:
        return jsonify({"error": "Missing required fields"}), 400
    if billing_type not in ['hourly', 'session']:
         return jsonify({"error": "Invalid billing_type"}), 400

    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO treatment_methods (name, billing_type, rate) VALUES (%s, %s, %s) RETURNING id",
                (name, billing_type, rate)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({"id": new_id, "name": name, "billing_type": billing_type, "rate": float(rate)}), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- Treatments API ---
@app.route('/api/treatments', methods=['GET'])
def get_treatments():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cur:
            # Join met clients en methods om namen op te halen
            cur.execute("""
                SELECT t.id, t.treatment_date, t.duration_hours, t.notes, t.is_billed,
                       c.name as client_name, tm.name as method_name, tm.billing_type
                FROM treatments t
                JOIN clients c ON t.client_id = c.id
                JOIN treatment_methods tm ON t.treatment_method_id = tm.id
                ORDER BY t.treatment_date DESC, t.created_at DESC
            """)
            treatments = cur.fetchall()
            treatments_list = [
                {"id": row[0], "treatment_date": row[1].isoformat(), "duration_hours": float(row[2]) if row[2] is not None else None,
                 "notes": row[3], "is_billed": row[4], "client_name": row[5], "method_name": row[6],
                 "billing_type": row[7]}
                for row in treatments
            ]
            return jsonify(treatments_list)
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@app.route('/api/treatments', methods=['POST'])
def add_treatment():
    data = request.get_json()
    client_id = data.get('client_id')
    treatment_method_id = data.get('treatment_method_id')
    treatment_date = data.get('treatment_date')
    duration_hours = data.get('duration_hours')
    notes = data.get('notes')

    if not client_id or not treatment_method_id or not treatment_date:
         return jsonify({"error": "Missing required fields"}), 400

    # Basic validation voor duration (vereist als type 'hourly' is)
    # Dit vereist een extra DB query om het type op te halen, voor eenvoud weggelaten hier
    # if billing_type == 'hourly' and duration_hours is None:
    #    return jsonify({"error": "Duration is required for hourly billing"}), 400

    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO treatments (client_id, treatment_method_id, treatment_date, duration_hours, notes)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (client_id, treatment_method_id, treatment_date, duration_hours, notes)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            # Retourneer het nieuwe object (eventueel opnieuw ophalen met joins voor namen)
            return jsonify({"id": new_id, **data}), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- Invoices API (Placeholders) ---
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    # Placeholder: Haal facturen op uit de DB
    # Voeg joins toe om client naam etc. op te halen
    mock_invoices = [
        {"id": "inv_1", "invoice_number": "FACT-2025-001", "client_name": "Test Client A", "invoice_date": "2025-03-31", "total_amount": 150.00, "status": "open"},
        {"id": "inv_2", "invoice_number": "FACT-2025-002", "client_name": "Test Client B", "invoice_date": "2025-03-31", "total_amount": 80.00, "status": "paid"},
    ]
    return jsonify(mock_invoices)

@app.route('/api/invoices/generate', methods=['POST'])
def generate_invoices():
    # Placeholder: Implementeer logica om facturen te genereren
    # 1. Zoek onbetaalde behandelingen (is_billed = false) voor een periode/client
    # 2. Groepeer per client
    # 3. Maak invoice record aan
    # 4. Bereken totaal
    # 5. Update treatments (is_billed = true, invoice_id = new_invoice.id)
    print("LOG: Invoice generation triggered", request.get_json())
    return jsonify({"message": "Invoice generation started (placeholder)"}), 202 # Accepted

@app.route('/api/invoices/<invoice_id>/pdf', methods=['GET'])
def get_invoice_pdf(invoice_id):
    # Placeholder: Implementeer PDF generatie
    # 1. Haal factuur data + bijbehorende behandelingen op
    # 2. Render HTML template met Jinja2
    # 3. Gebruik WeasyPrint om HTML -> PDF te converteren
    # 4. Retourneer PDF als response
    print(f"LOG: PDF requested for invoice {invoice_id}")
    # Voorbeeld response (geen echte PDF)
    return Response(f"PDF voor factuur {invoice_id} (placeholder)", mimetype='application/pdf', headers={'Content-Disposition': f'attachment;filename=factuur_{invoice_id}.pdf'})

@app.route('/api/invoices/<invoice_id>/xls', methods=['GET'])
def get_invoice_xls(invoice_id):
    # Placeholder: Implementeer XLS generatie
    # 1. Haal factuur data op
    # 2. Gebruik openpyxl om een .xlsx bestand te maken in memory
    # 3. Retourneer .xlsx als response
    print(f"LOG: XLS requested for invoice {invoice_id}")
    # Voorbeeld response (geen echte XLS)
    return Response(f"XLS voor factuur {invoice_id} (placeholder)", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': f'attachment;filename=factuur_{invoice_id}.xlsx'})


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', 5000)) # Gebruik PORT env var voor Render

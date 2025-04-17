import os
import sys  # Voor printen naar stderr
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client

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
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not DATABASE_URL:
    print("FATAL: DATABASE_URL environment variable not set.", file=sys.stderr)
    sys.exit(1)

if not SUPABASE_KEY:
    print("FATAL: SUPABASE_KEY environment variable not set.", file=sys.stderr)
    sys.exit(1)

supabase = create_client(DATABASE_URL, SUPABASE_KEY)

# --- Clients API ---
@app.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        response = supabase.table('clients').select('id, name, email, phone').order('name').execute()
        clients_list = response.data
        return jsonify(clients_list)
    except Exception as e:
        print(f"Error fetching clients: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve clients"}), 500

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

    try:
        client_data = {
            "name": name,
            "email": email,
            "phone": phone
        }
        
        response = supabase.table('clients').insert(client_data).execute()
        
        if response.data and len(response.data) > 0:
            new_client = response.data[0]
            return jsonify(new_client), 201
        else:
            return jsonify({"error": "Failed to add client"}), 500
    except Exception as e:
        print(f"Error adding client: {e}", file=sys.stderr)
        if "unique constraint" in str(e).lower():
            return jsonify({"error": "Client with this information might already exist."}), 409
        return jsonify({"error": "Failed to add client"}), 500

# --- Treatment Methods API ---
@app.route('/api/treatment-methods', methods=['GET'])
def get_treatment_methods():
    try:
        response = supabase.table('treatment_methods').select('id, name, billing_type, rate').order('name').execute()
        methods = response.data
        
        # Converteer rate naar float in-place om Decimal objecten te vermijden
        for method in methods:
            if method['rate'] is not None:
                method['rate'] = float(method['rate'])
        
        return jsonify(methods)
    except Exception as e:
        print(f"Error fetching treatment methods: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve treatment methods"}), 500

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

    try:
        method_data = {
            "name": name,
            "billing_type": billing_type,
            "rate": rate
        }
        
        response = supabase.table('treatment_methods').insert(method_data).execute()
        
        if response.data and len(response.data) > 0:
            new_method = response.data[0]
            new_method['rate'] = float(new_method['rate']) if new_method['rate'] is not None else None
            return jsonify(new_method), 201
        else:
            return jsonify({"error": "Failed to add treatment method"}), 500
    except Exception as e:
        print(f"Error adding treatment method: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to add treatment method"}), 500

# --- Treatments API ---
@app.route('/api/treatments', methods=['GET'])
def get_treatments():
    try:
        response = supabase.table('treatments').select('*').order('treatment_date',desc=True).execute()
        
        treatments_list = response.data
        
        # Converteer data typen indien nodig
        for treatment in treatments_list:
            if treatment.get('rate') is not None:
                treatment['rate'] = float(treatment['rate'])
            if treatment.get('duration_hours') is not None:
                treatment['duration_hours'] = float(treatment['duration_hours'])
        
        return jsonify(treatments_list)
        
        # Alternatieve methode als RPC niet beschikbaar is:
        # Maak hiervoor een view aan in Supabase en benader deze direct
        # response = supabase.table('treatments_view').select('*').order('treatment_date.desc').execute()
        # return jsonify(response.data)
    except Exception as e:
        print(f"Error fetching treatments: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve treatments"}), 500

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

    try:
        treatment_data = {
            "client_id": client_id,
            "treatment_method_id": treatment_method_id,
            "treatment_date": treatment_date,
            "duration_hours": duration_hours,
            "notes": notes,
            "is_billed": False
        }
        
        response = supabase.table('treatments').insert(treatment_data).execute()
        
        if response.data and len(response.data) > 0:
            new_treatment = response.data[0]
            
            # Zorg ervoor dat duration_hours een float is in de response
            if new_treatment.get('duration_hours') is not None:
                new_treatment['duration_hours'] = float(new_treatment['duration_hours'])
                
            return jsonify(new_treatment), 201
        else:
            return jsonify({"error": "Failed to add treatment"}), 500
    except Exception as e:
        print(f"Error adding treatment: {e}", file=sys.stderr)
        if "foreign key constraint" in str(e).lower():
            return jsonify({"error": "Invalid client_id or treatment_method_id provided."}), 400
        return jsonify({"error": "Failed to add treatment"}), 500

# --- Invoices API (Placeholders) ---
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    try:
        response = supabase.from_('invoices').select('id,client_id,invoice_number,invoice_date,due_date,status,total_amount,created_at,updated_at,clients(id,name)').order('invoice_date').execute()
        
        invoice_list = response.data
      
        return jsonify(invoice_list)
    except Exception as e:
        print(f"Error fetching treatments: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve treatments"}), 500

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

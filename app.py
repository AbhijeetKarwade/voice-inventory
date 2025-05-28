import os
import json
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
import voiceInventory
from voiceInventory import excel_2JSON, start_session, stop_session, active_session, clear_entry, delete_entry

# Define the data directory for Render's persistent disk
DATA_DIR = '/opt/render/project/data'

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory(os.getcwd(), 'index.html')

# Load vendors, materials, and units from JSON files
def load_data():
    try:
        with open(os.path.join(DATA_DIR, 'vendors.json')) as vendors_file:
            vendors = json.load(vendors_file)
        with open(os.path.join(DATA_DIR, 'materials.json')) as materials_file:
            materials = json.load(materials_file)
        with open(os.path.join(DATA_DIR, 'units.json')) as units_file:
            units = json.load(units_file)
        return vendors, materials, units
    except Exception as e:
        return [], [], []

# Endpoint to get vendors, materials, and units
@app.route('/data', methods=['GET'])
def get_data():
    vendors, materials, units = load_data()
    return jsonify({'vendors': vendors, 'materials': materials, 'units': units})

# Endpoint to get vendors
@app.route('/get_vendors', methods=['GET'])
def get_vendors():
    vendors, _, _ = load_data()
    return jsonify({'vendors': vendors})

# Endpoint to get materials
@app.route('/get_materials', methods=['GET'])
def get_materials():
    _, materials, _ = load_data()
    return jsonify({'materials': materials})

# Endpoint to add a new vendor
@app.route('/add_vendor', methods=['POST'])
def add_vendor():
    new_vendor = request.json.get('vendor')
    if new_vendor:
        vendors, materials, units = load_data()
        vendors.append({'vendor': new_vendor})
        with open(os.path.join(DATA_DIR, 'vendors.json'), 'w') as vendors_file:
            json.dump(vendors, vendors_file, indent=4)
        return jsonify({'message': 'Vendor added successfully!'}), 201
    return jsonify({'error': 'Vendor name is required!'}), 400

# Endpoint to add a new material
@app.route('/add_material', methods=['POST'])
def add_material():
    new_material = request.json.get('material')
    new_unit = request.json.get('unit')
    if new_material:
        vendors, materials, units = load_data()
        materials.append({'material': new_material, 'unit': new_unit})
        units.append({'unit': new_unit})
        with open(os.path.join(DATA_DIR, 'materials.json'), 'w') as materials_file:
            json.dump(materials, materials_file, indent=4)
        with open(os.path.join(DATA_DIR, 'units.json'), 'w') as units_file:
            json.dump(units, units_file, indent=4)
        return jsonify({'message': 'Material with unit added successfully!'}), 201
    return jsonify({'error': 'Material name is required!'}), 400

# Endpoint to delete a vendor
@app.route('/delete_vendor', methods=['POST'])
def delete_vendor():
    vendor_to_delete = request.json.get('vendor')
    if vendor_to_delete:
        vendors, materials, units = load_data()
        vendors = [vendor for vendor in vendors if vendor['vendor'] != vendor_to_delete]
        with open(os.path.join(DATA_DIR, 'vendors.json'), 'w') as vendors_file:
            json.dump(vendors, vendors_file, indent=4)
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': 'Vendor not found!'}), 404

# Endpoint to delete a material
@app.route('/delete_material', methods=['POST'])
def delete_material():
    material_to_delete = request.json.get('material')
    if material_to_delete:
        vendors, materials, units = load_data()
        materials = [material for material in materials if material['material'] != material_to_delete]
        with open(os.path.join(DATA_DIR, 'materials.json'), 'w') as materials_file:
            json.dump(materials, materials_file, indent=4)
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': 'Material not found!'}), 404

# Endpoint to import Excel file and convert to JSON
@app.route('/import_excel', methods=['POST'])
def import_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided!'}), 400
    file = request.files['file']
    output_file = request.form.get('output_file')
    columns = request.form.get('columns').split(',')
    
    if not file or not output_file or not columns:
        return jsonify({'error': 'Missing file, output_file, or columns!'}), 400
    
    try:
        # Save the uploaded file temporarily
        temp_path = os.path.join(DATA_DIR, file.filename)
        file.save(temp_path)
        
        # Call excel_2JSON from voiceInventory.py
        voiceInventory.excel_2JSON(temp_path, os.path.join(DATA_DIR, output_file), *columns)
        
        # Remove the temporary file
        os.remove(temp_path)
        
        return jsonify({'message': f'Successfully converted {file.filename} to {output_file}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to save inventory items
@app.route('/save_inventory', methods=['POST'])
def save_inventory():
    items = request.json.get('items')
    if not items:
        return jsonify({'error': 'No items provided!'}), 400
    try:
        formatted_items = [[
            item['date'],
            item['vendor'],
            item['item'],
            item['quantity'],
            item['unit'],
            item['session']
        ] for item in items]
        for item in formatted_items:
            voiceInventory.save_2json(item[5], [item])
        return jsonify({'message': 'Inventory saved successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to export inventory to various formats
@app.route('/export_entries', methods=['POST'])
def export_entries():
    file_name = request.json.get('filename')
    format_type = request.json.get('format')
    voiceInventory.export_inventory(file_name, format_type)
    return jsonify({'success': True, 'message': 'File successfully created.', 'filename': f"{file_name}.{format_type.lower()}"}), 200

# Endpoint to download exported files
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DATA_DIR, filename, as_attachment=True)

# Endpoint to clear entries in a JSON file
@app.route('/clear_entries', methods=['POST'])
def clear_entries():
    filename = request.json.get('filename')
    voiceInventory.empty_jsonFile(os.path.join(DATA_DIR, filename))
    return jsonify({'message': 'JSON cleared'}), 200

# Endpoint to remove a specific entry
@app.route('/remove_entry', methods=['POST'])
def remove_entry():
    entry2delete = request.json.get('entry')
    delete_entry(json.dumps(entry2delete))
    return jsonify({'message': 'Entry deleted'}), 200

# Endpoint to check session status
@app.route('/session_status', methods=['GET'])
def session_status():
    result = active_session()
    return result

# Endpoint to complete a session
@app.route('/session_complete', methods=['POST'])
def session_complete():
    return jsonify({'message': 'Session completed', 'entry': clear_entry()})

# Endpoint to start a listening session
@app.route('/start_listening', methods=['POST'])
def start_listening():
    data = request.json
    for session in data:
        result = start_session(data[session])
    return jsonify({'message': result, 'beep': 'supplier'}), 202

# Endpoint to stop a listening session
@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    data = request.json
    for session in data:
        result = stop_session(data[session])
    return jsonify({'message': result}), 202

# Endpoint to process vendor input from client-side speech recognition
@app.route('/process_vendor', methods=['POST'])
def process_vendor():
    vendor_text = request.json.get('vendor')
    vendors, _, _ = load_data()
    df_vendors = pd.DataFrame(vendors)
    if not df_vendors.empty:
        df_vendors["Cleaned_Name"] = df_vendors["vendor"].apply(lambda x: voiceInventory.re.sub(r'[^a-zA-Z0-9\s+.]', '', voiceInventory.unidecode(str(x).strip().lower())).replace("  ", " "))
        matched_vendor = voiceInventory.match_text('vendors', vendor_text, df_vendors)
        if matched_vendor:
            return jsonify({'message': 'Vendor matched', 'vendor': matched_vendor, 'beep': 'correct', 'next': 'material'})
        return jsonify({'message': 'Vendor not found', 'beep': 'invalid', 'next': 'vendor'})
    return jsonify({'message': 'No vendors available', 'beep': 'invalid', 'next': 'vendor'})

# Endpoint to process material input from client-side speech recognition
@app.route('/process_material', methods=['POST'])
def process_material():
    material_text = request.json.get('material')
    vendor = request.json.get('vendor')
    _, materials, _ = load_data()
    df_items = pd.DataFrame(materials)
    if not df_items.empty:
        df_items["Cleaned_Name"] = df_items["material"].apply(lambda x: voiceInventory.re.sub(r'[^a-zA-Z0-9\s+x+.]', '', voiceInventory.unidecode(str(x).strip().lower())).replace("  ", " "))
        matched_material = voiceInventory.match_text('materials', material_text, df_items)
        if matched_material:
            return jsonify({'message': 'Material matched', 'vendor': vendor, 'material': matched_material, 'beep': 'correct', 'next': 'quantity'})
        return jsonify({'message': 'Material not found', 'beep': 'invalid', 'next': 'material'})
    return jsonify({'message': 'No materials available', 'beep': 'invalid', 'next': 'material'})

# Endpoint to process quantity input from client-side speech recognition
@app.route('/process_quantity', methods=['POST'])
def process_quantity():
    quantity_text = request.json.get('quantity')
    vendor = request.json.get('vendor')
    material = request.json.get('material')
    session_type = request.json.get('session')
    _, _, units = load_data()
    df_units = pd.DataFrame(units)
    
    text_split = quantity_text.split()
    quantity = voiceInventory.re.findall(r'\d+', text_split[0])
    
    if len(text_split) > 1 and not df_units.empty:
        df_units["Cleaned_Name"] = df_units["unit"].apply(lambda x: voiceInventory.re.sub(r'[^a-zA-Z0-9\s+x+.]', '', voiceInventory.unidecode(str(x).strip().lower())).replace("  ", " "))
        unit = voiceInventory.match_text('units', text_split[1], df_units)
    else:
        unit = 'undefined'

    if quantity:
        try:
            entry = [
                voiceInventory.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                vendor,
                material,
                quantity[0],
                unit,
                session_type
            ]
            voiceInventory.entry.append(entry)
            return jsonify({'message': 'Item added', 'entry': entry, 'beep': 'item_added'})
        except ValueError:
            return jsonify({'message': 'Invalid quantity', 'beep': 'invalid', 'next': 'quantity'})
    return jsonify({'message': 'No quantity detected', 'beep': 'invalid', 'next': 'quantity'})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')
@app.route('/debug_json/<filename>', methods=['GET'])
def debug_json(filename):
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
        return jsonify({'filename': filename, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT from environment, default to 5000 locally
    app.run(debug=True, host='0.0.0.0', port=port)


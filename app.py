import os
import json
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
import voiceInventory
from voiceInventory import excel_2JSON, start_session, stop_session, active_session, clear_entry, delete_entry

DATA_DIR = '/opt/render/project/data'
app = Flask(__name__)

@app.route('/')
def home():
    if os.path.exists('index.html'):
        return send_from_directory(os.getcwd(), 'index.html')
    else:
        return jsonify({'error': 'index.html not found'}), 404

def load_data():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        vendors_file = os.path.join(DATA_DIR, 'vendors.json')
        if not os.path.exists(vendors_file):
            with open(vendors_file, 'w') as f:
                json.dump([], f)
        materials_file = os.path.join(DATA_DIR, 'materials.json')
        if not os.path.exists(materials_file):
            with open(materials_file, 'w') as f:
                json.dump([], f)
        units_file = os.path.join(DATA_DIR, 'units.json')
        if not os.path.exists(units_file):
            with open(units_file, 'w') as f:
                json.dump([], f)
        with open(vendors_file) as f:
            vendors = json.load(f)
        with open(materials_file) as f:
            materials = json.load(f)
        with open(units_file) as f:
            units = json.load(f)
        return vendors, materials, units
    except Exception as e:
        print(f"Error loading data: {e}")
        return [], [], []

@app.route('/data', methods=['GET'])
def get_data():
    vendors, materials, units = load_data()
    return jsonify({'vendors': vendors, 'materials': materials, 'units': units})

@app.route('/get_vendors', methods=['GET'])
def get_vendors():
    vendors, _, _ = load_data()
    return jsonify({'vendors': vendors})

@app.route('/get_materials', methods=['GET'])
def get_materials():
    _, materials, _ = load_data()
    return jsonify({'materials': materials})

@app.route('/get_units', methods=['GET'])
def get_units():
    _, _, units = load_data()
    return jsonify({'units': units})

@app.route('/add_vendor', methods=['POST'])
def add_vendor():
    new_vendor = request.json.get('vendor')
    if new_vendor:
        result = voiceInventory.add_vendor(new_vendor)
        return jsonify(json.loads(result)), 201
    return jsonify({'error': 'Vendor name is required!'}), 400

@app.route('/add_material', methods=['POST'])
def add_material():
    new_material = request.json.get('material')
    new_unit = request.json.get('unit', 'undefined')
    if new_material:
        result = voiceInventory.add_materialUnit(new_material, new_unit)
        return jsonify(json.loads(result)), 201
    return jsonify({'error': 'Material name is required!'}), 400

@app.route('/add_unit', methods=['POST'])
def add_unit():
    new_unit = request.json.get('unit')
    if new_unit:
        result = voiceInventory.add_unit(new_unit)
        return jsonify(json.loads(result)), 201
    return jsonify({'error': 'Unit name is required!'}), 400

@app.route('/delete_vendor', methods=['POST'])
def delete_vendor():
    vendor_to_delete = request.json.get('vendor')
    if vendor_to_delete:
        result = voiceInventory.delete_vendor(vendor_to_delete)
        return jsonify(json.loads(result)), 200
    return jsonify({'success': False, 'message': 'Vendor not found!'}), 404

@app.route('/delete_material', methods=['POST'])
def delete_material():
    material_to_delete = request.json.get('material')
    if material_to_delete:
        result = voiceInventory.delete_material(material_to_delete)
        return jsonify(json.loads(result)), 200
    return jsonify({'success': False, 'message': 'Material not found!'}), 404

@app.route('/delete_unit', methods=['POST'])
def delete_unit():
    unit_to_delete = request.json.get('unit')
    if unit_to_delete:
        result = voiceInventory.delete_unit(unit_to_delete)
        return jsonify(json.loads(result)), 200
    return jsonify({'success': False, 'message': 'Unit not found!'}), 404

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
        temp_path = os.path.join(DATA_DIR, file.filename)
        file.save(temp_path)
        voiceInventory.excel_2JSON(temp_path, os.path.join(DATA_DIR, output_file), *columns)
        os.remove(temp_path)
        return jsonify({'message': f'Successfully converted {file.filename} to {output_file}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/export_entries', methods=['POST'])
def export_entries():
    file_name = request.json.get('filename')
    format_type = request.json.get('format')
    voiceInventory.export_inventory(file_name, format_type)
    return jsonify({'success': True, 'message': 'File successfully created.', 'filename': f"{file_name}.{format_type.lower()}"}), 200

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DATA_DIR, filename, as_attachment=True)

@app.route('/clear_entries', methods=['POST'])
def clear_entries():
    filename = request.json.get('filename')
    voiceInventory.empty_jsonFile(os.path.join(DATA_DIR, filename))
    return jsonify({'message': 'JSON cleared'}), 200

@app.route('/remove_entry', methods=['POST'])
def remove_entry():
    entry2delete = request.json.get('entry')
    voiceInventory.delete_entry(json.dumps(entry2delete))
    return jsonify({'message': 'Entry deleted'}), 200

@app.route('/session_status', methods=['GET'])
def session_status():
    result = voiceInventory.active_session()
    return result

@app.route('/session_complete', methods=['POST'])
def session_complete():
    return jsonify({'message': 'Session completed', 'entry': voiceInventory.clear_entry()})

@app.route('/start_listening', methods=['POST'])
def start_listening():
    data = request.json
    for session in data:
        result = voiceInventory.start_session(data[session])
    return jsonify({'message': result, 'beep': 'supplier'}), 202

@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    data = request.json
    for session in data:
        result = voiceInventory.stop_session(data[session])
    return jsonify({'message': result}), 202

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
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
from flask import Flask, jsonify, request, send_from_directory
import json
import os
import voiceInventory

from voiceInventory import excel_2JSON, start_session, stop_session, active_session, clear_entry, delete_entry
from voiceInventory import *

app = Flask(__name__)


@app.route('/')
def home():
    return send_from_directory(os.getcwd(), 'index.html')


# Load vendors and materials from JSON files
def load_data():
    with open('vendors.json') as vendors_file:
        vendors = json.load(vendors_file)
    with open('materials.json') as materials_file:
        materials = json.load(materials_file)
    with open('units.json') as units_file:
        units = json.load(units_file)
    return vendors, materials, units


# Endpoint to get vendors and materials
@app.route('/data', methods=['GET'])
def get_data():
    vendors, materials, units = load_data()
    return jsonify({'vendors': vendors, 'materials': materials, 'units': units})


# Endpoint to get vendors
@app.route('/get_vendors', methods=['GET'])
def get_vendors():
    with open('vendors.json') as vendors_file:
        vendors = json.load(vendors_file)
    return jsonify({'vendors': vendors})


# Endpoint to get materials
@app.route('/get_materials', methods=['GET'])
def get_materials():
    with open('materials.json') as materials_file:
        materials = json.load(materials_file)
        print(materials)
    return jsonify({'materials': materials})


# Endpoint to add a new vendor
@app.route('/add_vendor', methods=['POST'])
def add_vendor():
    new_vendor = request.json.get('vendor')
    if new_vendor:
        vendors, materials, units = load_data()
        vendors.append({'vendor': new_vendor})  # Assuming vendor is a dictionary
        with open('vendors.json', 'w') as vendors_file:
            json.dump(vendors, vendors_file)
        return jsonify({'message': 'Vendor added successfully!'}), 201
    return jsonify({'error': 'Vendor name is required!'}), 400


# Endpoint to add a new material
@app.route('/add_material', methods=['POST'])
def add_material():
    new_material = request.json.get('material')
    new_unit = request.json.get('unit')
    print(new_material, new_unit)
    if new_material:
        vendors, materials, units = load_data()
        materials.append({'material': new_material})
        units.append({'unit': new_unit}) 
        with open('materials.json', 'w') as materials_file:
            json.dump(materials, materials_file)
        with open('units.json', 'w') as units_file:
            json.dump(units, units_file)
        return jsonify({'message': 'Material with unit added successfully!'}), 201
    return jsonify({'error': 'Material name is required!'}), 400


@app.route('/delete_vendor', methods=['POST'])
def delete_vendor():
    vendor_to_delete = request.json.get('vendor')
    if vendor_to_delete:
        vendors, materials, units = load_data()
        vendors = [vendor for vendor in vendors if vendor['vendor'] != vendor_to_delete]
        with open('vendors.json', 'w') as vendors_file:
            json.dump(vendors, vendors_file)
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': 'Vendor not found!'}), 404


@app.route('/delete_material', methods=['POST'])
def delete_material():
    material_to_delete = request.json.get('material')
    if material_to_delete:
        vendors, materials, units = load_data()
        materials = [material for material in materials if material['material'] != material_to_delete]
        with open('materials.json', 'w') as materials_file:
            json.dump(materials, materials_file)
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': 'Material not found!'}), 404


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
        temp_path = os.path.join(os.getcwd(), file.filename)
        file.save(temp_path)
        
        # Call excel_2json from voiceInventory1.py
        voiceInventory.excel_2JSON(temp_path, output_file, *columns)
        
        # Remove the temporary file
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
            save_2json(item[5], [item])
        return jsonify({'message': 'Inventory saved successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/export_entries', methods=['POST'])
def export_entries():
    file_name = request.json.get('filename')
    format = request.json.get('format')
    export_inventory(file_name, format)
    return jsonify({'success': True, 'message': 'File successfully created.'}), 200


@app.route('/clear_entries', methods=['POST'])
def clear_entries():
    filename = request.json.get('filename')
    empty_jsonFile(filename)
    return jsonify({'message': 'JSON cleared'}), 200


@app.route('/remove_entry', methods=['POST'])
def remove_entry():
    entry2delete = request.json.get('entry')
    delete_entry(json.dumps(entry2delete))
    return jsonify({'message': 'Entry deleted'}), 200


@app.route('/session_status', methods=['GET'])
def session_status():
    result = active_session()
    print('Result:', result)
    return result


@app.route('/session_complete', methods=['POST'])
def session_complete():
    return(clear_entry())


@app.route('/start_listening', methods=['POST'])
def start_listening():
    data = request.json  # Get data from request
    # Process data
    for session in data:
        result = start_session(data[session])
    
    return jsonify({'message': result}), 202


@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    data = request.json  # Get data from request
    # Process data
    for session in data:
        result = stop_session(data[session])

    return jsonify({'message': result}), 202
    

# if __name__ == '__main__':

#     app.run(debug=True)

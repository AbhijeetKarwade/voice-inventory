import json
import pandas as pd
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt
from pandas.plotting import table
from datetime import datetime
import re
from unidecode import unidecode
from fuzzywuzzy import fuzz, process
import os

DATA_DIR = '/opt/render/project/data'
entry = []
stop_session_flag = False
session_active = False

def active_session():
    global session_active
    global entry
    if entry:
        dt = datetime.strptime(entry[0][0], "%Y-%m-%d %H:%M:%S")
        entry[0][0] = dt.strftime("%H:%M:%S")
    return json.dumps({'active': session_active, 'entry': entry})

def clear_entry():
    global entry
    entry = []
    return entry

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

def get_data():
    vendors, materials, units = load_data()
    return json.dumps({'vendors': vendors, 'materials': materials, 'units': units})

def get_vendors():
    vendors, _, _ = load_data()
    return json.dumps({'vendors': vendors})

def get_materials():
    _, materials, _ = load_data()
    return json.dumps({'materials': materials})

def get_units():
    _, _, units = load_data()
    return json.dumps({'units': units})

def add_vendor(new_vendor):
    vendors_data = get_vendors()
    vendors = json.loads(vendors_data)
    for vendor in vendors['vendors']:
        if vendor['vendor'] == new_vendor:
            return json.dumps({'message': 'Vendor already exists!'})
    vendors['vendors'].append({'vendor': new_vendor})
    with open(os.path.join(DATA_DIR, 'vendors.json'), 'w') as vendors_file:
        json.dump(vendors['vendors'], vendors_file, indent=4)
    return json.dumps({'message': 'Vendor added successfully!'})

def add_material(new_material):
    materials_data = get_materials()
    materials = json.loads(materials_data)
    for material in materials['materials']:
        if material['material'] == new_material:
            return json.dumps({'message': 'Material already exists!'})
    materials['materials'].append({'material': new_material})
    with open(os.path.join(DATA_DIR, 'materials.json'), 'w') as materials_file:
        json.dump(materials['materials'], materials_file, indent=4)
    return json.dumps({'message': 'Material added successfully!'})

def add_materialUnit(new_material, new_unit):
    unitsFlag = False
    materials_data = get_materials()
    materials = json.loads(materials_data)
    units_data = get_units()
    units = json.loads(units_data)
    for material in materials['materials']:
        if material['material'] == new_material:
            return json.dumps({'message': 'Material already exists!'})
    for unit in units['units']:
        if unit['unit'] == new_unit:
            unitsFlag = True
            break
    materials['materials'].append({'material': new_material, 'unit': new_unit})
    with open(os.path.join(DATA_DIR, 'materials.json'), 'w') as materials_file:
        json.dump(materials['materials'], materials_file, indent=4)
    if not unitsFlag:
        units['units'].append({'unit': new_unit})
        with open(os.path.join(DATA_DIR, 'units.json'), 'w') as units_file:
            json.dump(units['units'], units_file, indent=4)
    return json.dumps({'message': 'Material added successfully!'})

def add_unit(new_unit):
    units_data = get_units()
    units = json.loads(units_data)
    for unit in units['units']:
        if unit['unit'] == new_unit:
            return json.dumps({'message': 'Unit already exists!'})
    units['units'].append({'unit': new_unit})
    with open(os.path.join(DATA_DIR, 'units.json'), 'w') as units_file:
        json.dump(units['units'], units_file, indent=4)
    return json.dumps({'message': 'Unit added successfully!'})

def delete_vendor(vendor_to_delete):
    vendors_data = get_vendors()
    vendors = json.loads(vendors_data)
    for vendor in vendors['vendors']:
        if vendor['vendor'] == vendor_to_delete:
            vendors['vendors'] = [u for u in vendors['vendors'] if u['vendor'] != vendor_to_delete]
            with open(os.path.join(DATA_DIR, 'vendors.json'), 'w') as vendors_file:
                json.dump(vendors['vendors'], vendors_file, indent=4)
            return json.dumps({'message': 'Vendor deleted successfully!'})
    return json.dumps({'message': 'Vendor not found!'})

def delete_material(material_to_delete):
    materials_data = get_materials()
    materials = json.loads(materials_data)
    for material in materials['materials']:
        if material['material'] == material_to_delete:
            materials['materials'] = [u for u in materials['materials'] if u['material'] != material_to_delete]
            with open(os.path.join(DATA_DIR, 'materials.json'), 'w') as materials_file:
                json.dump(materials['materials'], materials_file, indent=4)
            return json.dumps({'message': 'Material deleted successfully!'})
    return json.dumps({'message': 'Material not found!'})

def delete_unit(unit_to_delete):
    units_data = get_units()
    units = json.loads(units_data)
    for unit in units['units']:
        if unit['unit'] == unit_to_delete:
            units['units'] = [u for u in units['units'] if u['unit'] != unit_to_delete]
            with open(os.path.join(DATA_DIR, 'units.json'), 'w') as units_file:
                json.dump(units['units'], units_file, indent=4)
            return json.dumps({'message': 'Unit deleted successfully!'})
    return json.dumps({'message': 'Unit not found!'})

def retrieve_inventory():
    json_file = os.path.join(DATA_DIR, 'inventory.json')
    try:
        with open(json_file, 'r') as file:
            data = file.read()
        return data
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {json_file} is not a valid JSON file.")
        return None

def delete_entry(entry2delete):
    json_file = os.path.join(DATA_DIR, 'inventory.json')
    try:
        with open(json_file, 'r') as file:
            data = file.read()
        data = json.loads(data.lower())
        entry2delete = json.loads(entry2delete.lower())
        new_inventory = [inv for inv in data if inv != entry2delete]
        with open(json_file, 'w') as f:
            json.dump(new_inventory, f, indent=4)
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {json_file} is not a valid JSON file.")
        return None

def export_inventory(file_name, format_type):
    json_file = os.path.join(DATA_DIR, 'inventory.json')
    output_file = os.path.join(DATA_DIR, file_name.split()[0])
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        if format_type.lower() == 'csv':
            df = pd.DataFrame(data)
            df.to_csv(f"{output_file}.csv", index=False)
            print(f"Data has been converted to CSV and saved as {output_file}.csv")
        elif format_type.lower() == 'excel':
            df = pd.DataFrame(data)
            df.to_excel(f"{output_file}.xlsx", index=False)
            print(f"Data has been converted to Excel and saved as {output_file}.xlsx")
        elif format_type.lower() == 'pdf':
            df = pd.DataFrame(data)
            fig, ax = plt.subplots(figsize=(12, len(df)*0.5 + 1))
            ax.axis('off')
            tbl = table(ax, df, loc='center', cellLoc='center')
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(10)
            tbl.scale(1, 1.5)
            plt.savefig(f"{output_file}.pdf", bbox_inches='tight')
            plt.close()
            print(f"Data has been converted to PDF and saved as {output_file}.pdf")
        else:
            print("Unsupported format type. Please choose 'csv', 'excel', or 'pdf'.")
    except json.JSONDecodeError:
        print(f"Error: The file {json_file} contains invalid JSON.")
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def empty_jsonFile(file_name):
    try:
        with open(file_name, 'w') as file:
            file.write('[]')
        return json.dumps({'message': f'The file {file_name} has been cleared.'})
    except Exception as e:
        print(f"An error occurred while clearing the file {file_name}: {e}")
        return json.dumps({'message': f'An error occurred while clearing the file {file_name}: {e}'})

def excel_2JSON(file_name, output_file, *columns):
    try:
        xls = pd.ExcelFile(file_name)
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return
    all_data = []
    for sheet_name in xls.sheet_names:
        print(f"Sheet: {sheet_name}")
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            cols_present = df.columns.tolist()
            cols_to_read = [col for col in columns if col in cols_present]
            if cols_to_read:
                selected_df = df[cols_to_read].dropna(how='all')
                selected_df = selected_df[~(selected_df.map(lambda x: isinstance(x, str) and x.strip() == '').all(axis=1))]
                if selected_df.empty:
                    print(f"No data found in columns {cols_to_read} after removing blank rows.")
                else:
                    selected_df = selected_df.map(lambda x: x.lower() if isinstance(x, str) else x)
                    all_data.extend(selected_df.to_dict(orient='records'))
            else:
                print(f"None of the specified columns {columns} found in this sheet.")
        except Exception as e:
            print(f"Error processing sheet '{sheet_name}': {e}")
    xls.close()
    base_name = os.path.basename(output_file).lower()
    if base_name == 'vendors.json':
        key_mapping = {columns[0]: 'vendor'}
    elif base_name == 'materials.json':
        key_mapping = {columns[0]: 'material'}
    elif base_name == 'units.json':
        key_mapping = {columns[0]: 'unit'}
    else:
        key_mapping = {col: col for col in columns}
    renamed_data = []
    for item in all_data:
        new_item = {}
        for orig_key, new_key in key_mapping.items():
            if orig_key in item:
                new_item[new_key] = item[orig_key]
        if new_item:
            renamed_data.append(new_item)
    print(f"Collected data: {renamed_data}")
    try:
        with open(output_file, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
    if base_name == 'vendors.json':
        if not isinstance(existing_data, list):
            existing_data = []
        for item in renamed_data:
            if 'vendor' in item:
                if not any(d['vendor'] == item['vendor'] for d in existing_data):
                    existing_data.append(item)
    elif base_name == 'materials.json':
        if not isinstance(existing_data, list):
            existing_data = []
        for item in renamed_data:
            if 'material' in item:
                if not any(d['material'] == item['material'] for d in existing_data):
                    existing_data.append(item)
    elif base_name == 'units.json':
        if not isinstance(existing_data, list):
            existing_data = []
        for item in renamed_data:
            if 'unit' in item:
                if not any(d['unit'] == item['unit'] for d in existing_data):
                    existing_data.append(item)
    else:
        if not isinstance(existing_data, list):
            existing_data = []
        existing_data.extend(renamed_data)
    if base_name == 'vendors.json':
        unique_data = []
        seen_vendors = set()
        for item in existing_data:
            if 'vendor' in item and item['vendor'] not in seen_vendors:
                seen_vendors.add(item['vendor'])
                unique_data.append(item)
        existing_data = unique_data
    elif base_name == 'materials.json':
        unique_data = []
        seen_pairs = set()
        for item in existing_data:
            if 'material' in item:
                pair = item['material']
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    unique_data.append(item)
        existing_data = unique_data
    elif base_name == 'units.json':
        unique_data = []
        seen_pairs = set()
        for item in existing_data:
            if 'unit' in item:
                pair = item['unit']
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    unique_data.append(item)
        existing_data = unique_data
    with open(output_file, 'w') as f:
        json.dump(existing_data, f, indent=4)

def save_2json(sessionType, data, filename="inventory.json"):
    filepath = os.path.join(DATA_DIR, filename)
    json_data = [
        {
            "Date": item[0],
            "Vendor": item[1],
            "Item": item[2],
            "Quantity": item[3],
            "Unit": item[4],
            "Session": sessionType
        } for item in data
    ]
    if not os.path.exists(filepath):
        with open(filepath, 'w') as file:
            json.dump([], file)
    with open(filepath, mode="r", encoding='utf-8') as file:
        try:
            existing_data = json.load(file)
        except json.JSONDecodeError:
            existing_data = []
    json_data = existing_data + json_data
    with open(filepath, mode="w", encoding='utf-8') as file:
        json.dump(json_data, file, indent=4)
    print(f"Saved to: {filepath}")

def match_item(item_name, df_items, threshold=70):
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s+.]', '', unidecode(item_name.strip().lower())).replace("  ", " ")
    best_match = process.extractOne(cleaned_input, df_items["Cleaned_Name"], scorer=fuzz.token_sort_ratio)
    if best_match and best_match[1] >= threshold:
        row = df_items[df_items["Cleaned_Name"] == best_match[0]].iloc[0]
        return row["material"], row["unit"]
    return None, None

def get_item_quantity(text):
    text = unidecode(text.lower())
    pattern = r'([a-zA-Z0-9\s\.\*x+]+?)(?:quantity\s*|qnty\s*|qty\s*)(\d+)(?=\s*[a-zA-Z0-9\s\.\*x+]*?(?:quantity\s*|qnty\s*|qty\s*)|$|\s*$)'
    matches = re.findall(pattern, text)
    return [(match[0].strip(), int(match[1])) for match in matches] if matches else None

def match_vendor(vendor_name, df_vendors, threshold=70):
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s+.]', '', unidecode(vendor_name.strip().lower())).replace("  ", " ")
    best_match = process.extractOne(cleaned_input, df_vendors["Cleaned_Name"], scorer=fuzz.token_sort_ratio)
    return df_vendors[df_vendors["Cleaned_Name"] == best_match[0]].iloc[0]["vendor"] if best_match and best_match[1] >= threshold else None

def match_text(match_type, input_text, df_type, threshold=60):
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s+.]', '', unidecode(input_text.strip().lower())).replace("  ", " ")
    best_match = process.extractOne(cleaned_input, df_type["Cleaned_Name"], scorer=fuzz.token_sort_ratio)
    if match_type == 'vendors':
        return df_type[df_type["Cleaned_Name"] == best_match[0]].iloc[0]["vendor"] if best_match and best_match[1] >= threshold else None
    elif match_type == 'materials':
        return df_type[df_type["Cleaned_Name"] == best_match[0]].iloc[0]["material"] if best_match and best_match[1] >= threshold else None
    elif match_type == 'units':
        return df_type[df_type["Cleaned_Name"] == best_match[0]].iloc[0]["unit"] if best_match and best_match[1] >= threshold else None

def load_json(file_name):
    base_name = os.path.basename(file_name).lower()
    with open(file_name, mode="r", encoding='utf-8') as file:
        json_data = json.load(file)
    if base_name == 'vendors.json':
        if isinstance(json_data, list):
            df = pd.DataFrame(json_data)
        else:
            if "vendors" not in json_data:
                raise ValueError("JSON file must contain a 'vendors' key")
            df = pd.DataFrame(json_data["vendors"])
        if "vendor" not in df.columns:
            raise ValueError("JSON file must contain 'vendor' column")
        df = df.dropna(subset=["vendor"])
        df["Cleaned_Name"] = df["vendor"].apply(lambda x: 
            re.sub(r'[^a-zA-Z0-9\s+.]', '', unidecode(str(x).strip().lower())).replace("  ", " "))
        return df
    elif base_name == 'materials.json':
        df = pd.DataFrame(json_data)
        if "material" not in df.columns:
            raise ValueError("JSON file must contain 'material' column")
        df = df.dropna(subset=["material"])
        df["Cleaned_Name"] = df["material"].apply(lambda x: 
            re.sub(r'[^a-zA-Z0-9\s+x+.]', '', unidecode(str(x).strip().lower())).replace("  ", " "))
        return df
    elif base_name == 'units.json':
        df = pd.DataFrame(json_data)
        if "unit" not in df.columns:
            raise ValueError("JSON file must contain 'unit' column")
        df = df.dropna(subset=["unit"])
        df["Cleaned_Name"] = df["unit"].apply(lambda x: 
            re.sub(r'[^a-zA-Z0-9\s+x+.]', '', unidecode(str(x).strip().lower())).replace("  ", " "))
        return df
    else:
        raise ValueError(f"Unsupported file: {file_name}. Expected 'materials.json' or 'vendors.json' or units.json")

def start_session(sessionType):
    global session_active
    if sessionType == 'inward':
        session_active = True
        return "Started inward entry"
    elif sessionType == 'outward':
        session_active = True
        return 'Started outward entry'
    return "Invalid session type"

def stop_session(sessionType):
    global session_active
    global stop_session_flag
    if sessionType == 'inward':
        session_active = False
        stop_session_flag = True
        return "Stopped inward entry"
    elif sessionType == 'outward':
        session_active = False
        stop_session_flag = True
        return 'Stopped outward entry'
    return "Invalid session type"

def main():
    export_inventory('demo_output', 'pdf')

if __name__ == "__main__":
    main()
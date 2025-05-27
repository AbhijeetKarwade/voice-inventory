import json
import pandas as pd
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt
from pandas.plotting import table
from datetime import datetime
import re
from unidecode import unidecode
from fuzzywuzzy import fuzz, process
import speech_recognition as sr 
import os
import time #28-04 
import platform  #29-04 for beep

entry = []
stop_session_flag = False
session_active = False


# Shares the status of active session
def active_session():
    global session_active
    global entry
    if entry:
        print(entry[0])
        dt = datetime.strptime(entry[0][0], "%Y-%m-%d %H:%M:%S")
        # entry[0][0] = dt.strftime("%H:%M:%S")
    return json.dumps({'active': session_active, 'entry': entry})


# Clears entries of active session
def clear_entry():
    global entry
    entry = []
    return entry


# Load vendors, materials and units from JSON files
def load_data():
    with open('vendors.json') as vendors_file:
        vendors = json.load(vendors_file)
    with open('materials.json') as materials_file:
        materials = json.load(materials_file)
    with open('units.json') as units_file:
        units = json.load(units_file)
    return vendors, materials, units


# Load vendors, materials and units from JSON files
def get_data():
    vendors, materials, units = load_data()
    return json.dumps({'vendors': vendors, 'materials': materials, 'units': units})


# Load vendors from JSON file
def get_vendors():
    with open('vendors.json') as vendors_file:
        vendors = json.load(vendors_file)
    return json.dumps({'vendors': vendors})


# Load materials from JSON files
def get_materials():
    with open('materials.json') as materials_file:
        materials = json.load(materials_file)
    return json.dumps({'materials': materials})


# Load units from JSON files
def get_units():
    with open('units.json') as units_file:
        units = json.load(units_file)
    return json.dumps({'units': units})


# Endpoint to add a new vendor
def add_vendor(new_vendor):
    vendors_data = get_vendors()    # Get the JSON string
    vendors = json.loads(vendors_data)  # Convert JSON string back to Python dictionary

    # Check if the new vendor already exists
    for vendor in vendors['vendors']:
        if vendor['vendor'] == new_vendor:
            return json.dumps({'message': 'Vendor already exists!'})

    # Add new vendor    
    vendors['vendors'].append({'vendor': new_vendor})  
    with open('vendors.json', 'w') as vendors_file:
        json.dump(vendors['vendors'], vendors_file)
    return json.dumps({'message': 'Vendor added successfully!'})
        
        
# Endpoint to add a new material
def add_material(new_material):
    materials_data = get_materials()    # Get the JSON string
    materials = json.loads(materials_data)  # Convert JSON string back to Python dictionary

    # Check if the new material already exists
    for material in materials['materials']:
        if material['material'] == new_material:
            return json.dumps({'message': 'Material already exists!'})

    # Add the new material
    materials['materials'].append({'material': new_material}) 
    with open('materials.json', 'w') as materials_file:
        json.dump(materials['materials'], materials_file)
    return json.dumps({'message': 'Material added successfully!'})


# Endpoint to add a new material
def add_materialUnit(new_material, new_unit):
    unitsFlag = False

    materials_data = get_materials()    # Get the JSON string
    materials = json.loads(materials_data)  # Convert JSON string back to Python dictionary

    units_data = get_units()    # Get the JSON string
    units = json.loads(units_data)  # Convert JSON string back to Python dictionary

    # Check if the new material already exists
    for material in materials['materials']:
        if material['material'] == new_material:
            return json.dumps({'message': 'Material already exists!'})

    # Check if the new unit already exists
    for unit in units['units']:
        if unit['unit'] == new_unit:
            unitsFlag = True
            break
        else:
            unitsFlag = False
        
    # Add the new material
    materials['materials'].append({'material': new_material, 'unit': new_unit}) 
    with open('materials.json', 'w') as materials_file:
        json.dump(materials['materials'], materials_file)

    if(unitsFlag == False):
        # Add the new unit
        units['units'].append({'unit': new_unit})  # Assuming unit is a dictionary
        with open('units.json', 'w') as units_file:
            json.dump(units['units'], units_file)

    return json.dumps({'message': 'Material added successfully!'})


# Endpoint to add a new unit
def add_unit(new_unit):
    units_data = get_units()  # Get the JSON string of units
    units = json.loads(units_data)  # Convert JSON string back to Python dictionary

    # Check if the new unit already exists
    for unit in units['units']:
        if unit['unit'] == new_unit:
            return json.dumps({'message': 'Unit already exists!'})
 
    # If not, add the new unit
    units['units'].append({'unit': new_unit})  # Assuming unit is a dictionary
    with open('units.json', 'w') as units_file:
        json.dump(units['units'], units_file)
    return json.dumps({'message': 'Unit added successfully!'})
        
        
# Endpoint to delete a Vendor
def delete_vendor(vendor_to_delete):
    vendors_data = get_vendors()    # Get the JSON string
    vendors = json.loads(vendors_data)  # Convert JSON string back to Python list of dictionaries

    # Check if the vendor exists and remove it
    for vendor in vendors['vendors']:
        if vendor['vendor'] == vendor_to_delete:
            vendors['vendors'] = [u for u in vendors['vendors'] if u['vendor'] != vendor_to_delete]
            with open('vendors.json', 'w') as vendors_file:
                json.dump(vendors['vendors'], vendors_file)
            return json.dumps({'message': 'Vendor deleted successfully!'})
        
    return json.dumps({'message': 'Vendor not found!'})


# Endpoint to delete a Material
def delete_material(material_to_delete):
    materials_data = get_materials()    # Get the JSON string
    materials = json.loads(materials_data)

    # Check if the material exists and remove it
    for material in materials['materials']:
        if material['material'] == material_to_delete:
            materials['materials'] = [u for u in materials['materials'] if u['material'] != material_to_delete] # Remove the material
            with open('materials.json', 'w') as materials_file:
                json.dump(materials['materials'], materials_file)
            return json.dumps({'message': 'Material deleted successfully!'})
    
    return json.dumps({'message': 'Material not found!'})


# Endpoint to delete a Unit
def delete_unit(unit_to_delete):
    units_data = get_units()  # Get the JSON string of units
    units = json.loads(units_data)  # Convert JSON string back to Python dictionary

    # Check if the unit exists and remove it
    for unit in units['units']:
        if unit['unit'] == unit_to_delete:
            units['units'] = [u for u in units['units'] if u['unit'] != unit_to_delete]  # Remove the unit
            with open('units.json', 'w') as units_file:
                json.dump(units['units'], units_file)  # Write updated units back to the file
            return json.dumps({'message': 'Unit deleted successfully!'})

    return json.dumps({'message': 'Unit not found!'})
    
    
# Load a JSON file and return its contents as a JSON string.
def retrieve_inventory():
    json_file = 'inventory.json'
    try:
        with open(json_file, 'r') as file:
            data = file.read()  # Read the file contents as a string
        return data  # Return the JSON string
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {json_file} is not a valid JSON file.")
        return None


# Deletes entry from an inventory.json file.
def delete_entry(entry2delete):
    json_file = 'inventory.json'

    try:
        with open(json_file, 'r') as file:
            data = file.read()              # Read the file contents as a string

        # Convert to json in lowercase
        data = json.loads(data.lower())     
        entry2delete = json.loads(entry2delete.lower())

        # Find and remove the entry.  We create a new list, excluding the entry to delete.
        new_inventory = [inv for inv in data if inv != entry2delete]

        # Write the updated inventory data back to the JSON file.
        with open(json_file, 'w') as f:
            json.dump(new_inventory, f, indent=4)

    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {json_file} is not a valid JSON file.")
        return None
    

# Load a JSON file and return its contents in different formats.
def export_inventory(file_name, format_type):
    json_file = 'inventory.json'
    output_file = file_name.split()
    
    try:
        # Load JSON data
        with open(json_file, 'r') as file:
            data = json.load(file)
        print(data)
        if format_type == 'csv':
            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(data)
            df.to_csv(output_file[0]+".csv", index=False)
            print(f"Data has been converted to CSV and saved as {output_file[0]}")

        elif format_type == 'excel':
            # Convert to DataFrame and save as Excel
            df = pd.DataFrame(data)
            df.to_excel(output_file[0]+'.xlsx', index=False)
            print(f"Data has been converted to Excel and saved as {output_file[0]}")

        elif format_type == 'pdf':
            # Create a PDF document
            # Load JSON data
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Convert JSON data to DataFrame
            df = pd.DataFrame(data)

            # Create a matplotlib figure and axis
            fig, ax = plt.subplots(figsize=(12, len(df)*0.5 + 1))
            ax.axis('off')  # Hide axes

            # Create table plot
            tbl = table(ax, df, loc='center', cellLoc='center')
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(10)
            tbl.scale(1, 1.5)

            # Save the figure as a PDF file
            plt.savefig(output_file[0]+'.pdf', bbox_inches='tight')
            plt.close()
            print(f"Data has been converted to PDF and saved as {output_file[0]}")
        else:
            print("Unsupported format type. Please choose 'csv', 'excel', or 'pdf'.")
    except json.JSONDecodeError:
        print(f"Error: The file {json_file} contains invalid JSON.")
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Clears the contents by emptying the JSON file   21-04-2025
def empty_jsonFile(file_name):
    """Clear the contents of the specified JSON file."""
    try:
        with open(file_name, 'w') as file:
            file.write('[]')  # Write an empty JSON array to the file
        return json.dumps({'message': 'The file {file_name} has been cleared.'})
    except Exception as e:
        print(f"An error occurred while clearing the file {file_name}: {e}")
        return json.dumps({'message': 'An error occurred while clearing the file {file_name}: {e}'})


# Reads excel file's specific column of all tabs and converts it to JSON
def excel_2JSON(file_name, output_file, *columns):
    try:
        # Load the Excel file
        xls = pd.ExcelFile(file_name)
        
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return
    
    all_data = []

    # Iterate over all sheet names
    for sheet_name in xls.sheet_names:
        print(f"Sheet: {sheet_name}")
        try:
            # Read the sheet into a DataFrame
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Check which columns are present
            cols_present = df.columns.tolist()
            cols_to_read = [col for col in columns if col in cols_present]
            
            if cols_to_read:
                # Select the columns and drop rows where all selected columns are NaN or blank
                selected_df = df[cols_to_read].dropna(how='all')
                
                # Remove rows where all values are empty strings or whitespace
                selected_df = selected_df[~(selected_df.map(lambda x: isinstance(x, str) and x.strip() == '').all(axis=1))]
                
                if selected_df.empty:
                    print(f"No data found in columns {cols_to_read} after removing blank rows.")
                else:
                    # Convert all data to lowercase strings
                    selected_df = selected_df.map(lambda x: x.lower() if isinstance(x, str) else x)
                    
                    # Append data to all_data list as dicts
                    all_data.extend(selected_df.to_dict(orient='records'))
            else:
                print(f"None of the specified columns {columns} found in this sheet.")
        except Exception as e:
            print(f"Error processing sheet '{sheet_name}': {e}")

    # Ensure the file is closed.
    xls.close()
    # Determine JSON key(s) based on output_file name
    base_name = os.path.basename(output_file).lower()

    if base_name == 'vendors.json':
        key_mapping = {
            columns[0]: 'vendor',  # Assuming first column corresponds to 'vendor'
        }
    elif base_name == 'materials.json':
        # Define a mapping from original column names to desired keys
        key_mapping = {
            columns[0]: 'material',  # Assuming first column corresponds to 'material'
        }
    elif base_name == 'units.json':
        # Define a mapping from original column names to desired keys
        key_mapping = {
            columns[0]: 'unit',  # Assuming first column corresponds to 'unit'
        }    
    else:
        key_mapping = {col: col for col in columns}  # Default mapping for other files

    renamed_data = []
    for item in all_data:
        new_item = {}
        for orig_key, new_key in key_mapping.items():
            if orig_key in item:
                new_item[new_key] = item[orig_key]
        if new_item:
            renamed_data.append(new_item)

    # After collecting all_data from sheets
    print(f"Collected data: {renamed_data}")

    try:
        with open(output_file, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    if base_name == 'vendors.json':
        # Ensure existing_data is a list of dicts with 'vendor' key
        if not isinstance(existing_data, list):
            existing_data = []
        # Append only entries with 'vendor' key, avoiding duplicates based on 'vendor'
        for item in renamed_data:
            if 'vendor' in item:
                # Check for duplicates based on 'vendor'
                if not any(d['vendor'] == item['vendor'] for d in existing_data):
                    existing_data.append(item)
    elif base_name == 'materials.json':
        # Ensure existing_data is a list of dicts with 'material' 
        if not isinstance(existing_data, list):
            existing_data = []
        # Append only entries with 'material' keys, avoiding duplicates based on 'material'
        for item in renamed_data:
            if 'material' in item:
                # Check for duplicates based on both 'material'
                if not any(d['material'] == item['material'] for d in existing_data): 
                    existing_data.append(item)
    elif base_name == 'units.json':
        # Ensure existing_data is a list of dicts with 'unit'
        if not isinstance(existing_data, list):
            existing_data = []
        # Append only entries with 'unit' keys, avoiding duplicates based on 'unit'
        for item in renamed_data:
            if 'unit' in item:
                # Check for duplicates based on both 'unit'
                if not any(d['unit'] == item['unit'] for d in existing_data):
                    existing_data.append(item)
    else:
        # For other files, append all renamed_data entries without duplicate checking
        if not isinstance(existing_data, list):
            existing_data = []
        existing_data.extend(renamed_data)

    # Remove duplicates for materials.json based on both 'material' and 'unit'
    if base_name == 'vendors.json':
        # Keep the first occurrence of each vendor
        unique_data = []
        seen_vendors = set()
        for item in existing_data:
            if 'vendor' in item and item['vendor'] not in seen_vendors:
                seen_vendors.add(item['vendor'])
                unique_data.append(item)
        existing_data = unique_data
    elif base_name == 'materials.json':
        # Keep the first occurrence of each (material, unit) pair
        unique_data = []
        seen_pairs = set()
        for item in existing_data:
            if 'material' in item :
                pair = item['material']
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    unique_data.append(item)
        existing_data = unique_data
    elif base_name == 'units.json':
        # Keep the first occurrence of each (material, unit) pair
        unique_data = []
        seen_pairs = set()
        for item in existing_data:
            if 'unit' in item:
                pair = item['unit']
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    unique_data.append(item)
        existing_data = unique_data

    # Write back the updated data to the JSON file
    with open(output_file, 'w') as f:
        json.dump(existing_data, f, indent=4)


# Speak chat engine
# def speak(text):
#     engine = pyttsx3.init()
#     engine.setProperty("rate", 150)
#     print(text)
#     engine.say(text)
#     engine.runAndWait()

def speak(text):
    print(f"[Speak disabled] {text}")  # Only log text on Render


# Saves the record to JSON (inventory.json)
def save_2json(sessionType, data, filename="inventory.json"):
    filepath = os.path.abspath(filename)
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
    if os.path.exists(filepath):
        with open(filepath, mode="r", encoding='utf-8') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
        json_data = existing_data + json_data
    with open(filepath, mode="w", encoding='utf-8') as file:
        json.dump(json_data, file, indent=4)
    print(f"✅ Saved to: {filepath}")
    

# Beep sound function for cross-platform compatibility
def play_beep(frequency=1000, duration=200):
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(frequency, duration)
    else:
        # For macOS and Linux, use os.system with appropriate command
        try:
            os.system(f"beep -f {frequency} -l {duration}")
        except:
            # Fallback to simple print if beep command is unavailable
            print("\a")  # ASCII bell character

# Beep patterns for prompts and feedback 29-04
def beep_prompt_supplier():
    play_beep(frequency=800, duration=200)  # Single beep for supplier prompt

def beep_prompt_item():
    play_beep(frequency=800, duration=200)  # Single beeps for item prompt

def beep_prompt_quantity():
    play_beep(frequency=800, duration=200)  # Single beeps for quantity prompt

def beep_invalid_input():
    play_beep(frequency=3000, duration=800)  # Single High beep for invalid input

def beep_item_added():
    play_beep(frequency=1200, duration=200)  # Two high beeps for item added
    time.sleep(0.1)
    play_beep(frequency=1200, duration=200) 


# Compares the text from audio with dataframe of items
def match_item(item_name, df_items, threshold=70):
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s+.]', '', unidecode(item_name.strip().lower())).replace("  ", " ")
    best_match = process.extractOne(cleaned_input, df_items["Cleaned_Name"], scorer=fuzz.token_sort_ratio)
    if best_match and best_match[1] >= threshold:
        row = df_items[df_items["Cleaned_Name"] == best_match[0]].iloc[0]
        return row["material"], row["unit"]
    return None, None
    

# Takes text as an input and returns a item name along with its quantity
def get_item_quantity(text):
    text = unidecode(text.lower())
    pattern = r'([a-zA-Z0-9\s\.\*x+]+?)(?:quantity\s*|qnty\s*|qty\s*)(\d+)(?=\s*[a-zA-Z0-9\s\.\*x+]*?(?:quantity\s*|qnty\s*|qty\s*)|$|\s*$)'
    matches = re.findall(pattern, text)
    return [(match[0].strip(), int(match[1])) for match in matches] if matches else None
    

# Compares the text from audio with dataframe of vendors 
def match_vendor(vendor_name, df_vendors, threshold=70):
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s+.]', '', unidecode(vendor_name.strip().lower())).replace("  ", " ")
    best_match = process.extractOne(cleaned_input, df_vendors["Cleaned_Name"], scorer=fuzz.token_sort_ratio)
    return df_vendors[df_vendors["Cleaned_Name"] == best_match[0]].iloc[0]["vendor"] if best_match and best_match[1] >= threshold else None
    

# Compares the text from audio with dataframes 
def match_text(match_type, input_text, df_type, threshold=60):
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s+.]', '', unidecode(input_text.strip().lower())).replace("  ", " ")
   
    best_match = process.extractOne(cleaned_input, df_type["Cleaned_Name"], scorer=fuzz.token_sort_ratio)
   
    if match_type == 'vendors':
        return df_type[df_type["Cleaned_Name"] == best_match[0]].iloc[0]["vendor"] if best_match and best_match[1] >= threshold else None
    elif match_type == 'materials':
        return df_type[df_type["Cleaned_Name"] == best_match[0]].iloc[0]["material"] if best_match and best_match[1] >= threshold else None
    elif match_type == 'units':
        return df_type[df_type["Cleaned_Name"] == best_match[0]].iloc[0]["unit"] if best_match and best_match[1] >= threshold else None
    

# Converts audio to text. Takes audio as an input and returns text.    
def audio_2text():
    global stop_session_flag
    
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        
        if stop_session_flag:
            stop_session_flag = False
            speak("Session completed.")
            return
        
        print("🎤 Listening...")
        
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language="en-IN").lower()
            print(f"✅ You said: {text}")
            return text
        except sr.WaitTimeoutError:
            print("⏳ No speech detected, listening again...")
        except sr.UnknownValueError:
            print("I could not understand. Please try again.")
        except (sr.RequestError, ConnectionAbortedError, Exception) as e:
            print(f"Error: {str(e)}")
            return None


# Start a new session for a new vendor & materials.
def process_session(sessionType, df_vendors, df_items, df_units):
    global entry
    global stop_session_flag
    global session_active

    entry = []
    count = 0

    # Loop to get vendor name
    while True:
        if stop_session_flag:
            stop_session_flag = False
            speak("Session completed.")
            return
        
        beep_prompt_supplier()
        print('----1----')

        # Call to listen audio & convert to text (Vendor's name)
        input_text = audio_2text()

        if input_text in ["stop", "exit", "done", "close"]:
            session_active = False          
            speak("Session completed.")
            return

        # Compare text from audio with the list of vendors from JSON(Dataframe)
        if not input_text or not (matched_text := match_text('vendors', input_text, df_vendors)):
            play_beep(frequency=2500, duration=800)  # high-pitched beep for incorrect vendor
            count = count+1
            if count>4:
                session_active = False
                count = 0
                print("Exit...")
                return
            continue
        else:
            play_beep(frequency=1000, duration=200)  # Low-pitched beep for correct vendor
            vendor = matched_text
            break
    
    # Loop to get material name
    while vendor:
        if stop_session_flag:
            stop_session_flag = False
            speak("Session completed.")
            return
        
        print('----2----')
        beep_prompt_item()

        # Call to listen audio & convert to text (Material name)
        input_text = audio_2text()

        if input_text in ["stop", "exit", "done", "close"]:
            session_active = False          
            speak("Session completed.")
            return

        if not input_text:
            play_beep(frequency=2500, duration=800)  # High-pitched beep for incorrect item
            count = count+1
            if count>4:
                session_active = False
                count = 0
                return
            continue

        material = match_text('materials', input_text, df_items)

        if not material:
            play_beep(frequency=2500, duration=800)  # High-pitched beep for incorrect item
            count = count+1
            if count>4:
                session_active = False
                count = 0
                return
            continue
        else:
            play_beep(frequency=1000, duration=200)  # low-pitched beep for correct item
            
        
        while material:
            if stop_session_flag:
                stop_session_flag = False
                speak("Session completed.")
                return
            
            print('----3----')
            beep_prompt_item()  

            input_text = audio_2text()

            if input_text in ["stop", "exit", "done", "close"]:
                session_active = False          
                speak("Session completed.")
                return

            if not input_text:
                play_beep(frequency=2500, duration=800)  # High-pitched beep for incorrect item
                count = count+1
                if count>4:
                    session_active = False
                    count = 0
                    return
                continue
            else:
                text_split = input_text.split()
                
                quantity = re.findall(r'\d+', text_split[0])
                # quantity = quantity

#               solve error on quantity speak (09-05-2025***)
                if len(text_split) > 1:
                    unit = match_text('units', text_split[1], df_units)
                else:
                    unit = 'undefined'

                if quantity:                
                    try:
                        entry.append([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            vendor,
                            material,
                            quantity[0],  #09-05-2025 removed array brackets
                            unit,
                            sessionType
                        ])

                        beep_item_added()

                        break
                    except ValueError:
                        beep_invalid_input()
                        continue


# Loads & process the JSON file
def load_json(file_name):

    # Extract the base file name to determine file type 
    base_name = os.path.basename(file_name).lower()

    # Load the JSON file
    with open(file_name, mode="r", encoding='utf-8') as file:
        json_data = json.load(file)

    if base_name == 'vendors.json':
        # Check if json_data is already a list (vendors.json contains a list of vendor dicts)
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
    
    elif base_name == 'materials.json':   #Removed unit column from material (09-05-2025)
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


# Starting point of recording inventories    
def start_inventory(sessionType): 
    print("Loading vendor database...")
    df_vendors = load_json("vendors.json")
    print(f"✅ Loaded {len(df_vendors)} vendors")
    
    print("Loading product database...")
    df_items = load_json("materials.json")    
    print(f"✅ Loaded {len(df_items)} materials")

    print("Loading product database...")
    df_units = load_json("units.json")    
    print(f"✅ Loaded {len(df_units)} units")

    # Audio message at start
    speak("System ready")  
    # Call a new session
    process_session(sessionType, df_vendors, df_items, df_units)


# Stop Inventory 
def stop_inventory(sessionType):
    print("Stop inventory session")
    global stop_session_flag
    stop_session_flag = True


# Endpoint to start/stop of a recording session        
def start_session(sessionType):
    global session_active

    if(sessionType == 'inward'):        
        session_active = True
        # Code for inward session
        start_inventory('inward')
        return("Started inward entry")
    elif(sessionType == 'outward'):
        session_active = True
        # Code for outward session
        start_inventory('outward')
        return('Started outward entry')


# Endpoint to stop the recording session
def stop_session(sessionType):
    global session_active
    if(sessionType == 'inward'):
        session_active = False
        # Code to stop inward entry
        stop_inventory('inward')
        return("Stopped inward entry")
    elif(sessionType == 'outward'):
        session_active = False
        # Code to stop outward entry
        stop_inventory('outward')
        return('Stopped outward entry')


# Main function to start the session
def main():
    # print(get_data())
    # start_inventory('inward')
    # start_inventory('outward')
    # excel_2JSON('OmT ProductItem List.xlsx', 'materials.json', 'Item name*')
    export_inventory('demo_output', 'pdf')

# Run the main function
if __name__ == "__main__":
    main()

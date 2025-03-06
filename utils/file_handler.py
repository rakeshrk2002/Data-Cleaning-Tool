import os
import pandas as pd

def save_uploaded_file(file, id, upload_folder):

     # For saving the uploaded file

    ext = os.path.splitext(file.filename)[1].lower()
    file_path = os.path.join(upload_folder, f'data_{id}{ext}')
    file.save(file_path)
    return file_path

def load_data(id, upload_folder):
    
    # Loading file as a data frame 

    for file_name in os.listdir(upload_folder):
        if file_name.startswith(f"data_{id}"):
            file_path = os.path.join(upload_folder, file_name)
            ext = os.path.splitext(file_name)[1].lower()
            try:
                if ext == '.csv':
                    df = pd.read_csv(file_path)
                elif ext in ['.xls', '.xlsx']:
                    df = pd.read_excel(file_path)
                elif ext == '.json':
                    df = pd.read_json(file_path)
                else:
                    return None, f"Unsupported file format: {ext}"
            except Exception as e:
                return None, f"Error loading file: {e}"
            return df, None
    return None, "File not found"

def get_column_types(df):
    
    # Shows the type of the column in the UI (eg: Age(numerical), Name(Categorical) )

    return {col: 'numerical' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical' for col in df.columns}

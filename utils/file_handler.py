import os
import pandas as pd

def save_uploaded_file(file, id, upload_folder):

     # For saving the uploaded CSV file

    file_path = os.path.join(upload_folder, f'data_{id}.csv')
    file.save(file_path)

    return file_path

def load_csv(id, upload_folder):
    
    # Loading CSV file as a data frame 

    file_path = os.path.join(upload_folder, f'data_{id}.csv')
    if not os.path.exists(file_path):
        return None, "File not found"
    
    df = pd.read_csv(file_path)
    return df, None

def get_column_types(df):
    
    # Shows the type of the column in the UI (eg: Age(numerical), Name(Categorical) )

    return {col: 'numerical' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical' for col in df.columns}

from flask import Flask, request, redirect, url_for, render_template
import os
import uuid
import pandas as pd
from utils.file_handler import save_uploaded_file, load_data, get_column_types
from utils.data_processing import process_dataframe

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Renders the upload page."""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload (CSV, Excel, JSON)."""
    file = request.files.get('file')
    if not file or file.filename == '':
        return "No file selected", 400
    
    # Check for allowed file types
    allowed_extensions = ('.csv', '.xls', '.xlsx', '.json')
    if not file.filename.lower().endswith(allowed_extensions):
        return f"Only CSV, Excel, and JSON files are supported. Provided file: {file.filename}", 400

    id = str(uuid.uuid4())
    file_path = save_uploaded_file(file, id, app.config['UPLOAD_FOLDER'])
    return redirect(url_for('view_data', id=id))

@app.route('/view/<id>')
def view_data(id):
    """Display the uploaded file (CSV, Excel, or JSON) as an HTML table."""
    df, error = load_data(id, app.config['UPLOAD_FOLDER'])
    if error:
        return error, 404
    return render_template('view.html', data=df.to_html(classes='data-table', index=False), id=id)

@app.route('/prepare/<id>')
def prepare_data(id):
    """Render form for data preparation."""
    df, error = load_data(id, app.config['UPLOAD_FOLDER'])
    if error:
        return error, 404
    return render_template(
        'prepare.html',
        columns=df.columns.tolist(),
        col_types=get_column_types(df),
        data=df.to_dict(orient='records'),
        id=id
    )

@app.route('/process/<id>', methods=['POST'])
def process_data(id):
    """Apply selected processing operations on the data"""
    # Load the original file to get column info
    original_df, error = load_data(id, app.config['UPLOAD_FOLDER'])
    if error:
        return error, 404

    edited_data = request.form.get('editedData')
    if edited_data:
        import json
        edited_df = pd.DataFrame(json.loads(edited_data))
        # Convert columns that are originally numeric or that we expect to be numeric
        known_numeric = ['age', 'salary', 'id']  # add other numeric columns if needed
        for col in original_df.columns:
            # Either the original dtype was numeric or the column name is in our list
            if pd.api.types.is_numeric_dtype(original_df[col]) or col.lower() in known_numeric:
                edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce')
        df = edited_df
    else:
        df = original_df

    processed_df, operations = process_dataframe(df, request.form)
    processed_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'prepared_{id}.csv')
    processed_df.to_csv(processed_file_path, index=False)

    return render_template('summary.html', summary={
        'rows': processed_df.shape[0],
        'columns': processed_df.shape[1],
        'operations': operations if operations else ["No operations applied"],
        'preview': processed_df.to_html(classes='data-table')
    }, id=id)


@app.route('/download/<id>')
def download_file(id):
    """Download the processed CSV file."""
    from flask import send_file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'prepared_{id}.csv')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name='prepared_data.csv')
    else:
        return "Prepared file not found", 404

if __name__ == '__main__':
    app.run(debug=True)

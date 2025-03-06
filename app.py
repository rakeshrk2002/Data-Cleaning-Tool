from flask import Flask, request, redirect, url_for, render_template
import os
import uuid
from utils.file_handler import save_uploaded_file, load_csv, get_column_types
from utils.data_processing import process_dataframe

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Render the upload page."""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload."""
    file = request.files.get('file')
    if not file or file.filename == '':
        return "No file selected", 400
    if not file.filename.endswith('.csv'):
        return "Only CSV files are supported", 400

    id = str(uuid.uuid4())
    file_path = save_uploaded_file(file, id, app.config['UPLOAD_FOLDER'])
    return redirect(url_for('view_data', id=id))

@app.route('/view/<id>')
def view_data(id):
    """Display the uploaded CSV file."""
    df, error = load_csv(id, app.config['UPLOAD_FOLDER'])
    if error:
        return error, 404
    return render_template('view.html', data=df.to_html(classes='data-table', index=False), id=id)

@app.route('/prepare/<id>')
def prepare_data(id):
    """Render form for data preparation."""
    df, error = load_csv(id, app.config['UPLOAD_FOLDER'])
    if error:
        return error, 404
    return render_template('prepare.html', columns=df.columns.tolist(), col_types=get_column_types(df), id=id)

@app.route('/process/<id>', methods=['POST'])
def process_data(id):
    """Apply selected processing operations on the data"""
    df, error = load_csv(id, app.config['UPLOAD_FOLDER'])
    if error:
        return error, 404

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
    """Download the processed CSV file"""
    from flask import send_file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'prepared_{id}.csv')
    return send_file(file_path, as_attachment=True, download_name='prepared_data.csv') if os.path.exists(file_path) else ("Prepared file not found", 404)

if __name__ == '__main__':
    app.run(debug=True)

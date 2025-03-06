import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer

# This function helps in processing the data
def process_dataframe(df, form_data):
    operations_applied = []

    # Drops selected columns
    drop_cols = form_data.getlist('drop_cols')
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)
        operations_applied.append(f"Dropped columns: {', '.join(drop_cols)}")

    # Remove duplicates from the selected column 
    if form_data.get('remove_duplicates') == 'on':
        initial_rows = df.shape[0]
        df.drop_duplicates(inplace=True)
        final_rows = df.shape[0]
        operations_applied.append(f"Removed {initial_rows - final_rows} duplicate rows")

    # Determines the column type based on the given dataset
    col_types = {col: 'numerical' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical' for col in df.columns}

    # Handle missing values and encoding based on user inputs
    for col in df.columns:
        missing_method = form_data.get(f'{col}_missing')
        if missing_method and missing_method != 'none':
            if missing_method == 'mean' and col_types[col] == 'numerical':
                df[col].fillna(df[col].mean(), inplace=True)
                operations_applied.append(f"Filled missing values in '{col}' with mean")
            elif missing_method == 'median' and col_types[col] == 'numerical':
                df[col].fillna(df[col].median(), inplace=True)
                operations_applied.append(f"Filled missing values in '{col}' with median")
            elif missing_method == 'mode':
                df[col].fillna(df[col].mode()[0], inplace=True)
                operations_applied.append(f"Filled missing values in '{col}' with mode")
            elif missing_method == 'constant':
                df[col].fillna(form_data.get(f'{col}_constant_value', ''), inplace=True)
                operations_applied.append(f"Filled missing values in '{col}' with a constant value")

        # Advanced Missing Value Handling (KNN & Iterative Imputer)
        advanced_missing = form_data.get(f'{col}_advanced_missing')
        if advanced_missing and advanced_missing != 'none' and col_types[col] == 'numerical':
            if advanced_missing == 'knn':
                imputer = KNNImputer()
                df[[col]] = imputer.fit_transform(df[[col]])
                operations_applied.append(f"Applied KNN Imputer to '{col}'")
            elif advanced_missing == 'iterative':
                imputer = IterativeImputer()
                df[[col]] = imputer.fit_transform(df[[col]])
                operations_applied.append(f"Applied Iterative Imputer to '{col}'")

        # Encoding for categorical columns
        encoding = form_data.get(f'{col}_encoding', 'none')
        if col_types[col] == 'categorical':
            if encoding == 'onehot':
                df = pd.get_dummies(df, columns=[col], prefix=col)
                operations_applied.append(f"One-hot encoded '{col}'")
            elif encoding == 'label':
                label_enc = LabelEncoder()
                df[col] = label_enc.fit_transform(df[col].astype(str))
                operations_applied.append(f"Label encoded '{col}'")

    # Scaling the data 
    scaling = form_data.get('scaling')
    if scaling and scaling != 'none':
        numerical_cols = df.select_dtypes(include=['number']).columns
        if numerical_cols.size > 0:
            scaler = StandardScaler() if scaling == 'standard' else MinMaxScaler()
            df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
            operations_applied.append(f"Applied {scaling} scaling to numerical columns")

    return df, operations_applied

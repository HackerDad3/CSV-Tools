import pandas as pd
import os

def remove_standalone_rows():
    # Get user input for the input CSV file
    input_csv = input("Enter the input CSV file path: ").strip().strip('"')
    
    # Determine output file path in the same directory
    output_csv = os.path.join(os.path.dirname(input_csv), "grouped_documents.csv")
    
    # Try different encoding options to handle potential Unicode issues
    try:
        df = pd.read_csv(input_csv, encoding="utf-8")
    except UnicodeDecodeError:
        print("UTF-8 decoding failed, trying ISO-8859-1...")
        df = pd.read_csv(input_csv, encoding="ISO-8859-1")
    
    # Ensure 'Row #' column is treated as string
    df['Row #'] = df['Row #'].astype(str)
    
    # Extract parent document numbers by splitting at the decimal
    df['Parent'] = df['Row #'].apply(lambda x: x.split('.')[0])
    
    # Identify grouped rows (those that have at least one sibling or child)
    grouped_parents = df['Parent'].value_counts()
    grouped_parents = grouped_parents[grouped_parents > 1].index.tolist()
    
    # Filter out standalone rows
    df_grouped = df[df['Parent'].isin(grouped_parents)].drop(columns=['Parent'])
    
    # Save the filtered data to a new CSV file
    df_grouped.to_csv(output_csv, index=False)
    
    print(f"Grouped documents CSV saved as: {output_csv}")

# Run the function
remove_standalone_rows()

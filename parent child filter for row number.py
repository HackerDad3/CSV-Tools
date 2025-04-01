import os
import pandas as pd

def clean_value(val):
    """
    Remove the braille blank character (U+2800) and any extra whitespace.
    """
    return str(val).replace('\u2800', '').strip()

def is_parent(row_val):
    """
    Determines if a row represents a parent.
    A parent row has a row number that is a whole number.
    """
    try:
        # Clean the row value before conversion
        cleaned = clean_value(row_val)
        return float(cleaned) % 1 == 0
    except Exception as e:
        return False

def main():
    # Prompt for the CSV file path and clean the input
    file_path = input("Enter the path to the CSV file: ").strip().strip('"')
    
    # Read the CSV file and clean up column headers
    df = pd.read_csv(file_path, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    # Verify that the required columns exist
    if "Row #" not in df.columns or "Bates/Control #" not in df.columns:
        print("CSV does not contain the required columns 'Row #' and 'Bates/Control #'.")
        return

    # Clean the values in the key columns
    df["Row #"] = df["Row #"].apply(clean_value)
    df["Bates/Control #"] = df["Bates/Control #"].apply(clean_value)
    
    # Initialize variables for processing
    output_rows = []
    current_parent_bates = None
    children = []
    
    # Iterate over each row; assumes parents come before their children
    for idx, row in df.iterrows():
        row_val = row["Row #"]
        bates = row["Bates/Control #"]
        
        if is_parent(row_val):
            # If there's an existing parent, append its record with concatenated children
            if current_parent_bates is not None:
                children_str = f"({', '.join(children)})" if children else ""
                parent_val = current_parent_bates
                if parent_val.startswith('#'):
                    parent_val = f'"{parent_val}"'
                output_rows.append({
                    "Bates/Control #": parent_val,
                    "Children": children_str
                })
            # Start a new parent record and reset children list
            current_parent_bates = bates
            children = []
        else:
            # This row is a child; add its Bates/Control # to the children list
            children.append(bates)
    
    # Write out the last parent record if one exists
    if current_parent_bates is not None:
        children_str = f"({', '.join(children)})" if children else ""
        parent_val = current_parent_bates
        if parent_val.startswith('#'):
            parent_val = f'"{parent_val}"'
        output_rows.append({
            "Bates/Control #": parent_val,
            "Children": children_str
        })
    
    # Create a DataFrame from the output records and save as CSV in the same directory as the input file
    output_df = pd.DataFrame(output_rows)
    input_dir = os.path.dirname(os.path.abspath(file_path))
    output_file = os.path.join(input_dir, "output.csv")
    output_df.to_csv(output_file, index=False)
    
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()

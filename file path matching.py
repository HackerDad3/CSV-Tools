import pandas as pd

def fill_missing_document_ids(csv1_path, csv2_path, output_csv_path, unmatched_report_path):
    # Read CSV files into DataFrames with specified encoding
    csv1 = pd.read_csv(csv1_path, encoding='latin1')  # Change encoding if needed
    csv2 = pd.read_csv(csv2_path, encoding='latin1')  # Change encoding if needed

    # Ensure column names are consistent and trim whitespace if necessary
    csv1.columns = csv1.columns.str.strip()
    csv2.columns = csv2.columns.str.strip()

    # Track unmatched file paths
    unmatched = []

    # Fill missing Document IDs in CSV1
    for index, row in csv1.iterrows():
        if pd.isna(row['Document id']):  # Check if Document id is missing
            file_path = row['File path']
            # Try to find a match in CSV2
            match = csv2[csv2['Duplicate Path'] == file_path]
            if not match.empty:
                # Assign the Original Bates value to Document id
                csv1.at[index, 'Document id'] = match.iloc[0]['Original Bates']
            else:
                # Add to unmatched list
                unmatched.append({'File path': file_path})

    # Output the updated DataFrame to a new CSV
    csv1[['Document id', 'File path']].to_csv(output_csv_path, index=False)
    print(f"Updated CSV saved to {output_csv_path}")

    # Output unmatched file paths to a report CSV
    if unmatched:
        unmatched_df = pd.DataFrame(unmatched)
        unmatched_df.to_csv(unmatched_report_path, index=False)
        print(f"Unmatched file paths report saved to {unmatched_report_path}")
    else:
        print("All file paths were successfully matched.")

# File paths (replace with your actual file paths)
csv1_path = r"C:\\Users\\Willi\\Downloads\\missing bates.csv"
csv2_path = r"C:\\Users\\Willi\\Downloads\\Duplicate Paths.csv"
output_csv_path = r'C:\\Users\\Willi\\Downloads\\updated_csv1.csv'  # Path for the output CSV
unmatched_report_path = r'C:\\Users\\Willi\\Downloads\\unmatched_report.csv'  # Path for the unmatched report CSV

# Run the function
fill_missing_document_ids(csv1_path, csv2_path, output_csv_path, unmatched_report_path)

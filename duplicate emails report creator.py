#!/usr/bin/env python3
import os
import pandas as pd
from tqdm import tqdm

def main():
    # Prompt the user for the input CSV file path.
    # This also strips any extra spaces and wrapping double quotes.
    input_csv = input("Enter the path to the input CSV file: ").strip().strip('"')
    
    # Verify the file exists.
    if not os.path.exists(input_csv):
        print("Error: The input CSV file does not exist.")
        return

    # Determine the output file path (report.csv in the same directory as the input file).
    input_dir = os.path.dirname(input_csv)
    output_csv = os.path.join(input_dir, "report.csv")
    
    # Read the CSV into a pandas DataFrame.
    try:
        df = pd.read_csv(input_csv, encoding="utf-8-sig")
    except Exception as e:
        print("Error reading the CSV file:", e)
        return

    # Ensure the "Row #" column is a stripped string.
    if "Row #" not in df.columns:
        print("Error: The CSV file does not contain a 'Row #' column.")
        return
    df["Row #"] = df["Row #"].astype(str).str.strip()

    # Identify duplicate rows using string search:
    # A duplicate row is one whose "Row #" field contains a period.
    df["is_dup"] = df["Row #"].str.contains(r'\.')

    # Separate original rows (no period) and duplicate rows (contain a period).
    originals = df[~df["is_dup"]].copy()
    duplicates = df[df["is_dup"]].copy()

    # Build a dictionary mapping from the integer value of the original "Row #"
    # to its corresponding row (as a Series).
    orig_map = {}
    for idx, row in originals.iterrows():
        try:
            # Convert the original row number to an integer.
            key = int(float(row["Row #"]))
            orig_map[key] = row
        except ValueError:
            print(f"Warning: Could not parse original row number '{row['Row #']}'. Skipping this row.")
            continue

    output_rows = []
    # Process each duplicate row with a progress bar.
    for idx, dup in tqdm(duplicates.iterrows(), total=duplicates.shape[0],
                         desc="Processing duplicates", unit="dup"):
        dup_row_str = dup["Row #"]
        try:
            # Extract the integer part of the duplicate row number.
            # For example, if dup_row_str is "2.1", splitting on "." gives "2".
            orig_key = int(dup_row_str.split('.')[0])
        except Exception as e:
            print(f"Error parsing duplicate row number '{dup_row_str}':", e)
            continue

        if orig_key not in orig_map:
            print(f"Warning: Original row for duplicate row '{dup_row_str}' not found.")
            continue

        orig = orig_map[orig_key]
        
        # Build the output row.
        # - "Duplicate Document ID" and "Duplicate Bates #" come from the duplicate row.
        # - "Original Document ID" and "Origianal Bates" come from the original row’s
        #    "Bates/Control #" and "End Bates/Control #" respectively.
        # - The remaining columns (Type, Document ID, etc.) are taken from the original row.
        out_row = {
            "Duplicate Document ID": dup["Document ID"],
            "Duplicate Bates #": dup["Bates/Control #"],
            "Original Document ID": orig["Bates/Control #"],
            "Origianal Bates": orig["End Bates/Control #"],
            "Type": orig["Type"],
            "Document ID": orig["Document ID"],
            "Coded": orig["Coded"],
            "Rating": orig["Rating"],
            "Date": orig["Date"],
            "Title": orig["Title"],
            "From": orig["From"],
            "To": orig["To"],
            "Primary Date": orig["Primary Date"],
            "Redactions": orig["Redactions"]
        }
        output_rows.append(out_row)

    # Define the desired column order for the report.
    report_columns = [
        "Duplicate Document ID",
        "Duplicate Bates #",
        "Original Document ID",
        "Origianal Bates",
        "Type",
        "Document ID",
        "Coded",
        "Rating",
        "Date",
        "Title",
        "From",
        "To",
        "Primary Date",
        "Redactions"
    ]
    report_df = pd.DataFrame(output_rows, columns=report_columns)

    # Write the report CSV in the same directory as the input CSV.
    try:
        report_df.to_csv(output_csv, index=False, encoding="utf-8")
        print(f"Report successfully written to: {output_csv}")
    except Exception as e:
        print("Error writing the report CSV:", e)

if __name__ == "__main__":
    main()

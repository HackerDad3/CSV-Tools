import pandas as pd
import os
from tqdm import tqdm
import unicodedata
import re

def normalize_path(path):
    """Normalize file paths by removing special characters, normalizing Unicode, and stripping whitespace."""
    # Normalize Unicode characters (e.g., convert â€“ to -)
    path = unicodedata.normalize('NFKD', path)
    # Replace special characters with a hyphen or remove them
    path = re.sub(r'[^\w\s./-]', '', path)
    # Convert to lowercase and strip extra whitespace
    path = path.lower().strip()
    return path

def update_document_ids(master_csv, duplicate_report_csv):
    # Read the master CSV file, removing BOM if present
    master_df = pd.read_csv(master_csv, encoding='utf-8-sig', low_memory=False)

    # Normalize column names by stripping whitespace and converting to lowercase
    master_df.columns = master_df.columns.str.strip().str.lower()

    # Check for required columns in the master CSV
    if 'document id' not in master_df.columns or 'file path' not in master_df.columns:
        raise ValueError("Master CSV must contain 'document id' and 'file path' columns.")

    # Read the duplicate report CSV file
    duplicate_df = pd.read_csv(duplicate_report_csv, encoding='utf-8', low_memory=False)

    # Normalize column names in the duplicate report CSV
    duplicate_df.columns = duplicate_df.columns.str.strip().str.lower()

    # Check for required columns in the duplicate report CSV
    if 'original bates' not in duplicate_df.columns or 'duplicate path' not in duplicate_df.columns:
        raise ValueError("Duplicate report CSV must contain 'original bates' and 'duplicate path' columns.")

    # Normalize file paths in both dataframes
    master_df['normalized_path'] = master_df['file path'].apply(normalize_path)
    duplicate_df['normalized_path'] = duplicate_df['duplicate path'].apply(normalize_path)

    # Create a dictionary to map normalized duplicate paths to original Bates numbers
    duplicate_dict = duplicate_df.set_index('normalized_path')['original bates'].to_dict()

    # Prepare a list for unmatched entries
    unmatched = []

    # Update the master DataFrame with a progress bar
    for index, row in tqdm(master_df.iterrows(), total=len(master_df), desc="Processing rows", unit="row"):
        if pd.isna(row['document id']):  # If Document id is blank
            normalized_path = row['normalized_path']
            if normalized_path in duplicate_dict:
                # Update with the corresponding Original Bates
                master_df.at[index, 'document id'] = duplicate_dict[normalized_path]
            else:
                # Add to unmatched list if no match is found
                unmatched.append(row.to_dict())

    # Drop the normalized_path column
    master_df.drop(columns=['normalized_path'], inplace=True)

    # Determine the output directory (same as master CSV)
    output_dir = os.path.dirname(master_csv)

    # Define output file paths
    output_master_csv = os.path.join(output_dir, "updated_master.csv")
    unmatched_report_csv = os.path.join(output_dir, "unmatched_report.csv")

    # Save the updated master DataFrame to a new CSV
    master_df.to_csv(output_master_csv, index=False, encoding='utf-8-sig')
    print(f"Updated master CSV written to {output_master_csv}")

    # Save the unmatched entries to a separate CSV, including all columns from the master CSV
    unmatched_df = pd.DataFrame(unmatched)
    unmatched_df.to_csv(unmatched_report_csv, index=False, encoding='utf-8-sig')
    print(f"Unmatched report CSV written to {unmatched_report_csv}")

if __name__ == "__main__":
    # File paths
    master_csv_path = r"C:\Users\Willi\Downloads\Civmec Report\2025-01-13_08_25_52PM_Upload_details_report_for_20250109_Civmec_Expert_Documents.csv"
    duplicate_report_csv_path = r"C:\Users\Willi\Downloads\Civmec Report\20250109 Civmec Expert Documents-deduped-file-info.csv"

    # Call the function
    update_document_ids(master_csv_path, duplicate_report_csv_path)

import pandas as pd
import os
from tqdm import tqdm

def add_civ_nrt_to_master(master_csv, civ_csv, nrt_csv):
    # Read the master CSV
    master_df = pd.read_csv(master_csv, encoding='utf-8-sig', low_memory=False)

    # Check for required column in the master CSV
    if 'MD5 Hash' not in master_df.columns:
        raise ValueError("Master CSV must contain the 'MD5 Hash' column.")

    # Read the CIV and NRT CSV files
    civ_df = pd.read_csv(civ_csv, encoding='utf-8-sig', low_memory=False)
    nrt_df = pd.read_csv(nrt_csv, encoding='utf-8-sig', low_memory=False)

    # Check for required columns in the CIV and NRT CSVs
    for df, name in [(civ_df, 'CIV CSV'), (nrt_df, 'NRT CSV')]:
        if 'Bates/Control #' not in df.columns or 'MD5 Hash' not in df.columns:
            raise ValueError(f"{name} must contain 'Bates/Control #' and 'MD5 Hash' columns.")

    # Create dictionaries to map MD5 Hash to Bates/Control # for CIV and NRT
    civ_md5_to_bates = civ_df.set_index('MD5 Hash')['Bates/Control #'].to_dict()
    nrt_md5_to_bates = nrt_df.set_index('MD5 Hash')['Bates/Control #'].to_dict()

    # Initialize the new columns in the master DataFrame
    master_df['CIV Number'] = ''
    master_df['NRT Number'] = ''

    # Prepare a list for unmatched MD5 hashes
    unmatched = []

    # Add a progress bar
    tqdm.pandas(desc="Matching MD5 Hashes")

    # Populate the new columns
    for index, row in tqdm(master_df.iterrows(), total=len(master_df), desc="Processing rows", unit="row"):
        md5 = row['MD5 Hash']
        civ_value = civ_md5_to_bates.get(md5, '')
        nrt_value = nrt_md5_to_bates.get(md5, '')
        master_df.at[index, 'CIV Number'] = civ_value
        master_df.at[index, 'NRT Number'] = nrt_value

        # If no match was found in either CSV, add to unmatched
        if not civ_value and not nrt_value:
            unmatched.append(row.to_dict())

    # Determine the output directory (same as master CSV)
    output_dir = os.path.dirname(master_csv)

    # Define the output file paths
    output_master_csv = os.path.join(output_dir, "updated_master_with_civ_nrt.csv")
    unmatched_report_csv = os.path.join(output_dir, "unmatched_md5_report.csv")

    # Save the updated master DataFrame to a new CSV
    master_df.to_csv(output_master_csv, index=False, encoding='utf-8-sig')
    print(f"Updated master CSV written to {output_master_csv}")

    # Save the unmatched entries to a separate CSV
    unmatched_df = pd.DataFrame(unmatched)
    unmatched_df.to_csv(unmatched_report_csv, index=False, encoding='utf-8-sig')
    print(f"Unmatched MD5 report written to {unmatched_report_csv}")

if __name__ == "__main__":
    # File paths (replace with actual paths)
    master_csv_path = r"C:\Users\Willi\Downloads\Civmec Report\updated_master_with_md5.csv"
    civ_csv_path = r"C:\Users\Willi\Downloads\Civmec Report\civmec_md5.csv"
    nrt_csv_path = r"C:\Users\Willi\Downloads\Civmec Report\NRT_MD5_hashes.csv"

    # Call the function
    add_civ_nrt_to_master(master_csv_path, civ_csv_path, nrt_csv_path)

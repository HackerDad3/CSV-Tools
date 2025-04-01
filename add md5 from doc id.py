import pandas as pd
import os
from tqdm import tqdm

def add_md5_to_master(master_csv, bates_csv):
    # Read the master CSV
    master_df = pd.read_csv(master_csv, encoding='utf-8-sig', low_memory=False)

    # Check for required column in the master CSV
    if 'Document id' not in master_df.columns:
        raise ValueError("Master CSV must contain the 'Document id' column.")

    # Read the Bates CSV
    bates_df = pd.read_csv(bates_csv, encoding='utf-8-sig', low_memory=False)

    # Check for required columns in the Bates CSV
    if 'Bates/Control #' not in bates_df.columns or 'MD5 Hash' not in bates_df.columns:
        raise ValueError("Bates CSV must contain 'Bates/Control #' and 'MD5 Hash' columns.")

    # Create a dictionary to map Bates/Control # to MD5 Hash
    bates_to_md5 = bates_df.set_index('Bates/Control #')['MD5 Hash'].to_dict()

    # Initialize the MD5 Hash column in the master DataFrame
    master_df['MD5 Hash'] = ''

    # Add a progress bar
    tqdm.pandas(desc="Matching MD5 Hashes")

    # Populate the MD5 Hash column in the master DataFrame
    master_df['MD5 Hash'] = master_df['Document id'].progress_apply(
        lambda doc_id: bates_to_md5.get(doc_id, '')
    )

    # Determine the output directory (same as master CSV)
    output_dir = os.path.dirname(master_csv)

    # Define the output file path
    output_csv = os.path.join(output_dir, "updated_master_with_md5.csv")

    # Save the updated master DataFrame to a new CSV
    master_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"Updated master CSV written to {output_csv}")

if __name__ == "__main__":
    # File paths (replace with actual paths)
    master_csv_path = r"C:\Users\Willi\Downloads\Civmec Report\updated_master_No MD5.csv"
    bates_csv_path = r"C:\Users\Willi\Downloads\Civmec Report\md5_list.csv"

    # Call the function
    add_md5_to_master(master_csv_path, bates_csv_path)

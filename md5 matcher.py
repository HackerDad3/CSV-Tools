import pandas as pd
from tqdm import tqdm
import os

def match_md5(master_csv, second_csv):
    # Read in the master CSV
    master_df = pd.read_csv(master_csv, encoding='ISO-8859-1')
    
    # Ensure the master file contains the 'MD5 Hash' column
    if 'MD5 Hash' not in master_df.columns:
        raise ValueError("Master CSV does not contain the 'MD5 Hash' column.")

    # Read in the second CSV
    second_df = pd.read_csv(second_csv, encoding='ISO-8859-1')
    
    # Ensure the second file contains the 'MD5 Hash' column
    if 'MD5 Hash' not in second_df.columns:
        raise ValueError("Second CSV does not contain the 'MD5 Hash' column.")

    # Create a set of MD5 hashes from the second CSV for faster lookup
    second_md5_set = set(second_df['MD5 Hash'])

    # Add a new column to the master DataFrame to indicate match status
    match_status = []

    print("Checking for matches...")
    for md5 in tqdm(master_df['MD5 Hash'], desc="Progress", unit="hash"):
        match_status.append(md5 in second_md5_set)

    master_df['Match Found'] = match_status

    # Generate the output file path in the same directory as the master CSV
    master_dir = os.path.dirname(master_csv)
    output_csv = os.path.join(master_dir, "output.csv")

    # Write the output to a new CSV
    master_df.to_csv(output_csv, index=False)
    print(f"Output written to {output_csv}")

if __name__ == "__main__":
    # Replace with your file paths
    master_csv_path = r"C:\Users\Willi\Downloads\master csv.csv"
    second_csv_path = r"C:\Users\Willi\Downloads\review db md5s.csv"

    match_md5(master_csv_path, second_csv_path)

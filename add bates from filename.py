import pandas as pd
import os

def match_filenames(input_csv, master_csv):
    # Read the input CSV containing filenames without extensions
    input_df = pd.read_csv(input_csv, encoding='ISO-8859-1')

    # Check if the required column exists in the input CSV
    if 'Filename' not in input_df.columns:
        raise ValueError("Input CSV does not contain the 'Filename' column.")

    # Read the master CSV containing filenames with extensions and Bates numbers
    master_df = pd.read_csv(master_csv, encoding='ISO-8859-1')

    # Check if the required columns exist in the master CSV
    if 'Filename' not in master_df.columns or 'Bates/Control #' not in master_df.columns:
        raise ValueError("Master CSV must contain 'Filename' and 'Bates/Control #' columns.")

    # Create a dictionary mapping filenames without extensions to their full names and Bates numbers
    master_dict = {
        os.path.splitext(row['Filename'])[0]: (row['Filename'], row['Bates/Control #'])
        for _, row in master_df.iterrows()
    }

    # Prepare the output matches and unmatched filenames
    matches = []
    unmatched = []

    for filename in input_df['Filename']:
        if filename in master_dict:
            full_filename, bates_number = master_dict[filename]
            matches.append(f"{bates_number} ({full_filename})")
        else:
            unmatched.append(filename)

    # Determine the output directory (same as master CSV)
    output_dir = os.path.dirname(master_csv)

    # Define output file paths
    output_txt = os.path.join(output_dir, "output_matches.txt")
    unmatched_csv = os.path.join(output_dir, "unmatched_filenames.csv")

    # Write the matches to the output text file
    with open(output_txt, 'w') as f:
        for match in matches:
            f.write(match + '\n')

    # Write the unmatched filenames to a new CSV file
    unmatched_df = pd.DataFrame(unmatched, columns=['Filename'])
    unmatched_df.to_csv(unmatched_csv, index=False)

    print(f"Output written to {output_txt}")
    print(f"Unmatched filenames written to {unmatched_csv}")

if __name__ == "__main__":
    # Replace with your file paths
    input_csv_path = r"C:\Users\Willi\Downloads\New input.csv"
    master_csv_path = r"C:\Users\Willi\Downloads\master csv.csv"

    match_filenames(input_csv_path, master_csv_path)

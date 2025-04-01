import os
import pandas as pd
from tqdm import tqdm

def main():
    # Ask user for the CSV file path and clean the input.
    file_path = input("Enter the CSV file path: ").strip().strip('"')
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print("File not found. Please check the file path and try again.")
        return

    # Read the CSV file using pandas.
    df = pd.read_csv(file_path)
    
    # Ensure the expected columns exist
    expected_columns = ["Bates/Control #", "Note Text"]
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        print(f"Missing expected columns: {missing_cols}")
        return

    # Set up tqdm progress bar for the processing step.
    tqdm.pandas(desc="Processing rows")
    
    # Create a new column "Hyperlinked": if "Note Text" is non-empty then "Yes", else "No"
    df['Hyperlinked'] = df['Note Text'].progress_apply(
        lambda note: 'Yes' if pd.notnull(note) and str(note).strip() != '' else 'No'
    )
    
    # Create a new DataFrame with just the required columns.
    output_df = df[['Bates/Control #', 'Hyperlinked']]
    
    # Save the output CSV in the same directory as the input file.
    output_directory = os.path.dirname(file_path)
    output_file = os.path.join(output_directory, "output_report.csv")
    output_df.to_csv(output_file, index=False)
    
    print(f"Report saved to {output_file}")

if __name__ == '__main__':
    main()

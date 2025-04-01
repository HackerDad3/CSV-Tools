import os
import pandas as pd

def generate_file_list(start_dir):
    records = []
    # Walk through all directories starting at start_dir.
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            # Extract the file name without its extension.
            bates = os.path.splitext(file)[0]
            # Get the relative path from the starting directory.
            full_path = os.path.join(root, file)
            native_path = os.path.relpath(full_path, start_dir)
            records.append({"Bates/Control #": bates, "Native Path": native_path})
    return records

def main():
    start_dir = input("Enter the starting directory: ")
    output_csv = input("Enter the output CSV file path (or press Enter to use 'output.csv'): ") or "output.csv"

    file_list = generate_file_list(start_dir)
    df = pd.DataFrame(file_list)
    # Save the DataFrame to CSV with UTF-8 encoding.
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"CSV file saved to: {output_csv}")

if __name__ == '__main__':
    main()

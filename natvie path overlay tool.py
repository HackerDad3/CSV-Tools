import os
import pandas as pd

def generate_file_list(start_dir):
    records = []
    # Get the base name of the starting directory.
    base_name = os.path.basename(os.path.normpath(start_dir))
    # Walk through all directories starting at start_dir.
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            # Get the file name without its extension.
            bates = os.path.splitext(file)[0]
            # Build the full path.
            full_path = os.path.join(root, file)
            # Compute the relative path from the starting directory.
            rel_path = os.path.relpath(full_path, start_dir)
            # Prepend the base name of the starting directory.
            native_path = os.path.join(base_name, rel_path)
            records.append({"Bates/Control #": bates, "Native Path": native_path})
    return records

def main():
    # Get and clean user input for the starting directory.
    start_dir = input("Enter the starting directory: ").strip().strip('")')
    # Get and clean user input for the output CSV file name (without extension).
    file_name = input("Enter the name for the output CSV file (without extension): ").strip().strip('")')
    
    # Create the output directory (start_dir/data) if it doesn't exist.
    output_dir = os.path.join(start_dir, "data")
    os.makedirs(output_dir, exist_ok=True)
    # Build the full CSV file path.
    output_csv = os.path.join(output_dir, file_name + ".csv")
    
    # Generate file records and write to CSV with UTF-8 encoding.
    file_list = generate_file_list(start_dir)
    df = pd.DataFrame(file_list)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    
    print(f"CSV file saved to: {output_csv}")

if __name__ == '__main__':
    main()

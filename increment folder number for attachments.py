import os
import pandas as pd
from tqdm import tqdm

def update_other_bates(input_csv: str, output_csv: str):
    """
    Read a CSV with Bates/control numbers and row identifiers,
    then for each 'host' row (with integer 'Row #'), propagate its
    Bates number to its attachments by incrementing the folder number.
    Writes an output CSV with an 'Other Bates' column updated.
    """
    # Load the CSV file, treating all columns as strings to preserve leading zeros, etc.
    df = pd.read_csv(input_csv, dtype=str, keep_default_na=False)

    # Ensure the 'Other Bates' column exists to store updated Bates numbers
    if 'Other Bates' not in df.columns:
        df['Other Bates'] = ''

    # Identify host rows: those with a 'Row #' that is a whole integer (e.g., '1', '2', etc.)
    df['is_host'] = df['Row #'].str.match(r'^\d+$')

    # Build a lookup of host metadata for later use
    hosts = {}
    for idx, row in df[df['is_host']].iterrows():
        # Split the Bates number into its four components: pfx1.pfx2.folder.page
        parts = row['Bates/Control #'].split('.')
        if len(parts) != 4:
            # Unexpected format; stop and report
            raise ValueError(f"Unexpected Bates format at row {idx}: '{row['Bates/Control #']}'")
        pfx1, pfx2, folder, page = parts

        # Store metadata for each host, converting folder to integer for arithmetic
        hosts[row['Row #']] = {
            'idx': idx,
            'pfx1': pfx1,
            'pfx2': pfx2,
            'base_folder': int(folder),
            'page': page
        }
        # Initialize the 'Other Bates' of the host to its own Bates number
        df.at[idx, 'Other Bates'] = row['Bates/Control #']

    # Group non-host rows (attachments) under their corresponding host by splitting at first dot
    attach_groups = {}
    for idx, row in df[~df['is_host']].iterrows():
        # Determine the host number (e.g., '1' from '1.2', '1.10', etc.)
        host_num = row['Row #'].split('.', 1)[0]
        # Store tuple of (dataframe index, row# as float) for sorting
        attach_groups.setdefault(host_num, []).append((idx, float(row['Row #'])))

    # Process each host and assign updated Bates numbers to its attachments
    for host_num, info in tqdm(hosts.items(), desc="Hosts processed", unit="host"):
        # Get list of attachments for this host (could be empty)
        group = attach_groups.get(host_num, [])
        if not group:
            continue  # No attachments; move to next host

        # Sort attachments by their 'Row #' numeric value (to ensure proper order)
        group.sort(key=lambda x: x[1])

        # Assign new folder numbers sequentially, starting after the host's folder
        for i, (idx, _) in enumerate(group, start=1):
            # Compute new folder number with zero-padding to 3 digits
            new_folder = f"{info['base_folder'] + i:03}"
            # Reconstruct the Bates number string: pfx1.pfx2.new_folder.page
            new_bates = f"{info['pfx1']}.{info['pfx2']}.{new_folder}.{info['page']}"
            # Set the 'Other Bates' for this attachment row
            df.at[idx, 'Other Bates'] = new_bates

    # Remove the helper column before saving
    df.drop(columns=['is_host'], inplace=True)
    # Write the updated DataFrame back to CSV, preserving all rows
    df.to_csv(output_csv, index=False)
    print(f"✔️ Updated CSV written to: {output_csv}")


if __name__ == "__main__":
    # Prompt the user to enter the path to the input CSV file
    raw = input("Enter path to input CSV: ")
    input_csv = raw.strip().strip('"')

    # Construct the output filename by appending '_updated' before the extension
    folder, fname = os.path.split(input_csv)
    name, ext = os.path.splitext(fname)
    output_csv = os.path.join(folder, f"{name}_updated{ext or '.csv'}")

    # Run the update function with the specified input and output paths
    update_other_bates(input_csv, output_csv)

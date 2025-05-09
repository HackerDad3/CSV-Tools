import os
import pandas as pd
from tqdm import tqdm


def update_other_bates(input_csv: str, output_csv: str):
    """
    Read a CSV with Bates/control numbers, 'Row #' identifiers, and an existing 'Other Bates' for hosts.
    For each host row (integer 'Row #'), use its 'Other Bates' as the base, then assign new
    'Other Bates' values to each attachment by incrementing the folder segment in that base value.
    Attachments are processed in the exact order they appear in the CSV.
    Writes an output CSV containing all original columns (including 'Bates/Control #' and 'Row #')
    plus the updated 'Other Bates' column, preserving 'Bates/Control #' as a key for downstream usage.
    """
    # Load all columns as strings to preserve formatting
    df = pd.read_csv(input_csv, dtype=str, keep_default_na=False)

    # Ensure 'Other Bates' column exists
    if 'Other Bates' not in df.columns:
        df['Other Bates'] = ''

    # Normalize 'Row #' by stripping out non-digit/non-dot characters
    df['RowNum'] = df['Row #'].str.replace(r'[^\d.]', '', regex=True)
    # Identify host rows: RowNum is a whole integer (e.g., '1', '2')
    df['is_host'] = df['RowNum'].str.match(r'^\d+$')

    # Prepare host metadata from existing 'Other Bates'
    hosts = {}
    for idx, row in df[df['is_host']].iterrows():
        base_other = row['Other Bates']
        if not base_other:
            raise ValueError(f"Host at row {idx} is missing an 'Other Bates' value.")
        parts = base_other.split('.')
        if len(parts) != 4:
            raise ValueError(f"Unexpected 'Other Bates' format at row {idx}: '{base_other}'")
        pfx1, pfx2, folder_str, page = parts
        hosts[row['RowNum']] = {
            'base_folder': int(folder_str),
            'pfx1': pfx1,
            'pfx2': pfx2,
            'page': page
        }
    
    # Clear attachments' Other Bates so we can fill fresh values
    df.loc[~df['is_host'], 'Other Bates'] = ''

    # Group attachments under their host, preserving CSV order
    attach_groups = {}
    for idx, row in df[~df['is_host']].iterrows():
        host_num = row['RowNum'].split('.', 1)[0]
        attach_groups.setdefault(host_num, []).append(idx)

    # Assign new 'Other Bates' to each attachment
    for host_num, info in tqdm(hosts.items(), desc="Hosts processed", unit="host"):
        attachments = attach_groups.get(host_num, [])
        for i, idx in enumerate(attachments, start=1):
            new_folder = f"{info['base_folder'] + i:03}"
            new_bates = f"{info['pfx1']}.{info['pfx2']}.{new_folder}.{info['page']}"
            df.at[idx, 'Other Bates'] = new_bates

    # Remove helper columns and write output
    df.drop(columns=['RowNum', 'is_host'], inplace=True)
    # Ensure 'Bates/Control #' remains for external programs
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✔️ Updated CSV written to: {output_csv}")


if __name__ == "__main__":
    raw = input("Enter path to input CSV: ")
    input_csv = raw.strip().strip('"')
    folder, fname = os.path.split(input_csv)
    name, ext = os.path.splitext(fname)
    output_csv = os.path.join(folder, f"{name}_updated{ext or '.csv'}")
    update_other_bates(input_csv, output_csv)

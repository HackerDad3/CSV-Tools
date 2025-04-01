import os
import pandas as pd
import csv

def clean_value(val):
    """
    Remove the braille blank character (U+2800) and any extra whitespace.
    """
    return str(val).replace('\u2800', '').strip()

def is_parent(row_val):
    """
    Determines if a row represents a parent.
    A parent row has a row number that is a whole number.
    """
    try:
        cleaned = clean_value(row_val)
        return float(cleaned) % 1 == 0
    except Exception:
        return False

def main():
    # Prompt for the master list CSV file path.
    master_path = input("Enter the path to the master list CSV file: ").strip().strip('"')
    # Prompt for the relationships CSV file path.
    rel_path = input("Enter the path to the relationships CSV file: ").strip().strip('"')
    
    # Read and clean the master list CSV.
    master_df = pd.read_csv(master_path, skipinitialspace=True)
    master_df.columns = master_df.columns.str.strip()
    if "Bates/Control #" not in master_df.columns:
        print("Master CSV does not contain the required column 'Bates/Control #'.")
        return
    master_df["Bates/Control #"] = master_df["Bates/Control #"].apply(clean_value)
    master_set = set(master_df["Bates/Control #"].unique())
    
    # Read and clean the relationships CSV.
    rel_df = pd.read_csv(rel_path, skipinitialspace=True)
    rel_df.columns = rel_df.columns.str.strip()
    if "Row #" not in rel_df.columns or "Bates/Control #" not in rel_df.columns:
        print("Relationships CSV does not contain required columns 'Row #' and 'Bates/Control #'.")
        return
    rel_df["Row #"] = rel_df["Row #"].apply(clean_value)
    rel_df["Bates/Control #"] = rel_df["Bates/Control #"].apply(clean_value)
    
    # Initialize a dictionary mapping each Bates/Control (from the master list) to a set of related children.
    relationships = {b: set() for b in master_set}
    
    current_parent = None  # Track the current parent as we iterate the rows.
    
    # Process each row in the relationships CSV.
    for idx, row in rel_df.iterrows():
        row_val = row["Row #"]
        bates = row["Bates/Control #"]
        
        if is_parent(row_val):
            # New parent row.
            current_parent = bates
        else:
            # Child row: only add relationship if both the current parent and the child are in the master list.
            if (current_parent in master_set) and (bates in master_set):
                relationships[current_parent].add(bates)
                relationships[bates].add(current_parent)
    
    # Build the output rows using only Bates numbers from the master list.
    output_rows = []
    for bates in sorted(master_set):  # Sorted for consistent order.
        children = sorted(relationships[bates])
        children_str = f"({', '.join(children)})" if children else ""
        parent_val = bates
        # Enclose with exactly one pair of double quotes if it starts with "#"
        if parent_val.startswith("#"):
            parent_val = f'"{parent_val}"'
        output_rows.append({
            "Bates/Control #": parent_val,
            "Children": children_str
        })
    
    # Save the output CSV in the same directory as the relationships CSV.
    output_dir = os.path.dirname(os.path.abspath(rel_path))
    output_file = os.path.join(output_dir, "output.csv")
    
    # Write the CSV using the csv module with no automatic quoting.
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar="\\")
        writer.writerow(["Bates/Control #", "Children"])
        for row in output_rows:
            parent_val = row["Bates/Control #"]
            children_val = row["Children"]
            # Manually wrap children in quotes if non-empty and containing a comma.
            if children_val and "," in children_val:
                children_val = f'"{children_val}"'
            writer.writerow([parent_val, children_val])
            
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()

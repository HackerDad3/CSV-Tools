import pandas as pd
import os

def process_csv(input_csv, output_csv, prefix, box, folder_num, include_suffix):
    # Read CSV into a DataFrame.
    df = pd.read_csv(input_csv, encoding="utf-8")
    
    # Ensure that the "Other Bates" column exists and is treated as text.
    if "Other Bates" not in df.columns:
        df["Other Bates"] = ""
    else:
        df["Other Bates"] = df["Other Bates"].astype(object)
    
    # Add new columns for Parent ID and Begin Family.
    df["Parent ID"] = ""
    df["Begin Family"] = ""
    
    # Create a mask for rows representing files inside a ZIP (those with "//").
    inner_mask = df["File Path"].str.contains("//", na=False)
    df_inner = df[inner_mask].copy()
    
    # Split "File Path" into two parts:
    #   - zip_group: the part before the "//" (the ZIP file name)
    #   - inside_path: the part after the "//"
    df_inner["zip_group"] = df_inner["File Path"].str.split("//").str[0]
    df_inner["inside_path"] = df_inner["File Path"].str.split("//").str[1]
    
    # From inside_path, extract the folder and the filename.
    # Assumption: if splitting by "/" yields more than one part,
    # then the folder is the second element (index 1) and the filename is the last element.
    df_inner["folder"] = df_inner["inside_path"].apply(
        lambda x: x.split("/")[1] if len(x.split("/")) > 1 else ""
    )
    df_inner["filename"] = df_inner["inside_path"].apply(
        lambda x: x.split("/")[-1] if x else ""
    )
    
    # Initialize the page (Bates) counter.
    bates_counter = 1

    # Helper function to build the Bates number using user inputs and the counter.
    def make_bates(counter):
        bates = f"{prefix}.{box}.{folder_num}.{counter:04d}"
        if include_suffix:
            bates += "_0001"
        return bates
    
    # ------------------------------
    # Process rows that are inside a folder.
    # ------------------------------
    in_folder = df_inner[df_inner["folder"] != ""].copy()
    groups = in_folder.groupby(["zip_group", "folder"])
    
    # Process each folder group in sorted order (by zip_group then folder).
    for (zip_grp, folder_name) in sorted(groups.groups.keys(), key=lambda x: (x[0], x[1])):
        group_df = groups.get_group((zip_grp, folder_name)).copy()
        # Sort the rows within the folder (by File Path; adjust as needed)
        group_df = group_df.sort_values("File Path")
        
        # Partition the group into FE files, Civmec files, and any others.
        fe_rows = group_df[group_df["filename"].str.startswith("FE")]
        civmec_rows = group_df[group_df["filename"].str.startswith("Civmec")]
        others = group_df[~(group_df["filename"].str.startswith("FE") |
                             group_df["filename"].str.startswith("Civmec"))]
        
        # Assign Bates numbers in the order: FE, then Civmec, then others.
        for idx in fe_rows.index:
            df.loc[idx, "Other Bates"] = make_bates(bates_counter)
            bates_counter += 1
        for idx in civmec_rows.index:
            df.loc[idx, "Other Bates"] = make_bates(bates_counter)
            bates_counter += 1
        for idx in others.index:
            df.loc[idx, "Other Bates"] = make_bates(bates_counter)
            bates_counter += 1
        
        # For folder documents, designate the FE document as the parent.
        # Use the Bates/Control # value from the first FE row as the parent value.
        if not fe_rows.empty:
            parent_control = fe_rows.iloc[0]["Bates/Control #"]
            # For each row in the folder group:
            for idx in group_df.index:
                fname = group_df.loc[idx, "filename"]
                if fname.startswith("FE"):
                    # For FE document: Parent ID remains blank; Begin Family is set.
                    df.loc[idx, "Begin Family"] = parent_control
                elif fname.startswith("Civmec"):
                    # For Civmec: Set both Parent ID and Begin Family.
                    df.loc[idx, "Parent ID"] = parent_control
                    df.loc[idx, "Begin Family"] = parent_control
                # For any other files in the folder, leave Parent ID and Begin Family blank.
    
    # ------------------------------
    # Process rows that are inside the ZIP but not in a folder.
    # ------------------------------
    not_in_folder = df_inner[df_inner["folder"] == ""].copy()
    if not not_in_folder.empty:
        not_in_folder = not_in_folder.sort_values("File Path")
        fe_rows = not_in_folder[not_in_folder["filename"].str.startswith("FE")]
        civmec_rows = not_in_folder[not_in_folder["filename"].str.startswith("Civmec")]
        others = not_in_folder[~(not_in_folder["filename"].str.startswith("FE") |
                                   not_in_folder["filename"].str.startswith("Civmec"))]
        
        for idx in fe_rows.index:
            df.loc[idx, "Other Bates"] = make_bates(bates_counter)
            bates_counter += 1
        for idx in civmec_rows.index:
            df.loc[idx, "Other Bates"] = make_bates(bates_counter)
            bates_counter += 1
        for idx in others.index:
            df.loc[idx, "Other Bates"] = make_bates(bates_counter)
            bates_counter += 1
        # For non-folder items, Parent ID and Begin Family remain blank.
    
    # ------------------------------
    # Write the updated DataFrame to the output CSV.
    # ------------------------------
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"Output saved to: {output_csv}")

if __name__ == "__main__":
    # Prompt for the input CSV file path.
    input_csv = input("Enter the path to the input CSV file: ").strip().strip('"')
    
    # Determine the directory of the input file.
    input_dir = os.path.dirname(input_csv)
    if not input_dir:
        input_dir = "."
    
    # Define the output CSV path (saved to the same directory as the input).
    output_csv = os.path.join(input_dir, "output.csv")
    
    # Prompt for the Bates number parts.
    prefix = input("Enter the prefix for the Bates number: ").strip()
    box_number = input("Enter the box number for the Bates number: ").strip()
    folder_number = input("Enter the folder number for the Bates number: ").strip()
    
    # Ask if a suffix should be included.
    suffix_choice = input("Do you want a suffix? (yes/no): ").strip().lower()
    include_suffix = suffix_choice in ["yes", "y"]
    
    process_csv(input_csv, output_csv, prefix, box_number, folder_number, include_suffix)

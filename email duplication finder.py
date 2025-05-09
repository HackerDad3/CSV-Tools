import pandas as pd
import os
from tqdm import tqdm

def main():
    # Prompt for CSV file paths and clean the inputs.
    csv1_path = input("Enter the CSV file path for the full email database (CSV1): ").strip().strip('\'"')
    csv2_path = input("Enter the CSV file path for the specific group (CSV2): ").strip().strip('\'"')
    
    # Determine the output directory based on CSV2.
    output_dir = os.path.dirname(csv2_path) or "."
    grouped_output_file = os.path.join(output_dir, "grouped_duplicates_output.csv")
    individual_duplicates_output_file = os.path.join(output_dir, "duplicates_individual_output.csv")
    non_duplicates_output_file = os.path.join(output_dir, "non_duplicates_output.csv")
    email_duplication_report_file = os.path.join(output_dir, "email_duplication_report.csv")
    
    # Read both CSV files.
    df_full = pd.read_csv(csv1_path)
    df_group = pd.read_csv(csv2_path)
    
    # Build a set of (Title, Date) pairs from CSV1.
    full_titles_dates = set(zip(df_full['Title'], df_full['Date']))
    
    # Mark rows in CSV2 as duplicates if their (Title, Date) exists in CSV1.
    df_group['is_duplicate'] = df_group.apply(
        lambda row: (row['Title'], row['Date']) in full_titles_dates, axis=1)
    
    # Separate CSV2 rows into duplicates and non-duplicates.
    df_duplicates_csv2 = df_group[df_group['is_duplicate']]
    df_non_duplicates_csv2 = df_group[~df_group['is_duplicate']]
    
    # Save non-duplicate CSV2 rows.
    df_non_duplicates_csv2.to_csv(non_duplicates_output_file, index=False)
    print(f"Non-duplicate records saved to {non_duplicates_output_file}")
    
    # Save individual duplicate rows from CSV2.
    df_duplicates_csv2.to_csv(individual_duplicates_output_file, index=False)
    print(f"Individual duplicate records saved to {individual_duplicates_output_file}")
    
    # For the grouped duplicates report, combine data from CSV1 and CSV2.
    # First, get the (Title, Date) pairs from CSV2 that are duplicates.
    duplicate_titles_dates = set(df_duplicates_csv2[['Title', 'Date']].itertuples(index=False, name=None))
    # Get matching rows from CSV1.
    df_duplicates_csv1 = df_full[df_full.apply(lambda row: (row['Title'], row['Date']) in duplicate_titles_dates, axis=1)]
    # Combine the duplicate rows from CSV1 and CSV2.
    union_duplicates = pd.concat([df_duplicates_csv1, df_duplicates_csv2], ignore_index=True)
    
    # Helper function to join unique values.
    def join_unique(series):
        return ', '.join(series.astype(str).unique())
    
    grouped_data = []
    grouped = union_duplicates.groupby(['Title', 'Date'])
    for (title, date), group in tqdm(grouped, total=len(grouped), desc="Grouping duplicates"):
        grouped_data.append({
            'Title': title,
            'Date': date,
            'Bates/Control #': ', '.join(group['Bates/Control #'].astype(str)),
            'Document ID': ', '.join(group['Document ID'].astype(str).unique()),
            'From': join_unique(group['From']),
            'To': join_unique(group['To']),
            'CC': join_unique(group['CC'])
        })
    
    if grouped_data:
        grouped_df = pd.DataFrame(grouped_data)
        grouped_df.to_csv(grouped_output_file, index=False)
        print(f"Grouped duplicate records saved to {grouped_output_file}")
    else:
        print("No duplicate groups found for grouping.")
    
    # Generate the Email Duplication Report.
    # For each duplicate in CSV2, join with the corresponding CSV1 row(s) on Title and Date.
    # This merge will produce one row per CSV1 row joined with each matching CSV2 row.
    df_duplicates_csv2_filtered = df_duplicates_csv2.copy()
    email_dup_report = pd.merge(
        df_full, 
        df_duplicates_csv2_filtered, 
        on=['Title', 'Date'], 
        suffixes=('_csv1', '_csv2')
    )
    
    # Select the required columns.
    email_dup_report = email_dup_report[[
        'Title', 'Date',
        'Bates/Control #_csv1', 'Document ID_csv1', 'File Path_csv1',
        'Bates/Control #_csv2', 'Document ID_csv2', 'File Path_csv2'
    ]]
    
    email_dup_report.to_csv(email_duplication_report_file, index=False)
    print(f"Email Duplication Report saved to {email_duplication_report_file}")

if __name__ == '__main__':
    main()

import pandas as pd
import os

def compare_csv(csv1, csv2, column_name="Bates/Control #"):
    # Load both CSV files into dataframes
    df1 = pd.read_csv(csv1)
    df2 = pd.read_csv(csv2)
    
    # Ensure the column name exists in both dataframes
    if column_name not in df1.columns or column_name not in df2.columns:
        raise ValueError(f"Column '{column_name}' not found in one or both CSV files.")
    
    # Get the set of Bates numbers from each CSV
    bates_csv1 = set(df1[column_name].dropna())
    bates_csv2 = set(df2[column_name].dropna())
    
    # Find the extra Bates numbers in CSV1 compared to CSV2
    extra_in_csv1 = bates_csv1 - bates_csv2
    missing_in_csv1 = bates_csv2 - bates_csv1
    
    # Prepare the differences to be written to a CSV file
    differences = []
    
    # Add extra Bates numbers in CSV1
    if extra_in_csv1:
        for bates in extra_in_csv1:
            differences.append({"Bates Number": bates, "Status": "Extra in CSV1"})
    
    # Add missing Bates numbers in CSV1
    if missing_in_csv1:
        for bates in missing_in_csv1:
            differences.append({"Bates Number": bates, "Status": "Missing in CSV1"})
    
    # Define the output file path (same directory as csv1)
    output_file = os.path.join(os.path.dirname(csv1), "bates_comparison_results.csv")
    
    # Convert the differences list to a DataFrame and save it as CSV
    differences_df = pd.DataFrame(differences)
    differences_df.to_csv(output_file, index=False)
    
    print(f"Differences saved to: {output_file}")

# Example usage
csv1_path = input("Paste csv 1 file path:").strip().strip('"')
csv2_path = input("Paste file pth for csv2:").strip().strip('"')
compare_csv(csv1_path, csv2_path)

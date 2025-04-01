import pandas as pd
from collections import defaultdict
import os

def group_bates_by_pattern(csv_path, pattern_column, bates_column, file_column=None):
    """
    Group Bates numbers by pattern or file (based on the CSV).
    If file_column is provided, group by PDF file, else by ReferencedBates (Pattern).
    """
    df = pd.read_csv(csv_path)

    # Strip any leading/trailing spaces in column names
    df.columns = df.columns.str.strip()

    grouped_data = defaultdict(list)

    if file_column:
        # Group by PDF file (Pattern is in the PDF file name, remove '.pdf')
        for _, row in df.iterrows():
            pattern = row[file_column].replace(".pdf", "")  # Remove extension
            bates_number = row[bates_column]
            grouped_data[pattern].append(bates_number)
    else:
        # Group by ReferencedBates (CSV 1 - Pattern)
        for _, row in df.iterrows():
            referenced_bates = row[pattern_column]
            bates_number = row[bates_column]
            grouped_data[referenced_bates].append(bates_number)
    
    return grouped_data

def compare_grouped_bates(grouped_csv1, grouped_csv2):
    results = []

    # Compare the grouped Bates numbers for CSV 1 to CSV 2
    for referenced_bates in grouped_csv1:
        if referenced_bates in grouped_csv2:
            # Find missing Bates numbers in CSV 2 (CSV 1 has them but CSV 2 does not)
            missing_in_csv2 = set(grouped_csv1[referenced_bates]) - set(grouped_csv2[referenced_bates])

            # Add missing Bates numbers to results
            for missing_bates in missing_in_csv2:
                results.append({"Pattern": referenced_bates, "Bates/Control #": missing_bates, "Status": "Missing in CSV 2"})
        else:
            # If the referenced_bates doesn't exist in CSV 2 at all, it's completely missing
            for bates_number in grouped_csv1[referenced_bates]:
                results.append({"Pattern": referenced_bates, "Bates/Control #": bates_number, "Status": "Missing in CSV 2"})

    # Find extra Bates numbers in CSV 2 (those present in CSV 2 but not in CSV 1)
    for referenced_bates in grouped_csv2:
        if referenced_bates not in grouped_csv1:
            for bates_number in grouped_csv2[referenced_bates]:
                results.append({"Pattern": referenced_bates, "Bates/Control #": bates_number, "Status": "Extra in CSV 2"})

    return results

def main():
    # Input file paths
    csv1_path = input("Enter the path to the first CSV (from notes text): ").strip().strip('"')
    csv2_path = input("Enter the path to the second CSV (from PDF extraction): ").strip().strip('"')

    # Read CSV 1 directory path to save results in the same directory
    input_directory = os.path.dirname(csv1_path)

    # Group Bates numbers by ReferencedBates for CSV 1 (grouped by referenced Bates)
    grouped_csv1 = group_bates_by_pattern(csv1_path, 'ReferencedBates', 'Bates/Control #')

    # Group Bates numbers by PDF file (grouped by file name) for CSV 2
    grouped_csv2 = group_bates_by_pattern(csv2_path, 'Pattern', 'Bates/Control #', file_column='PDF_File')

    # Compare grouped Bates numbers between CSV 1 and CSV 2
    results = compare_grouped_bates(grouped_csv1, grouped_csv2)

    # Create a DataFrame from the results
    result_df = pd.DataFrame(results)

    # Create the output file path in the same directory as CSV 1
    output_csv_path = os.path.join(input_directory, 'comparison_results.csv')

    # Save the results to a new CSV
    result_df.to_csv(output_csv_path, index=False)

    print(f"Comparison complete. Results saved to {output_csv_path}")

if __name__ == "__main__":
    main()

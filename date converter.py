import pandas as pd
import os

def parse_date(value, dayfirst):
    """
    Try to parse a date string using the specified dayfirst parameter.
    If parsing fails, try with the opposite setting.
    If both attempts fail, return the original value.
    """
    original_value = value
    if isinstance(value, str):
        value = value.strip()
    # Try parsing with the provided dayfirst setting
    dt = pd.to_datetime(value, dayfirst=dayfirst, errors='coerce')
    if pd.isna(dt):
        # Fallback: try parsing with the opposite interpretation
        dt_alt = pd.to_datetime(value, dayfirst=not dayfirst, errors='coerce')
        if pd.notna(dt_alt):
            return dt_alt
        else:
            # If parsing still fails, return the original value
            return original_value
    return dt

def main():
    # Get the input file path from the user
    input_file = input("Enter the input CSV file path: ").strip().strip('"')
    
    # Ask user for the date format of the input dates (DMY or MDY)
    date_format_input = input("Enter the date format of the input dates (enter DMY for day-month-year or MDY for month-day-year): ").strip().upper()
    dayfirst = True if date_format_input == "DMY" else False
    
    # Read the CSV file into a DataFrame
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Check if the "Date" column exists
    if "Date" not in df.columns:
        print("No 'Date' column found in the CSV file.")
        return

    # Apply the parse_date function to each value in the "Date" column
    def format_date(val):
        parsed = parse_date(val, dayfirst)
        # Only format if the value is a Timestamp (i.e., parsed successfully)
        if isinstance(parsed, pd.Timestamp):
            return parsed.strftime("%d-%b-%Y")
        else:
            return parsed

    df["Date"] = df["Date"].apply(format_date)
    
    # Construct the output file path: same directory, same filename with '_Date Coverted' appended
    dir_name = os.path.dirname(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(dir_name, f"{base_name}_Date Coverted.csv")
    
    # Write the output CSV
    try:
        df.to_csv(output_file, index=False)
        print(f"Converted CSV saved to: {output_file}")
    except Exception as e:
        print(f"Error writing output CSV: {e}")

if __name__ == '__main__':
    main()

import pandas as pd
import os

def parse_date(value, dayfirst):
    """
    Try to parse a date string using the specified dayfirst flag.
    If parsing fails, try with the opposite setting.
    If both attempts fail, return the original value.
    """
    original_value = value
    if isinstance(value, str):
        value = value.strip()
    dt = pd.to_datetime(value, dayfirst=dayfirst, errors='coerce')
    if pd.isna(dt):
        dt_alt = pd.to_datetime(value, dayfirst=not dayfirst, errors='coerce')
        if pd.notna(dt_alt):
            return dt_alt
        return original_value
    return dt

def main():
    # 1. Get input file
    input_file = input("Enter the input CSV file path: ").strip().strip('"')

    # 2. Select input date-order
    print("\nSelect the input date format:")
    print("  1) Day–Month–Year (DMY)")
    print("  2) Month–Day–Year (MDY)")
    choice = input("Enter choice (1 or 2): ").strip()
    dayfirst = True if choice == "1" else False

    # 3. Select output format
    print("\nSelect the output date format:")
    print("  1) dd-MMM-yyyy       e.g. 01-Jan-2025")
    print("  2) dd-MMM-yyyy hh:mm e.g. 01-Jan-2025 14:30")
    fmt_choice = input("Enter choice (1 or 2): ").strip()
    if fmt_choice == "2":
        out_fmt = "%d-%b-%Y %H:%M"
    else:
        out_fmt = "%d-%b-%Y"

    # 4. Read CSV
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # 5. Ensure there's a Date column
    if "Date" not in df.columns:
        print("No 'Date' column found in the CSV file.")
        return

    # 6. Apply parsing + formatting
    def format_date(val):
        parsed = parse_date(val, dayfirst)
        if isinstance(parsed, pd.Timestamp):
            return parsed.strftime(out_fmt)
        return parsed

    df["Date"] = df["Date"].apply(format_date)

    # 7. Save out
    dir_name   = os.path.dirname(input_file)
    base_name  = os.path.splitext(os.path.basename(input_file))[0]
    output_csv = os.path.join(dir_name, f"{base_name}_Date_Converted.csv")

    try:
        df.to_csv(output_csv, index=False)
        print(f"\n✅ Converted CSV saved to: {output_csv}")
    except Exception as e:
        print(f"Error writing output CSV: {e}")

if __name__ == "__main__":
    main()

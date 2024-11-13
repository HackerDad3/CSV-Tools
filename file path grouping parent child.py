import pandas as pd
import os

# Load the CSV file
file_path = r"C:\Users\Willi\Downloads\20241113T1037_UTC8_Tranche_4_begin_family.csv"
df = pd.read_csv(file_path)

# Ensure that the Begin Family column is treated as a string
df['Begin Family'] = df['Begin Family'].astype(str)

# Function to identify parent and child documents and copy the parent's Other Bates to Begin Family
def identify_parent_child(df):
    # Extract the folder name from the file path
    df['Folder_Name'] = df['File Path'].apply(lambda x: os.path.basename(os.path.dirname(x)))

    # Identify parents
    parent_documents = df[df['Filename'].str.split('.').str[0] == df['Folder_Name']]
    parent_names = parent_documents['Folder_Name'].unique()

    # Create Parent_Child_Status column
    df['Parent_Child_Status'] = df.apply(
        lambda x: 'Parent' if os.path.splitext(x['Filename'])[0] == x['Folder_Name'] else
                   'Child' if x['Folder_Name'] in parent_names else 'Non_Parent',
        axis=1
    )

    # Create Child_Of column
    df['Child_Of'] = df.apply(lambda x: x['Folder_Name'] if x['Parent_Child_Status'] == 'Child' else None, axis=1)

    # Copy parent's Other Bates to Begin Family column for both parent and children
    for folder_name in parent_names:
        parent_row = df[(df['Parent_Child_Status'] == 'Parent') & (df['Folder_Name'] == folder_name)]
        if not parent_row.empty:
            parent_other_bates = parent_row['Other Bates'].values[0]
            # Update Begin Family for both parent and its children
            df.loc[df['Folder_Name'] == folder_name, 'Begin Family'] = str(parent_other_bates)

    return df

# Reorder the DataFrame with the updated parent-child identification
df = identify_parent_child(df)

# Create a sorting key
df['Sort_Key'] = df['Parent_Child_Status'].replace({'Parent': '0', 'Child': '1', 'Non_Parent': '2'})

# Sort the DataFrame to ensure correct grouping
df.sort_values(by=['Folder_Name', 'Sort_Key'], ascending=[True, True], inplace=True)

# Drop the helper columns used for sorting
df.drop(columns=['Sort_Key'], inplace=True)

# Create a new index to maintain parent-child relationships
df.reset_index(drop=True, inplace=True)

# Save the reordered DataFrame to a new CSV file
output_file_path = os.path.join(os.path.dirname(file_path), f'{os.path.splitext(os.path.basename(file_path))[0]}_ReOrdered.csv')
df.to_csv(output_file_path, index=False)

print(f'Reordered CSV saved as {output_file_path}')

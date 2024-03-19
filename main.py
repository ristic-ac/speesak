# Import custom module from modules/xlsx.py
import modules.xlsx as mxlsx
import modules.os as mos
import pandas as pd

# Get all filenames from xlsx/
xlsx_files = mos.get_xlsx_files()

print(xlsx_files)

# Find files with with two letters without extension
xlsx_files = [f for f in xlsx_files if len(f) == 7]
print(xlsx_files)

# Modify filenames to not include .xlsx extension
xlsx_files = [f.split(".")[0] for f in xlsx_files]
print(xlsx_files)

# Pair up files with and without K so that pairs are such as (file.xlsx, fileK.xlsx)
xlsx_files = [(f + ".xlsx", f + "K.xlsx") for f in xlsx_files]
print(xlsx_files)

df_groups_combined = pd.DataFrame()
df_complete_combined = pd.DataFrame()

# For each pair of files
for xlsx_file, xlsx_k_file in xlsx_files:
    print("For files: ", xlsx_file, xlsx_k_file)
    df_groups = mxlsx.xlsx_to_array(xlsx_file)
    # print(df)
    df_complete = mxlsx.xlsx_k_to_array(xlsx_k_file)
    # print(df_k)

    df_groups_combined = df_groups_combined.append(df_groups)
    df_complete_combined = df_complete_combined.append(df_complete)

    # Find intersection based on "Broj indeksa"
    df_merged = pd.merge(df_groups, df_complete, on="Broj indeksa", how="inner")
    # print(df_merged)

    # Find 'Broj indeksa' that are in df but not in df_merged
    df_in_groups_not_in_complete = df_groups[~df_groups['Broj indeksa'].isin(df_merged['Broj indeksa'])]
    print("Not in list where all students are together, but is in list by groups:")
    print(df_in_groups_not_in_complete)

print(len(df_groups_combined))
print(len(df_complete_combined))

# Find rows in df_complete that have 'Način slušanja' == 'Ponovo sluša'
df_complete_repeated = df_complete_combined[df_complete_combined['Način slušanja'] == 'Ponovo sluša']
print("Students that are repeating: ", df_complete_repeated)

# Extract "Broj indeksa" from df_complete_repeated
df_complete_repeated_index = df_complete_repeated['Broj indeksa']
print("Index of students that are repeating: ", df_complete_repeated_index)

# Find rows in df_groups_combined that have 'Broj indeksa' in df_complete_repeated_index
df_groups_repeated = df_groups_combined[df_groups_combined['Broj indeksa'].isin(df_complete_repeated_index)]
print("Students in groups that are repeating: ",df_groups_repeated)
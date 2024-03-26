# Import custom module from modules/xlsx.py
import modules.xlsx as mxlsx
import modules.os as mos
import modules.stats as mstats
import modules.utils as mutils
import pandas as pd

STUDENTS_PER_GROUP = 16

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

availability_by_groups = []

for xlsx_file, xlsx_k_file in xlsx_files:
    print("----------------------------------------")
    print("For files: ", xlsx_file, xlsx_k_file)
    df_groups = mxlsx.xlsx_to_array(xlsx_file)
    df_complete = mxlsx.xlsx_k_to_array(xlsx_k_file)

    mutils.calculate_group_availability(STUDENTS_PER_GROUP, availability_by_groups, xlsx_file, df_groups)

    df_groups_combined = df_groups_combined.append(df_groups)
    df_complete_combined = df_complete_combined.append(df_complete)

    # Find intersection based on "Broj indeksa"
    df_merged = pd.merge(df_groups, df_complete, on="Broj indeksa", how="inner")

    # Find 'Broj indeksa' that are in df but not in df_merged
    mutils.find_inconsistencies(df_groups, df_merged)

    print()

# Drop "Redni broj" column from df_groups_combined
df_groups_combined = df_groups_combined.drop(columns="Redni_broj")

# Add column Smer, which is first two letters "Broj indeksa"
df_groups_combined['Smer'] = df_groups_combined['Broj indeksa'].str[:2]

mstats.student_status_stats(df_complete_combined)
mstats.student_not_regular_in_group_stats(df_groups_combined, df_complete_combined)

# Wait for user input to continue
# input("Press Enter to continue...")
print()

# For each file print number of groups
print("Number of groups per file: ")
print(availability_by_groups) 

# Load data from xlsx/PRIJAVE.xlsx
df_poll = mxlsx.xlsx_to_array("PRIJAVE.xlsx")
df_poll = mutils.refactor_indexes(df_poll)
df_poll = mutils.exclude_non_payers(df_complete_combined, df_poll)
df_poll = df_poll.reset_index(drop=True)

# For each row in df_poll, find "Način slušanja" in df_complete_combined and add it to df_poll
df_poll['Način slušanja'] = df_poll['Broj indeksa'].map(df_complete_combined.set_index('Broj indeksa')['Način slušanja'])
mstats.student_status_stats(df_poll)

# Print students that are in df_poll and in df_groups_combined print them and remove them from df_poll
df_poll = mutils.remove_polled_students_already_in_group(df_groups_combined, df_poll)
grouped = mstats.student_status_stats(df_poll)

dfs = [(status,students) for status, students in df_poll.groupby('Način slušanja')]

dfs = mutils.prioritize_new_students(dfs)

appointed_student_indexes = []
no_students_before_first_appointing = len(df_groups_combined)

df_groups_combined = mutils.appoint_to_existing_groups(df_groups_combined, availability_by_groups, dfs, appointed_student_indexes)

residual_students = []
mutils.track_residual_students(dfs, appointed_student_indexes, residual_students)

no_students_after_first_appointing = len(df_groups_combined)

if no_students_after_first_appointing - no_students_before_first_appointing != len(appointed_student_indexes):
    print("Error: Number of appointed students is not equal to difference between number of students before and after appointing.")
    print("Check if students are appointed correctly.")
    exit(1)

# Change order of columns in df_groups_combined to: "Grupa", "Smer", "Broj indeksa", "Prezime", "Ime"
df_groups_combined = df_groups_combined[["Smer", "Grupa", "Broj indeksa", "Prezime", "Ime"]]

# Sort df_groups_combined by "Smer" and "Grupa"
df_groups_combined = df_groups_combined.sort_values(by=["Smer", "Grupa"])

# Export df_groups_combined to schedules/regular_groups.xlsx
df_groups_combined.to_excel("schedules/regular_groups.xlsx", index=False)

# Load data from additinal-classrooms.csv
df_additional_classrooms = pd.read_csv("additional-classrooms/classrooms.csv")

# Sort df_additional_classrooms by "Ucionica"
df_additional_classrooms = df_additional_classrooms.sort_values(by=["Ucionica"])
df_additional_classrooms.reset_index(drop=True, inplace=True)
print(df_additional_classrooms)

# Convert residual_students to DataFrame
df_residual_students = pd.DataFrame(residual_students)
df_residual_students.reset_index(drop=True, inplace=True)

# Add column "Ucionica" and "Termin" to df_residual_students
df_residual_students["Ucionica"] = ""
df_residual_students["Termin"] = ""

additional_students_appointed = 0
additional_students_to_appoint = len(df_residual_students)
print("To appoint: ", additional_students_to_appoint)
# print(df_residual_students)

# For each classroom in df_additional_classrooms
additional_students_appointed = mutils.appoint_residual_students(df_additional_classrooms, df_residual_students, additional_students_appointed, additional_students_to_appoint)
print(df_residual_students)

print("Appointed: ", additional_students_appointed)
print("To appoint: ", additional_students_to_appoint)

if additional_students_appointed != additional_students_to_appoint:
    print("Error: Number of appointed students is not equal to number of students to appoint.")
    print("Check if students are appointed correctly.")
    exit(1)

# Drop "Način slušanja" column from df_residual_students
df_residual_students = df_residual_students.drop(columns="Način slušanja")

# Export df_residual_students to schedules/additional_groups.xlsx
df_residual_students.to_excel("schedules/additional_groups.xlsx", index=False)
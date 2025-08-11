# Import custom module from modules/xlsx.py
import modules.xlsx as mxlsx
import modules.os as mos
import modules.stats as mstats
import modules.utils as mutils
import pandas as pd

STUDENTS_PER_GROUP = 16

# Get all filenames from xlsx/
xlsx_files = mos.get_xlsx_files()

# Find files with with two letters without extension
xlsx_files = [f for f in xlsx_files if len(f) == 7]
# Modify filenames to not include .xlsx extension
xlsx_files = [f.split(".")[0] for f in xlsx_files]
# Pair up files with and without K so that pairs are such as (file.xlsx, fileK.xlsx)
xlsx_files = [(f + ".xlsx", f + "K.xlsx") for f in xlsx_files]

students_in_groups = pd.DataFrame()
students_in_complete = pd.DataFrame()

classroom_availability_by_groups = []

missing_students = []

for xlsx_file_name, xlsx_k_file_name in xlsx_files:
    students_groups = mxlsx.convert_xlsx_groups_to_dataframe(xlsx_file_name)
    students_complete = mxlsx.convert_xlsx_complete_to_dataframe(xlsx_k_file_name)

    mutils.calculate_group_availability(STUDENTS_PER_GROUP, classroom_availability_by_groups, xlsx_file_name, students_groups)

    # We incrementally add data to dataframes
    students_in_groups = pd.concat([students_in_groups, students_groups], ignore_index=True)
    students_in_complete = pd.concat([students_in_complete, students_complete], ignore_index=True)

    # Check if students in groups are also in complete list
    students_in_groups_missing_from_complete = students_groups[~students_groups['Broj indeksa'].isin(students_complete['Broj indeksa'])]
    if not students_in_groups_missing_from_complete.empty:
        missing_students.append(students_in_groups_missing_from_complete)

if missing_students:
    print("Studenti koji su u grupama, a nisu u kompletnom spisku: ")
    for df in missing_students:
        print(df)
print()
# Drop "Redni broj" column from df_groups_combined
students_in_groups = students_in_groups.drop(columns="Redni_broj")

# Add column Smer, which is first two letters "Broj indeksa"
students_in_groups['Smer'] = students_in_groups['Broj indeksa'].str[:2]

mstats.student_status_stats(students_in_complete)
mstats.student_not_regular_in_group_stats(students_in_groups, students_in_complete)

print("Broj grupa po smerovima: ")
for smer, group_stats in classroom_availability_by_groups:
    nonzero_groups = group_stats[group_stats > 0]
    if not nonzero_groups.empty:
        print(f"Smer: {smer}")
        for grupa, slobodna_mesta in nonzero_groups.items():
            print(f"  Grupa {grupa}: {slobodna_mesta} slobodnih mesta")
print("=============================")

print("Ukupan broj mesta u svim grupama: ")
total_available_places = sum(df_group_stats.sum() for _, df_group_stats in classroom_availability_by_groups
)
print(total_available_places)
print()

# Load data from xlsx/PRIJAVE.xlsx
students_poll = pd.read_excel("xlsx/PRIJAVE.xlsx")
students_poll = students_poll[["Ime", "Prezime", "Smer", "Broj upisa", "Godina upisa"]].copy()
students_poll["Broj indeksa"] = (
    students_poll["Smer"] + " " +
    students_poll["Broj upisa"].astype(str) + "/" +
    students_poll["Godina upisa"].astype(str)
)
students_poll = students_poll[["Ime", "Prezime", "Broj indeksa"]]

print("Broj studenata u prijavama: ", len(students_poll))
students_poll = mutils.refactor_indexes(students_poll)
students_poll = students_poll.drop_duplicates(subset="Broj indeksa").reset_index(drop=True)
print("Broj studenata u prijavama nakon izbacivanja duplikata: ", len(students_poll))

EXCLUDE_NON_PAYERS = False

if EXCLUDE_NON_PAYERS:
    students_poll = mutils.exclude_non_payers(students_in_complete, students_poll)
    print("Broj studenata u prijavama nakon izbacivanja neplatiša: ", len(students_poll))
    print()

students_poll['Način polaganja'] = students_poll['Broj indeksa'].map(
    students_in_complete.drop_duplicates(subset='Broj indeksa').set_index('Broj indeksa')['Način polaganja']
).fillna('Ponovo sluša')
mstats.student_status_stats(students_poll, poll=True)

students_poll = mutils.remove_polled_students_already_in_group(students_in_groups, students_poll)
grouped = mstats.student_status_stats(students_poll, poll=True)

dfs = [(status,students) for status, students in students_poll.groupby('Način polaganja')]
dfs = mutils.prioritize_new_students(dfs)

appointed_student_indexes = []
no_students_before_first_appointing = len(students_in_groups)

students_in_groups = mutils.appoint_to_existing_groups(students_in_groups, classroom_availability_by_groups, dfs, appointed_student_indexes)

residual_students = []
mutils.track_residual_students(dfs, appointed_student_indexes, residual_students)

no_students_after_first_appointing = len(students_in_groups)

if no_students_after_first_appointing - no_students_before_first_appointing != len(appointed_student_indexes):
    print("Greška: Broj raspoređenih studenata nije jednak razlici broja studenata pre i posle raspoređivanja.")
    print("Proverite da li su studenti pravilno raspoređeni.")
    exit(1)

students_in_groups["Grupa"] = students_in_groups["Grupa"].astype(int)

students_in_groups = students_in_groups.sort_values(["Smer", "Grupa"]).reset_index(drop=True)

# Set control column "RB" and "RBG", these mean "Redni Broj" and "Redni Broj u Grupi" (control numbers)
students_in_groups['RB'] = students_in_groups.index + 1
students_in_groups['RBG'] = students_in_groups.index % STUDENTS_PER_GROUP + 1

students_in_groups = students_in_groups[["RB", 'RBG', "Smer", "Grupa", "Broj indeksa", "Prezime", "Ime"]]

students_in_groups.to_excel("schedules/regular_groups.xlsx", index=False)

df_additional_classrooms = pd.read_csv("additional-classrooms/classrooms.csv")
df_additional_classrooms = df_additional_classrooms.sort_values(["Termin", "Ucionica"]).reset_index(drop=True)
print("Ucitao dodatne ucionice: ")
print(df_additional_classrooms)

# Convert residual_students to DataFrame
df_residual_students = pd.DataFrame(residual_students)
df_residual_students.reset_index(drop=True, inplace=True)

# Add column "Ucionica" and "Termin" to df_residual_students
df_residual_students["Ucionica"] = ""
df_residual_students["Termin"] = ""

additional_students_appointed = 0
additional_students_to_appoint = len(df_residual_students)

# For each classroom in df_additional_classrooms
additional_students_appointed = mutils.appoint_residual_students(df_additional_classrooms, df_residual_students, additional_students_appointed, additional_students_to_appoint)

if additional_students_appointed != additional_students_to_appoint:
    print("Greška: Broj raspoređenih studenata nije jednak broju studenata koje treba rasporediti.")
    print("Proverite da li su studenti pravilno raspoređeni.")
    exit(1)

# Set control column "RB"
df_residual_students["RB"] = df_residual_students.index + 1

# Convert RBG column to int
df_residual_students["RBG"] = df_residual_students["RBG"].astype(int)

# Change order of columns in df_residual_students to: "RB", "RBG", "Termin", "Ucionica", "Broj indeksa", "Prezime", "Ime"
df_residual_students = df_residual_students[["RB", "RBG", "Termin", "Ucionica", "Broj indeksa", "Prezime", "Ime"]]

# Export df_residual_students to schedules/additional_groups.xlsx
df_residual_students.to_excel("schedules/additional_groups.xlsx", index=False)
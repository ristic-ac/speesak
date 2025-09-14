# Import custom module from modules/xlsx.py
import modules.xlsx as mxlsx
import modules.os as mos
import modules.stats as mstats
import modules.utils as mutils
import pandas as pd
import sys
import os
from dotenv import load_dotenv

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

# Determine which PRIJAVE file(s) to load based on .env variable or command-line argument

load_dotenv()
provera = os.getenv("PROVERA", "").lower()

if provera == "domaci":
    prijave_filenames = ["xlsx/PRIJAVE-SOV.xlsx", "xlsx/PRIJAVE-DOMACI.xlsx"]
elif provera == "t1234":
    prijave_filenames = ["xlsx/PRIJAVE-T1234.xlsx"]
else:
    # Exit with error if provera is not set correctly
    print("Greška: Nije postavljen ili je neispravan parametar PROVERA. Dozvoljeni parametri su: t1234, domaci")
    sys.exit(1)

# Rename variables for clarity
students_to_appoint = pd.DataFrame()   # Students who are to be appointed to groups
students_to_exclude = pd.DataFrame()   # Students who are to be excluded from further processing

# If domaci mode
if len(prijave_filenames) == 2 and provera == "domaci":
    students_poll_sov = pd.read_excel(prijave_filenames[0])
    students_poll_sov = students_poll_sov[["Ime", "Prezime", "Smer", "Broj upisa", "Godina upisa"]].copy()
    students_poll_sov["Broj indeksa"] = (
        students_poll_sov["Smer"] + " " +
        students_poll_sov["Broj upisa"].astype(str) + "/" +
        students_poll_sov["Godina upisa"].astype(str)
    )
    students_poll_sov = students_poll_sov[["Ime", "Prezime", "Broj indeksa"]]

    students_poll_domaci = pd.read_excel(prijave_filenames[1])
    students_poll_domaci = students_poll_domaci[["Ime", "Prezime", "Smer", "Broj upisa", "Godina upisa"]].copy()
    students_poll_domaci["Broj indeksa"] = (
        students_poll_domaci["Smer"] + " " +
        students_poll_domaci["Broj upisa"].astype(str) + "/" +
        students_poll_domaci["Godina upisa"].astype(str)
    )
    students_poll_domaci = students_poll_domaci[["Ime", "Prezime", "Broj indeksa"]]

    # Exclude students from domaci, include only sov
    students_to_appoint = students_poll_sov
    students_to_exclude = students_poll_domaci
# If T1234 mode
elif len(prijave_filenames) == 1 and provera == "t1234":
    students_poll_t1234 = pd.read_excel(prijave_filenames[0])
    students_poll_t1234 = students_poll_t1234[["Ime", "Prezime", "Smer", "Broj upisa", "Godina upisa"]].copy()
    students_poll_t1234["Broj indeksa"] = (
        students_poll_t1234["Smer"] + " " +
        students_poll_t1234["Broj upisa"].astype(str) + "/" +
        students_poll_t1234["Godina upisa"].astype(str)
    )
    students_to_appoint = students_poll_t1234[["Ime", "Prezime", "Broj indeksa"]]
else:
    exit("Nepoznat parametar. Dozvoljeni parametri su: t1234, domaci")

print("Broj studenata u prijavama za izradu u učionicama: ", len(students_to_appoint))
students_to_appoint = mutils.refactor_indexes(students_to_appoint)
students_to_appoint = students_to_appoint.drop_duplicates(subset="Broj indeksa").reset_index(drop=True)
print("Broj studenata u prijavama nakon izbacivanja duplikata: ", len(students_to_appoint))

# If domaci mode, do the same for students_to_exclude
if len(prijave_filenames) == 2 and provera == "domaci":
    students_to_exclude = mutils.refactor_indexes(students_to_exclude)
    students_to_exclude = students_to_exclude.drop_duplicates(subset="Broj indeksa").reset_index(drop=True)
    print("Broj studenata koji se izuzimaju iz rasporeda jer su odabrali domaći: ", len(students_to_exclude))

EXCLUDE_NON_PAYERS = False

if EXCLUDE_NON_PAYERS:
    students_to_appoint = mutils.exclude_non_payers(students_in_complete, students_to_appoint)
    print("Broj studenata u prijavama nakon izbacivanja neplatiša: ", len(students_to_appoint))
    print()

students_to_appoint['Način polaganja'] = students_to_appoint['Broj indeksa'].map(
    students_in_complete.drop_duplicates(subset='Broj indeksa').set_index('Broj indeksa')['Način polaganja']
).fillna('Ponovo sluša')
mstats.student_status_stats(students_to_appoint, poll=True)

students_to_appoint = mutils.remove_polled_students_already_in_group(students_in_groups, students_to_appoint)
grouped = mstats.student_status_stats(students_to_appoint, poll=True)

# If domaci mode, exclude students_to_exclude from students_in_groups and students_to_appoint
if len(prijave_filenames) == 2 and provera == "domaci":
    # Find students who are in both appoint and exclude lists
    in_both = students_to_appoint[students_to_appoint['Broj indeksa'].isin(students_to_exclude['Broj indeksa'])]
    students_in_groups = students_in_groups[~students_in_groups['Broj indeksa'].isin(students_to_exclude['Broj indeksa'])]
    students_to_appoint = students_to_appoint[~students_to_appoint['Broj indeksa'].isin(students_to_exclude['Broj indeksa'])]
    print("Broj studenata u grupama nakon izbacivanja: ", len(students_in_groups))
    print("Broj studenata u prijavama nakon izbacivanja: ", len(students_to_appoint))
    # Reset classroom_availability_by_groups
    classroom_availability_by_groups = []
    # Calculate group stats after exclusion, each group should have 16 places in total, calculate from students_in_groups column "Grupa"
    mutils.calculate_group_availability(STUDENTS_PER_GROUP, classroom_availability_by_groups, None, students_in_groups)
    print("Broj grupa po smerovima nakon izbacivanja: ")
    for smer, group_stats in classroom_availability_by_groups:
        nonzero_groups = group_stats[group_stats > 0]
        if not nonzero_groups.empty:
            print(f"Smer: {smer}")
            for grupa, slobodna_mesta in nonzero_groups.items():
                print(f"  Grupa {grupa}: {slobodna_mesta} slobodnih mesta")
    print("=============================")


dfs = [(status,students) for status, students in students_to_appoint.groupby('Način polaganja')]
dfs = mutils.prioritize_new_students(dfs)

appointed_student_indexes = []
no_students_before_first_appointing = len(students_in_groups)
print("Broj studenata pre prvog raspoređivanja: ", no_students_before_first_appointing)

if provera == "domaci":
    students_in_groups = mutils.appoint_using_average(students_in_groups, classroom_availability_by_groups, dfs, appointed_student_indexes)
else:
    students_in_groups = mutils.appoint_to_existing_groups(students_in_groups, classroom_availability_by_groups, dfs, appointed_student_indexes)
print("Stanje grupa POSLE raspoređivanja:")
residual_students = []
mutils.track_residual_students(dfs, appointed_student_indexes, residual_students)

no_students_after_first_appointing = len(students_in_groups)

print("Broj studenata posle prvog raspoređivanja: ", no_students_after_first_appointing)
print("Broj raspoređenih studenata: ", len(appointed_student_indexes))

if no_students_after_first_appointing - no_students_before_first_appointing != len(appointed_student_indexes):
    print("Greška: Broj raspoređenih studenata nije jednak razlici broja studenata pre i posle raspoređivanja.")
    print("Proverite da li su studenti pravilno raspoređeni.")
    exit(1)

students_in_groups["Grupa"] = students_in_groups["Grupa"].astype(int)

students_in_groups = students_in_groups.sort_values(["Smer", "Grupa"]).reset_index(drop=True)

# Set control column "RB" and "RBG", these mean "Redni Broj" and "Redni Broj u Grupi" (control numbers)
students_in_groups['RB'] = students_in_groups.index + 1
students_in_groups['RBG'] = students_in_groups.groupby(['Smer', 'Grupa']).cumcount() + 1

students_in_groups = students_in_groups[["RB", 'RBG', "Smer", "Grupa", "Broj indeksa", "Prezime", "Ime"]]

# Create domaci and t1234 folders if they do not exist
os.makedirs("schedules/domaci", exist_ok=True)
os.makedirs("schedules/t1234", exist_ok=True)

# Save students_in_groups to the appropriate file based on the mode
if len(prijave_filenames) == 2 and provera == "domaci":
    out_path = "schedules/domaci/regular_groups.xlsx"
else:
    out_path = "schedules/t1234/regular_groups.xlsx"

students_in_groups.to_excel(out_path, index=False)

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

# Only export if there are any additionally appointed students
if not df_residual_students.empty:
    # Set control column "RB"
    df_residual_students["RB"] = df_residual_students.index + 1

    # Convert RBG column to int
    df_residual_students["RBG"] = df_residual_students["RBG"].astype(int)

    # Change order of columns 
    df_residual_students = df_residual_students[["RB", "RBG", "Termin", "Ucionica", "Broj indeksa", "Prezime", "Ime"]]

    # Export df_residual_students to schedules/additional_groups.xlsx
    if len(prijave_filenames) == 2 and provera == "domaci":
        df_residual_students.to_excel("schedules/domaci/additional_groups.xlsx", index=False)
    else:
        df_residual_students.to_excel("schedules/t1234/additional_groups.xlsx", index=False)

if provera == "domaci":
    if not in_both.empty:
        print("Studenti koji su i u prijavama za učionicu i za domaći (duplikati):")
        print(in_both)
print("Kraj programa.")
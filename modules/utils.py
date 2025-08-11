import pandas as pd

# Funkcija za refaktorisanje indeksa u DataFrame-u (ukoliko se koriste odvojeni text-boxovi na anketi ovo je maltene nepotrebno koristiti)
def refactor_indexes(df_poll):
    df_poll_index = df_poll['Broj indeksa']
    df_poll_index = df_poll_index.str.extract(r"([A-Za-z]{2})\s?(\d+)[\/-](\d+)")

    if len(df_poll_index) != len(df_poll):
        print("Greška: Broj izvučenih podataka nije jednak broju redova u df_poll, verovatno zbog formata regularnog izraza.")
        print("Proverite regex i promenite ga da odgovara formatu 'Broj indeksa' u PRIJAVE.xlsx")
        exit(1)

    df_poll['Broj indeksa'] = df_poll_index[0].str.upper() + " " + df_poll_index[1] + "/" + df_poll_index[2]
    return df_poll

# Funkcija za izbacivanje studenata koji nisu platili
def exclude_non_payers(df_complete_combined, df_poll):
    df_poll_not_in_complete = df_poll[~df_poll['Broj indeksa'].isin(df_complete_combined['Broj indeksa'])]
    print("Broj studenata u prijavama koji nisu u kompletnoj listi (nisu platili): ", len(df_poll_not_in_complete)) # TODO: Check if missing from complete are non-payers
    if not df_poll_not_in_complete.empty:
        print("Studenti u prijavama koji nisu u kompletnoj listi: ")
        print(df_poll_not_in_complete)
    print()
    df_poll = df_poll[~df_poll['Broj indeksa'].isin(df_poll_not_in_complete['Broj indeksa'])]
    df_poll = df_poll.reset_index(drop=True)
    return df_poll

# Funkcija za izračunavanje dostupnosti grupa (koliko praznih mesta ima u grupama)
def calculate_group_availability(STUDENTS_PER_GROUP, availability_by_groups, xlsx_file, df_groups):
    df_group_stats = df_groups.groupby("Grupa").size().sort_index()
    df_group_stats = STUDENTS_PER_GROUP - df_group_stats
    study_program = xlsx_file[:2]
    availability_by_groups.append((study_program, df_group_stats))

# Funkcija za uklanjanje studenata koji su već u grupama a prijavili se na anketi
def remove_polled_students_already_in_group(df_groups_combined, df_poll):
    df_poll_in_groups = df_poll[df_poll['Broj indeksa'].isin(df_groups_combined['Broj indeksa'])].reset_index(drop=True)
    print("Broj studenata u prijavama koji su već u grupama: ", len(df_poll_in_groups))
    if not df_poll_in_groups.empty:
        print("Studenti u prijavama koji su već u grupama: ")
        print(df_poll_in_groups)
    print()
    df_poll = df_poll[~df_poll['Broj indeksa'].isin(df_poll_in_groups['Broj indeksa'])] # 
    return df_poll

# Funkcija za prioritizaciju studenata koji prvi put slušaju predmet
def prioritize_new_students(dfs):
    for i in range(len(dfs)):
        if dfs[i][0] == 'Prvi put sluša (Unapred slušanje)':
            dfs[0], dfs[i] = dfs[i], dfs[0]
            break
    return dfs

# Funkcija za pronalaženje grupe sa slobodnim mestom
def find_group(availability_by_groups):
    for study_program, availability_groups in availability_by_groups:
        for group, availability in availability_groups.items():
            if availability <= 0:
                continue
            availability_groups[group] = availability - 1
            return study_program, group
    return None, None

# Funkcija za dodeljivanje studenata postojećim grupama
def appoint_to_existing_groups(df_groups_combined, availability_by_groups, dfs, appointed_student_indexes):
    for status, students in dfs:
        for index, student in students.iterrows():
            study_program, group = find_group(availability_by_groups)
            if group is None:
                print("Nema više dostupnih grupa za dodeljivanje studenata.")
                break
            new_row = pd.DataFrame([{"Grupa": group, "Broj indeksa": student["Broj indeksa"], "Prezime": student["Prezime"], "Ime": student["Ime"], "Smer": study_program}])
            df_groups_combined = pd.concat([df_groups_combined, new_row], ignore_index=True)
            appointed_student_indexes.append(student["Broj indeksa"])
    return df_groups_combined

# Funkcija za praćenje preostalih studenata koji nisu dodeljeni
def track_residual_students(dfs, appointed_student_indexes, residual_students):
    for status, students in dfs:
        for index, student in students.iterrows():
            if student["Broj indeksa"] not in appointed_student_indexes:
                residual_students.append(student)

# Funkcija za dodeljivanje preostalih studenata u dodatne učionice
def appoint_residual_students(df_additional_classrooms, df_residual_students, additional_students_appointed, additional_students_to_appoint):
    BROJ_MI = 32
    BROJ_NTP = 16
    for index, row in df_additional_classrooms.iterrows():
        classroom = row["Ucionica"]
        time = row["Termin"]
        if classroom[:2] == "MI":
            for _ in range(BROJ_MI):
                if additional_students_appointed >= additional_students_to_appoint:
                    print("Dodeljeni su svi studenti.")
                    return additional_students_appointed
                df_residual_students.loc[additional_students_appointed, "Ucionica"] = classroom
                df_residual_students.loc[additional_students_appointed, "Termin"] = time
                df_residual_students.loc[additional_students_appointed, "RBG"] = int(additional_students_appointed % BROJ_MI + 1)
                additional_students_appointed += 1

        elif classroom[:3] == "NTP":
            for _ in range(BROJ_NTP):
                if additional_students_appointed >= additional_students_to_appoint:
                    print("Dodeljeni su svi studenti.")
                    return additional_students_appointed
                df_residual_students.loc[additional_students_appointed, "Ucionica"] = classroom
                df_residual_students.loc[additional_students_appointed, "Termin"] = time
                df_residual_students.loc[additional_students_appointed, "RBG"] = int(additional_students_appointed % BROJ_NTP + 1)
                additional_students_appointed += 1
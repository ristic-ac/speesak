def refactor_indexes(df_poll):
    df_poll_index = df_poll['Broj indeksa']
    df_poll_index = df_poll_index.str.extract(r"([A-Za-z]{2})\s?(\d+)[\/-](\d+)")

    if len(df_poll_index) != len(df_poll):
        print("Error: Number of extracted data is not equal to number of rows in df_poll, possibly because of regex format.")
        print("Lookup regex and change it to match the format of 'Broj indeksa' in PRIJAVE.xlsx")
        exit(1)

    df_poll['Broj indeksa'] = df_poll_index[0] + " " + df_poll_index[1] + "/" + df_poll_index[2]
    df_poll = df_poll.drop_duplicates(subset="Broj indeksa")
    return df_poll

def exclude_non_payers(df_complete_combined, df_poll):
    df_poll_not_in_complete = df_poll[~df_poll['Broj indeksa'].isin(df_complete_combined['Broj indeksa'])]
    print("Students from poll that are not in complete list: ")
    print(df_poll_not_in_complete)
    df_poll = df_poll[~df_poll['Broj indeksa'].isin(df_poll_not_in_complete['Broj indeksa'])]
    return df_poll

def calculate_group_availability(STUDENTS_PER_GROUP, availability_by_groups, xlsx_file, df_groups):
    df_group_stats = df_groups.groupby("Grupa").size().sort_index()
    df_group_stats = STUDENTS_PER_GROUP - df_group_stats
    study_program = xlsx_file[:2]
    availability_by_groups.append((study_program, df_group_stats))

def find_inconsistencies(df_groups, df_merged):
    df_in_groups_not_in_complete = df_groups[~df_groups['Broj indeksa'].isin(df_merged['Broj indeksa'])]
    if len(df_in_groups_not_in_complete) > 0:
        print("Students in groups that are not in complete list: ")
        print(df_in_groups_not_in_complete)

def remove_polled_students_already_in_group(df_groups_combined, df_poll):
    df_poll_in_groups = df_poll[df_poll['Broj indeksa'].isin(df_groups_combined['Broj indeksa'])]
    print("Students in poll that are in groups: ")
    print(df_poll_in_groups)
    df_poll = df_poll[~df_poll['Broj indeksa'].isin(df_poll_in_groups['Broj indeksa'])]
    return df_poll

def prioritize_new_students(dfs):
    for i in range(len(dfs)):
        if dfs[i][0] == 'Prvi put sluša (Unapred slušanje)':
            dfs[0], dfs[i] = dfs[i], dfs[0]
            break
    return dfs


def find_group(availability_by_groups):
    for study_program, availability_groups in availability_by_groups:
        for group, availability in availability_groups.iteritems():
            if availability <= 0:
                continue
            availability_groups[group] = availability - 1
            return study_program, group
    return None, None

def appoint_to_existing_groups(df_groups_combined, availability_by_groups, dfs, appointed_student_indexes):
    for status, students in dfs:
    # Foreach row in students
        for index, student in students.iterrows():
            study_program, group = find_group(availability_by_groups)
            if group is None:
                print("No more groups available.")
                break
        # Add student to df_groups_combined
            df_groups_combined = df_groups_combined.append({"Grupa": group, "Broj indeksa": student["Broj indeksa"], "Prezime": student["Prezime"], "Ime": student["Ime"], "Smer": study_program}, ignore_index=True)
            appointed_student_indexes.append(student["Broj indeksa"])
    return df_groups_combined

def track_residual_students(dfs, appointed_student_indexes, residual_students):
    for status, students in dfs:
        for index, student in students.iterrows():
            if student["Broj indeksa"] not in appointed_student_indexes:
                residual_students.append(student)

def appoint_residual_students(df_additional_classrooms, df_residual_students, additional_students_appointed, additional_students_to_appoint):
    for index, row in df_additional_classrooms.iterrows():
        classroom = row["Ucionica"]
        time = row["Termin"]
        if classroom[:2] == "MI":
            for _ in range(32):
                if additional_students_appointed >= additional_students_to_appoint:
                    print("Appointed all students.")
                    return additional_students_appointed
                df_residual_students.loc[additional_students_appointed, "Ucionica"] = classroom
                df_residual_students.loc[additional_students_appointed, "Termin"] = time
                additional_students_appointed += 1
        elif classroom[:3] == "NTP":
            for _ in range(16):
                if additional_students_appointed >= additional_students_to_appoint:
                    print("Appointed all students.")
                    return additional_students_appointed
                df_residual_students.loc[additional_students_appointed, "Ucionica"] = classroom
                df_residual_students.loc[additional_students_appointed, "Termin"] = time
                additional_students_appointed += 1
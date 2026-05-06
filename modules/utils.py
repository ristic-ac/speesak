import pandas as pd

def refactor_indexes(df_poll):
    """
    Refaktoriše kolonu 'Broj indeksa' u datom DataFrame-u u standardizovani format.

    Ova funkcija izdvaja i preformatira brojeve indeksa iz kolone 'Broj indeksa',
    očekujući da odgovaraju obrascu: dva slova, opciono razmak, cifre, '/', ili '-', i još cifara.
    Preformatirani indeks će biti u obliku 'AA NNNN/YY', gde:
        - 'AA' su velika slova,
        - 'NNNN' su cifre (broj indeksa),
        - 'YY' su cifre (godina).

    Ako broj izvučenih redova ne odgovara ulaznom DataFrame-u, funkcija ispisuje grešku
    i prekida program.

    Argumenti:
        df_poll (pd.DataFrame): DataFrame koji sadrži kolonu 'Broj indeksa' sa brojevima indeksa za preformatiranje.

    Povratna vrednost:
        pd.DataFrame: Ulazni DataFrame sa preformatiranom kolonom 'Broj indeksa'.

    Izuzeci:
        SystemExit: Ako broj izvučenih redova nije jednak broju redova u ulaznom DataFrame-u.
    """
    df_poll_index = df_poll['Broj indeksa']
    df_poll_index = df_poll_index.str.extract(r"([A-Za-z]{2})\s?(\d+)[\/-](\d+)")

    if len(df_poll_index) != len(df_poll):
        print("Greška: Broj izvučenih podataka nije jednak broju redova u df_poll, verovatno zbog formata regularnog izraza.")
        print("Proverite regex i promenite ga da odgovara formatu 'Broj indeksa' u PRIJAVE.xlsx")
        exit(1)

    df_poll['Broj indeksa'] = df_poll_index[0].str.upper() + " " + df_poll_index[1] + "/" + df_poll_index[2]
    return df_poll

def exclude_non_payers(df_complete_combined, df_poll):
    """
    Uklanja studente iz DataFrame-a prijava koji nisu prisutni u kompletnom kombinovanom DataFrame-u,
    čiji 'Način polaganja' nije jedan od dozvoljenih, ili čiji 'Studijski program/modul' je 'Nije upisao tekuću školsku godinu'.

    Dozvoljeni 'Način polaganja':
        - 'Polaže preko kolokvijuma'
        - 'Prvi put sluša (Redovno)'
        - 'Ponovo sluša'
        - 'Prvi put sluša (Unapred slušanje)'

    Argumenti:
        df_complete_combined (pd.DataFrame): DataFrame sa kompletnom listom studenata.
        df_poll (pd.DataFrame): DataFrame sa prijavljenim studentima.

    Povratna vrednost:
        pd.DataFrame: Filtrirani df_poll sa samo validnim studentima.

    Sporedni efekti:
        Ispisuje broj i detalje studenata iz df_poll koji su isključeni, sa razlogom isključenja.
    """
    allowed_nacin = [
        'Polaže preko kolokvijuma',
        'Prvi put sluša (Redovno)',
        'Ponovo sluša',
        'Prvi put sluša (Unapred slušanje)'
    ]
    # Mapiranje indeksa na način polaganja i studijski program/modul
    nacin_map = df_complete_combined.set_index('Broj indeksa')['Način polaganja'].to_dict()
    program_map = df_complete_combined.set_index('Broj indeksa')['Studijski program/modul'].to_dict()

    reasons = []
    mask = []

    for idx, row in df_poll.iterrows():
        broj_indeksa = row['Broj indeksa']
        nacin = nacin_map.get(broj_indeksa, None)
        program = program_map.get(broj_indeksa, None)
        if nacin is None or program is None:
            reasons.append("Nije pronađen u kompletnoj listi")
            mask.append(False)
        elif nacin not in allowed_nacin:
            reasons.append(f"Neodgovarajući Način polaganja: {nacin}")
            mask.append(False)
        elif program == 'Nije upisao tekuću školsku godinu':
            reasons.append("Nije upisao tekuću školsku godinu")
            mask.append(False)
        else:
            reasons.append("")
            mask.append(True)

    df_poll = df_poll.copy()
    df_poll['Razlog isključenja'] = reasons
    df_excluded = df_poll[~pd.Series(mask)]
    print("Broj studenata u prijavama koji nisu u kompletnoj listi ili imaju neodgovarajući Način polaganja ili nisu upisali tekuću godinu: ", len(df_excluded))
    if not df_excluded.empty:
        print("Studenti u prijavama koji su isključeni sa razlogom: ")
        print(df_excluded[['Broj indeksa', 'Prezime', 'Ime', 'Razlog isključenja']])
    print()
    return df_poll[pd.Series(mask)].reset_index(drop=True)

import pandas as pd

def calculate_group_availability(STUDENTS_PER_GROUP, availability_by_groups, xlsx_file, df_groups):
    """
    Izračunava preostalu dostupnost za svaku grupu i dodaje rezultat u prosleđenu listu.

    Argumenti:
        STUDENTS_PER_GROUP (int): Maksimalan broj studenata dozvoljen po grupi.
        availability_by_groups (list): Lista kojoj se dodaje izračunata dostupnost po grupama.
        xlsx_file (str | None): Naziv Excel fajla (ako postoji). Ako nije prosleđen, 
                                koristi se kolona 'Broj indeksa' za određivanje studijskog programa.
        df_groups (pandas.DataFrame): DataFrame koji sadrži raspodelu po grupama sa kolonom "Grupa"
                                      i opciono kolonom "Broj indeksa".

    Povratna vrednost:
        None: Funkcija rezultate dodaje direktno u availability_by_groups listu.

    Sporedni efekti:
        Menja availability_by_groups listu dodavanjem torka koji sadrži identifikator studijskog programa i Series sa dostupnošću po grupama.
    """

    # Grupisanje po kolonama "Grupa" i računanje koliko studenata ima po grupi
    df_group_stats = df_groups.groupby("Grupa").size().sort_index()

    # Računanje preostalih mesta po grupi
    df_group_stats = STUDENTS_PER_GROUP - df_group_stats

    # Određivanje studijskog programa i dodavanje rezultata
    if xlsx_file:
        study_program = xlsx_file[:2]  # Prva dva slova fajla, npr. RA, IN, PR
        availability_by_groups.append((study_program, df_group_stats))
    else:
        if "Broj indeksa" in df_groups.columns:
            # Grupisanje po smeru (prva dva slova broja indeksa)
            df_groups['Smer'] = df_groups['Broj indeksa'].astype(str).str[:2]
            for smer, group in df_groups.groupby('Smer'):
                group_stats = group.groupby("Grupa").size().sort_index()
                group_stats = STUDENTS_PER_GROUP - group_stats
                availability_by_groups.append((smer, group_stats))
            # Nakon korišćenja, možemo ukloniti privremenu kolonu 'Smer'
            # df_groups.drop(columns=['Smer'], inplace=True)
        else:
            raise ValueError("Nije prosleđen xlsx_file niti kolona 'Broj indeksa' za određivanje studijskog programa.")


def remove_polled_students_already_in_group(df_groups_combined, df_poll):
    """
    Uklanja studente iz DataFrame-a prijava koji su već prisutni u DataFrame-u grupa.

    Ova funkcija proverava koji studenti iz `df_poll` (DataFrame prijava) su već uključeni u `df_groups_combined` (DataFrame grupa) na osnovu kolone 'Broj indeksa'. Ispisuje broj i detalje takvih studenata, a zatim vraća filtriranu verziju `df_poll` bez tih studenata.

    Argumenti:
        df_groups_combined (pd.DataFrame): DataFrame koji sadrži studente već raspoređene u grupe, sa kolonom 'Broj indeksa'.
        df_poll (pd.DataFrame): DataFrame koji sadrži studente koji su se prijavili, sa kolonom 'Broj indeksa'.

    Povratna vrednost:
        pd.DataFrame: Filtrirani DataFrame koji sadrži samo studente iz `df_poll` koji nisu već u `df_groups_combined`.
    """
    df_poll_in_groups = df_poll[df_poll['Broj indeksa'].isin(df_groups_combined['Broj indeksa'])].reset_index(drop=True)
    print("Broj studenata u prijavama koji su već u grupama: ", len(df_poll_in_groups))
    if not df_poll_in_groups.empty:
        print("Studenti u prijavama koji su već u grupama: ")
        print(df_poll_in_groups)
    print()
    df_poll = df_poll[~df_poll['Broj indeksa'].isin(df_poll_in_groups['Broj indeksa'])] # 
    return df_poll

def prioritize_new_students(dfs):
    """
    Preraspoređuje listu tako da prvi podspisak odgovara studentima koji prvi put slušaju predmet.

    Argumenti:
        dfs (list of list): Lista gde je svaki element podlista koja predstavlja zapis o studentu.
            Prvi element svake podliste treba da bude string koji označava status studenta.

    Povratna vrednost:
        list of list: Preraspoređena lista sa podlistom za nove studente (gde je prvi element
            'Prvi put sluša (Unapred slušanje)') pomerenom na početak. Ako takva podlista ne postoji,
            lista se vraća neizmenjena.
    """
    for i in range(len(dfs)):
        if dfs[i][0] == 'Prvi put sluša (Unapred slušanje)':
            dfs[0], dfs[i] = dfs[i], dfs[0]
            break
    return dfs

def find_group(availability_by_groups):
    """
    Pronalazi i rezerviše dostupnu grupu iz kolekcije studijskih programa i njihovih dostupnosti po grupama.

    Iterira kroz prosleđenu mapu dostupnosti, tražeći prvu grupu sa dostupnošću većom od nule.
    Ako se takva grupa pronađe, smanjuje njenu dostupnost za jedan i vraća odgovarajući studijski program i grupu.
    Ako nema dostupnih grupa, vraća (None, None).

    Argumenti:
        availability_by_groups (Iterable[Tuple[Any, Dict[Any, int]]]): 
            Iterabilna kolekcija torki, gde svaka torka sadrži studijski program i rečnik koji mapira identifikatore grupa na broj preostalih mesta.

    Povratna vrednost:
        Tuple[Any, Any]: 
            Torka koja sadrži studijski program i identifikator prve pronađene dostupne grupe, ili (None, None) ako nema dostupnih grupa.
    """
    for study_program, availability_groups in availability_by_groups:
        for group, availability in availability_groups.items():
            if availability <= 0:
                continue
            availability_groups[group] = availability - 1
            return study_program, group
    return None, None

def appoint_to_existing_groups(df_groups_combined, availability_by_groups, dfs, appointed_student_indexes):
    """
    Dodeljuje studente postojećim grupama na osnovu dostupnosti i ažurira objedinjeni DataFrame grupa.

    Argumenti:
        df_groups_combined (pd.DataFrame): DataFrame sa svim trenutno raspoređenim studentima i njihovim grupama.
        availability_by_groups (list): Lista torki gde svaka torka sadrži identifikator studijskog programa i dostupnost po grupama.
        dfs (list of tuples): Lista torki gde svaka torka sadrži status i DataFrame studenata za dodelu.
        appointed_student_indexes (list): Lista u koju se dodaju brojevi indeksa studenata koji su dodeljeni grupama.

    Povratna vrednost:
        pd.DataFrame: Ažurirani DataFrame sa novododeljenim studentima u odgovarajuće grupe.

    Sporedni efekti:
        Menja listu appointed_student_indexes dodavanjem brojeva indeksa dodeljenih studenata.
        Ispisuje poruku ako nema više dostupnih grupa za dodelu.
    """
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

def appoint_using_average(df_groups_combined, availability_by_groups, dfs, appointed_student_indexes):
    """
    Dodeljuje studente postojećim grupama tako da se približno izjednači broj studenata po grupi.

    Argumenti:
        df_groups_combined (pd.DataFrame): DataFrame sa svim trenutno raspoređenim studentima i njihovim grupama.
        availability_by_groups (list): Lista torki gde svaka torka sadrži identifikator studijskog programa i dostupnost po grupama.
        dfs (list of tuples): Lista torki gde svaka torka sadrži status i DataFrame studenata za dodelu.
        appointed_student_indexes (list): Lista u koju se dodaju brojevi indeksa studenata koji su dodeljeni grupama.
        students_to_appoint_count (int): Ukupan broj studenata koji će biti dodeljeni.

    Povratna vrednost:
        pd.DataFrame: Ažurirani DataFrame sa novododeljenim studentima u odgovarajuće grupe.
    """

    total_groups = sum(len(group_stats) for _, group_stats in availability_by_groups)
    if total_groups == 0:
        print("Nema grupa za dodelu studenata.")
        return df_groups_combined

    # Pretvori dostupnost u DataFrame radi lakše obrade
    group_availability = []
    for study_program, group_stats in availability_by_groups:
        for grupa, slobodna_mesta in group_stats.items():
            # Broji studente u toj grupi i tom smeru (PR, RA, IN mogu imati istu grupu, ali su odvojeni)
            current_students = df_groups_combined[
                (df_groups_combined["Grupa"] == grupa) & (df_groups_combined["Smer"] == study_program)
            ].shape[0]
            group_availability.append({
                "Smer": study_program,
                "Grupa": grupa,
                "Slobodna_mesta": slobodna_mesta,
                "Trenutno_studenata": current_students
            })
    
    df_avail = pd.DataFrame(group_availability)

    # Dodeljujemo studente tako da se popunjavaju grupe sa ispodprosečnim brojem studenata
    for status, students in dfs:
        for index, student in students.iterrows():
            df_avail = df_avail.sort_values(by=["Trenutno_studenata", "Slobodna_mesta"], ascending=[True, False])
            target_group = df_avail.iloc[0] if not df_avail.empty else None

            if target_group is None or target_group["Slobodna_mesta"] <= 0:
                print("Nema više dostupnih mesta u grupama.")
                break

            # Dodaj studenta u target grupu
            new_row = pd.DataFrame([{
                "Grupa": target_group["Grupa"],
                "Broj indeksa": student["Broj indeksa"],
                "Prezime": student["Prezime"],
                "Ime": student["Ime"],
                "Smer": target_group["Smer"]
            }])
            df_groups_combined = pd.concat([df_groups_combined, new_row], ignore_index=True)
            appointed_student_indexes.append(student["Broj indeksa"])

            # Ažuriraj dostupnost
            df_avail.loc[df_avail["Grupa"] == target_group["Grupa"], "Trenutno_studenata"] += 1
            df_avail.loc[df_avail["Grupa"] == target_group["Grupa"], "Slobodna_mesta"] -= 1

            # Ispisi stanje nakon svake dodele
            print(f"Dodeljen student {student['Broj indeksa']} u grupu {target_group['Grupa']} (Smer: {target_group['Smer']}).")

    return df_groups_combined


def track_residual_students(dfs, appointed_student_indexes, residual_students):
    """
    Prati i dodaje studente koji nisu dodeljeni u listu preostalih studenata (residual_students).

    Argumenti:
        dfs (list of tuple): Lista gde je svaki element torka koja sadrži status i pandas DataFrame studenata.
        appointed_student_indexes (set ili list): Kolekcija brojeva indeksa studenata koji su već dodeljeni.
        residual_students (list): Lista u koju će biti dodati studenti koji nisu u appointed_student_indexes.

    Povratna vrednost:
        None: Funkcija menja listu residual_students na mestu.
    """
    for status, students in dfs:
        for index, student in students.iterrows():
            if student["Broj indeksa"] not in appointed_student_indexes:
                residual_students.append(student)

def appoint_residual_students(df_additional_classrooms, df_residual_students, additional_students_appointed, additional_students_to_appoint):
    # 1. Prepare Data
    df_rooms = df_additional_classrooms.copy()
    # Clean classroom Smer (remove spaces, handle NaNs)
    df_rooms['Smer'] = df_rooms['Smer'].fillna('').astype(str).str.strip().str.upper()
    
    # Extract Student Smer (first 2 chars of index, uppercase)
    df_residual_students['Smer'] = df_residual_students['Broj indeksa'].str.strip().str[:2].str.upper()
    
    # Initialize assignment columns
    df_residual_students['Ucionica'] = ""
    df_residual_students['Termin'] = ""
    df_residual_students['RBG'] = 0
    
    assigned_indices = set()
    df_rooms['Capacity'] = df_rooms['Ucionica'].apply(
        lambda x: 16 if x == "MI A2-2" or x.startswith("NTP") else 32 if x.startswith("MI") else 0
    )
    df_rooms['Occupancy'] = 0

    # --- PASS 1: TARGETED (IN to IN, RA to RA, PR to PR) ---
    for idx, row in df_rooms.iterrows():
        target = row['Smer']
        if target != "":
            # Find students with matching Smer
            matches = df_residual_students[
                (df_residual_students['Smer'] == target) & 
                (~df_residual_students.index.isin(assigned_indices))
            ].head(int(row['Capacity']))
            
            for s_idx, _ in matches.iterrows():
                occ = int(df_rooms.at[idx, 'Occupancy'])
                df_residual_students.at[s_idx, 'Ucionica'] = row['Ucionica']
                df_residual_students.at[s_idx, 'Termin'] = row['Termin']
                df_residual_students.at[s_idx, 'RBG'] = occ + 1
                assigned_indices.add(s_idx)
                df_rooms.at[idx, 'Occupancy'] += 1

    # --- PASS 2: FILL GAPS (Specified rooms that aren't full yet) ---
    for idx, row in df_rooms.iterrows():
        if row['Smer'] != "":
            remaining = int(row['Capacity'] - row['Occupancy'])
            if remaining > 0:
                rest = df_residual_students[~df_residual_students.index.isin(assigned_indices)].head(remaining)
                for s_idx, _ in rest.iterrows():
                    occ = int(df_rooms.at[idx, 'Occupancy'])
                    df_residual_students.at[s_idx, 'Ucionica'] = row['Ucionica']
                    df_residual_students.at[s_idx, 'Termin'] = row['Termin']
                    df_residual_students.at[s_idx, 'RBG'] = occ + 1
                    assigned_indices.add(s_idx)
                    df_rooms.at[idx, 'Occupancy'] += 1

    # --- PASS 3: GENERAL ROOMS (Unspecified Smer in CSV) ---
    for idx, row in df_rooms.iterrows():
        if row['Smer'] == "":
            remaining = int(row['Capacity'] - row['Occupancy'])
            if remaining > 0:
                gen_fill = df_residual_students[~df_residual_students.index.isin(assigned_indices)].head(remaining)
                for s_idx, _ in gen_fill.iterrows():
                    occ = int(df_rooms.at[idx, 'Occupancy'])
                    df_residual_students.at[s_idx, 'Ucionica'] = row['Ucionica']
                    df_residual_students.at[s_idx, 'Termin'] = row['Termin']
                    df_residual_students.at[s_idx, 'RBG'] = occ + 1
                    assigned_indices.add(s_idx)
                    df_rooms.at[idx, 'Occupancy'] += 1

    return len(assigned_indices)
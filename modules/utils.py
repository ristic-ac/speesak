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

def calculate_group_availability(STUDENTS_PER_GROUP, availability_by_groups, xlsx_file, df_groups):
    """
    Izračunava preostalu dostupnost za svaku grupu i dodaje rezultat u prosleđenu listu.

    Argumenti:
        STUDENTS_PER_GROUP (int): Maksimalan broj studenata dozvoljen po grupi.
        availability_by_groups (list): Lista kojoj se dodaje izračunata dostupnost po grupama.
        xlsx_file (str): Naziv Excel fajla, koristi se za izdvajanje identifikatora studijskog programa.
        df_groups (pandas.DataFrame): DataFrame koji sadrži raspodelu po grupama sa kolonom "Grupa".

    Povratna vrednost:
        None: Funkcija rezultate dodaje direktno u availability_by_groups listu.

    Sporedni efekti:
        Menja availability_by_groups listu dodavanjem torka koji sadrži identifikator studijskog programa i Series sa dostupnošću po grupama.
    """
    df_group_stats = df_groups.groupby("Grupa").size().sort_index()
    df_group_stats = STUDENTS_PER_GROUP - df_group_stats
    study_program = xlsx_file[:2]
    availability_by_groups.append((study_program, df_group_stats))

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
    """
    Dodeljuje preostale studente dodatnim učionicama na osnovu raspoloživog kapaciteta.

    Ova funkcija prolazi kroz prosleđeni DataFrame dodatnih učionica i dodeljuje studente iz DataFrame-a preostalih studenata tim učionicama, ažurirajući njihove podatke o učionici, terminu i broju grupe. Dodeljivanje traje dok se ne dodeli zadati broj dodatnih studenata ili dok se ne popune sva dostupna mesta.

    Argumenti:
        df_additional_classrooms (pd.DataFrame): DataFrame sa informacijama o dodatnim učionicama, sa kolonama "Ucionica" i "Termin".
        df_residual_students (pd.DataFrame): DataFrame studenata koji treba da budu dodeljeni; ažurira se na mestu sa podacima o učionici, terminu i broju grupe.
        additional_students_appointed (int): Trenutni broj već dodeljenih studenata.
        additional_students_to_appoint (int): Ukupan broj studenata koji treba da budu dodeljeni.

    Povratna vrednost:
        int: Ažuriran broj dodeljenih studenata nakon procesa dodele.

    Napomene:
        - Učionice koje počinju sa "MI" imaju kapacitet od 32 studenta.
        - Učionice koje počinju sa "NTP" imaju kapacitet od 16 studenata.
        - Funkcija ažurira kolone 'Ucionica', 'Termin' i 'RBG' u df_residual_students za svakog dodeljenog studenta.
        - Ako su svi studenti dodeljeni pre nego što se popune sva mesta, funkcija ispisuje poruku i vraća se ranije.
    """
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
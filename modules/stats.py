def student_status_stats(df_complete_combined, poll =False):
    """
    Izračunava i prikazuje broj studenata grupisanih po koloni 'Način polaganja'.

    Argumenti:
        df_complete_combined (pandas.DataFrame): DataFrame koji sadrži podatke o studentima, uključujući kolonu 'Način polaganja'.
        poll (bool, opcionalno): Ako je True, ispisuje poruku da su brojevi iz prijava; 
            ako je False, ispisuje da su brojevi iz kompletne liste. Podrazumevano je False.

    Povratna vrednost:
        pandas.Series: Serija sa brojem studenata za svaku jedinstvenu vrednost u koloni 'Način polaganja'.
    """
    df_complete_grouped = df_complete_combined.groupby("Način polaganja").size()
    if poll:
        print("Brojnost studenata po 'Način polaganja' u prijavama: ")
    else:
        print("Brojnost studenata po 'Način polaganja' u kompletnoj listi: ")
    print(df_complete_grouped)
    print()
    return df_complete_grouped

def student_not_regular_in_group_stats(df_groups_combined, df_complete_combined):
    """
    Funkcija za statistiku studenata koji nisu redovni, a nalaze se u grupama.

    Ova funkcija filtrira studente koji u kompletnoj listi nisu označeni kao 'Prvi put sluša (Redovno)',
    pronalazi te studente unutar DataFrame-a sa grupama i ispisuje broj i detalje takvih studenata.

    Argumenti:
        df_groups_combined (pd.DataFrame): DataFrame sa raspodelom studenata po grupama, koji sadrži kolone 'Broj indeksa', 'Grupa', 'Prezime' i 'Ime'.
        df_complete_combined (pd.DataFrame): DataFrame sa kompletnim podacima o studentima, koji sadrži kolone 'Broj indeksa' i 'Način polaganja'.

    Ispisuje:
        - Broj studenata u grupama koji nisu 'Prvi put sluša (Redovno)'.
        - Tabelu sa grupom, brojem indeksa, prezimenom, imenom i načinom slušanja za te studente (ako ih ima).
    """
    df_complete_not_regular = df_complete_combined[df_complete_combined['Način polaganja'] != 'Prvi put sluša (Redovno)']
    df_complete_not_regular_index = df_complete_not_regular['Broj indeksa']
    df_groups_not_regular = df_groups_combined[df_groups_combined['Broj indeksa'].isin(df_complete_not_regular_index)]
    print("Broj studenata u grupama koji nisu 'Prvi put sluša (Redovno)' studenti: ", len(df_groups_not_regular))
    if not df_groups_not_regular.empty:
        print("Studenti u grupama koji nisu 'Prvi put sluša (Redovno)' studenti: ")
        merged = df_groups_not_regular.merge(
            df_complete_not_regular[['Broj indeksa', 'Način polaganja']],
            on='Broj indeksa',
            how='left'
        )
        print(merged[['Grupa', 'Broj indeksa', 'Prezime', 'Ime', 'Način polaganja']])
    print()

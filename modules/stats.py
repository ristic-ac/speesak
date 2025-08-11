# Funkcija za statistiku po Načinu slušanja predmeta
def student_status_stats(df_complete_combined, poll =False):
    df_complete_grouped = df_complete_combined.groupby("Način slušanja").size()
    if poll:
        print("Brojnost studenata po 'Način slušanja' u prijavama: ")
    else:
        print("Brojnost studenata po 'Način slušanja' u kompletnoj listi: ")
    print(df_complete_grouped)
    print()
    return df_complete_grouped

# Funkcija za statistiku studenata koji nisu redovni, a nalaze se u grupama
def student_not_regular_in_group_stats(df_groups_combined, df_complete_combined):
    df_complete_not_regular = df_complete_combined[df_complete_combined['Način slušanja'] != 'Prvi put sluša (Redovno)']
    df_complete_not_regular_index = df_complete_not_regular['Broj indeksa']
    df_groups_not_regular = df_groups_combined[df_groups_combined['Broj indeksa'].isin(df_complete_not_regular_index)]
    print("Broj studenata u grupama koji nisu 'Prvi put sluša (Redovno)' studenti: ", len(df_groups_not_regular))
    if not df_groups_not_regular.empty:
        print("Studenti u grupama koji nisu 'Prvi put sluša (Redovno)' studenti: ")
        merged = df_groups_not_regular.merge(
            df_complete_not_regular[['Broj indeksa', 'Način slušanja']],
            on='Broj indeksa',
            how='left'
        )
        print(merged[['Grupa', 'Broj indeksa', 'Prezime', 'Ime', 'Način slušanja']])
    print()

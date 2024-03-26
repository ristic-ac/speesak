# Group df_complete_combined by "Način slušanja" and count number of students 
def student_status_stats(df_complete_combined):
    df_complete_grouped = df_complete_combined.groupby("Način slušanja").size()
    print("Number of students by 'Način slušanja': ")
    print(df_complete_grouped)
    return df_complete_grouped

def student_not_regular_in_group_stats(df_groups_combined, df_complete_combined):
    df_complete_not_regular = df_complete_combined[df_complete_combined['Način slušanja'] != 'Prvi put sluša (Redovno)']
    df_complete_not_regular_index = df_complete_not_regular['Broj indeksa']
    df_groups_not_regular = df_groups_combined[df_groups_combined['Broj indeksa'].isin(df_complete_not_regular_index)]
    print("Number of students in groups that are not regular: ", len(df_groups_not_regular))


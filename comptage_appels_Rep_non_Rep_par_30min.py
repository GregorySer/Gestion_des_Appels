###By Greg ENJOY!!!! ###

import pandas as pd
import numpy as np

#définit la fonction de conversion décimal - temps
def decimal_to_time(decimal_time):
    hours = int(decimal_time)
    minutes = int((decimal_time * 60) % 60)
    return f"{hours:02d}:{minutes:02d}"


# Demande du chemin du fichier
chemin = input("Quel est le chemin complet du fichier xlsx de données à traiter: ")

# Chargement des données sans en-têtes
df = pd.read_excel(chemin, header=None)

# Vérifier si le dataframe a au moins deux colonnes
if len(df.columns) >= 2:
    # Renommez les colonnes en 'time' et 'status'
    df.rename(columns={df.columns[0]: 'time', df.columns[1]: 'status'}, inplace=True)
else:
    # Sinon, créez les colonnes 'time' et 'status' avec des valeurs vides
    df['time'] = np.nan
    df['status'] = np.nan

# Conversion du temps en décimal
df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time
df['time_decimal'] = df['time'].apply(lambda t: round(t.hour + t.minute / 60 + t.second / 3600, 4))

# Calcul des intervalles de temps
df['interval_start'] = np.floor(df['time_decimal'] * 2) / 2
df['interval_end'] = df['interval_start'] + 0.5

# Comptage des appels par intervalle de temps
result = df.groupby(['interval_start', 'interval_end', 'status']).size().unstack(fill_value=0)

# Reset index
result.reset_index(inplace=True)

# Création d'un dataframe avec toutes les tranches possibles
all_intervals = pd.DataFrame({'interval_start': np.arange(0, 24, 0.5), 'interval_end': np.arange(0.5, 24.5, 0.5)})

# Fusion de 'all_intervals' avec 'result' et remplissage des NaN par des zéros
final_result = pd.merge(all_intervals, result, how='left', on=['interval_start', 'interval_end']).fillna(0)

# Convertir les colonnes en entier
final_result[['répondu', 'non répondu']] = final_result[['répondu', 'non répondu']].astype(int)

# Appels du matin
early_non_answered_calls = final_result.loc[(final_result['interval_start'] >= 0) & (final_result['interval_end'] <= 7), 'non répondu'].sum()
early_answered_calls = final_result.loc[(final_result['interval_start'] >= 0) & (final_result['interval_end'] <= 7), 'répondu'].sum()

# Appels du soir
late_non_answered_calls = final_result.loc[(final_result['interval_start'] >= 19) & (final_result['interval_end'] <= 24), 'non répondu'].sum()
late_answered_calls = final_result.loc[(final_result['interval_start'] >= 19) & (final_result['interval_end'] <= 24), 'répondu'].sum()

# Conversion des colonnes 'interval_start' et 'interval_end' en format de temps
final_result.reset_index(inplace=True)
final_result['interval_start'] = final_result['interval_start'].apply(decimal_to_time)
final_result['interval_end'] = final_result['interval_end'].apply(decimal_to_time)

print(final_result)
print(f"Il y a eu {early_answered_calls} appels répondus et {early_non_answered_calls} appels non répondus entre 00:00:00 et 07:00:00")
print(f"Il y a eu {late_answered_calls} appels répondus et {late_non_answered_calls} appels non répondus entre 19:00:00 et 24:00:00")

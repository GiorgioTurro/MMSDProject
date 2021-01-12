"""
Created on Tue Dec 22 20:04:20 2020.

@author: stevi
"""
import joblib
import pandas as pd


def cleanNullTerms(d):
    """Leva i valori nulli da un dizionario, anche innestati."""
    clean = {}
    for k, v in d.items():
        if isinstance(v, dict):
            nested = cleanNullTerms(v)
            if len(nested.keys()) > 0:
                clean[k] = nested
        elif v is not None:
            clean[k] = v
    return clean


def unpack_spec(spec_dict):
    """Ottengo una lista da un dizionario."""
    spec_list = []
    for s in spec_dict:
        spec_list.append([s, int(spec_dict[s])])
    return spec_list


def initialize_hospitals(risorse):
    """
    Creo un dizionario di dizionari di ospedali.

    Chiave principale "id ospedale", seconda chiave "anno" con valore un
    dizionario di chiave codice specialità con valore una lista delle capacità
    [capacità giornaliera (7 valori), capacità massima]).

    Il dizionario è:'id ospedale':'anno':'codice specialità':
    ['MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY',
     'capacita_max']
    """
    # Ottengo la lista dei codici ospedali senza duplicati
    hosp_series = risorse['codici_ospedale'].drop_duplicates()
    # Ottengo la lista degli anni senza duplicati
    year_series = risorse['year'].drop_duplicates()
    filename = 'hosp_series'
    joblib.dump(hosp_series, filename)
    filename = 'year_series'
    joblib.dump(year_series, filename)

    final_dict = {}
    print('Inizio creazione dizionario ospedali')
    for index, val in hosp_series.items():
        tmp_dict = {}
        for y in year_series:
            y_dict = {}
            for index, row in risorse.iterrows():
                if val == row['codici_ospedale']:
                    if y == row['year']:
                        y_dict[row['codici_specialita']] = [row['MONDAY'],
                                                            row['TUESDAY'],
                                                            row['WEDNESDAY'],
                                                            row['THURSDAY'],
                                                            row['FRIDAY'],
                                                            row['SATURDAY'],
                                                            row['SUNDAY'],
                                                            row['capacita_max']]
            tmp_dict[y] = y_dict
        final_dict[val] = tmp_dict

    print('Fine creazione dizionario ospedali')
    filename = 'new_resources'
    joblib.dump(final_dict, filename)
    return final_dict


def __codicespec_risorse(s):
    tmp_id_spec = str(s).split("_")[1]
    if tmp_id_spec.startswith("0"):
        id_spec = tmp_id_spec.split("0")[1]
    else:
        id_spec = tmp_id_spec
    return int(id_spec)


def __codicespec_ricoveri(s):
    return int(s)


def __parser_idspec(df):
    if 'codici_specialita' in df.columns:
        tmp = df['codici_specialita'].apply(__codicespec_risorse)
        df['codici_specialita'] = tmp
    else:
        if 'COD_BRANCA' in df.columns:
            df['COD_BRANCA'] = df['COD_BRANCA'].apply(__codicespec_ricoveri)
        else:
            raise Exception('Il nome della colonna dei codici delle specialità'
                            ' non è stato trovato')
    return df


def __risorse_parser(code):
    return str(code).split("_")[1]


def __ricoveri_parser(code):
    h, t = str(code).split("-")
    return h + t


def __parser_idhosp(df):
    if 'codici_ospedale' in df.columns:
        tmp = df['codici_ospedale'].apply(__risorse_parser)
        df['codici_ospedale'] = tmp
    else:
        if 'codice_struttura_erogante' in df.columns:
            tmp = df['codice_struttura_erogante'].apply(__ricoveri_parser)
            df['codice_struttura_erogante'] = tmp
        else:
            raise Exception('Il nome della colonna dei codici degli ospedali'
                            ' non è stato trovato')
    return df


def __load():
    print("IN LOAD")
    ricoveri = pd.read_csv("../dati_elaborati/elaborated_data/ricoveri.csv",
                           usecols=['anno', 'data_ricovero', 'gg_degenza',
                                    'codice_struttura_erogante', 'COD_BRANCA'])

    risorse = pd.read_csv("../dati_elaborati/elaborated_data/"
                          "specialtyCapacitySchedules.csv",
                          usecols=['codici_ospedale', 'codici_specialita',
                                   'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
                                   'FRIDAY', 'SATURDAY', 'SUNDAY',
                                   'capacita_max', 'year'])

    ricoveri["data_ricovero"] = pd.to_datetime(ricoveri["data_ricovero"])
    ricoveri.sort_values('data_ricovero', inplace=True)
    ricoveri = ricoveri.reset_index(drop=True)
    ricoveri = ricoveri.dropna()

    ricoveri = __parser_idhosp(ricoveri)
    ricoveri = __parser_idspec(ricoveri)

    risorse = __parser_idhosp(risorse)
    risorse = __parser_idspec(risorse)

    filename = 'risorse_simulazione'
    joblib.dump(risorse, filename)
    filename = 'ricoveri_simulazione'
    joblib.dump(ricoveri, filename)

    return risorse, ricoveri


def load_data():
    """
    Controlla se i dati 'risorse_simulazione' e 'ricoveri_simulazione' esistono.

    Se non esistono li crea parsificandoli rendendo i codi ospedali e codici
    specialità tutti uguali.

    Returns
    -------
    risorse : Pandas Dataframe
        Dataframe del file 'specialtyCapacitySchedules.csv', contiene le
        capacità delle specialità.
    ricoveri : Pandas Dataframe
        Dataframe del file 'ricoveri.csv', contiene tutte le informazioni dei
        pazienti.

    """
    try:
        risorse = joblib.load('risorse_simulazione')
        ricoveri = joblib.load('ricoveri_simulazione')
    except Exception:
        risorse, ricoveri = __load()

    return risorse, ricoveri


def load_hosp_dict(risorse):
    """
    Prova a caricare il dizionario degli ospedali, se non esiste lo crea.

    Parameters
    ----------
    risorse : Pandas Dataframe
        File caricato in precedenza attraverso load_data().

    Returns
    -------
    hosp_dict : Python Dictionary
        Dizionario degli ospedali con anno, specialità e capienze.

    """
    try:
        hosp_dict = joblib.load('new_resources')
    except Exception:
        hosp_dict = initialize_hospitals(risorse)

    return hosp_dict

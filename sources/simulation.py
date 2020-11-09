from datetime import datetime
from datetime import timedelta
import time
import pandas as pd
import simpy
import copy
from itertools import islice
from Sources.patient import patient
from Sources.Log import Log


def read_ricoveri():
    print("Reading ricoveri.csv")
    return pd.read_csv("../resources/elaborated_data/ricoveriNoDaySurgery.csv",
                       usecols=['anno', 'data_ricovero', 'gg_degenza', 'codice_struttura_erogante', 'COD_BRANCA'])


def read_risorse(env):
    resources = {}
    resources1 = {}
    print("Reading specialtyCapacitySchedules.csv")
    risorse = pd.read_csv("../resources/elaborated_data/specialtyCapacitySchedules.csv",
                          usecols=['codici_ospedale', 'codici_specialita', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
                                   'FRIDAY', 'SATURDAY', 'SUNDAY', 'capacita_max', 'year'])
    for index, row in risorse.iterrows():
        # Retrieving/creating
        hospital_dict_year = resources.get(row['year'], {})
        hospital_dict_year1 = resources1.get(row['year'], {})
        specialty_hospital_dict = hospital_dict_year.get(row['codici_ospedale'], {})
        specialty_hospital_dict1 = hospital_dict_year1.get(row['codici_ospedale'], {})
        capacity_array = specialty_hospital_dict.get(row['codici_specialita'], [])
        capacity_array.append(row['MONDAY'])
        capacity_array.append(row['TUESDAY'])
        capacity_array.append(row['WEDNESDAY'])
        capacity_array.append(row['THURSDAY'])
        capacity_array.append(row['FRIDAY'])
        capacity_array.append(row['SATURDAY'])
        capacity_array.append(row['SUNDAY'])
        # Assigning
        specialty_hospital_dict[row['codici_specialita']] = capacity_array
        specialty_hospital_dict1[row['codici_specialita']] = simpy.Resource(env, capacity=int(row['capacita_max']))
        hospital_dict_year[row['codici_ospedale']] = specialty_hospital_dict
        hospital_dict_year1[row['codici_ospedale']] = specialty_hospital_dict1
        resources[row['year']] = hospital_dict_year
        resources1[row['year']] = hospital_dict_year1
    return resources, resources1


env = simpy.Environment()
ricoveri = read_ricoveri()
day_resources, max_resources = read_risorse(env)
date = datetime.strptime(ricoveri['data_ricovero'][0], '%Y-%m-%d')
initial_time = time.mktime(date.timetuple())
log = Log()
current_day = date.weekday()
day_resources_counter = copy.deepcopy(day_resources)
for index1, row1 in ricoveri.iterrows():
    if index1 % 10000 == 0:
        print(index1)
    optional_resource = None
    data_ricovero = date.strptime(row1['data_ricovero'], '%Y-%m-%d')
    data_fine_ricovero = data_ricovero + timedelta(days=row1['gg_degenza'])
    if current_day == data_ricovero.weekday():
        day_resources_counter[data_ricovero.year][row1['codice_struttura_erogante']][row1['COD_BRANCA']][current_day] =\
            day_resources_counter[data_ricovero.year][row1['codice_struttura_erogante']][row1['COD_BRANCA']][
                                  current_day] - 1
        counter = day_resources_counter[data_ricovero.year][row1['codice_struttura_erogante']][row1['COD_BRANCA']][
            current_day]
        if day_resources_counter[data_ricovero.year][row1['codice_struttura_erogante']][row1['COD_BRANCA']][
                current_day] < 0:
            log.write_log('day_full_log', ('Patient: ' + str(index1) +
                                           ' tried to go on ' + str(data_ricovero) +
                                           ' in: ' + str(row1['codice_struttura_erogante']) +
                                           ' Speciality: ' + str(row1['COD_BRANCA']) +
                                           ' counter: ' + str(counter)))
            continue
    else:
        day_resources_counter = copy.deepcopy(day_resources)
        current_day = data_ricovero.weekday()
    if data_ricovero.year != data_fine_ricovero.year:
        dict_fine_anno = max_resources.get(data_fine_ricovero.year, None)
        if dict_fine_anno is not None:
            dict_struttura_fine_anno = dict_fine_anno.get(row1['codice_struttura_erogante'], None)
            if dict_struttura_fine_anno is not None:
                specialita_fine_anno = dict_struttura_fine_anno.get(row1['COD_BRANCA'], None)
                if specialita_fine_anno is not None:
                    optional_resource = specialita_fine_anno
    data_ricovero_virtuale = (time.mktime(data_ricovero.timetuple()) - initial_time) / 86400
    env.process(patient(env, log, index1, data_ricovero_virtuale, row1['gg_degenza'],
                        max_resources[data_ricovero.year]
                        [row1['codice_struttura_erogante']]
                        [row1['COD_BRANCA']],
                        optional_resource
                        ))
env.run()
log.close()

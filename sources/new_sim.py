#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 12:57:59 2021

@author: stevi
"""
import parser_data
import calendar
import datetime
import time
import copy
import save_info


class Hospital():
    """Classe per la creazione dell'oggetto Ospedale."""

    def __init__(self, id_hosp, id_spec, capacity):
        self.id_hosp = id_hosp
        self.id_spec = id_spec
        self.capacity = capacity  # lista lunga 8 valori (primi 7 settimana)
        self.waiting_queue = []
        self.counter_day_cap = 0
        self.rest_queue = []
        self.counter_day_queue = 0
        self.counter_max_queue = 0


class Patient():
    """Classe per la creazione dell'oggetto Paziente."""

    def __init__(self, id_patient, rest_time, patient_day_recovery,
                 patient_id_hosp, patient_id_spec):
        self.id_patient = id_patient
        self.patient_id_hosp = patient_id_hosp
        self.patient_id_spec = patient_id_spec
        self.rest_time = rest_time
        self.patient_day_recovery = patient_day_recovery
        self.patient_true_day_recovery = ''
        self.queue_motivation = ''
        self.counter_queue = 0


def patient_hospital(hosp_list, patient_id_hosp, patient_id_spec):
    """
    Trovo l'ospedale del paziente.

    Parameters
    ----------
    hosp_list : List di Oggetti Hospital
        Lista degli ospedali.
    patient_id_hosp : String
        Id dell'ospedale nel quale il paziente è andato.
    patient_id_spec : String
        Id della specialità nella quale il paziente è andato.

    Returns
    -------
    h : Oggetto Hospital
        Ospedale della lista nel quale il paziente è andato.

    """
    tmp_list = []
    for h in hosp_list:
        if int(h.id_hosp) == int(patient_id_hosp):
            tmp_list.append(h)

    target_hospital = 'None'
    for h in tmp_list:
        if int(h.id_spec) == int(patient_id_spec):
            target_hospital = h
    return target_hospital


def number_of_the_day(date_pat):
    """
    Trova il numero della settimana.

    Ricava il numero del giorno della settimana in base alla data di ricovero
    del paziente (Lunedì=0, martedì=1, ecc...).

    Parameters
    ----------
    patient : Riga del dataframe
        Informazioni del paziente presenti nel dataframe.

    Returns
    -------
    Int
        Il numero del giorno della settimana in cui è stato accettato il
        paziente.

    """
    year, month, day = (int(i) for i in date_pat.split("-"))
    day = calendar.weekday(year, month, day)
    return int(day)


def create_hospital_list(hosp_dict, year):
    """
    Creo una nuova lista di oggetti ospedale.

    Creo una lista di oggetti ospedale partendo dal dizionario, la creo in
    base all'anno passato di riferimento.

    Parameters
    ----------
    hosp_dict : Dizionario python
        Dizionario creato dai file csv contenente le info degli ospedali.
    year : Int
        Anno per cui mi interessa creare una lista di ospedali.

    Returns
    -------
    new_hosp_list : List di Oggetti Hospital
        Lista dei nuovi oggetti ospedali con le info del dizionario.

    """
    new_hosp_list = []
    for h in hosp_dict:
        for s in hosp_dict[h][year]:
            new_hosp_list.append(Hospital(h, s, hosp_dict[h][year][s]))

    return new_hosp_list


def update_hospital_capacity(old_hosp_list, new_hosp_list):
    """
    Aggiorno le code dei nuovi ospedali.

    Aggiorno le code di attesa della nuova lista di ospedali con le code della
    vecchia lista di ospedali.

    Parameters
    ----------
    old_hosp_list : List di Oggetti Hospital
        Lista degli ospedali con le info dell'anno precedente.
    new_hosp_list : List di Oggetti Hospital
        Nuova lista di ospedali con le info dell'anno nuovo.

    Returns
    -------
    new_hosp_list : List di Oggetti Hospital
        Nuova lista di ospedali con le info dell'anno nuovo e con le code di
        attesa copiate dall'anno precedente.

    """
    for old_h in old_hosp_list:
        for new_h in new_hosp_list:
            if int(old_h.id_hosp) == int(new_h.id_hosp):
                if int(old_h.id_spec) == int(new_h.id_spec):
                    new_h.waiting_queue = copy.deepcopy(old_h.waiting_queue)
                    new_h.rest_queue = copy.deepcopy(old_h.rest_queue)

    return new_hosp_list


def count_total_patient(patient_day_list):
    """
    Conta il numero di pazienti.

    Parameters
    ----------
    patient_day_list : List di Dataframe
        Lista di dataframe dei pazienti divisi per data.

    Returns
    -------
    tot : Int
        Numero totale di pazienti da analizzare.

    """
    tot = 0
    for df in patient_day_list:
        index = df.index
        tot = tot + len(index)

    return tot


def start_simulation(patients, hosp_dict):
    """
    Inizio simulazione.

    Come output della simulazione ci saranno 3 file .txt che raccoglieranno
    tutte le info necessarie per l'analisi della simulazione.

    Parameters
    ----------
    patients : Dataframe
        Dataframe con info sui pazienti da simulare.
    hosp_dict : Dizionario
        Dizionario creato dai file csv contenente le info degli ospedali.

    Returns
    -------
    None.

    """
    start = time.time()

    # Creo una lista di dataframe, ogni dataframe contiene tutti i pazienti
    # ricoverati lo stesso giorno
    gb = patients.groupby('data_ricovero')
    patient_day_list = [gb.get_group(x) for x in gb.groups]

    # Mi salvo il primo anno che incontro
    tmp_date = str(patient_day_list[0]['data_ricovero'].iloc[0])
    first_date = tmp_date.split(" ")[0]
    old_year = int(first_date.split("-")[0])

    # Creo la lista degli ospedali
    hosp_list = create_hospital_list(hosp_dict, old_year)

    print("Totale giorni: "+str(len(patient_day_list)))

    # Contatore dei giorni
    d = 0

    # Variabili Simulazione
    # giorni di attesa prima che il sistema arrivi ad una condizione di
    # equilibrio
    spurious_days = len(patient_day_list)
    # quantità di giorni da controllare per anticipare pazienti
    forward_days = 30
    # percentuale di riduzione della capacità giornaliera
    reduction_perc = 0
    # soglia dalla quale applicare la riduzione percentuale reduction_perc
    capacity_threshold = 13

    # Creo i file di log
    save_info.create_day_log(patient_day_list, hosp_list, spurious_days)

    save_info.create_queue_info()

    save_info.create_anticipated_queue()

    # Conto quanti pazienti ci sono
    pat = count_total_patient(patient_day_list)
    print("Totale pazienti: " + str(pat))

    # Inizio della simulazione
    for day in patient_day_list:
        queue_info = []
        anticipated_days = []
        list_anticipated_patients = []
        print("Giorno: "+str(d))

        # Controllo se è cambiato l'anno
        if not day.empty:
            new_date = str(day['data_ricovero'].iloc[0]).split(" ")[0]
            new_year = int(new_date.split("-")[0])
            first_date = new_date
        else:
            first_date = datetime.datetime.strptime(str(first_date), '%Y-%m-%d')
            tmp_day = first_date + datetime.timedelta(days=1)
            new_date = str(tmp_day).split(" ")[0]
            new_year = int(new_date.split("-")[0])
            first_date = new_date

        # Ottengo il numero del giorno della settimana
        dayNumber = number_of_the_day(new_date)

        # Se è cambiato l'anno riaggiorno tutte le capacità e riporto le
        # vecchie code
        if new_year != old_year:
            new_hosp_list = create_hospital_list(hosp_dict, new_year)
            hosp_list = update_hospital_capacity(hosp_list, new_hosp_list)
            old_year = new_year

        # Decremento i giorni di degenza, poi levo i pazienti a 0 giorni di
        # degenza.
        for h in hosp_list:
            if h.rest_queue != []:
                for p in h.rest_queue:
                    p.rest_time -= 1
                h.rest_queue = [p for p in h.rest_queue if p.rest_time > 0]

        # Controllo se posso ricoverare i pazienti nella lista di attesa
        for h in hosp_list:
            if h.waiting_queue != []:
                for p in h.waiting_queue:
                    if len(h.rest_queue) < int(h.capacity[7]):
                        if h.counter_day_cap < int(h.capacity[dayNumber]):
                            h.counter_day_cap += 1
                            h.rest_queue.append(p)
                            h.waiting_queue = ([n_p for n_p in h.waiting_queue
                                                if int(n_p.id_patient) !=
                                                int(p.id_patient)]
                                               )
                            p.patient_true_day_recovery = new_date
                            queue_info.append([p, h])

        # Controllo se posso ricoverare i nuovi pazienti
        for index, patient in day.iterrows():
            # Leggo e salvo le info del paziente
            patient_id_hosp = patient.loc['codice_struttura_erogante']
            patient_id_spec = patient.loc['COD_BRANCA']

            # Recupero l'oggetto ospedale del paziente
            target_hospital = patient_hospital(hosp_list, patient_id_hosp,
                                               patient_id_spec)
            patient_rest_time = int(patient.loc['gg_degenza'])

            patient_day_recovery = str(patient['data_ricovero']).split(" ")[0]

            # Creo l'oggetto paziente con tutte le info
            tmp_patient = Patient(index, patient_rest_time,
                                  patient_day_recovery, patient_id_hosp,
                                  patient_id_spec)

            # ottengo le due capacità
            hosp_max_capacity = int(target_hospital.capacity[7])
            hosp_day_capacity = int(target_hospital.capacity[dayNumber])
            # ci sono casi in cui la capacità giornaliera è 0, non li considero
            if hosp_day_capacity != 0:
                # diminuisco di una percentuale arrotondando per difetto con
                # vincolo sulla capacità
                if hosp_day_capacity > capacity_threshold:
                    hosp_day_capacity = int(hosp_day_capacity -
                                            (hosp_day_capacity * reduction_perc)
                                            )
                # se la capacità diventa nulla la metto a 1
                if hosp_day_capacity == 0:
                    hosp_day_capacity = 1

            # Inizio controllo vincoli
            # Controllo se si è sforata la capacità massima di posti letto
            if len(target_hospital.rest_queue) >= hosp_max_capacity:
                # controllo se anche il giorno è pieno, per il momento vengono
                # comunque inseriti nella coda della capacità massima ma il
                # paziente ha una motivazione diversa
                if target_hospital.counter_day_cap >= hosp_day_capacity:
                    tmp_patient.queue_motivation = 'all_max'
                    target_hospital.counter_max_queue = (target_hospital.
                                                         counter_max_queue + 1)
                    tmp_patient.counter_queue = (target_hospital.
                                                 counter_max_queue)
                    target_hospital.waiting_queue.append(tmp_patient)
                else:
                    tmp_patient.queue_motivation = 'cap_max'
                    target_hospital.counter_max_queue = (target_hospital.
                                                         counter_max_queue + 1)
                    tmp_patient.counter_queue = (target_hospital.
                                                 counter_max_queue)
                    target_hospital.waiting_queue.append(tmp_patient)
            else:
                # Controllo se si è sforata la capacità giornaliera massima
                if target_hospital.counter_day_cap >= hosp_day_capacity:
                    tmp_patient.queue_motivation = 'day_max'
                    target_hospital.counter_day_queue = (target_hospital.
                                                         counter_day_queue + 1)
                    tmp_patient.counter_queue = (target_hospital.
                                                 counter_day_queue)
                    target_hospital.waiting_queue.append(tmp_patient)
                else:
                    target_hospital.counter_day_cap = (target_hospital.
                                                       counter_day_cap + 1)
                    target_hospital.rest_queue.append(tmp_patient)

        # Controllo se posso anticipare l'ingresso di pazienti nei prossimi
        # n giorni se ho superato 'spurious_days' giorni

        if d > spurious_days:
            end = d + 1 + forward_days
            if end > len(patient_day_list):
                end = len(patient_day_list)
            # Prendo una finestra di dataframe
            anticipated_days = patient_day_list[d + 1:end]
            tmp_ant_day = []
            for next_day in anticipated_days:
                patient_removed = []
                for index, patient in next_day.iterrows():
                    patient_id_hosp = patient.loc['codice_struttura_erogante']
                    patient_id_spec = patient.loc['COD_BRANCA']
                    target_hospital = patient_hospital(hosp_list,
                                                       patient_id_hosp,
                                                       patient_id_spec)
                    if target_hospital != 'None':
                        if len(target_hospital.rest_queue) < hosp_max_capacity:
                            hosp_day_capacity = int(target_hospital.
                                                    capacity[dayNumber])
                            if target_hospital.counter_day_cap < hosp_day_capacity:
                                target_hospital.counter_day_cap = (target_hospital.
                                                                   counter_day_cap + 1)

                                patient_rest_time = int(patient.loc['gg_degenza'])
                                patient_day_recovery = (str(patient['data_ricovero']).
                                                            split(" ")[0])
                                tmp_patient = Patient(index, patient_rest_time,
                                                      patient_day_recovery,
                                                      patient_id_hosp,
                                                      patient_id_spec)
                                tmp_patient.patient_true_day_recovery = str(new_date)
                                target_hospital.rest_queue.append(tmp_patient)
                                list_anticipated_patients.append(tmp_patient)
                                patient_removed.append(index)

                for p in patient_removed:
                    next_day = next_day.drop(p)
                tmp_ant_day.append(next_day)
            # Sostituisco i dataframe in patient_day_list con quelli modificati
            # in anticipated_days
            patient_day_list[d + 1:end] = tmp_ant_day

        # Salvo le info dei pazienti ricoverati in anticipo
        save_info.anticipated_patient(list_anticipated_patients)

        # Salvo le info della giornata degli ospedali
        save_info.save_day_info(hosp_list, d, dayNumber)

        # Salvo le info della situazione code
        save_info.save_queue_info(queue_info, dayNumber)

        # Resetto i counter di tutti gli ospedali
        for h in hosp_list:
            h.counter_day_cap = 0
            h.counter_day_queue = 0
            h.counter_max_queue = 0

        # Nuovo giorno
        d += 1

    end = time.time()
    print(f"Durata di esecuzione: {(end - start)/60} minuti.")


if __name__ == '__main__':
    resources, patients = parser_data.load_data()
    hosp_dict = parser_data.load_hosp_dict(resources)
    start_simulation(patients, hosp_dict)

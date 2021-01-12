#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 13:59:01 2021

@author: stevi
"""


def create_day_log(patient_day_list, hosp_list):
    with open('log_day.txt', 'w') as log:
        n1 = len(patient_day_list)
        n2 = len(hosp_list)
        print(f"Il numero totale di giorni è {n1} e il numero di specialità è"
              f" {n2}\n", file=log)


def create_queue_info():
    with open('queue_info.txt', 'w') as q:
        print(f"Numero coda indica quanto ha sforato il paziente", file=q)


def save_day_info(hosp_list, day):
    with open('log_day.txt', 'a') as log:
        for h in hosp_list:
            n1 = len(h.rest_queue)
            n2 = h.capacity[7]
            n3 = len(h.waiting_queue)
            print(f"Giorno {day}: ospedale {h.id_hosp}: specialità {h.id_spec}:"
                  f" ricoveri {h.counter_day_cap}: letti occupati"
                  f" {n1}/{n2}: attesa {n3}",
                  file=log)
        print(f"\n", file=log)


def save_queue_info(queue_info, day):
    with open('queue_info.txt', 'a') as info:
        for p in queue_info:
            if p[0].patient_day_recovery != p[0].patient_true_day_recovery:
                i1 = p[0].id_patient
                i2 = p[0].patient_day_recovery
                i3 = p[0].patient_true_day_recovery
                i4 = p[0].patient_id_hosp
                i5 = p[0].patient_id_spec
                i6 = p[0].queue_motivation
                i7 = p[0].counter_queue
                if i6 == 'cap_max':
                    i8 = p[1].capacity[7]
                else:
                    i8 = p[1].capacity[day]
                print(f"Paziente {i1}, data ricovero {i2}, data effettivo ricovero "
                      f"{i3}, ospedale {i4}, specialità {i5}, motivazione {i6},"
                      f" numero coda {i7}/{i8}", file=info)


"""
da fare solo se data ricovero != data effettivo ricovero
print(f"Id paziente, data ricovero, data effettivo ricovero, id osp, id spec, motivazione"
      f"numero paziente del giorno/capacità max giornaliera, numero posto letto/capacità max posti letto")
numeri del paziente sulla coda, voglio sapere di quanto ha sforato
"""






















from datetime import datetime

import pandas as pd
import numpy as np

if __name__ == '__main__':
    pd.set_option('display.max_rows', 1000)
    pd.options.display.width = 0
    dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')

    ricoveri1 = pd.read_csv("../resources/2011/sdo1.csv",
                            usecols=['anno', 'data_ricovero', 'gg_degenza', 'data_prenotazione',
                                     'codice_struttura_erogante', 'disciplina_uo_ammissione']
                            )
    ricoveri2 = pd.read_csv("../resources/2012/sdo2.csv",
                            usecols=['anno', 'data_ricovero', 'gg_degenza', 'data_prenotazione',
                                     'codice_struttura_erogante', 'disciplina_uo_ammissione'])
    ricoveri3 = pd.read_csv("../resources/2013/sdo3.csv",
                            usecols=['anno', 'data_ricovero', 'gg_degenza', 'data_prenotazione',
                                     'codice_struttura_erogante', 'disciplina_uo_ammissione'])
    branca = pd.read_csv("../resources/general/branca.csv")

    ricoveri_concat = pd.concat([ricoveri1, ricoveri2, ricoveri3], axis=0, join='outer', ignore_index=False)

    ricoveri_concat['data_prenotazione'] = ricoveri_concat['data_prenotazione'].fillna(ricoveri1['data_ricovero'])
    joined = ricoveri_concat.merge(branca, how='left', left_on='disciplina_uo_ammissione', right_on='DES_BRANCA')
    joined['codice_struttura_erogante'] = 'res_' + joined['codice_struttura_erogante'].str.replace('-', '')
    joined['COD_BRANCA'] = joined['COD_BRANCA'].astype(str)
    joined['COD_BRANCA'] = joined['COD_BRANCA'].str.replace(r'\.0', '')
    joined = joined.sort_values(by=['data_ricovero'])
    joined = joined.reset_index(drop=True)
    joined.index.name = 'Index'

    joined.to_csv('../resources/elaborated_data/ricoveri.csv')

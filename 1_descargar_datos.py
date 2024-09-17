import os
import time

import numpy as np
import pandas as pd
from pandasql import sqldf
from istacpy.statisticalresources.cubes import get_statisticalresources_datasets_agency_resource_version as get_cubo
from istacpy.statisticalresources.queries import get_statisticalresources_queries_agency_resource as get_query
from istacpy.indicators.lite import indicators
import wget

try:

    # Funciones necesarias
    def reemplazar_etiquetas_por_valores(datos, diccionario_codigos):
        for clave, valor in list(diccionario_codigos.items()):
            datos.replace(clave, valor, inplace=True)
        return datos

    # Leer archivo indicadores

    df_indicadores = pd.read_excel('input_files/indicadores.xlsx', sheet_name='indicadores')

    archivos_actuales = os.listdir('descargados')

    indicadores_concretos = [160]
    indicadores_desde = 0

    if len(indicadores_concretos) == 0:
        indicadores_concretos = df_indicadores['id_indicador'].tolist()

    if indicadores_desde > 0:
        indicadores_concretos = [indicador for indicador in indicadores_concretos if indicador >= indicadores_desde]
        print(f'Empezando a descargar {len(indicadores_concretos)} indicadores')

    # para cada fila...
    for indice, fila in df_indicadores.iterrows():
        if fila.id_indicador in indicadores_concretos:
            print(f'indicador {fila.id_indicador}')
            url_descarga = fila.url_descarga

            if fila.tipo == "INE" or fila.tipo == "no_WDC":
                nombre_archivo = fila.archivo + '.px'
            elif fila.tipo == 'MIFOM':
                nombre_archivo = fila.archivo + '.xls'
            elif fila.tipo == 'MINPOLTE' or fila.tipo == 'BdE':
                nombre_archivo = fila.archivo + '.xlsx'
            elif fila.tipo == 'MITES':
                nombre_archivo = 'no'
            else:
                nombre_archivo = fila.archivo

            # comprobar que haya enlace de descarga
            if type(url_descarga) == str and nombre_archivo != 'no':

                # comprobar si hay un archivo que se llama igual
                if nombre_archivo in archivos_actuales:
                    # si lo hay, se borra
                    os.remove(f'descargados/{nombre_archivo}')
                else:
                    # si no lo hay, se continúa
                    pass

                # descargar el archivo
                for intento in range(1, 6):
                    print(f'    intento {intento}')
                    try:
                        time.sleep(2)
                        archivo_descargado = wget.download(url_descarga, out=f'descargados/{nombre_archivo}')
                        print(f'descargado: {nombre_archivo}')
                        break
                    except Exception as e:
                        print(f'ERROR - error en el indicador {nombre_archivo}')
                        print(e)
                        with open('output.txt', 'a') as output:
                            print(f'ERROR - error en el indicador {nombre_archivo}', file=output)

            else:
                # si es del ISTAC, llamar a la librería istacpy
                if fila.tipo.startswith('WDC'):

                    # si es un cubo usar la función de cubo
                    if fila.tipo == 'WDC_cubo':
                        cubo = get_cubo(agencyid="ISTAC", resourceid=fila.resource_id, version="~latest", as_dataframe=True)
                        df_cubo = cubo.dataframe
                        df_cubo_etq = df_cubo.replace(cubo.codelists)
                        df_cubo_etq.to_csv(f'descargados/{nombre_archivo}.csv', sep=';', index=False, encoding='utf-8')
                        print(f'descargado cubo: {nombre_archivo}')

                        # region operacion etiquetas
                        lista_etiquetas = cubo.codelists.keys()
                        # print(f'obteniendo tablas de etiquetas: {lista_etiquetas}')

                        # Obtener etiquetas para cada cubo
                        for columna in lista_etiquetas:
                            nombre_df_etiq = columna.lower()

                            # reemplazar los codigos por las etiquetas
                            dicc_reemplazar = cubo.codelists[columna]
                            reemplazar_etiquetas_por_valores(df_cubo[columna], dicc_reemplazar)

                            # crear tablas de etiquetas
                            df_etiq = pd.DataFrame(list(cubo.codelists[columna].items()),
                                                   columns=['cod', 'etiq'])
                            # print(df_etiq)

                            # subir tablas de etiquetas a sao_research
                            #df_etiq.to_sql(f'{nombre_archivo}_etq_{nombre_df_etiq}',
                                          # sao_research_connection,
                                          # index=False,
                                          # if_exists='replace') if guardar_sql else 1
                            #print(f'etiqueta subida a sao_research: {nombre_archivo}_etq_{nombre_df_etiq}') if guardar_sql else 1

                        # subir cubo a mysql

                        # endregion

                        # si es un query usar la función de query
                    elif fila.tipo == 'WDC_query':
                        query = get_query(agencyid="ISTAC", resourceid=fila.resource_id, as_dataframe=True)
                        df_query = query.dataframe
                        df_query_etq = df_query.replace(query.codelists)
                        df_query_etq.to_csv(f'descargados/{nombre_archivo}.csv', sep=';', index=False, encoding='utf-8')
                        print(f'descargada query: {nombre_archivo}')

                        # region operacion etiquetas
                        lista_etiq_query = query.codelists.keys()

                        for columna in lista_etiq_query:
                            nombre_df_etiq_query = columna.lower()

                            # reemplazar los codigos por las etiquetas
                            dicc_reemplazar_query = query.codelists[columna]
                            reemplazar_etiquetas_por_valores(df_query[columna], dicc_reemplazar_query)

                            # crear tablas de etiquetas
                            df_etiq_query = pd.DataFrame(list(query.codelists[columna].items()),
                                                         columns=['cod', 'etiq'])

                            #df_etiq_query.to_sql(f'{nombre_archivo}_etq_{nombre_df_etiq_query}',
                                                # sao_research_connection,
                                               #  index=False,
                                               #  if_exists='replace') if guardar_sql else 1

                        #subir query a mysql

                        # endregion

                    elif fila.tipo == "WDC_indicador":
                        codigo = fila.resource_id

                        df_tot = pd.DataFrame()

                        info = indicators.get_indicator(codigo)

                        codigos_temporales = list(info.time_granularities.values())

                        codigos_espaciales = list(info.geographical_granularities.values())

                        for cod_time in codigos_temporales:
                            for cod_geo in codigos_espaciales:
                                if cod_geo == 'T':
                                    pass
                                else:
                                    data = info.get_data(geo=cod_geo, time=cod_time)

                                    lista_columnas = list(data.data.keys())

                                    lista_valores = []

                                    for valores in list(data.data.values()):
                                        valores_ok = list(valores)
                                        lista_valores.append(valores_ok)

                                    df_pre = pd.DataFrame()

                                    df_pre['fechas'] = list(data.index)

                                    if cod_geo == 'R':
                                        granul_espacial = 'regional'
                                    elif cod_geo == 'I':
                                        granul_espacial = 'insular'
                                    elif cod_geo == 'M':
                                        granul_espacial = 'municipal'

                                    if cod_time == 'M':
                                        granul_temporal = 'mensual'
                                    elif cod_time == 'Q':
                                        granul_temporal = 'trimestral'
                                    elif cod_time == 'Y':
                                        granul_temporal = 'anual'

                                    df_pre['granularidad_espacial'] = granul_espacial
                                    df_pre['granularidad_temporal'] = granul_temporal

                                    for i in range(0, len(lista_columnas)):
                                        df_pre[lista_columnas[i]] = lista_valores[i]

                                    if len(df_tot) == 0:
                                        df_tot = pd.melt(df_pre,
                                                         id_vars=['fechas', 'granularidad_espacial', 'granularidad_temporal'],
                                                         var_name='territorio', value_name='valor')
                                    else:
                                        df_temp = pd.melt(df_pre,
                                                          id_vars=['fechas', 'granularidad_espacial', 'granularidad_temporal'],
                                                          var_name='territorio', value_name='valor')
                                        df_tot = pd.concat([df_tot, df_temp], axis=0)

                        df_tot.to_csv(f'descargados/{nombre_archivo}.csv', sep=';', index=False, encoding='utf8')

                        # subir indicador a mysql

                        print(f'descargado indicador {nombre_archivo}')


                else:
                    # si no es del ISTAC advertir de que no tiene enlace descarga
                    with open('output.txt', 'a') as output:
                        print(f'PRECAUCION - El indicador {nombre_archivo} no tiene enlace de descarga', file=output)

            print('---------')

        else:
            pass
except Exception as e:
    print(e)
    time.sleep(300)

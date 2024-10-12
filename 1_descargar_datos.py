import os
import time

import pandas as pd
import wget

from istacpy.statisticalresources.cubes import get_statisticalresources_datasets_agency_resource_version as get_cubo
from istacpy.statisticalresources.queries import get_statisticalresources_queries_agency_resource as get_query
from istacpy.indicators.lite import indicators

# Funciones necesarias
def reemplazar_etiquetas_por_valores(datos, diccionario_codigos):
    for clave, valor in list(diccionario_codigos.items()):
        datos.replace(clave, valor, inplace=True)
    return datos

def seleccionar_indicadores(ruta_archivo_indicadores, ruta_archivos_descargados, id_inicial, id_concreto=None, nombre_hoja=None):
    sheet_name = 'indicadores' if nombre_hoja is None else nombre_hoja
    df_indicadores = pd.read_excel(ruta_archivo_indicadores, sheet_name=sheet_name)
    if id_concreto is None:
        indicadores_concretos = df_indicadores['id_indicador'].tolist()
    else:
        indicadores_concretos = [indicador for indicador in id_concreto if indicador >= id_inicial]
        print(f"Empezando a descargar {len(indicadores_concretos)} indicadores")

    return [df_indicadores, indicadores_concretos, ruta_archivos_descargados]

def nombrar_archivo(fila):
    if fila.tipo == "INE" or fila.tipo == "no_WDC":
        nombre_archivo = fila.archivo + '.px'
    elif fila.tipo == 'MIFOM':
        nombre_archivo = fila.archivo + '.xls'
    elif fila.tipo == 'WDC_cubo' or fila.tipo == 'WDC_query':
        nombre_archivo = fila.archivo + '.csv'
    else:
        nombre_archivo = fila.archivo + '.csv'
    return nombre_archivo

def comprobar_descarga(nombre_archivo, ruta_archivos_descargados):
    if os.path.isfile(ruta_archivos_descargados + nombre_archivo):
        print(f'{nombre_archivo} ya descargado, eliminando la descarga anterior...')
        os.remove(ruta_archivos_descargados + nombre_archivo)
    else:
        pass

def descargar_archivo(fila, nombre_archivo, ruta_archivos_descargados, intentos=3):
    global archivo
    for intento in range(intentos):
        try:
            archivo = wget.download(fila.url_descarga, ruta_archivos_descargados + nombre_archivo)
            print(f'descargado: {nombre_archivo}')
            break
        except Exception as e:
            print(f'Error en la descarga de {nombre_archivo}: {e}')
            print(f'Comenzando intento {intento + 1} de 3')
            with open('output.txt', 'a') as output:
                print(f'ERROR - error en el indicador {nombre_archivo} en el intento intento {intento}/{intentos}', file=output)
            time.sleep(5)
            archivo = None
    time.sleep(1)
    return archivo

def descargar_cubo_query_istac(fila, nombre_archivo, ruta_archivos_descargados, intentos=3, etiquetas=True, tabla_etiquetas=False):
    for intento in range(intentos):
        try:
            cubo_query = get_cubo(agencyid="ISTAC", resourceid=fila.resource_id, version="~latest", as_dataframe=True)
            df_cubo = cubo_query.dataframe
            df_cubo_etq = df_cubo.replace(cubo_query.codelists) if etiquetas else df_cubo
            df_cubo_etq.to_csv(f'{ruta_archivos_descargados}/{nombre_archivo}', sep=';', index=False, encoding='utf-8')
            print(f'descargado {'cubo' if fila.tipo == 'WDC_cubo' else 'query'}: {nombre_archivo}')

            if tabla_etiquetas:
                lista_etiquetas = cubo_query.codelists.keys()
                # print(f'obteniendo tablas de etiquetas: {lista_etiquetas}')

                # Obtener etiquetas para cada cubo
                for etiqueta in lista_etiquetas:
                    nombre_df_etiq = etiqueta.lower()

                    # reemplazar los codigos por las etiquetas
                    dicc_reemplazar = cubo_query.codelists[etiqueta]
                    reemplazar_etiquetas_por_valores(df_cubo[etiqueta], dicc_reemplazar)

                    # crear tablas de etiquetas
                    df_etiq = pd.DataFrame(list(cubo_query.codelists[etiqueta].items()),
                                           columns=['cod', 'etiq'])
                    df_etiq.to_csv(f'{ruta_archivos_descargados}/{nombre_archivo.split('.')[0]}_etq_{nombre_df_etiq}.csv', sep=';', index=False, encoding='utf-8')
                    print(f'descargado tabla de etiquetas: {nombre_archivo.split('.')[0]}_etq_{nombre_df_etiq}.csv')
            break
        except Exception as e:
            print(f'Error en la descarga de {nombre_archivo}: {e}')
            print(f'Comenzando intento {intento + 1} de 3')
            with open('output.txt', 'a') as output:
                print(f'ERROR - error en el indicador {nombre_archivo} en el intento intento {intento}/{intentos}',
                      file=output)
            time.sleep(5)
    time.sleep(1)

def descargar_indicador_istac(fila, nombre_archivo, archivos_actuales, intentos=3):
    for intento in range(intentos):
        try:
            df_tot = pd.DataFrame()
            info = indicators.get_indicator(fila.resource_id)
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

            df_tot.to_csv(f'{archivos_actuales}/{nombre_archivo}', sep=';', index=False, encoding='utf8')
            print(f'descargado indicador {nombre_archivo}')

            break
        except Exception as e:
            print(f'Error en la descarga de {nombre_archivo}: {e}')
            print(f'Comenzando intento {intento + 1} de 3')
            with open('output.txt', 'a') as output:
                print(f'ERROR - error en el indicador {nombre_archivo} en el intento intento {intento}/{intentos}',
                      file=output)
            time.sleep(5)
    time.sleep(1)

if __name__ == '__main__':

    try:
        # seleccionar indicadores y archivos descargados anteriormente
        df_indicadores, indicadores_concretos, archivos_actuales = seleccionar_indicadores(
            'input_files/indicadores.xlsx',
            'descargados',
            0,
            [166, 158, 156]
        )

        # Descargar archivos
        for indice, fila in df_indicadores.iterrows():
            if fila.id_indicador in indicadores_concretos:
                print(f"indicador {fila.id_indicador}")

                # Definir el nombre del archivo
                nombre_archivo = nombrar_archivo(fila)

                # comprobar que haya enlace de descarga
                if type(fila.url_descarga) == str and nombre_archivo != 'no':

                    # comprobar si hay un archivo que se llama igual
                    comprobar_descarga(nombre_archivo, 'descargados/')

                    # descargar el archivo
                    archivo_descargado = descargar_archivo(fila, nombre_archivo, 'descargados/')

                # Si no hay enlace de descarga, comprobar si es un indicador del ISTAC
                else:
                    # si es un cubo usar la función de cubo
                    if fila.tipo == 'WDC_cubo' or fila.tipo == 'WDC_query':
                        # ejecutar la función de cubo o query
                        descargar_cubo_query_istac(fila, nombre_archivo, archivos_actuales)

                    elif fila.tipo == "WDC_indicador":
                        descargar_indicador_istac(fila, nombre_archivo, archivos_actuales)

                    else:
                        # si no es del ISTAC advertir de que no tiene enlace descarga
                        with open('output.txt', 'a') as output:
                            print(f'PRECAUCION - El indicador {nombre_archivo} no tiene enlace de descarga', file=output)

                print('---------')

            else:
                pass
    except Exception as e:
        print(e)
        print("Terminado")
        time.sleep(10)

import os
import pandas as pd
import openpyxl
from pyaxis import pyaxis
import sqlalchemy as sqlal
from pandasql import sqldf
import re

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1000)

# region funciones
# Función para reorganizar el texto si contiene una coma
def reorganizar_texto(texto):
    # Primero, separa cualquier número al principio del texto
    inicio_numeros = ''.join(re.findall('^\d*', texto)).strip()
    resto_texto = re.sub('^\d*', '', texto).strip()

    # Verifica si hay una coma en el resto del texto
    if ',' in resto_texto:
        partes = resto_texto.split(',')
        # Elimina espacios innecesarios y reorganiza
        texto_reorganizado = partes[1].strip() + ' ' + partes[0].strip()
    else:
        texto_reorganizado = resto_texto

    # Si había números al principio, añádelos al inicio del texto reorganizado
    if inicio_numeros:
        return inicio_numeros + ' ' + texto_reorganizado
    else:
        return texto_reorganizado

def sumar_datos_provinciales(prefijo, nueva_etiqueta_ter='Las Palmas'):
    dataframes = []
    for archivo in os.listdir('output_files'):
        if archivo == f'{prefijo}_gran_canaria.csv':
            dataframes.append(pd.read_csv(f'output_files/{prefijo}_gran_canaria.csv',sep=';', encoding='utf8'))
        if archivo == f'{prefijo}_fuerteventura.csv':
            dataframes.append(pd.read_csv(f'output_files/{prefijo}_fuerteventura.csv',sep=';', encoding='utf8'))
        if archivo == f'{prefijo}_lanzarote.csv':
            dataframes.append(pd.read_csv(f'output_files/{prefijo}_lanzarote.csv',sep=';', encoding='utf8'))
    if len(dataframes) == 0:
        pass
    else:
        # Combinar los dataframes
        df_combinado = pd.concat(dataframes)

        # Verificar si existe la columna 'grupo' en el dataframe combinado
        if 'grupo' in df_combinado.columns:
            # Agrupar por 'per' y 'grupo', y sumar los valores de la variable dependiente
            df_agrupado = df_combinado.groupby(['per', 'grupo']).sum().reset_index()
            df_agrupado.sort_values(by=['grupo', 'per'], inplace=True)
        else:
            # Agrupar solo por 'per' en caso de no tener 'grupo'
            df_agrupado = df_combinado.groupby(['per']).sum().reset_index()
            df_agrupado.sort_values(by=['per'], inplace=True)

        # Agregar la nueva etiqueta a la columna 'ter'
        df_agrupado['ter'] = nueva_etiqueta_ter

        # Determinar el orden de las columnas, colocando 'ter' al inicio
        columnas_iniciales = ['ter', 'per']
        # Agregar 'grupo' a la lista de columnas si existe
        if 'grupo' in df_agrupado.columns:
            columnas_iniciales.append('grupo')
        # Agregar el resto de las columnas, excluyendo las ya incluidas
        columnas_finales = columnas_iniciales + [col for col in df_agrupado.columns if col not in columnas_iniciales]

        df_resultante = df_agrupado[columnas_finales]
        df_resultante.to_csv(f'output_files/{prefijo}_las_palmas.csv', sep=';', index=False, encoding='utf8')

# endregion

# region conexion a saoresearch
sao_research_connection = sqlal.create_engine("mysql+pymysql://saoresearch:4Tg66a$r@87.106.125.96:3306/sao_research")
# endregion

# region listado indicadores a transformar
df_indicadores = pd.read_excel('input_files/indicadores.xlsx', sheet_name='indicadores')

lista_ids = df_indicadores['id_indicador'].tolist()

indicadores_concretos = [195]
indicadores_desde = 0

if len(indicadores_concretos) == 0:
    indicadores_concretos = df_indicadores['id_indicador'].tolist()

if indicadores_desde > 0:
    indicadores_concretos = [indicador for indicador in indicadores_concretos if indicador >= indicadores_desde]
    print(f'Empezando a descargar {len(indicadores_concretos)} indicadores')

# endregion

# transformar datos
for indice, fila in df_indicadores.iterrows():
    if fila.id_indicador in indicadores_concretos:
        print(f'indicador {fila.id_indicador}')

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


        # region población (listo)

        # 1.- Población residente (islas GC / LZ / FTV + provincia Las Palmas)
        # Hecho: output_files/poblacion_total_35_las_palmas.csv


        # 2.- Población residente por nacionalidad (desglose)
        # Hecho: output_files/poblacion_nacionalidad_35_las_palmas


        # 3.- Nacimientos
        sumar_datos_provinciales('nacimientos')


        # 3.- Defunciones
        sumar_datos_provinciales('defunciones')


        # 4.- Saldo migratorio
        sumar_datos_provinciales('saldo_migratorio')


        # 5.- Pirámide poblacional 2010 - 2022 (ISTAC) -- no hay dato 2023 --

        # 6.- Pirámide poblacional 2010 - 2023 (INE)
        # hecho: output_files/piramide_poblacion_2010_ine_35_las_palmas.csv
        # hecho: output_files/piramide_poblacion_2023_ine_35_las_palmas.csv


        # 7.- Índice de envejecimiento
        if fila.id_indicador == 187:
            df_pob_total = pd.read_csv('output_files/poblacion_total_35_las_palmas.csv', sep=';')
            df_pob_total['vd'] = df_pob_total['vd'].astype(float)
            df_pob_total['per'] = df_pob_total['per'].astype(str)
            df_pob_total.rename(columns={'vd': 'pob_total'}, inplace=True)

            # leer el archivo
            px = pyaxis.parse('descargados/2_1_187_pob_sexo_edad_islas_ine.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT Periodo AS per, `Grupo quinquenal de edad` as grupo, Islas as ter, `DATA` AS vd FROM df
            WHERE Periodo LIKE "%enero%"
            AND `Grupo quinquenal de edad` <> "Todas las edades"
            AND Islas NOT LIKE "07%"
            AND Islas = "35 Palmas, Las"
            AND (`Grupo quinquenal de edad` = "De 65 a 69 años" OR
            `Grupo quinquenal de edad` = "De 70 a 74 años" OR
            `Grupo quinquenal de edad` = "De 75 a 79 años" OR
            `Grupo quinquenal de edad` = "De 80 a 84 años" OR
            `Grupo quinquenal de edad` = "85 y más años")
            AND Sexo = "Total";
            """
            df_final = sqldf(query)

            df_final['per'] = df_final['per'].str[-4:]
            df_final['grupo'] = 'mayores de 64'
            df_final['vd'] = df_final['vd'].astype(float)
            df_final = df_final.groupby(['per', 'grupo']).agg({'vd': 'sum'}).reset_index()
            df_final = df_final[
                (df_final['per'].astype(int) >= 2010)
            ]
            df_final = df_final[['per', 'vd']]
            df_final['ter'] = '35 Las Palmas'
            df_final.rename(columns={'vd': 'pob_may_64'}, inplace=True)

            df_final = pd.merge(df_pob_total, df_final, how='inner', left_on=['ter', 'per'], right_on=['ter', 'per'])

            df_final['vd'] = df_final['pob_may_64'] / df_final['pob_total']
            df_final = df_final[['ter','per','vd']]
            df_final.sort_values(by=['per'], inplace=True)
            df_final.to_csv('output_files/indice_envejecimiento_las_palmas.csv', sep=';', index=False, encoding='utf8')


        # 8.- Tasa de dependencia
        if fila.id_indicador == 192:
            # leer el archivo
            px = pyaxis.parse('descargados/2_1_192_tasa_depend_prov.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            px_16 = pyaxis.parse('descargados/2_1_193_tasa_depend_16_prov.px', encoding='ISO-8859-1')
            df_16 = pd.DataFrame(px_16['DATA'])

            px_64 = pyaxis.parse('descargados/2_1_194_tasa_depend_64_prov.px', encoding='ISO-8859-1')
            df_64 = pd.DataFrame(px_64['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name='2_1_192_tasa_depend_prov', con=sao_research_connection, index=False, if_exists='replace')
            df_16.to_sql(name='2_1_193_tasa_depend_16_prov', con=sao_research_connection, index=False, if_exists='replace')
            df_64.to_sql(name='2_1_194_tasa_depend_64_prov', con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT "Las Palmas" AS ter, Periodo AS per, `DATA` AS vd FROM df
            WHERE Provincias LIKE "35 %"
            AND CAST(Periodo AS UNSIGNED) >= 2010
            ORDER BY Periodo
            """
            query_16 = """
            SELECT "Las Palmas" AS ter, Periodo AS per, `DATA` AS vd FROM df_16
            WHERE Provincias LIKE "35 %"
            AND CAST(Periodo AS UNSIGNED) >= 2010
            ORDER BY Periodo
            """
            query_64 = """
            SELECT "Las Palmas" AS ter, Periodo AS per, `DATA` AS vd FROM df_64
            WHERE Provincias LIKE "35 %"
            AND CAST(Periodo AS UNSIGNED) >= 2010
            ORDER BY Periodo
            """
            df_final = sqldf(query)
            df_final_16 = sqldf(query_16)
            df_final_64 = sqldf(query_64)

            df_final = pd.merge(df_final, df_final_16, how='inner', left_on=['ter','per'], right_on=['ter','per'])
            df_final.columns = ['ter', 'per', 'Tasa de dependencia', 'Tasa de dependencia de la población menor de 16 años']
            df_final = pd.merge(df_final, df_final_64, how='inner', left_on=['ter','per'], right_on=['ter','per'])
            df_final.columns = ['ter', 'per', 'Tasa de dependencia', 'Tasa de dependencia de la población menor de 16 años', 'Tasa de dependencia de la población mayor de 64 años']

            df_final.to_csv(f'output_files/tasa_dependencia_total_las_palmas.csv', sep=';', index=False, encoding='utf8')


        # 9.- Tasa bruta de natalidad
        if fila.id_indicador == 190:
            # leer el archivo
            px = pyaxis.parse('descargados/2_1_13_tasa_bruta_natal.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            px_lp = pyaxis.parse('descargados/2_1_191_tasa_bruta_natal_prov.px', encoding='ISO-8859-1')
            df_lp = pd.DataFrame(px_lp['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name='2_1_13_tasa_bruta_natal', con=sao_research_connection, index=False, if_exists='replace')
            df_lp.to_sql(name='2_1_191_tasa_bruta_natal_prov', con=sao_research_connection, index=False,
                         if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                    SELECT "Canarias" AS ter, Periodo AS per, `DATA` AS vd FROM df
                    WHERE `Comunidades y Ciudades Autónomas` LIKE "05%"
                    AND CAST(Periodo AS UNSIGNED) >= 2010
                    ORDER BY Periodo
                    """
            query_lp = """
                    SELECT "Las Palmas" AS ter, Periodo AS per, `DATA` AS vd FROM df_lp
                    WHERE Provincias LIKE "35%"
                    AND CAST(Periodo AS UNSIGNED) >= 2010
                    ORDER BY Periodo
                    """
            df_final = sqldf(query)
            df_final_lp = sqldf(query_lp)

            df_final = pd.concat([df_final, df_final_lp], axis=0, ignore_index=True)
            df_final = pd.pivot_table(df_final, values='vd', index=['per'], columns=['ter'], aggfunc="sum").reset_index()
            df_final.columns = ['per', 'Tasa Bruta de Natalidad Canarias', 'Tasa Bruta de Natalidad Las Palmas']

            df_final.to_csv(f'output_files/tasa_bruta_natalidad_las_palmas.csv', sep=';', index=False,
                            encoding='utf8')

        # endregion



        # region ciclo económico (listo)

        # 10.- PIB corriente
        sumar_datos_provinciales('pib_corriente')

        # 11.- PIB per cápita corriente
        df_pob = pd.read_csv('output_files/poblacion_julio.csv', sep=';', encoding='utf8')
        df_pob = df_pob[df_pob['ter'] == '35 Las Palmas']
        df_pob['ter'] = 'Las Palmas'
        df_pob.rename(columns={'vd': 'pob_julio'}, inplace=True)

        df_pib = pd.read_csv('output_files/pib_corriente_las_palmas.csv', sep=';', encoding='utf8')
        df_pib = df_pib[['ter', 'per', 'vd']]
        df_pib.rename(columns={'vd': 'pib'}, inplace=True)

        df_total = pd.merge(df_pib, df_pob, how='inner', left_on=['ter', 'per'], right_on=['ter', 'per'])
        df_total['vd'] = df_total['pib'] * 1000 / df_total['pob_julio']
        df_total = df_total[['ter', 'per', 'vd']]
        df_total.to_csv('output_files/pib_per_capita_las_palmas.csv', sep=';', index=False, encoding='utf8')


        # 12.- Índice PIB per cápita corriente / Canarias
        df_pib_pc_las_palmas = pd.read_csv('output_files/pib_per_capita_las_palmas.csv', sep=';', encoding='utf8')
        df_pib_pc_las_palmas.rename(columns={'vd': 'pib_pc_las_palmas'}, inplace=True)
        df_pib_pc_canarias = pd.read_excel('input_files/pib_canarias.xlsx', sheet_name='PIB_pc_canarias')
        df_pib_pc_canarias.rename(columns={'vd': 'pib_pc_canarias'}, inplace=True)

        df_total = pd.merge(df_pib_pc_las_palmas, df_pib_pc_canarias, how='inner', left_on=['per'], right_on=['per'])
        df_total['vd'] = df_total['pib_pc_las_palmas'] / df_total['pib_pc_canarias'] * 100
        df_total['ter'] = 'Las Palmas / Canarias'
        df_total = df_total[['ter', 'per', 'vd']]
        df_total.to_csv('output_files/indice_pib_per_capita_canarias_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 13.- Índice PIB per cápita corriente / España
        df_pib_pc_las_palmas = pd.read_csv('output_files/pib_per_capita_las_palmas.csv', sep=';', encoding='utf8')
        df_pib_pc_las_palmas.rename(columns={'vd': 'pib_pc_las_palmas'}, inplace=True)
        df_pib_pc_esp = pd.read_excel('input_files/pib_nacional.xlsx', sheet_name='PIB_pc_nacional')
        df_pib_pc_esp.rename(columns={'vd': 'pib_pc_españa'}, inplace=True)

        df_total = pd.merge(df_pib_pc_las_palmas, df_pib_pc_esp, how='inner', left_on=['per'], right_on=['per'])
        df_total['vd'] = df_total['pib_pc_las_palmas'] / df_total['pib_pc_españa'] * 100
        df_total['ter'] = 'Las Palmas / España'
        df_total = df_total[['ter', 'per', 'vd']]
        df_total.to_csv('output_files/indice_pib_per_capita_españa_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # NUEVO 2023 -- Productividad
        if fila.id_indicador == 195:
            df_esp = pd.read_excel('input_files/productividad_españa.xlsx', sheet_name='productividad')

            df_can = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='pib')
            df_can['ter'] = 'Canarias'
            df_can['per'] = df_can['per'].replace({'2022*': '2022', '2023*': '2023'})
            df_can = df_can[(df_can['per'].astype(int) >= 2010)]
            df_can['per'] = df_can['per'].astype(int)
            df_can = df_can.groupby(['ter', 'per', 'grupo']).agg({'vd': 'sum'}).reset_index()
            df_can.sort_values(by=['grupo', 'ter'], inplace=True)
            df_can = pd.pivot_table(df_can, values='vd', index=['ter', 'per'], columns=['grupo'],
                                    aggfunc="sum").reset_index()
            df_can['vd'] = df_can['PIB'] * 1000 / df_can['Empleo']
            df_can = df_can[['ter', 'per', 'vd']]
            df_can.to_csv('output_files/productividad_total_canarias.csv', sep=';', index=False, encoding='utf8')

            df_prov = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='totales_las palmas')
            df_prov = pd.pivot_table(df_prov, values='vd', index=['ter', 'per'], columns=['grupo'],
                                      aggfunc="sum").reset_index()
            df_prov['vd'] = df_prov['PIB'] * 1000 / df_prov['Empleo']
            df_prov = df_prov[['ter', 'per', 'vd']]
            df_prov['per'] = df_prov['per'].replace({'2022*': '2022', '2023*': '2023'})
            df_prov = df_prov[(df_prov['per'].astype(int) >= 2010)]
            df_prov['per'] = df_prov['per'].astype(int)
            df_prov = pd.concat([df_prov, df_can, df_esp], axis=0, ignore_index=True)
            df_prov = pd.pivot_table(df_prov, values='vd', index='per', columns='ter',
                                               aggfunc='sum').reset_index()
            df_prov['per'] = df_prov['per'].astype(str)
            df_prov['ter'] = 'Las Palmas'
            df_prov.to_csv(f'output_files/productividad_total_las_palmas.csv',
                                     sep=';', index=False, encoding='utf8')

        # 14.- VAB Agricultura
        sumar_datos_provinciales('vab_agricultura')

        # 15.- VAB Construcción
        sumar_datos_provinciales('vab_construccion')

        # 16.- VAB Industria
        sumar_datos_provinciales('vab_industria')

        # 17.- VAB Servicios
        sumar_datos_provinciales('vab_servicios')

        # 18.- Estructura VAB 2010
        sumar_datos_provinciales('estructura_vab_2010')

        # 19.- Estructura VAB 2023
        sumar_datos_provinciales('estructura_vab_2023')

        # endregion



        # region Agricultura (listo)

        # 20.- VAB y empleo en Agricultura
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='agricultura')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df.sort_values(by=['ter','grupo','per'], inplace=True)
            df = df[
                (df['per'].astype(int) >= 2009) &
                ((df['ter'] == 'Fuerteventura') |
                 (df['ter'] == 'Gran Canaria') |
                 (df['ter'] == 'Lanzarote'))
            ]
            # df['ter'] = 'Las Palmas'
            df = df.groupby(['per', 'grupo']).agg({'vd': 'sum'}).reset_index()
            df['ter'] = 'Las Palmas'

            df_final = pd.pivot_table(df, values='vd', index=['ter', 'per'], columns=['grupo'], aggfunc="sum").reset_index()

            # PRODUCTIVIDAD
            df_final['vd'] = df_final['VAB'] * 1000 / df_final['Empleo']
            df_final_prod = df_final[['ter', 'per', 'vd']]
            df_final_prod.to_csv('output_files/productividad_agricultura_las_palmas.csv', sep=';', index=False, encoding='utf8')

            df_final['vd1'] = df_final['VAB'].pct_change() * 100
            df_final['vd2'] = df_final['Empleo'].pct_change() * 100
            df_final.dropna(inplace=True)
            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]
            df_final.to_csv('output_files/vab_empleo_agricultura_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 21.- Empleo registrado en Agricultura
        sumar_datos_provinciales('empleo_registrado_agricultura')

        # 22.- Superficie cultivada
        sumar_datos_provinciales('superficie_cultivada')

        # 23.- Producción agrícola
        sumar_datos_provinciales('produccion_agricola')

        # 24.- Exportación de plátanos
        sumar_datos_provinciales('exportacion_platanos')

        # endregion



        # region industria (listo)

        # 25.- VAB y empleo registrado en el sector de la industria
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='industria')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df.sort_values(by=['ter','grupo','per'], inplace=True)
            df = df[
                (df['per'].astype(int) >= 2009) &
                ((df['ter'] == 'Fuerteventura') |
                 (df['ter'] == 'Gran Canaria') |
                 (df['ter'] == 'Lanzarote'))
            ]
            # df['ter'] = 'Las Palmas'
            df = df.groupby(['per', 'grupo']).agg({'vd': 'sum'}).reset_index()
            df['ter'] = 'Las Palmas'

            df_final = pd.pivot_table(df, values='vd', index=['ter', 'per'], columns=['grupo'], aggfunc="sum").reset_index()

            # PRODUCTIVIDAD
            df_final['vd'] = df_final['VAB'] * 1000 / df_final['Empleo']
            df_final_prod = df_final[['ter', 'per', 'vd']]
            df_final_prod.to_csv('output_files/productividad_industria_las_palmas.csv', sep=';', index=False, encoding='utf8')

            df_final['vd1'] = df_final['VAB'].pct_change() * 100
            df_final['vd2'] = df_final['Empleo'].pct_change() * 100
            df_final.dropna(inplace=True)
            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]
            df_final.to_csv('output_files/vab_empleo_industria_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 26.- Empleo registradio en Industria
        sumar_datos_provinciales('empleo_registrado_industria')

        # 27.- Energía eléctrica disponible
        sumar_datos_provinciales('energia_electrica')


        # endregion



        # region construccion (listo)

        # 28.- VAB y empleo en la construccion
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='construcción')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df.sort_values(by=['ter','grupo','per'], inplace=True)
            df = df[
                (df['per'].astype(int) >= 2009) &
                ((df['ter'] == 'Fuerteventura') |
                 (df['ter'] == 'Gran Canaria') |
                 (df['ter'] == 'Lanzarote'))
            ]
            # df['ter'] = 'Las Palmas'
            df = df.groupby(['per', 'grupo']).agg({'vd': 'sum'}).reset_index()
            df['ter'] = 'Las Palmas'

            df_final = pd.pivot_table(df, values='vd', index=['ter', 'per'], columns=['grupo'], aggfunc="sum").reset_index()

            # PRODUCTIVIDAD
            df_final['vd'] = df_final['VAB'] * 1000 / df_final['Empleo']
            df_final_prod = df_final[['ter', 'per', 'vd']]
            df_final_prod.to_csv('output_files/productividad_construccion_las_palmas.csv', sep=';', index=False, encoding='utf8')

            df_final['vd1'] = df_final['VAB'].pct_change() * 100
            df_final['vd2'] = df_final['Empleo'].pct_change() * 100
            df_final.dropna(inplace=True)
            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]
            df_final.to_csv('output_files/vab_empleo_construccion_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 29.- Empleo registrado en la Construcción
        sumar_datos_provinciales('empleo_registrado_construccion')

        # 30.- Consumo de cemento
        sumar_datos_provinciales('consumo_cemento')

        # NUEVO PROVINCIAL -- Hioptecas constituidas
        if fila.id_indicador == 54:
            # leer el archivo
            df = pd.read_csv('descargados/1_4_54_hipot_const_prov.csv', sep=";", encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                    SELECT "Las Palmas" AS ter, TIME_PERIOD AS per, OBSERVACIONES AS vd FROM df 
                    WHERE TIME_PERIOD NOT LIKE "%/%"
                    AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
                    AND TERRITORIO = "Las Palmas"
                    AND FINCA_NATURALEZA = "Fincas"
                    AND MEDIDAS = "Número de hipotecas"
                    AND SECTOR_INSTITUCIONAL = "Sociedades de depósitos, excepto el banco central"
                    """
            df_final = sqldf(query)

            df_final.to_csv(f'output_files/hipotecas_constituidas_las_palmas.csv', sep=';', index=False,
                            encoding='utf8')
        # endregion



        # region Turismo (listo)

        # 32.- Turistas nacionales e internacionales
        sumar_datos_provinciales('turistas_nacionales_internacionales')

        # 33.- Cruceristas
        sumar_datos_provinciales('cruceristas')

        # 34.- Turistas por país de procedencia
        sumar_datos_provinciales('turistas_segun_pais')

        # 35.- Gasto de los turistas internacionales
        sumar_datos_provinciales('gasto_turistas_internacionales')

        # 37.- Número de plazas
        sumar_datos_provinciales('numero_plazas')
        df_n_plazas = pd.read_csv('output_files/numero_plazas_las_palmas.csv', sep=';', encoding='utf8')
        df_n_plazas.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
        df_n_plazas.to_csv('output_files/numero_plazas_las_palmas.csv', sep=';', index=False, encoding='utf8')


        # 39.- Pernoctaciones
        sumar_datos_provinciales('pernoctaciones_turistas_nac')
        df_pernoctaciones_nac = pd.read_csv('output_files/pernoctaciones_turistas_nac_las_palmas.csv', sep=';', encoding='utf8')

        sumar_datos_provinciales('pernoctaciones_turistas_internac')
        df_pernoctaciones_internac = pd.read_csv('output_files/pernoctaciones_turistas_internac_las_palmas.csv', sep=';', encoding='utf8')

        df_total = pd.concat([df_pernoctaciones_nac, df_pernoctaciones_internac], axis=0).groupby(['per', 'grupo']).agg({'vd': 'sum'}).reset_index().sort_values(by=['grupo', 'per'])
        df_total['ter'] = 'Las Palmas'
        df_total.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
        df_total.to_csv('output_files/pernoctaciones_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 38.- Tasa de ocupación por plazas
        df_pernoctaciones = pd.read_csv('output_files/pernoctaciones_las_palmas.csv', sep=';', encoding='utf8')
        df_pernoctaciones.rename(columns={'vd': 'pernoctaciones'}, inplace=True)
        df_n_plazas = pd.read_csv('output_files/numero_plazas_las_palmas.csv', sep=';', encoding='utf8')
        df_n_plazas.rename(columns={'vd': 'n_plazas'}, inplace=True)

        df_total = pd.merge(df_pernoctaciones, df_n_plazas, how='inner', left_on=['ter', 'per', 'grupo'], right_on=['ter', 'per', 'grupo'])
        df_total['vd'] = df_total['pernoctaciones'] / (df_total['n_plazas'] * 365) * 100
        df_total.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
        df_total = df_total[['ter', 'per', 'grupo', 'vd']]
        df_total.to_csv('output_files/tasa_ocupacion_plazas_las_palmas.csv', sep=';', index=False, encoding='utf8')


        # 40.- estancia media
        df_pernoctaciones = pd.read_csv('output_files/pernoctaciones_las_palmas.csv', sep=';', encoding='utf8')
        df_pernoctaciones.rename(columns={'vd': 'pernoctaciones'}, inplace=True)

        # leer el archivo
        df_1 = pd.read_csv("descargados/1_8_175_pern_est_med_hotel.csv", sep=';', encoding='utf8')
        df_2 = pd.read_csv("descargados/1_8_176_pern_est_med_apart.csv", sep=';', encoding='utf8')

        # transformar el archivo
        pass

        # subirlo a saoresearch
        df_1.to_sql(name="1_8_175_pern_est_med_hotel", con=sao_research_connection, index=False, if_exists='replace')
        df_2.to_sql(name="1_8_176_pern_est_med_apart", con=sao_research_connection, index=False, if_exists='replace')

        # adaptarlo a la gráfica
        query_1 = """
                    SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Hoteles" AS grupo, SUM(OBSERVACIONES) AS vd FROM df_1 
                    WHERE MEDIDAS = "Viajeros entrados"
                    AND TIME_PERIOD NOT LIKE "%/%"
                    AND (
                    TERRITORIO = 'El Hierro'
                    OR TERRITORIO = 'La Gomera'
                    OR TERRITORIO = 'La Palma'
                    OR TERRITORIO = 'Tenerife'
                    OR TERRITORIO = 'Gran Canaria'
                    OR TERRITORIO = 'Fuerteventura'
                    OR TERRITORIO = 'Lanzarote'
                    OR TERRITORIO = 'Canarias'
                    )
                    AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
                    AND (NACIONALIDAD LIKE "Mundo%" OR NACIONALIDAD = "España")
                    GROUP BY TERRITORIO, TIME_PERIOD
                    """
        query_2 = """
                    SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Apartamentos turísticos" AS grupo, SUM(OBSERVACIONES) AS vd FROM df_2  
                    WHERE MEDIDAS = "Viajeros entrados"
                    AND TIME_PERIOD NOT LIKE "%/%"
                    AND (
                    TERRITORIO = 'El Hierro'
                    OR TERRITORIO = 'La Gomera'
                    OR TERRITORIO = 'La Palma'
                    OR TERRITORIO = 'Tenerife'
                    OR TERRITORIO = 'Gran Canaria'
                    OR TERRITORIO = 'Fuerteventura'
                    OR TERRITORIO = 'Lanzarote'
                    OR TERRITORIO = 'Canarias'
                    )
                    AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
                    AND (NACIONALIDAD LIKE "Mundo%" OR NACIONALIDAD = "España")
                    GROUP BY TERRITORIO, TIME_PERIOD
                    """

        df_final_1 = sqldf(query_1)
        df_final_2 = sqldf(query_2)
        df_final = pd.concat([df_final_1, df_final_2], axis=0, ignore_index=True)

        for territorio in df_final['ter'].unique():
            df_final_filtrado = df_final[df_final['ter'] == territorio]
            df_final_filtrado.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
            df_final_filtrado.to_csv(
                f'output_files/viajeros_entrados_{territorio.lower().replace(" ", "_")}.csv',
                sep=';', index=False, encoding='utf8')

        sumar_datos_provinciales('viajeros_entrados')

        df_viajeros_entrados = pd.read_csv('output_files/viajeros_entrados_las_palmas.csv', sep=';', encoding='utf8')
        df_viajeros_entrados.rename(columns={'vd': 'viajeros_entrados'}, inplace=True)

        df_total = pd.merge(df_pernoctaciones, df_viajeros_entrados, how='inner', left_on=['ter', 'per', 'grupo'],
                            right_on=['ter', 'per', 'grupo'])
        df_total['vd'] = df_total['pernoctaciones'] / df_total['viajeros_entrados']
        df_total = df_total[['ter', 'per', 'grupo', 'vd']]
        df_total.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
        df_total.to_csv('output_files/estancia_media_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # endregion



        # region comercio (listo)
        # 42.- Empleo registrado en el sector comercial
        sumar_datos_provinciales('empleo_registrado_comercio')

        # 43.- matriculacion de vehiculos
        sumar_datos_provinciales('matriculacion_vehiculos')

        # endregion



        # region Transporte (listo)

        # 44.- Pasajeros llegados por vía aérea
        sumar_datos_provinciales('pasajeros_via_aerea')

        # 45.- Transporte marítimo de pasajeros
        sumar_datos_provinciales('transporte_maritimo_pasajeros')

        # 46.- Trasnporte marítimo de mercancias
        sumar_datos_provinciales('transporte_maritimo_mercancias')

        # endregion



        # region servicios (listo)
        # 47.- VAB y empleo en el sector serrvicios
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='servicios')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df.sort_values(by=['ter','grupo','per'], inplace=True)
            df = df[
                (df['per'].astype(int) >= 2009) &
                ((df['ter'] == 'Fuerteventura') |
                 (df['ter'] == 'Gran Canaria') |
                 (df['ter'] == 'Lanzarote'))
            ]
            # df['ter'] = 'Las Palmas'
            df = df.groupby(['per', 'grupo']).agg({'vd': 'sum'}).reset_index()
            df['ter'] = 'Las Palmas'

            df_final = pd.pivot_table(df, values='vd', index=['ter', 'per'], columns=['grupo'], aggfunc="sum").reset_index()

            # PRODUCTIVIDAD
            df_final['vd'] = df_final['VAB'] * 1000 / df_final['Empleo']
            df_final_prod = df_final[['ter', 'per', 'vd']]
            df_final_prod.to_csv('output_files/productividad_servicios_las_palmas.csv', sep=';', index=False, encoding='utf8')

            df_final['vd1'] = df_final['VAB'].pct_change() * 100
            df_final['vd2'] = df_final['Empleo'].pct_change() * 100
            df_final.dropna(inplace=True)
            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]
            df_final.to_csv('output_files/vab_empleo_servicios_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 48.- Empleo registrado en el sector servicios
        sumar_datos_provinciales('empleo_registrado_servicios')

        # 49.- Empleo registrado en la hostelería
        sumar_datos_provinciales('empleo_registrado_hosteleria')

        # endregion



        # region mercado laboral (listo)

        # 50.- Afiliados a la seguridad social
        sumar_datos_provinciales('afiliados_ss')

        # 51.- poblacion ocupada
        sumar_datos_provinciales('ocupados')

        # 52.- empleo registrado por sectores
        if fila.id_indicador == 47:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_47_empleo_registrado.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                SELECT DISTINCT TIME_PERIOD AS per, TERRITORIO as ter, ACTIVIDAD_ECONOMICA as grupo, OBSERVACIONES as vd FROM df
                WHERE (ACTIVIDAD_ECONOMICA = "Agricultura, ganadería, silvicultura y pesca" OR
                ACTIVIDAD_ECONOMICA = "Industria" OR
                ACTIVIDAD_ECONOMICA = "Construcción" OR
                ACTIVIDAD_ECONOMICA = "Servicios")
                AND SITUACION_EMPLEO = 'Total'
                AND TIME_PERIOD NOT LIKE "% %"
                AND (
                    TERRITORIO = 'El Hierro'
                    OR TERRITORIO = 'La Gomera'
                    OR TERRITORIO = 'La Palma'
                    OR TERRITORIO = 'Tenerife'
                    OR TERRITORIO = 'Gran Canaria'
                    OR TERRITORIO = 'Fuerteventura'
                    OR TERRITORIO = 'Lanzarote'
                    OR TERRITORIO = 'Canarias'
                )
                AND CAST(TIME_PERIOD AS UNSIGNED) >= 2009
            """
            df_final = sqldf(query)

            sectores_etq = {
                "Agricultura, ganadería, silvicultura y pesca": "Agricultura",
                "Industria": "Industria",
                "Construcción": "Construcción",
                "Servicios": "Servicios"
            }

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio].copy()
                df_final_filtrado['grupo'] = df_final_filtrado['grupo'].map(sectores_etq)
                df_final_filtrado.to_csv(
                    f'output_files/empleo_registrado_sectores_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

            sumar_datos_provinciales('empleo_registrado_sectores')

            df_empleo_registrado_sectores = pd.read_csv('output_files/empleo_registrado_sectores_las_palmas.csv', sep=';', encoding='utf8')
            df_empleo_registrado_sectores = pd.pivot_table(df_empleo_registrado_sectores, values='vd', index=['ter', 'per'], columns=['grupo'],
                                      aggfunc="sum").reset_index()
            df_empleo_registrado_sectores['Agricultura'] = df_empleo_registrado_sectores['Agricultura'].pct_change()
            df_empleo_registrado_sectores['Industria'] = df_empleo_registrado_sectores['Industria'].pct_change()
            df_empleo_registrado_sectores['Construcción'] = df_empleo_registrado_sectores['Construcción'].pct_change()
            df_empleo_registrado_sectores['Servicios'] = df_empleo_registrado_sectores['Servicios'].pct_change()
            df_empleo_registrado_sectores = df_empleo_registrado_sectores[
                ['per', 'ter', 'Agricultura', 'Industria', 'Construcción', 'Servicios']]
            df_empleo_registrado_sectores.dropna(inplace=True)
            df_empleo_registrado_sectores.to_csv('output_files/empleo_registrado_sectores_tv_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 53.- Estructura del empleo registrado 2010
        sumar_datos_provinciales('empleo_registrado_sectores_2010')

        # 54.- Estructura del empleo registrado 2023
        sumar_datos_provinciales('empleo_registrado_sectores_2023')

        # 55.- poblacion activa y tasa de actividad -- EPA ISTAC --
        if fila.id_indicador == 94:
            sumar_datos_provinciales('activos_tasa_actividad')
            df_activos = pd.read_csv('output_files/activos_tasa_actividad_las_palmas.csv', sep=';', encoding='utf8')
            df_activos = df_activos[['ter', 'per', 'vd1']]
            df_activos['per'] = df_activos['per'].astype(str)

            df_2 = pd.read_csv("descargados/1_5_94_epa_istac_islas.csv", sep=';', encoding='utf8')

            df_final_2 = df_2[
                (df_2['SITUACION_LABORAL'] == "Personas en edad de trabajar") &
                (df_2['SEXO'] == "Total") &
                (df_2['EDAD'] == "Total") &
                (df_2['TIME_PERIOD'].str[:4].astype(int) >= 2010) &
                (df_2['TIME_PERIOD'].str[:4].astype(int) < 2024)
                ]
            df_final_2 = df_final_2[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final_2 = df_final_2.groupby([df_final_2['TERRITORIO'], df_final_2['TIME_PERIOD'].str[:4]]).agg(
                {'OBSERVACIONES': 'mean'}).reset_index()
            df_final_2.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'pers_edad_trab'
            }, inplace=True)

            for territorio in df_final_2['ter'].unique():
                df_final_filtrado = df_final_2[df_final_2['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/personas_edad_trabajar_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False,
                    encoding='utf8')

            sumar_datos_provinciales('personas_edad_trabajar')
            df_edad_trabajar = pd.read_csv('output_files/personas_edad_trabajar_las_palmas.csv', sep=';', encoding='utf8')
            df_edad_trabajar['per'] = df_edad_trabajar['per'].astype(str)

            df_final = pd.merge(df_edad_trabajar, df_activos, how='inner', left_on=['per', 'ter'], right_on=['per', 'ter'])
            df_final['vd2'] = df_final['vd1'] / df_final['pers_edad_trab'] * 100
            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]
            df_final.to_csv('output_files/activos_tasa_actividad_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 56.- Tasa de actividad masculina y femenina
        if fila.id_indicador == 94:
            df_1 = pd.read_csv("descargados/1_5_94_epa_istac_islas.csv", sep=';', encoding='utf8')

            df_final_1 = df_1[
                (df_1['SITUACION_LABORAL'] == "Personas activas") &
                (df_1['SEXO'] != "Total") &
                (df_1['EDAD'] == "Total") &
                (df_1['TIME_PERIOD'].str[:4].astype(int) >= 2010) &
                (df_1['TIME_PERIOD'].str[:4].astype(int) < 2024)
                ]
            df_final_1 = df_final_1[['TERRITORIO', 'TIME_PERIOD', 'SEXO', 'OBSERVACIONES']]
            df_final_1 = df_final_1.groupby([df_final_1['TERRITORIO'], df_final_1['SEXO'], df_final_1['TIME_PERIOD'].str[:4]]).agg(
                {'OBSERVACIONES': 'mean'}).reset_index()
            df_final_1.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'SEXO': 'grupo',
                'OBSERVACIONES': 'pers_acti'
            }, inplace=True)

            for territorio in df_final_1['ter'].unique():
                df_final_filtrado = df_final_1[df_final_1['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/personas_activas_sexo_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False,
                    encoding='utf8')

            sumar_datos_provinciales('personas_activas_sexo')
            df_activos = pd.read_csv('output_files/personas_activas_sexo_las_palmas.csv', sep=';',
                                           encoding='utf8')

            df_2 = pd.read_csv("descargados/1_5_94_epa_istac_islas.csv", sep=';', encoding='utf8')

            df_final_2 = df_2[
                (df_2['SITUACION_LABORAL'] == "Personas en edad de trabajar") &
                (df_2['SEXO'] != "Total") &
                (df_2['EDAD'] == "Total") &
                (df_2['TIME_PERIOD'].str[:4].astype(int) >= 2010) &
                (df_2['TIME_PERIOD'].str[:4].astype(int) < 2024)
                ]
            df_final_2 = df_final_2[['TERRITORIO', 'TIME_PERIOD', 'SEXO', 'OBSERVACIONES']]
            df_final_2 = df_final_2.groupby([df_final_2['TERRITORIO'], df_final_2['SEXO'], df_final_2['TIME_PERIOD'].str[:4]]).agg(
                {'OBSERVACIONES': 'mean'}).reset_index()
            df_final_2.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'SEXO': 'grupo',
                'OBSERVACIONES': 'pers_edad_trab'
            }, inplace=True)

            for territorio in df_final_2['ter'].unique():
                df_final_filtrado = df_final_2[df_final_2['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/personas_edad_trabajar_sexo_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False,
                    encoding='utf8')

            sumar_datos_provinciales('personas_edad_trabajar_sexo')
            df_edad_trabajar = pd.read_csv('output_files/personas_edad_trabajar_sexo_las_palmas.csv', sep=';',
                                           encoding='utf8')

            df_final = pd.merge(df_activos, df_edad_trabajar, how='inner', left_on=['per', 'ter', 'grupo'], right_on=['per', 'ter', 'grupo'])
            df_final['vd'] = df_final['pers_acti'] / df_final['pers_edad_trab'] * 100
            df_final = df_final[['ter', 'per', 'grupo', 'vd']]
            df_final.to_csv('output_files/tasa_actividad_sexos_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 57.- poblacion parada y tasa de paro -- EPA ISTAC --
        if fila.id_indicador == 94:
            sumar_datos_provinciales('parados_tasa_paro')
            df_parados = pd.read_csv('output_files/parados_tasa_paro_las_palmas.csv', sep=';', encoding='utf8')
            df_parados = df_parados[['ter', 'per', 'vd1']]
            df_parados['per'] = df_parados['per'].astype(str)

            df_2 = pd.read_csv("descargados/1_5_94_epa_istac_islas.csv", sep=';', encoding='utf8')

            df_final_2 = df_2[
                (df_2['SITUACION_LABORAL'] == "Personas activas") &
                (df_2['SEXO'] == "Total") &
                (df_2['EDAD'] == "Total") &
                (df_2['TIME_PERIOD'].str[:4].astype(int) >= 2010) &
                (df_2['TIME_PERIOD'].str[:4].astype(int) < 2024)
                ]
            df_final_2 = df_final_2[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final_2 = df_final_2.groupby([df_final_2['TERRITORIO'], df_final_2['TIME_PERIOD'].str[:4]]).agg(
                {'OBSERVACIONES': 'mean'}).reset_index()
            df_final_2.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'pers_acti'
            }, inplace=True)

            for territorio in df_final_2['ter'].unique():
                df_final_filtrado = df_final_2[df_final_2['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/personas_activas_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False,
                    encoding='utf8')

            sumar_datos_provinciales('personas_activas')
            df_edad_trabajar = pd.read_csv('output_files/personas_activas_las_palmas.csv', sep=';',
                                           encoding='utf8')
            df_edad_trabajar['per'] = df_edad_trabajar['per'].astype(str)

            df_final = pd.merge(df_edad_trabajar, df_parados, how='inner', left_on=['per', 'ter'],
                                right_on=['per', 'ter'])
            df_final['vd2'] = df_final['vd1'] / df_final['pers_acti'] * 100
            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]
            df_final.to_csv('output_files/parados_tasa_paro_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # 58.- Tasa de paro masculina y femenina
        if fila.id_indicador == 94:
            df_1 = pd.read_csv("descargados/1_5_94_epa_istac_islas.csv", sep=';', encoding='utf8')

            df_final_1 = df_1[
                (df_1['SITUACION_LABORAL'] == "Personas desempleadas") &
                (df_1['SEXO'] != "Total") &
                (df_1['EDAD'] == "Total") &
                (df_1['TIME_PERIOD'].str[:4].astype(int) >= 2010) &
                (df_1['TIME_PERIOD'].str[:4].astype(int) < 2024)
                ]
            df_final_1 = df_final_1[['TERRITORIO', 'TIME_PERIOD', 'SEXO', 'OBSERVACIONES']]
            df_final_1 = df_final_1.groupby(
                [df_final_1['TERRITORIO'], df_final_1['SEXO'], df_final_1['TIME_PERIOD'].str[:4]]).agg(
                {'OBSERVACIONES': 'mean'}).reset_index()
            df_final_1.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'SEXO': 'grupo',
                'OBSERVACIONES': 'pers_para'
            }, inplace=True)

            for territorio in df_final_1['ter'].unique():
                df_final_filtrado = df_final_1[df_final_1['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/personas_paradas_sexo_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False,
                    encoding='utf8')

            sumar_datos_provinciales('personas_paradas_sexo')
            df_activos = pd.read_csv('output_files/personas_paradas_sexo_las_palmas.csv', sep=';',
                                     encoding='utf8')

            df_2 = pd.read_csv("descargados/1_5_94_epa_istac_islas.csv", sep=';', encoding='utf8')

            df_final_2 = df_2[
                (df_2['SITUACION_LABORAL'] == "Personas activas") &
                (df_2['SEXO'] != "Total") &
                (df_2['EDAD'] == "Total") &
                (df_2['TIME_PERIOD'].str[:4].astype(int) >= 2010) &
                (df_2['TIME_PERIOD'].str[:4].astype(int) < 2024)
                ]
            df_final_2 = df_final_2[['TERRITORIO', 'TIME_PERIOD', 'SEXO', 'OBSERVACIONES']]
            df_final_2 = df_final_2.groupby(
                [df_final_2['TERRITORIO'], df_final_2['SEXO'], df_final_2['TIME_PERIOD'].str[:4]]).agg(
                {'OBSERVACIONES': 'mean'}).reset_index()
            df_final_2.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'SEXO': 'grupo',
                'OBSERVACIONES': 'pers_acti'
            }, inplace=True)

            for territorio in df_final_2['ter'].unique():
                df_final_filtrado = df_final_2[df_final_2['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/personas_activas_sexo_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False,
                    encoding='utf8')

            sumar_datos_provinciales('personas_activas_sexo')
            df_edad_trabajar = pd.read_csv('output_files/personas_activas_sexo_las_palmas.csv', sep=';',
                                           encoding='utf8')

            df_final = pd.merge(df_activos, df_edad_trabajar, how='inner', left_on=['per', 'ter', 'grupo'],
                                right_on=['per', 'ter', 'grupo'])
            df_final['vd'] = df_final['pers_para'] / df_final['pers_acti'] * 100
            df_final = df_final[['ter', 'per', 'grupo', 'vd']]
            df_final.to_csv('output_files/tasa_paro_sexos_las_palmas.csv', sep=';', index=False, encoding='utf8')

        # endregion



        # region sector público (listo)

        # 59.- empleo registrado en adm. pub. educ. y sanidad
        sumar_datos_provinciales('empleo_registrado_admin_pub')


        # endregion



        # region empresa y entorno regulatorio (listo)

        # 61.- Empresas inscritas en la seguridad social (por sectores)
        sumar_datos_provinciales('empresas_inscritas_ss')

        # 62.- empresas inscritas en la seguridad social
        sumar_datos_provinciales('empresas_inscritas_ss_sectores')


        # endregion

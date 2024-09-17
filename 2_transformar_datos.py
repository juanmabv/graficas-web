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
# endregion

# region conexion a saoresearch
sao_research_connection = sqlal.create_engine("mysql+pymysql://saoresearch:4Tg66a$r@87.106.125.96:3306/sao_research")
# endregion

# region listado indicadores a transformar
df_indicadores = pd.read_excel('input_files/indicadores.xlsx', sheet_name='indicadores')

lista_ids = df_indicadores['id_indicador'].tolist()

indicadores_concretos = [160]
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

        # 1.- Población residente (islas TF / LP / LG / EH)
        if fila.id_indicador == 2:
            # leer el archivo
            px = pyaxis.parse('descargados/2_1_2_pob_sexo_edad_sc.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])
            df.to_csv('pruebas/POBLACION_INE_PROV_SANTA_CRUZ.csv', sep=';', index=False, encoding='utf8')

            alias_sc = {
                "38001 Adeje": "Tenerife",
                "38002 Agulo": "La Gomera",
                "38003 Alajeró": "La Gomera",
                "38004 Arafo": "Tenerife",
                "38005 Arico": "Tenerife",
                "38006 Arona": "Tenerife",
                "38007 Barlovento": "La Palma",
                "38008 Breña Alta": "La Palma",
                "38009 Breña Baja": "La Palma",
                "38010 Buenavista del Norte": "Tenerife",
                "38011 Candelaria": "Tenerife",
                "38012 Fasnia": "Tenerife",
                "38013 Frontera": "El Hierro",
                "38014 Fuencaliente de la Palma": "La Palma",
                "38015 Garachico": "Tenerife",
                "38016 Garafía": "La Palma",
                "38017 Granadilla de Abona": "Tenerife",
                "38018 Guancha, La": "Tenerife",
                "38019 Guía de Isora": "Tenerife",
                "38020 Güímar": "Tenerife",
                "38021 Hermigua": "La Gomera",
                "38022 Icod de los Vinos": "Tenerife",
                "38024 Llanos de Aridane, Los": "La Palma",
                "38025 Matanza de Acentejo, La": "Tenerife",
                "38026 Orotava, La": "Tenerife",
                "38027 Paso, El": "La Palma",
                "38901 Pinar de El Hierro, El": "El Hierro",
                "38028 Puerto de la Cruz": "Tenerife",
                "38029 Puntagorda": "La Palma",
                "38030 Puntallana": "La Palma",
                "38031 Realejos, Los": "Tenerife",
                "38032 Rosario, El": "Tenerife",
                "38033 San Andrés y Sauces": "La Palma",
                "38023 San Cristóbal de La Laguna": "Tenerife",
                "38034 San Juan de la Rambla": "Tenerife",
                "38035 San Miguel de Abona": "Tenerife",
                "38036 San Sebastián de la Gomera": "La Gomera",
                "38037 Santa Cruz de la Palma": "La Palma",
                "38038 Santa Cruz de Tenerife": "Tenerife",
                "38039 Santa Úrsula": "Tenerife",
                "38040 Santiago del Teide": "Tenerife",
                "38041 Sauzal, El": "Tenerife",
                "38042 Silos, Los": "Tenerife",
                "38043 Tacoronte": "Tenerife",
                "38044 Tanque, El": "Tenerife",
                "38045 Tazacorte": "La Palma",
                "38046 Tegueste": "Tenerife",
                "38047 Tijarafe": "La Palma",
                "38049 Valle Gran Rey": "La Gomera",
                "38050 Vallehermoso": "La Gomera",
                "38048 Valverde": "El Hierro",
                "38051 Victoria de Acentejo, La": "Tenerife",
                "38052 Vilaflor de Chasna": "Tenerife",
                "38053 Villa de Mazo": "La Palma"
            }
            df['isla'] = df['Municipios'].map(alias_sc)

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT 
                isla AS ter, 
                CAST(Periodo AS UNSIGNED) AS per, 
                SUM(`DATA`) AS vd 
            FROM 
                df 
            WHERE 
                isla IS NOT NULL 
                AND Sexo = 'Total' 
                AND CAST(Periodo AS UNSIGNED) >= 2010 
            GROUP BY 
                isla, 
                CAST(Periodo AS UNSIGNED);
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/poblacion_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 1.- Población residente (islas GC / LZ / FTV + provincia Las Palmas)
        if fila.id_indicador == 186:
            # leer el archivo
            px = pyaxis.parse('descargados/2_1_186_pob_sexo_edad_lp.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])
            df.to_csv('pruebas/POBLACION_INE_PROV_LAS_PALMAS.csv', sep=';', index=False, encoding='utf8')

            alias_lp = {
                "35 Palmas, Las": "Las Palmas",
                "35001 Agaete": "Gran Canaria",
                "35002 Agüimes": "Gran Canaria",
                "35020 Aldea de San Nicolás, La": "Gran Canaria",
                "35003 Antigua": "Fuerteventura",
                "35004 Arrecife": "Lanzarote",
                "35005 Artenara": "Gran Canaria",
                "35006 Arucas": "Gran Canaria",
                "35007 Betancuria": "Fuerteventura",
                "35008 Firgas": "Gran Canaria",
                "35009 Gáldar": "Gran Canaria",
                "35010 Haría": "Lanzarote",
                "35011 Ingenio": "Gran Canaria",
                "35012 Mogán": "Gran Canaria",
                "35013 Moya": "Gran Canaria",
                "35014 Oliva, La": "Fuerteventura",
                "35015 Pájara": "Fuerteventura",
                "35016 Palmas de Gran Canaria, Las": "Gran Canaria",
                "35017 Puerto del Rosario": "Fuerteventura",
                "35018 San Bartolomé": "Lanzarote",
                "35019 San Bartolomé de Tirajana": "Gran Canaria",
                "35021 Santa Brígida": "Gran Canaria",
                "35022 Santa Lucía de Tirajana": "Gran Canaria",
                "35023 Santa María de Guía de Gran Canaria": "Gran Canaria",
                "35024 Teguise": "Lanzarote",
                "35025 Tejeda": "Gran Canaria",
                "35026 Telde": "Gran Canaria",
                "35027 Teror": "Gran Canaria",
                "35028 Tías": "Lanzarote",
                "35029 Tinajo": "Lanzarote",
                "35030 Tuineje": "Fuerteventura",
                "35032 Valleseco": "Gran Canaria",
                "35031 Valsequillo de Gran Canaria": "Gran Canaria",
                "35033 Vega de San Mateo": "Gran Canaria",
                "35034 Yaiza": "Lanzarote"
            }
            df['isla'] = df['Municipios'].map(alias_lp)

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                        SELECT
                            isla AS ter,
                            CAST(Periodo AS UNSIGNED) AS per,
                            SUM(`DATA`) AS vd
                        FROM
                            df
                        WHERE
                            isla IS NOT NULL
                            AND Sexo = 'Total'
                            AND CAST(Periodo AS UNSIGNED) >= 2010
                        GROUP BY
                            isla,
                            CAST(Periodo AS UNSIGNED);
                        """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/poblacion_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                                         index=False, encoding='utf8')

        # 2.- Población residente por nacionalidad (total)
        if fila.id_indicador == 3:
            # leer el archivo
            px = pyaxis.parse('descargados/2_1_3_pob_sexo_nacion.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT Islas as ter, Periodo AS per, `DATA` AS vd FROM df WHERE Islas NOT LIKE "07%" AND Islas <> 'Formentera' AND Islas <> 'Ibiza' AND Islas <> 'Mallorca' AND Islas <> 'Menorca' and Periodo LIKE "%enero%" AND Sexo = 'Total' AND Nacionalidad = 'Total';"""
            df_final = sqldf(query)
            df_final['ter'] = df_final['ter'].apply(reorganizar_texto)
            df_final['per'] = df_final['per'].str[-4:]
            df_final = df_final[df_final['per'].astype(int) >= 2010]
            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/poblacion_total_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 2.- Población residente por nacionalidad (desglose)
        if fila.id_indicador == 3:
            # leer el archivo
            px = pyaxis.parse('descargados/2_1_3_pob_sexo_nacion.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT Islas as ter, Periodo AS per, Nacionalidad as grupo, `DATA` AS vd FROM df WHERE Islas NOT LIKE "07%" AND Islas <> 'Formentera' AND Islas <> 'Ibiza' AND Islas <> 'Mallorca' AND Islas <> 'Menorca' and Periodo LIKE "%enero%" AND Sexo = 'Total' AND Nacionalidad <> 'Total';"""
            df_final = sqldf(query)
            df_final['ter'] = df_final['ter'].apply(reorganizar_texto)
            df_final['per'] = df_final['per'].str[-4:]
            df_final = df_final[df_final['per'].astype(int) >= 2010]
            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/poblacion_nacionalidad_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                                         index=False, encoding='utf8')

        # 3.- Nacimientos
        if fila.id_indicador == 165:
            # leer el archivo
            px = pyaxis.parse('descargados/1_1_165_istac_nacimientos.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT `Municipios de residencia de las madres` as ter, `Años` AS per, `DATA` AS vd FROM df in2 WHERE Sexos = "AMBOS SEXOS" AND CAST(`Años` AS UNSIGNED) >= 2010;"""
            df_final = sqldf(query)
            df_final = df_final[df_final['ter'].str.isupper()]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/nacimientos_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 3.- Defunciones
        if fila.id_indicador == 166:
            # leer el archivo
            df = pd.read_csv('descargados/1_1_166_istac_defunciones.csv', sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT TIME_PERIOD AS per, TERRITORIO AS ter, OBSERVACIONES AS vd FROM df WHERE SEXO = "Total" AND EDAD = "Total" AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010;"""
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/defunciones_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

        # 4.- Saldo migratorio
        if fila.id_indicador == 6:
            # leer el archivo
            px = pyaxis.parse('descargados/1_1_6_saldo_migratorio.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])
            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT Islas AS ter, Años AS per, `Saldo migratorio` AS grupo, `DATA` AS vd FROM df WHERE (`Saldo migratorio` = 'Saldo exterior con el extranjero' OR `Saldo migratorio` = 'Saldo exterior con otras CC.AA.') AND Nacionalidades = 'TOTAL' AND Sexos ='AMBOS SEXOS' AND CAST(Años AS UNSIGNED) >= 2010"""
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/saldo_migratorio_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                                         index=False, encoding='utf8')

        # 5.- Pirámide poblacional 2010 (ISTAC)
        if fila.id_indicador == 1:
            # leer el archivo
            df = pd.read_csv('descargados/1_1_1_pob_sexo_edad.csv', sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT TERRITORIO as ter, TIME_PERIOD AS per, EDAD as grupo, OBSERVACIONES AS vd FROM df WHERE TIME_PERIOD = 2010 AND (EDAD LIKE "De % años" OR EDAD LIKE "Menor de 5 años") AND EDAD <> "De 15 a 64 años" AND SEXO  = "Total" AND (TERRITORIO = "Canarias" OR TERRITORIO = "El Hierro" OR TERRITORIO = "La Gomera" OR TERRITORIO = "La Palma" OR TERRITORIO = "Tenerife" OR  TERRITORIO = "Fuerteventura" OR TERRITORIO = "Lanzarote" OR TERRITORIO = "Gran Canaria")"""
            df_final = sqldf(query)

            alias_colores = {
                "De 95 a 99 años": "Población dependiente",
                "De 90 a 94 años": "Población dependiente",
                "De 85 a 89 años": "Población dependiente",
                "De 80 a 84 años": "Población dependiente",
                "De 75 a 79 años": "Población dependiente",
                "De 70 a 74 años": "Población dependiente",
                "De 65 a 69 años": "Población en edad de trabajar",
                "De 60 a 64 años": "Población en edad de trabajar",
                "De 55 a 59 años": "Población en edad de trabajar",
                "De 50 a 54 años": "Población en edad de trabajar",
                "De 45 a 49 años": "Población en edad de trabajar",
                "De 40 a 44 años": "Población en edad de trabajar",
                "De 35 a 39 años": "Población en edad de trabajar",
                "De 30 a 34 años": "Población en edad de trabajar",
                "De 25 a 29 años": "Población en edad de trabajar",
                "De 20 a 24 años": "Población en edad de trabajar",
                "De 15 a 19 años": "Población dependiente",
                "De 10 a 14 años": "Población dependiente",
                "De 5 a 9 años": "Población dependiente",
                "Menor de 5 años": "Población dependiente",
            }

            df_final['color'] = df_final['grupo'].map(alias_colores)
            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/priamide_poblacion_2010_istac_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                                         index=False, encoding='utf8')

        # 6.- Pirámide poblacional 2022 (ISTAC)
        if fila.id_indicador == 1:
            # leer el archivo
            df = pd.read_csv('descargados/1_1_1_pob_sexo_edad.csv', sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT TERRITORIO as ter, TIME_PERIOD AS per, EDAD as grupo, OBSERVACIONES AS vd FROM df WHERE TIME_PERIOD = 2022 AND (EDAD LIKE "De % años" OR EDAD LIKE "Menor de 5 años") AND EDAD <> "De 15 a 64 años" AND SEXO  = "Total" AND (TERRITORIO = "Canarias" OR TERRITORIO = "El Hierro" OR TERRITORIO = "La Gomera" OR TERRITORIO = "La Palma" OR TERRITORIO = "Tenerife" OR  TERRITORIO = "Fuerteventura" OR TERRITORIO = "Lanzarote" OR TERRITORIO = "Gran Canaria")"""
            df_final = sqldf(query)

            alias_colores = {
                "De 95 a 99 años": "Población dependiente",
                "De 90 a 94 años": "Población dependiente",
                "De 85 a 89 años": "Población dependiente",
                "De 80 a 84 años": "Población dependiente",
                "De 75 a 79 años": "Población dependiente",
                "De 70 a 74 años": "Población dependiente",
                "De 65 a 69 años": "Población en edad de trabajar",
                "De 60 a 64 años": "Población en edad de trabajar",
                "De 55 a 59 años": "Población en edad de trabajar",
                "De 50 a 54 años": "Población en edad de trabajar",
                "De 45 a 49 años": "Población en edad de trabajar",
                "De 40 a 44 años": "Población en edad de trabajar",
                "De 35 a 39 años": "Población en edad de trabajar",
                "De 30 a 34 años": "Población en edad de trabajar",
                "De 25 a 29 años": "Población en edad de trabajar",
                "De 20 a 24 años": "Población en edad de trabajar",
                "De 15 a 19 años": "Población dependiente",
                "De 10 a 14 años": "Población dependiente",
                "De 5 a 9 años": "Población dependiente",
                "Menor de 5 años": "Población dependiente",
            }

            df_final['color'] = df_final['grupo'].map(alias_colores)
            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/priamide_poblacion_2022_istac_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 5.- Pirámide poblacional 2010 (INE)
        if fila.id_indicador == 187:
            # leer el archivo
            px = pyaxis.parse('descargados/2_1_187_pob_sexo_edad_islas_ine.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT `Grupo quinquenal de edad` as per, Islas as ter, `DATA` AS vd FROM df WHERE Periodo LIKE "%2010" AND `Grupo quinquenal de edad` <> 'Todas las edades' AND Islas NOT LIKE "07%" AND Islas <> 'Formentera' AND Islas <> 'Ibiza' AND Islas <> 'Mallorca' AND Islas <> 'Menorca' and Periodo LIKE "%enero%" AND Sexo = 'Total';"""
            df_final = sqldf(query)

            alias_colores = {
                "85 y más años": "Población dependiente",
                "De 80 a 84 años": "Población dependiente",
                "De 75 a 79 años": "Población dependiente",
                "De 70 a 74 años": "Población dependiente",
                "De 65 a 69 años": "Población en edad de trabajar",
                "De 60 a 64 años": "Población en edad de trabajar",
                "De 55 a 59 años": "Población en edad de trabajar",
                "De 50 a 54 años": "Población en edad de trabajar",
                "De 45 a 49 años": "Población en edad de trabajar",
                "De 40 a 44 años": "Población en edad de trabajar",
                "De 35 a 39 años": "Población en edad de trabajar",
                "De 30 a 34 años": "Población en edad de trabajar",
                "De 25 a 29 años": "Población en edad de trabajar",
                "De 20 a 24 años": "Población en edad de trabajar",
                "De 15 a 19 años": "Población dependiente",
                "De 10 a 14 años": "Población dependiente",
                "De 5 a 9 años": "Población dependiente",
                "De 0 a 4 años": "Población dependiente",
            }

            df_final['grupo'] = df_final['per'].map(alias_colores)

            df_final['ter'] = df_final['ter'].apply(reorganizar_texto)
            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/piramide_poblacion_2010_ine_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 6.- Pirámide poblacional 2023 (INE)
        if fila.id_indicador == 187:
            # leer el archivo
            px = pyaxis.parse('descargados/2_1_187_pob_sexo_edad_islas_ine.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT `Grupo quinquenal de edad` as per, Islas as ter, `DATA` AS vd FROM df WHERE Periodo LIKE "%2023" AND `Grupo quinquenal de edad` <> 'Todas las edades' AND Islas NOT LIKE "07%" AND Islas <> 'Formentera' AND Islas <> 'Ibiza' AND Islas <> 'Mallorca' AND Islas <> 'Menorca' and Periodo LIKE "%enero%" AND Sexo = 'Total';"""
            df_final = sqldf(query)

            alias_colores = {
                "85 y más años": "Población dependiente",
                "De 80 a 84 años": "Población dependiente",
                "De 75 a 79 años": "Población dependiente",
                "De 70 a 74 años": "Población dependiente",
                "De 65 a 69 años": "Población en edad de trabajar",
                "De 60 a 64 años": "Población en edad de trabajar",
                "De 55 a 59 años": "Población en edad de trabajar",
                "De 50 a 54 años": "Población en edad de trabajar",
                "De 45 a 49 años": "Población en edad de trabajar",
                "De 40 a 44 años": "Población en edad de trabajar",
                "De 35 a 39 años": "Población en edad de trabajar",
                "De 30 a 34 años": "Población en edad de trabajar",
                "De 25 a 29 años": "Población en edad de trabajar",
                "De 20 a 24 años": "Población en edad de trabajar",
                "De 15 a 19 años": "Población dependiente",
                "De 10 a 14 años": "Población dependiente",
                "De 5 a 9 años": "Población dependiente",
                "De 0 a 4 años": "Población dependiente",
            }

            df_final['grupo'] = df_final['per'].map(alias_colores)

            df_final['ter'] = df_final['ter'].apply(reorganizar_texto)
            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/piramide_poblacion_2023_ine_{territorio.lower().replace(" ", "_")}.csv',
                    sep=';', index=False, encoding='utf8')

        # 7.- Índice de envejecimiento
        if fila.id_indicador == 7:
            # Canarias
            df_pob_las_palmas = pd.read_csv('output_files/poblacion_total_35_las_palmas.csv', sep=';', encoding='utf8')
            df_pob_santa_cruz = pd.read_csv('output_files/poblacion_total_38_santa_cruz_de_tenerife.csv', sep=';', encoding='utf8')

            df_pob_canarias = pd.concat([df_pob_las_palmas, df_pob_santa_cruz], axis=0, ignore_index=True)
            df_pob_canarias = df_pob_canarias.groupby(['per']).agg({'vd': 'sum'}).reset_index()
            df_pob_canarias['ter'] = "Canarias"
            df_pob_canarias['per'] = df_pob_canarias['per'].astype(str)

            px = pyaxis.parse('descargados/2_1_187_pob_sexo_edad_islas_ine.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            query_canarias = """
            SELECT Periodo AS per, "Mayores de 64" as grupo, "Canarias" as ter, SUM(`DATA`) AS vd FROM df
            WHERE Periodo LIKE "%enero%"
            AND `Grupo quinquenal de edad` <> "Todas las edades"
            AND Islas NOT LIKE "07%"
            AND (Islas = "35 Palmas, Las" OR Islas = "38 Santa Cruz de Tenerife")
            AND (`Grupo quinquenal de edad` = "De 65 a 69 años" OR
            `Grupo quinquenal de edad` = "De 70 a 74 años" OR
            `Grupo quinquenal de edad` = "De 75 a 79 años" OR
            `Grupo quinquenal de edad` = "De 80 a 84 años" OR
            `Grupo quinquenal de edad` = "85 y más años")
            AND Sexo = "Total"
            GROUP BY Periodo;
            """

            df_may_64_canarias = sqldf(query_canarias)
            df_may_64_canarias['per'] = df_may_64_canarias['per'].str[-4:]

            df_final_canarias = pd.merge(df_may_64_canarias, df_pob_canarias, how='inner', left_on=['per', 'ter'], right_on=['per', 'ter'])
            df_final_canarias['vd'] = df_final_canarias['vd_x'] / df_final_canarias['vd_y']
            df_final_canarias = df_final_canarias[['ter', 'per', 'vd']]
            df_final_canarias.to_csv('output_files/indice_envejecimiento_canarias.csv', sep=';', index=False, encoding='utf8')

            # Islas
            lista_islas = ['el_hierro', 'fuerteventura', 'gran_canaria', 'la_gomera', 'la_palma', 'lanzarote', 'tenerife']
            dicc_isla_territorio = {'el_hierro': 'Hierro, El',
            'fuerteventura': 'Fuerteventura',
            'gran_canaria': 'Gran Canaria',
            'la_gomera': 'Gomera, La',
            'la_palma': 'Palma, La',
            'lanzarote': 'Lanzarote',
            'tenerife': 'Tenerife'}

            for isla in lista_islas:
                isla_territorio = dicc_isla_territorio[isla]

                df_pob_isla = pd.read_csv(f'output_files/poblacion_total_{isla}.csv', sep=';', encoding='utf8')
                df_pob_isla['per'] = df_pob_isla['per'].astype(str)

                px = pyaxis.parse('descargados/2_1_187_pob_sexo_edad_islas_ine.px', encoding='ISO-8859-1')
                df = pd.DataFrame(px['DATA'])

                query_isla = f"""
                            SELECT Periodo AS per, "Mayores de 64" as grupo, "{reorganizar_texto(isla_territorio)}" as ter, SUM(`DATA`) AS vd FROM df
                            WHERE Periodo LIKE "%enero%"
                            AND `Grupo quinquenal de edad` <> "Todas las edades"
                            AND Islas NOT LIKE "07%"
                            AND Islas = "{isla_territorio}"
                            AND (`Grupo quinquenal de edad` = "De 65 a 69 años" OR
                            `Grupo quinquenal de edad` = "De 70 a 74 años" OR
                            `Grupo quinquenal de edad` = "De 75 a 79 años" OR
                            `Grupo quinquenal de edad` = "De 80 a 84 años" OR
                            `Grupo quinquenal de edad` = "85 y más años")
                            AND Sexo = "Total"
                            GROUP BY Periodo;
                            """
                df_may_64_isla = sqldf(query_isla)

                df_may_64_isla['per'] = df_may_64_isla['per'].str[-4:]
                df_may_64_isla['vd'] = df_may_64_isla['vd'].astype(float)

                df_final_isla = pd.merge(df_may_64_isla, df_pob_isla, how='inner', left_on=['per', 'ter'],
                                             right_on=['per', 'ter'])
                df_final_isla['vd'] = df_final_isla['vd_x'] / df_final_isla['vd_y']
                df_final_isla = df_final_isla[['ter', 'per', 'vd']]
                df_final_isla.to_csv(f'output_files/indice_envejecimiento_{isla}.csv', sep=';', index=False, encoding='utf8')


            # region antiguo
            # # leer el archivo
            # px = pyaxis.parse('descargados/1_1_7_ind_envej.px', encoding='ISO-8859-1')
            # df = pd.DataFrame(px['DATA'])
            #
            # # transformar el archivo
            # pass
            #
            # # subirlo a saoresearch
            # df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')
            #
            # # adaptarlo a la gráfica
            # query = """SELECT `Municipios por islas` as ter, `Años` AS per, `DATA` AS vd FROM df WHERE CAST(`Años` AS UNSIGNED) >= 2010;"""
            # df_final = sqldf(query)
            # df_final = df_final[df_final['ter'].str.isupper()]
            #
            # for territorio in df_final['ter'].unique():
            #     df_final_filtrado = df_final[df_final['ter'] == territorio]
            #     df_final_filtrado.to_csv(f'output_files/indice_envejecimiento_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')
            # endregion

        # 8.- Tasa de dependencia
        if fila.id_indicador == 8:
            px = pyaxis.parse('descargados/2_1_187_pob_sexo_edad_islas_ine.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            lista_islas = ['el_hierro', 'fuerteventura', 'gran_canaria', 'la_gomera', 'la_palma', 'lanzarote',
                           'tenerife']
            dicc_isla_territorio = {'el_hierro': 'Hierro, El',
                                    'fuerteventura': 'Fuerteventura',
                                    'gran_canaria': 'Gran Canaria',
                                    'la_gomera': 'Gomera, La',
                                    'la_palma': 'Palma, La',
                                    'lanzarote': 'Lanzarote',
                                    'tenerife': 'Tenerife'}

            for isla in lista_islas:
                isla_territorio = dicc_isla_territorio[isla]

                df_pob_isla = pd.read_csv(f'output_files/poblacion_total_{isla}.csv', sep=';', encoding='utf8')
                df_pob_isla['per'] = df_pob_isla['per'].astype(str)

                px = pyaxis.parse('descargados/2_1_187_pob_sexo_edad_islas_ine.px', encoding='ISO-8859-1')
                df = pd.DataFrame(px['DATA'])

                query_isla = f"""
                SELECT Periodo AS per, `Grupo quinquenal de edad` AS grupo, Islas AS ter, `DATA` AS vd FROM df
                WHERE Periodo LIKE "%enero%"
                AND `Grupo quinquenal de edad` <> "Todas las edades"
                AND Islas = "{dicc_isla_territorio[isla]}"
                AND Islas NOT LIKE "Formentera"
                AND Islas NOT LIKE "Mallorca"
                AND Islas NOT LIKE "Menorca"
                AND Islas NOT LIKE "Ibiza"
                AND Sexo = "Total";
                """
                df_final = sqldf(query_isla)

                alias_grupos_edad = {
                    "85 y más años": "mayor_64",
                    "De 80 a 84 años": "mayor_64",
                    "De 75 a 79 años": "mayor_64",
                    "De 70 a 74 años": "mayor_64",
                    "De 65 a 69 años": "mayor_64",
                    "De 60 a 64 años": "edad_trabajar",
                    "De 55 a 59 años": "edad_trabajar",
                    "De 50 a 54 años": "edad_trabajar",
                    "De 45 a 49 años": "edad_trabajar",
                    "De 40 a 44 años": "edad_trabajar",
                    "De 35 a 39 años": "edad_trabajar",
                    "De 30 a 34 años": "edad_trabajar",
                    "De 25 a 29 años": "edad_trabajar",
                    "De 20 a 24 años": "edad_trabajar",
                    "De 15 a 19 años": "menor_16",
                    "De 10 a 14 años": "menor_16",
                    "De 5 a 9 años": "menor_16",
                    "De 0 a 4 años": "menor_16",
                }

                df_final['grupo'] = df_final['grupo'].map(alias_grupos_edad)
                df_final['per'] = df_final['per'].str[-4:]
                df_final = df_final[df_final['per'].astype(int) >= 2010]
                df_final['vd'] = df_final['vd'].astype(float)
                df_final = df_final.groupby(['per', 'ter', 'grupo']).agg({'vd': 'sum'}).reset_index()
                df_final = pd.pivot_table(df_final, values='vd', columns='grupo', index=['ter', 'per'], aggfunc='sum').reset_index()
                df_final['Tasa de dependencia'] = ((df_final['mayor_64'] + df_final['menor_16']) / df_final['edad_trabajar']) * 100
                df_final['Tasa de dependencia de la población menor de 16 años'] = (df_final['menor_16'] / df_final['edad_trabajar']) * 100
                df_final['Tasa de dependencia de la población mayor de 64 años'] = (df_final['mayor_64'] / df_final['edad_trabajar']) * 100
                df_final = df_final[['ter', 'per', 'Tasa de dependencia', 'Tasa de dependencia de la población menor de 16 años', 'Tasa de dependencia de la población mayor de 64 años']]
                df_final.to_csv(f'output_files/tasa_dependencia_total_{isla}.csv', sep=';', index=False, encoding='utf8')

                # df_isla['per'] = df_isla['per'].str[-4:]
                # df_isla['vd'] = df_isla['vd'].astype(float)
                #
                # df_final_isla = pd.merge(df_may_64_isla, df_pob_isla, how='inner', left_on=['per', 'ter'],
                #                          right_on=['per', 'ter'])
                # df_final_isla['vd'] = df_final_isla['vd_x'] / df_final_isla['vd_y'] * 100
                # df_final_isla = df_final_isla[['ter', 'per', 'vd']]
                # df_final_isla.to_csv(f'output_files/indice_envejecimiento_{isla}.csv', sep=';', index=False,
                #                      encoding='utf8')

            # region antiguo

            # # leer el archivo
            # px = pyaxis.parse('descargados/1_1_8_tasa_depend.px', encoding='ISO-8859-1')
            # df = pd.DataFrame(px['DATA'])
            #
            # # transformar el archivo
            # pass
            #
            # # subirlo a saoresearch
            # df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')
            #
            # # adaptarlo a la gráfica
            # query = """SELECT `Municipios por islas` as ter, `Años` AS per, `DATA` AS vd FROM df;"""
            # df_final = sqldf(query)
            # df_final = df_final[df_final['ter'].str.isupper()]
            # df_final = df_final[df_final['per'].astype(int) >= 2010]
            #
            # for territorio in df_final['ter'].unique():
            #     df_final_filtrado = df_final[df_final['ter'] == territorio]
            #     df_final_filtrado.to_csv(
            #         f'output_files/tasa_dependencia_total_{territorio.lower().replace(" ", "_")}.csv', sep=';',
            #         index=False, encoding='utf8')

            # endregion

        # 9.- Tasa bruta de natalidad
        if fila.id_indicador == 12:
            # leer el archivo
            px = pyaxis.parse('descargados/1_1_12_tasa_bruta_natal.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """SELECT `Islas de residencia de las madres` as ter, `Años` AS per, `DATA` AS vd FROM df WHERE CAST(`Años` AS UNSIGNED) >= 2010;"""
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/tasa_bruta_natalidad_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # endregion



        # region ciclo económico (productividad)

        # 10.- PIB corriente
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='pib')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df_final = df[(df['grupo'] == "PIB")]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/pib_corriente_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 11.- PIB per cápita corriente
        if fila.id_indicador == 189:
            df_pib = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='pib')
            df_pib['per'] = df_pib['per'].replace({'2022*': '2022', '2023*': '2023'})
            df_pib['per'] = df_pib['per'].astype(str)
            df_pib = df_pib[(df_pib['grupo'] == "PIB")]

            # leer el archivo población
            px = pyaxis.parse('descargados/2_1_3_pob_sexo_nacion.px', encoding='ISO-8859-1')
            df_pob = pd.DataFrame(px['DATA'])

            # transformar el archivo población
            pass

            # subirlo a saoresearch población
            df_pob.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')
            query = """SELECT Islas as ter, Periodo AS per, `DATA` AS vd FROM df_pob WHERE Islas NOT LIKE "07%" AND Islas <> 'Formentera' AND Islas <> 'Ibiza' AND Islas <> 'Mallorca' AND Islas <> 'Menorca' and Periodo LIKE "%julio%" AND Sexo = 'Total' AND Nacionalidad = 'Total';"""
            df_pob = sqldf(query)
            df_pob['ter'] = df_pob['ter'].apply(reorganizar_texto)
            df_pob['per'] = df_pob['per'].str[-4:]
            df_pob = df_pob[df_pob['per'].astype(int) >= 2010]

            df_pob_23 = pd.read_csv('input_files/poblacion_julio_23.csv', sep=';', encoding='utf8')
            df_pob_23['Islas'] = df_pob_23['Islas'].apply(reorganizar_texto)
            df_pob_23 = df_pob_23[['Islas', 'Total']]
            df_pob_23 = df_pob_23.rename(columns={
                'Islas': 'ter',
                'Total': 'vd'
            })
            df_pob_23['per'] = "2023"

            df_pob = pd.concat([df_pob, df_pob_23], axis=0, ignore_index=True)
            df_pob.sort_values(by=['ter', 'per'], inplace=True)
            df_pob.to_csv('output_files/poblacion_julio.csv', sep=';', index=False, encoding='utf8')

            df_final = pd.merge(df_pib, df_pob, how='inner', left_on=['per', 'ter'], right_on=['per', 'ter'])
            df_final['vd'] = df_final['vd_x'].astype(float) / df_final['vd_y'].astype(float) * 1000
            df_final = df_final[['ter', 'per', 'vd']]
            df_final.to_csv('output_files/pib_per_capita_islas.csv', sep=";", index=False, encoding='utf8')

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/pib_per_capita_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')


        # 12.- Índice PIB per cápita corriente / Canarias
        if fila.id_indicador == 189:
            df_islas = pd.read_csv('output_files/pib_per_capita_islas.csv', sep=';', encoding='utf8')

            df_canarias = pd.read_excel('input_files/pib_canarias.xlsx', sheet_name='PIB_pc_canarias')

            for territorio in df_islas['ter'].unique():
                df_islas_filtrado = df_islas[df_islas['ter'] == territorio]
                df_islas_filtrado = pd.merge(df_islas_filtrado, df_canarias, how='inner', left_on='per', right_on='per')
                df_islas_filtrado['vd'] = df_islas_filtrado['vd_x'] / df_islas_filtrado['vd_y'] * 100
                df_islas_filtrado['ter'] = df_islas_filtrado['ter_x']
                df_islas_filtrado = df_islas_filtrado[['ter', 'per', 'vd']]
                df_islas_filtrado.to_csv(f'output_files/indice_pib_per_capita_canarias_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

        # 13.- Índice PIB per cápita corriente / España
        if fila.id_indicador == 189:
            df_islas = pd.read_csv('output_files/pib_per_capita_islas.csv', sep=';', encoding='utf8')

            df_nacional = pd.read_excel('input_files/pib_nacional.xlsx', sheet_name='PIB_pc_nacional')

            for territorio in df_islas['ter'].unique():
                df_islas_filtrado = df_islas[df_islas['ter'] == territorio]
                df_islas_filtrado = pd.merge(df_islas_filtrado, df_nacional, how='inner', left_on='per', right_on='per')
                df_islas_filtrado['vd'] = df_islas_filtrado['vd_x'] / df_islas_filtrado['vd_y'] * 100
                df_islas_filtrado['ter'] = df_islas_filtrado['ter_x']
                df_islas_filtrado = df_islas_filtrado[['ter', 'per', 'vd']]
                df_islas_filtrado.to_csv(f'output_files/indice_pib_per_capita_españa_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

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
            df_can = pd.pivot_table(df_can, values='vd', index=['ter', 'per'], columns=['grupo'], aggfunc="sum").reset_index()
            df_can['vd'] = df_can['PIB'] * 1000 / df_can['Empleo']
            df_can = df_can[['ter', 'per', 'vd']]
            df_can.to_csv('output_files/productividad_total_canarias.csv', sep=';', encoding='utf8')

            df_islas = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='pib')
            df_islas = pd.pivot_table(df_islas, values='vd', index=['ter', 'per'], columns=['grupo'], aggfunc="sum").reset_index()
            df_islas['vd'] = df_islas['PIB'] * 1000 / df_islas['Empleo']
            df_islas = df_islas[['ter', 'per', 'vd']]
            for territorio in df_islas['ter'].unique():
                df_islas_filtrado = df_islas[df_islas['ter'] == territorio]
                df_islas_filtrado['per'] = df_islas_filtrado['per'].replace({'2022*': '2022', '2023*': '2023'})
                df_islas_filtrado = df_islas_filtrado[(df_islas_filtrado['per'].astype(int) >= 2010)]
                df_islas_filtrado['per'] = df_islas_filtrado['per'].astype(int)
                df_islas_filtrado = pd.concat([df_islas_filtrado, df_can, df_esp], axis=0, ignore_index=True)
                df_islas_filtrado = pd.pivot_table(df_islas_filtrado, values='vd', index='per', columns='ter', aggfunc='sum').reset_index()
                df_islas_filtrado['per'] = df_islas_filtrado['per'].astype(str)
                df_islas_filtrado['ter'] = territorio
                df_islas_filtrado.to_csv(f'output_files/productividad_total_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')


        # 14.- VAB Agricultura
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='agricultura')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df_final = df[(df['grupo'] == "VAB")]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/vab_agricultura_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 15.- VAB Construcción
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='construcción')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df_final = df[(df['grupo'] == "VAB")]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/vab_construccion_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 16.- VAB Industria
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='industria')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df_final = df[(df['grupo'] == "VAB")]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/vab_industria_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 17.- VAB Servicios
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='servicios')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df_final = df[(df['grupo'] == "VAB")]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/vab_servicios_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 18.- Estructura VAB 2010
        if fila.id_indicador == 189:
            df_agricultura = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='agricultura')
            df_agricultura = df_agricultura[df_agricultura['grupo'] == 'VAB']
            df_agricultura['grupo'] = 'agricultura'
            df_construccion = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='construcción')
            df_construccion = df_construccion[df_construccion['grupo'] == 'VAB']
            df_construccion['grupo'] = 'construcción'
            df_industria = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='industria')
            df_industria = df_industria[df_industria['grupo'] == 'VAB']
            df_industria['grupo'] = 'industria'
            df_servicios = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='servicios')
            df_servicios = df_servicios[df_servicios['grupo'] == 'VAB']
            df_servicios['grupo'] = 'servicios'

            df_final = pd.concat([
                df_agricultura[(df_agricultura['per'] == 2010) & (df_agricultura['grupo'] == 'agricultura')],
                df_construccion[(df_construccion['per'] == 2010) & (df_construccion['grupo'] == 'construcción')],
                df_industria[(df_industria['per'] == 2010) & (df_industria['grupo'] == 'industria')],
                df_servicios[(df_servicios['per'] == 2010) & (df_servicios['grupo'] == 'servicios')],
            ], axis=0, ignore_index=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/estructura_vab_2010_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 19.- Estructura VAB 2023
        if fila.id_indicador == 189:
            df_agricultura = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='agricultura')
            df_agricultura = df_agricultura.replace({'2022*': '2022', '2023*': '2023'})
            df_agricultura = df_agricultura[df_agricultura['grupo'] == 'VAB']
            df_agricultura['grupo'] = 'agricultura'
            df_construccion = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='construcción')
            df_construccion = df_construccion.replace({'2022*': '2022', '2023*': '2023'})
            df_construccion = df_construccion[df_construccion['grupo'] == 'VAB']
            df_construccion['grupo'] = 'construcción'
            df_industria = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='industria')
            df_industria = df_industria.replace({'2022*': '2022', '2023*': '2023'})
            df_industria = df_industria[df_industria['grupo'] == 'VAB']
            df_industria['grupo'] = 'industria'
            df_servicios = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='servicios')
            df_servicios = df_servicios.replace({'2022*': '2022', '2023*': '2023'})
            df_servicios = df_servicios[df_servicios['grupo'] == 'VAB']
            df_servicios['grupo'] = 'servicios'

            df_final = pd.concat([
                df_agricultura[(df_agricultura['per'] == "2023") & (df_agricultura['grupo'] == 'agricultura')],
                df_construccion[(df_construccion['per'] == "2023") & (df_construccion['grupo'] == 'construcción')],
                df_industria[(df_industria['per'] == "2023") & (df_industria['grupo'] == 'industria')],
                df_servicios[(df_servicios['per'] == "2023") & (df_servicios['grupo'] == 'servicios')],
            ], axis=0, ignore_index=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                # df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/estructura_vab_2023_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # endregion



        # region Agricultura

        # 20.- VAB y empleo en Agricultura
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='agricultura')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df.sort_values(by=['ter','grupo','per'], inplace=True)
            df = df[df['per'].astype(int) >= 2009]
            df_final = pd.pivot_table(df, values='vd', index=['ter', 'per'], columns=['grupo'], aggfunc="sum").reset_index()

            # PRODUCTIVIDAD
            df_final['vd'] = df_final['VAB'] * 1000 / df_final['Empleo']
            df_final_prod = df_final[['ter', 'per', 'vd']]
            for territorio in df_final['ter'].unique():
                df_final_prod_filtrado = df_final_prod[df_final['ter'] == territorio]
                df_final_prod_filtrado = df_final_prod_filtrado[df_final_prod_filtrado['per'].astype(int) >= 2010]
                df_final_prod_filtrado.to_csv(
                    f'output_files/productividad_agricultura_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

            df_final['vd1'] = df_final['VAB'].pct_change() * 100
            df_final['vd2'] = df_final['Empleo'].pct_change() * 100
            df_final.dropna(inplace=True)

            df_final = df_final[['ter','per','vd1','vd2']]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.to_csv(
                    f'output_files/vab_empleo_agricultura_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')



        # 21.- Empleo registrado en Agricultura
        if fila.id_indicador == 47:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_47_empleo_registrado.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

           # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                SELECT DISTINCT TIME_PERIOD AS per, TERRITORIO as ter, OBSERVACIONES as vd FROM df
                WHERE ACTIVIDAD_ECONOMICA = "Agricultura, ganadería, silvicultura y pesca"
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
                AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_agricultura_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 22.- Superficie cultivada
        if fila.id_indicador == 48:
            # leer el archivo
            df = pd.read_csv('descargados/1_3_48_superf_cultiv.csv', sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT territorio AS ter, fechas AS per, valor AS vd FROM df
            WHERE fechas >= 2010 AND
            granularidad_espacial = "insular" AND 
            granularidad_temporal = "anual"
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/superficie_cultivada_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 23.- Producción agrícola
        if fila.id_indicador == 49:
            # leer el archivo
            df = pd.read_csv('descargados/1_3_49_prod_agric.csv', sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            # df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final = df[
                df['PRODUCTO_AGRICOLA'] == "Cultivos"
            ]
            df_final = df_final[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'vd'
            }, inplace=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/produccion_agricola_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 24.- Exportación de plátanos
        if fila.id_indicador == 50:
            # leer el archivo
            df = pd.read_csv('descargados/1_3_50_export_platanos.csv', sep=';', encoding='utf8')
            # transformar el archivo
            pass

            # subirlo a saoresearch
            # df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final = df[
                (df['TERRITORIO_ORIGEN_DESTINO_COMERCIAL'] == "Total") &
                (~df['TIME_PERIOD'].str.contains('/'))
                ]
            df_final = df_final[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'vd'
            }, inplace=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/exportacion_platanos_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # endregion



        # region industria

        # 25.- VAB y empleo registrado en el sector de la industria
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='industria')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df.sort_values(by=['ter', 'grupo', 'per'], inplace=True)
            df = df[df['per'].astype(int) >= 2009]
            df_final = pd.pivot_table(df, values='vd', index=['ter', 'per'], columns=['grupo'],
                                      aggfunc="sum").reset_index()

            # PRODUCTIVIDAD
            df_final['vd'] = df_final['VAB'] * 1000 / df_final['Empleo']
            df_final_prod = df_final[['ter', 'per', 'vd']]
            for territorio in df_final['ter'].unique():
                df_final_prod_filtrado = df_final_prod[df_final['ter'] == territorio]
                df_final_prod_filtrado = df_final_prod_filtrado[df_final_prod_filtrado['per'].astype(int) >= 2010]
                df_final_prod_filtrado.to_csv(
                    f'output_files/productividad_industria_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

            df_final['vd1'] = df_final['VAB'].pct_change() * 100
            df_final['vd2'] = df_final['Empleo'].pct_change() * 100
            df_final.dropna(inplace=True)

            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.to_csv(
                    f'output_files/vab_empleo_industria_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 26.- Empleo registradio en Industria
        if fila.id_indicador == 47:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_47_empleo_registrado.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                SELECT DISTINCT TIME_PERIOD AS per, TERRITORIO as ter, OBSERVACIONES as vd FROM df
                WHERE ACTIVIDAD_ECONOMICA = "Industria"
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
                AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_industria_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 27.- Energía eléctrica disponible
        if fila.id_indicador == 52:
            # leer el archivo
            df = pd.read_csv("descargados/1_4_52_energ_elect.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, OBSERVACIONES AS vd FROM df 
            WHERE MEDIDAS = "Energía eléctrica"
            AND TIME_PERIOD NOT LIKE "%/%"
            AND FLUJO_ENERGIA = "Demanda interior"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010;
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/energia_electrica_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # endregion



        # region construccion

        # 28.- VAB y empleo en la construccion
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='construcción')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df.sort_values(by=['ter', 'grupo', 'per'], inplace=True)
            df = df[df['per'].astype(int) >= 2009]
            df_final = pd.pivot_table(df, values='vd', index=['ter', 'per'], columns=['grupo'],
                                      aggfunc="sum").reset_index()

            # PRODUCTIVIDAD
            df_final['vd'] = df_final['VAB'] * 1000 / df_final['Empleo']
            df_final_prod = df_final[['ter', 'per', 'vd']]
            for territorio in df_final['ter'].unique():
                df_final_prod_filtrado = df_final_prod[df_final['ter'] == territorio]
                df_final_prod_filtrado = df_final_prod_filtrado[df_final_prod_filtrado['per'].astype(int) >= 2010]
                df_final_prod_filtrado.to_csv(
                    f'output_files/productividad_construccion_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

            df_final['vd1'] = df_final['VAB'].pct_change() * 100
            df_final['vd2'] = df_final['Empleo'].pct_change() * 100
            df_final.dropna(inplace=True)

            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.to_csv(
                    f'output_files/vab_empleo_construccion_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 29.- Empleo registrado en la Construcción
        if fila.id_indicador == 47:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_47_empleo_registrado.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                SELECT DISTINCT TIME_PERIOD AS per, TERRITORIO as ter, OBSERVACIONES as vd FROM df
                WHERE ACTIVIDAD_ECONOMICA = "Construcción"
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
                AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_construccion_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 30.- Consumo de cemento
        if fila.id_indicador == 53:
            # leer el archivo
            df = pd.read_csv("descargados/1_4_53_venta_may_cemen.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, OBSERVACIONES AS vd FROM df
            WHERE MEDIDAS = "Venta de cemento"
            AND TIME_PERIOD NOT LIKE "%/%"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010;
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(f'output_files/consumo_cemento_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # endregion



        # region Turismo (listo)

        # 32.- Turistas nacionales e internacionales
        if fila.id_indicador == 170:
            # leer el archivo
            df = pd.read_csv("descargados/1_8_170_tur_res_tipo_islas.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, LUGAR_RESIDENCIA AS grupo, OBSERVACIONES AS vd FROM df
            WHERE TIPO_VIAJERO = "Turista"
            AND (LUGAR_RESIDENCIA LIKE "España%" OR
            LUGAR_RESIDENCIA LIKE "Mundo%")
            AND MEDIDAS = "Turistas"
            """
            df_final = sqldf(query)

            dicc_procedencias = {
                'España (excluida Canarias)': 'Nacionales',
                'Mundo (excluida España)': 'Internacionales'
            }

            df_final['grupo'] = df_final['grupo'].map(dicc_procedencias)
            df_final['per'] = df_final['per'].str[-4:]
            df_final = df_final[(df_final['per'].astype(int) >= 2010) & (df_final['per'].astype(int) < 2024)]
            df_final = df_final.groupby(['ter', 'per', 'grupo']).agg({'vd': 'sum'}).reset_index()

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['grupo', 'per'], inplace=True)
                df_final_filtrado.to_csv(f'output_files/turistas_nacionales_internacionales_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

        # 33.- Cruceristas
        if fila.id_indicador == 122:
            # leer el archivo
            px = pyaxis.parse('descargados/1_8_122_trans_mari_viaj_pe.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT Puertos AS ter, Periodos AS per, `DATA` AS vd FROM df
            WHERE Indicadores = "Pasajeros de crucero"
            AND Periodos LIKE "%TOTAL%"
            """
            df_final = sqldf(query)

            df_final['per'] = df_final['per'].str[:4]

            dicc_puertos = {
                'CANARIAS': 'Canarias',
                'Puerto de Arrecife': 'Lanzarote',
                'Puerto del Rosario': 'Fuerteventura',
                'Puerto de La Luz y Las Palmas': 'Gran Canaria',
                'Puerto de Salinetas': 'Gran Canaria',
                'Puerto de Arinaga': 'Gran Canaria',
                'Puerto de Santa Cruz de Tenerife': 'Tenerife',
                'Puerto de Los Cristianos': 'Tenerife',
                'Puerto de Granadilla': 'Tenerife',
                'Puerto de San Sebastián de La Gomera': 'La Gomera',
                'Puerto de Santa Cruz de La Palma': 'La Palma',
                'Puerto de La Estaca': 'El Hierro'
            }
            df_final['ter'] = df_final['ter'].map(dicc_puertos)
            df_final = df_final[df_final['per'].astype(int) >= 2010]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado['vd'] = pd.to_numeric(df_final_filtrado['vd'], errors='coerce')
                df_final_filtrado = df_final_filtrado.groupby(['ter', 'per']).agg({'vd': 'sum'}).reset_index()
                df_final_filtrado.to_csv(
                    f'output_files/cruceristas_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 34.- Turistas por país de procedencia
        if fila.id_indicador == 170:
            # leer el archivo
            df = pd.read_csv("descargados/1_8_170_tur_res_tipo_islas.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, LUGAR_RESIDENCIA AS grupo, OBSERVACIONES AS vd FROM df
            WHERE TIPO_VIAJERO = "Turista"
            AND LUGAR_RESIDENCIA != "Total"
            AND LUGAR_RESIDENCIA NOT LIKE "Mundo%"
            AND MEDIDAS = "Turistas"
            """
            df_final = sqldf(query)

            df_final['grupo'] = df_final['grupo'].replace({'España (excluida Canarias)': 'Resto de España', 'Otros países o territorios del mundo (excluida España)': 'Otros países'})
            df_final['per'] = df_final['per'].str[-4:]
            df_final = df_final[(df_final['per'].astype(int) == 2010) | (df_final['per'].astype(int) == 2023)]
            df_final = df_final.groupby(['ter', 'per', 'grupo']).agg({'vd': 'sum'}).reset_index()

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['per', 'grupo'], inplace=True)
                df_final_filtrado.to_csv(f'output_files/turistas_segun_pais_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

        # 35.- Gasto de los turistas internacionales
        if fila.id_indicador == 172:
            # leer el archivo
            df = pd.read_csv("descargados/1_8_172_gasto_turis_islas.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, PAIS_RESIDENCIA AS grupo, OBSERVACIONES AS vd FROM df 
            WHERE MEDIDAS = "Gasto"
            AND CONCEPTOS_GASTOS_TURISTICOS = "Total"
            AND TIME_PERIOD NOT LIKE "% %"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            AND (PAIS_RESIDENCIA = "España (excluida Canarias)" OR
            PAIS_RESIDENCIA = "Total")
            ORDER BY TIME_PERIOD
            """
            df_final = sqldf(query)

            df_final = pd.pivot_table(df_final, values='vd', index=['ter', 'per'], columns=['grupo'], aggfunc="sum").reset_index()

            df_final['vd'] = df_final['Total'] - df_final['España (excluida Canarias)']
            df_final = df_final[['ter', 'per', 'vd']]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/gasto_turistas_internacionales_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

        # 36.- Gasto medio por turista
        if fila.id_indicador == 173:
            # leer el archivo
            df = pd.read_csv("descargados/1_8_173_gasto_med_tur_islas.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, OBSERVACIONES AS vd FROM df
            WHERE MEDIDAS = "Gasto por turista"
            AND CONCEPTOS_GASTOS_TURISTICOS = "Total"
            AND TIME_PERIOD NOT LIKE "% %"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            AND PAIS_RESIDENCIA = "Total"
            ORDER BY TERRITORIO, TIME_PERIOD
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/gasto_medio_turista_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

        # 37.- Numero de plazas
        if fila.id_indicador == 174:
            # leer el archivo
            df_1 = pd.read_csv("descargados/1_8_174_n_plazas_aloj_tur_hotel.csv", sep=';', encoding='utf8')
            df_2 = pd.read_csv("descargados/1_8_188_n_plazas_aloj_tur_aptos.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df_1.to_sql(name="1_8_174_n_plazas_aloj_tur_hotel", con=sao_research_connection, index=False, if_exists='replace')
            df_2.to_sql(name="1_8_188_n_plazas_aloj_tur_aptos", con=sao_research_connection, index=False, if_exists='replace')
            # adaptarlo a la gráfica
            query_1 = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Hoteles" AS grupo, OBSERVACIONES AS vd FROM df_1
            WHERE TIME_PERIOD NOT LIKE "%/%"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
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
            AND MEDIDAS = "Plazas"
            AND ALOJAMIENTO_TURISTICO_CATEGORIA = "Total"
            ORDER BY TERRITORIO, TIME_PERIOD 
            """
            query_2 = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Apartamentos turísticos" AS grupo, OBSERVACIONES AS vd FROM df_2
            WHERE TIME_PERIOD NOT LIKE "%/%"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
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
            AND MEDIDAS = "Plazas"
            AND ALOJAMIENTO_TURISTICO_CATEGORIA = "Total"
            ORDER BY TERRITORIO, TIME_PERIOD 
            """
            df_final_1 = sqldf(query_1)
            df_final_2 = sqldf(query_2)
            df_final = pd.concat([df_final_1, df_final_2], axis=0, ignore_index=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/numero_plazas_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

        # 38.- Tasa de ocupacion por plazas
        if fila.id_indicador == 174:
            # leer el archivo
            df_1 = pd.read_csv("descargados/1_8_174_n_plazas_aloj_tur_hotel.csv", sep=';', encoding='utf8')
            df_2 = pd.read_csv("descargados/1_8_188_n_plazas_aloj_tur_aptos.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df_1.to_sql(name="1_8_174_n_plazas_aloj_tur_hotel", con=sao_research_connection, index=False, if_exists='replace')
            df_2.to_sql(name="1_8_188_n_plazas_aloj_tur_aptos", con=sao_research_connection, index=False, if_exists='replace')
            # adaptarlo a la gráfica
            query_1 = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Hoteles" AS grupo, OBSERVACIONES AS vd FROM df_1
            WHERE TIME_PERIOD NOT LIKE "%/%"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
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
            AND MEDIDAS = "Tasa de ocupación por plaza"
            AND ALOJAMIENTO_TURISTICO_CATEGORIA = "Total"
            ORDER BY TERRITORIO, TIME_PERIOD 
            """
            query_2 = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Apartamentos turísticos" AS grupo, OBSERVACIONES AS vd FROM df_2
            WHERE TIME_PERIOD NOT LIKE "%/%"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
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
            AND MEDIDAS = "Tasa de ocupación por plaza"
            AND ALOJAMIENTO_TURISTICO_CATEGORIA = "Total"
            ORDER BY TERRITORIO, TIME_PERIOD 
            """
            df_final_1 = sqldf(query_1)
            df_final_2 = sqldf(query_2)
            df_final = pd.concat([df_final_1, df_final_2], axis=0, ignore_index=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/tasa_ocupacion_plazas_{territorio.lower().replace(" ", "_")}.csv',
                                         sep=';', index=False, encoding='utf8')

        # 39.1.- Pernoctaciones de los turistas internacionales
        if fila.id_indicador == 175:
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
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Hoteles" AS grupo, OBSERVACIONES AS vd FROM df_1
            WHERE MEDIDAS = "Pernoctaciones"
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
            AND NACIONALIDAD LIKE "Mundo%"
            """
            query_2 = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Apartamentos turísticos" AS grupo, OBSERVACIONES AS vd FROM df_2
            WHERE MEDIDAS = "Pernoctaciones"
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
            AND NACIONALIDAD LIKE "Mundo%"
            """

            df_final_1 = sqldf(query_1)
            df_final_2 = sqldf(query_2)
            df_final = pd.concat([df_final_1, df_final_2], axis=0, ignore_index=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/pernoctaciones_turistas_internac_{territorio.lower().replace(" ", "_")}.csv',
                    sep=';', index=False, encoding='utf8')

        # 39.2.- Pernoctaciones de los turistas nacionales
        if fila.id_indicador == 175:
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
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Hoteles" AS grupo, OBSERVACIONES AS vd FROM df_1 
            WHERE MEDIDAS = "Pernoctaciones"
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
            AND NACIONALIDAD = "España"
            """
            query_2 = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Apartamentos turísticos" AS grupo, OBSERVACIONES AS vd FROM df_2
            WHERE MEDIDAS = "Pernoctaciones"
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
            AND NACIONALIDAD = "España"
            """

            df_final_1 = sqldf(query_1)
            df_final_2 = sqldf(query_2)
            df_final = pd.concat([df_final_1, df_final_2], axis=0, ignore_index=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/pernoctaciones_turistas_nac_{territorio.lower().replace(" ", "_")}.csv',
                    sep=';', index=False, encoding='utf8')

        # 40.1.- estancia media turistas internacionales
        if fila.id_indicador == 175:
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
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, ALOJAMIENTO_TURISTICO_TIPO AS grupo, OBSERVACIONES AS vd FROM df_1
            WHERE MEDIDAS = "Estancia media"
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
            AND NACIONALIDAD LIKE "Mundo%"
            """
            query_2 = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Apartamentos turísticos" AS grupo, OBSERVACIONES AS vd FROM df_2
            WHERE MEDIDAS = "Estancia media"
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
            AND NACIONALIDAD LIKE "Mundo%"
            """

            df_final_1 = sqldf(query_1)
            df_final_2 = sqldf(query_2)
            df_final = pd.concat([df_final_1, df_final_2], axis=0, ignore_index=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/estancia_media_turistas_internac_{territorio.lower().replace(" ", "_")}.csv',
                    sep=';', index=False, encoding='utf8')

        # 40.2.- estancia media turistas nacionales
        if fila.id_indicador == 175:
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
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, ALOJAMIENTO_TURISTICO_TIPO AS grupo, OBSERVACIONES AS vd FROM df_1 
            WHERE MEDIDAS = "Estancia media"
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
            AND NACIONALIDAD = "España"
            """
            query_2 = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, "Apartamentos turísticos" AS grupo, OBSERVACIONES AS vd FROM df_2
            WHERE MEDIDAS = "Estancia media"
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
            AND NACIONALIDAD = "España"
            """

            df_final_1 = sqldf(query_1)
            df_final_2 = sqldf(query_2)
            df_final = pd.concat([df_final_1, df_final_2], axis=0, ignore_index=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['ter', 'grupo', 'per'], ascending=[True, False, True], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/estancia_media_turistas_nac_{territorio.lower().replace(" ", "_")}.csv',
                    sep=';', index=False, encoding='utf8')

        # endregion



        # region comercio (listo)
        # 41.- indice de confianza del consumidor
        if fila.id_indicador == 171:
            # leer el archivo
            df = pd.read_csv('descargados/1_8_171_icc_com_trim.csv', sep=';', encoding='utf8')
            # transformar el archivo
            pass

            # subirlo a saoresearch
            # df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final = df[
                (df['MEDIDAS'] == "Índice de Confianza del Consumidor") &
                (~df['TERRITORIO'].str.contains('-'))
                ]
            df_final = df_final[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'vd'
            }, inplace=True)

            dicc_periodos = {
                'Primer trimestre': 'T1',
                'Segundo trimestre': 'T2',
                'Tercer trimestre': 'T3',
                'Cuarto trimestre': 'T4'
            }

            df_final['per'] = df_final['per'].replace(dicc_periodos, regex=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.dropna(inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/indice_confiaza_consumidor_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 42.- Empleo registrado en el sector comercial
        if fila.id_indicador == 47:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_47_empleo_registrado.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                SELECT DISTINCT TIME_PERIOD AS per, TERRITORIO as ter, OBSERVACIONES as vd FROM df
                WHERE ACTIVIDAD_ECONOMICA = "Comercio al por mayor y al por menor; reparación de vehículos de motor y motocicletas"
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
                AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_comercio_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 43.- matriculacion de vehiculos
        if fila.id_indicador == 118:
            # leer el archivo
            df = pd.read_csv('descargados/1_8_118_matric_vehic.csv', sep=';', encoding='utf8')
            # transformar el archivo
            pass

            # subirlo a saoresearch
            # df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final = df[
                (df['TIPO_VEHICULO'] != "Total") &
                (df['TIPO_VEHICULO'] != "Automóvil") &
                (df['PROCEDENCIA'] != "Total") &
                (df['MEDIDAS'] == "Vehículo") &
                (df['TIME_PERIOD'].astype(int) >= 2010)
                ]
            df_final = df_final[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES', 'TIPO_VEHICULO']]
            df_final.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'TIPO_VEHICULO': 'grupo',
                'OBSERVACIONES': 'vd'
            }, inplace=True)

            dicc_vehiculos = {
                'Vehículo mixto adaptable': 'Resto de automóviles',
                'Vehículo especial': 'Vehículos especiales',
                'Turismo': 'Turismos',
                'Tractocamión': 'Resto de automóviles',
                'Todo terreno': 'Resto de automóviles',
                'Remolque y semirremolque': 'Remolques y semirremolques',
                'Motocicleta': 'Motocicletas',
                'Furgoneta': 'Resto de automóviles',
                'Ciclomotor': 'Ciclomotores',
                'Camión': 'Resto de automóviles',
                'Autocaravana': 'Resto de automóviles',
                'Guagua': 'Resto de automóviles'
            }

            df_final['grupo'] = df_final['grupo'].map(dicc_vehiculos)
            df_final = df_final.groupby([df_final['ter'], df_final['per'], df_final['grupo']]).agg({'vd': 'sum'}).reset_index()

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/matriculacion_vehiculos_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # endregion



        # region Transporte (listo)

        # 44.- Pasajeros llegados por vía aérea
        if fila.id_indicador == 119:
            # leer el archivo
            df = pd.read_csv("descargados/1_8_119_trans_aere_pasaj_istac.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, OBSERVACIONES AS vd FROM df 
            WHERE MEDIDAS = "Pasajeros"
            AND AEROPUERTO_ESCALA = "Total"
            AND MOVIMIENTO_AERONAVE = "Total"
            AND SERVICIO_AEREO = "Comercial"
            AND TIME_PERIOD NOT LIKE "%/%"
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.sort_values(by=['per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/pasajeros_via_aerea_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 45.- Transporte marítimo de pasajeros
        if fila.id_indicador == 122:
            # leer el archivo
            px = pyaxis.parse('descargados/1_8_122_trans_mari_viaj_pe.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT Puertos AS ter, Periodos AS per, `DATA` AS vd FROM df
            WHERE (Indicadores = "Pasajeros en línea regular" OR Indicadores = "Pasajeros de crucero")
            AND Periodos LIKE "%TOTAL%"
            """
            df_final = sqldf(query)

            df_final['per'] = df_final['per'].str[:4]

            dicc_puertos = {
                'CANARIAS': 'Canarias',
                'Puerto de Arrecife': 'Lanzarote',
                'Puerto del Rosario': 'Fuerteventura',
                'Puerto de La Luz y Las Palmas': 'Gran Canaria',
                'Puerto de Salinetas': 'Gran Canaria',
                'Puerto de Arinaga': 'Gran Canaria',
                'Puerto de Santa Cruz de Tenerife': 'Tenerife',
                'Puerto de Los Cristianos': 'Tenerife',
                'Puerto de Granadilla': 'Tenerife',
                'Puerto de San Sebastián de La Gomera': 'La Gomera',
                'Puerto de Santa Cruz de La Palma': 'La Palma',
                'Puerto de La Estaca': 'El Hierro'
            }
            df_final['ter'] = df_final['ter'].map(dicc_puertos)
            df_final = df_final[df_final['per'].astype(int) >= 2010]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado['vd'] = pd.to_numeric(df_final_filtrado['vd'], errors='coerce')
                df_final_filtrado = df_final_filtrado.groupby(['ter', 'per']).agg({'vd': 'sum'}).reset_index()
                df_final_filtrado.to_csv(
                    f'output_files/transporte_maritimo_pasajeros_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 46.- Trasnporte marítimo de mercancias
        if fila.id_indicador == 143:
            # leer el archivo
            px = pyaxis.parse('descargados/1_8_143_trans_mar_merc.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT Puertos AS ter, Periodos AS per, `DATA` AS vd FROM df 
            WHERE Indicadores = "TRÁFICO TOTAL DE MERCANCÍAS"
            AND Periodos LIKE "%TOTAL%"
            """
            df_final = sqldf(query)

            df_final['per'] = df_final['per'].str[:4]

            dicc_puertos = {
                'CANARIAS': 'Canarias',
                'Puerto de Arrecife': 'Lanzarote',
                'Puerto del Rosario': 'Fuerteventura',
                'Puerto de La Luz y Las Palmas': 'Gran Canaria',
                'Puerto de Salinetas': 'Gran Canaria',
                'Puerto de Arinaga': 'Gran Canaria',
                'Puerto de Santa Cruz de Tenerife': 'Tenerife',
                'Puerto de Los Cristianos': 'Tenerife',
                'Puerto de Granadilla': 'Tenerife',
                'Puerto de San Sebastián de La Gomera': 'La Gomera',
                'Puerto de Santa Cruz de La Palma': 'La Palma',
                'Puerto de La Estaca': 'El Hierro'
            }
            df_final['ter'] = df_final['ter'].map(dicc_puertos)
            df_final = df_final[df_final['per'].astype(int) >= 2010]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado['vd'] = pd.to_numeric(df_final_filtrado['vd'], errors='coerce')
                df_final_filtrado = df_final_filtrado.groupby(['ter', 'per']).agg({'vd': 'sum'}).reset_index()
                df_final_filtrado.to_csv(
                    f'output_files/transporte_maritimo_mercancias_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')


        # endregion



        # region servicios
        # 47.- VAB y empleo en el sector serrvicios
        if fila.id_indicador == 189:
            df = pd.read_excel('input_files/pib_vab.xlsx', sheet_name='servicios')
            df['per'] = df['per'].replace({'2022*': '2022', '2023*': '2023'})
            df['per'] = df['per'].astype(str)
            df.sort_values(by=['ter', 'grupo', 'per'], inplace=True)
            df = df[df['per'].astype(int) >= 2009]
            df_final = pd.pivot_table(df, values='vd', index=['ter', 'per'], columns=['grupo'],
                                      aggfunc="sum").reset_index()

            # PRODUCTIVIDAD
            df_final['vd'] = df_final['VAB'] * 1000 / df_final['Empleo']
            df_final_prod = df_final[['ter', 'per', 'vd']]
            for territorio in df_final['ter'].unique():
                df_final_prod_filtrado = df_final_prod[df_final['ter'] == territorio]
                df_final_prod_filtrado = df_final_prod_filtrado[df_final_prod_filtrado['per'].astype(int) >= 2010]
                df_final_prod_filtrado.to_csv(
                    f'output_files/productividad_servicios_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

            df_final['vd1'] = df_final['VAB'].pct_change() * 100
            df_final['vd2'] = df_final['Empleo'].pct_change() * 100
            df_final.dropna(inplace=True)

            df_final = df_final[['ter', 'per', 'vd1', 'vd2']]

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado = df_final_filtrado[df_final_filtrado['per'].astype(int) >= 2010]
                df_final_filtrado.to_csv(
                    f'output_files/vab_empleo_servicios_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 48.- Empleo registrado en el sector servicios
        if fila.id_indicador == 47:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_47_empleo_registrado.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                SELECT DISTINCT TIME_PERIOD AS per, TERRITORIO as ter, OBSERVACIONES as vd FROM df
                WHERE ACTIVIDAD_ECONOMICA = "Servicios"
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
                AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_servicios_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')


        # 49.- Empleo registrado en la hostelería
        if fila.id_indicador == 47:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_47_empleo_registrado.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                SELECT DISTINCT TIME_PERIOD AS per, TERRITORIO as ter, OBSERVACIONES as vd FROM df
                WHERE ACTIVIDAD_ECONOMICA = "Hostelería"
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
                AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_hosteleria_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # endregion



        # region mercado laboral (listo)

        # 50.- Afiliados a la seguridad social
        if fila.id_indicador == 181:

            # leer el archivo
            df = pd.read_csv("descargados/1_5_181_afil_ss_ins_istac.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final = df[
                (df['LUGAR_COTIZACION'] != "Desconocido") &
                (df['SEXO'] == "Total") &
                (df['REGIMEN_COTIZACION'] == "Total") &
                (df['TIME_PERIOD'].str[-4:].astype(int) >= 2010) &
                (df['TIME_PERIOD'].str[-4:].astype(int) < 2024)
                ]
            df_final = df_final[['LUGAR_COTIZACION', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final = df_final.groupby([df_final['LUGAR_COTIZACION'], df_final['TIME_PERIOD'].str[-4:]]).agg({'OBSERVACIONES': 'mean'}).reset_index()
            df_final.rename(columns={
                'LUGAR_COTIZACION': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'vd'
            }, inplace=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/afiliados_ss_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 51.- poblacion ocupada
        if fila.id_indicador == 94:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_94_epa_istac_islas.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final = df[
                (df['SITUACION_LABORAL'] == "Personas ocupadas") &
                (df['SEXO'] == "Total") &
                (df['EDAD'] == "Total") &
                (df['TIME_PERIOD'].str[:4].astype(int) >= 2010) &
                (df['TIME_PERIOD'].str[:4].astype(int) < 2024)
                ]
            df_final = df_final[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final = df_final.groupby([df_final['TERRITORIO'], df_final['TIME_PERIOD'].str[:4]]).agg(
                {'OBSERVACIONES': 'mean'}).reset_index()
            df_final.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'vd'
            }, inplace=True)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/ocupados_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

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

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio].copy()
                df_final_filtrado = df_final_filtrado.pivot(index=['per', 'ter'], columns='grupo')['vd'].reset_index()
                df_final_filtrado['Agricultura'] = df_final_filtrado['Agricultura, ganadería, silvicultura y pesca'].pct_change()
                df_final_filtrado['Industria'] = df_final_filtrado['Industria'].pct_change()
                df_final_filtrado['Construcción'] = df_final_filtrado['Construcción'].pct_change()
                df_final_filtrado['Servicios'] = df_final_filtrado['Servicios'].pct_change()
                df_final_filtrado = df_final_filtrado[['per', 'ter', 'Agricultura', 'Industria', 'Construcción', 'Servicios']]
                df_final_filtrado.dropna(inplace=True)
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_sectores_tv_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 53.- Estructura del empleo registrado 2010
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
                AND CAST(TIME_PERIOD AS UNSIGNED) = 2010
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
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_sectores_2010_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 54.- Estructura del empleo registrado 2023
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
                AND CAST(TIME_PERIOD AS UNSIGNED) = 2023
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
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_sectores_2023_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 55.- poblacion activa y tasa de actividad
        if fila.id_indicador == 182:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_182_tasa_act_com.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final_1 = df[
                (df['MEDIDAS'] == "Tasa de actividad") &
                (df['SEXO'] == "Total") &
                (~df['TERRITORIO'].str.contains('-')) &
                (df['TIME_PERIOD'].str[:4].astype(int) >= 2010)
                ]
            df_final_1 = df_final_1[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final_1 = df_final_1.groupby([df_final_1['TERRITORIO'], df_final_1['TIME_PERIOD'].str[:4]]).agg(
                {'OBSERVACIONES': 'mean'}).reset_index()
            df_final_1.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'vd2'
            }, inplace=True)

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
                'OBSERVACIONES': 'vd1'
            }, inplace=True)

            df_final = pd.merge(df_final_2, df_final_1, how='inner', left_on=['per', 'ter'], right_on=['per', 'ter'])

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/activos_tasa_actividad_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False,
                    encoding='utf8')

        # 56.- Tasa de actividad masculina y femenina
        if fila.id_indicador == 182:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_182_tasa_act_com.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final = df[
                (df['MEDIDAS'] == "Tasa de actividad") &
                (df['SEXO'] != "Total") &
                (~df['TERRITORIO'].str.contains('-')) &
                (df['TIME_PERIOD'].str[:4].astype(int) >= 2010)
            ]
            df_final = df_final.groupby([df_final['TERRITORIO'], df_final['TIME_PERIOD'].str[:4], df_final['SEXO']]).agg({'OBSERVACIONES': 'mean'}).reset_index()
            df_final.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'SEXO': 'grupo',
                'OBSERVACIONES': 'vd'
            }, inplace=True)

            sexo_etq = {
                "Hombres": "Masculina",
                "Mujeres": "Femenina",
            }

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio].copy()
                df_final_filtrado['grupo'] = df_final_filtrado['grupo'].map(sexo_etq)
                df_final_filtrado.sort_values(by=['grupo', 'per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/tasa_actividad_sexos_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # 57.- poblacion parada y tasa de paro
        if fila.id_indicador == 182:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_182_tasa_act_com.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final_1 = df[
                (df['MEDIDAS'] == "Tasa de paro") &
                (df['SEXO'] == "Total") &
                (~df['TERRITORIO'].str.contains('-')) &
                (df['TIME_PERIOD'].str[:4].astype(int) >= 2010)
            ]
            df_final_1 = df_final_1[['TERRITORIO', 'TIME_PERIOD', 'OBSERVACIONES']]
            df_final_1 = df_final_1.groupby([df_final_1['TERRITORIO'], df_final_1['TIME_PERIOD'].str[:4]]).agg({'OBSERVACIONES': 'mean'}).reset_index()
            df_final_1.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'OBSERVACIONES': 'vd2'
            }, inplace=True)

            df_2 = pd.read_csv("descargados/1_5_94_epa_istac_islas.csv", sep=';', encoding='utf8')

            df_final_2 = df_2[
                (df_2['SITUACION_LABORAL'] == "Personas desempleadas") &
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
                'OBSERVACIONES': 'vd1'
            }, inplace=True)

            df_final = pd.merge(df_final_2, df_final_1, how='inner', left_on=['per', 'ter'], right_on=['per', 'ter'])

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio].copy()
                df_final_filtrado.to_csv(
                    f'output_files/parados_tasa_paro_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 58.- Tasa de paro masculina y femenina
        if fila.id_indicador == 182:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_182_tasa_act_com.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            df_final = df[
                (df['MEDIDAS'] == "Tasa de paro") &
                (df['SEXO'] != "Total") &
                (~df['TERRITORIO'].str.contains('-')) &
                (df['TIME_PERIOD'].str[:4].astype(int) >= 2010)
            ]
            df_final = df_final.groupby([df_final['TERRITORIO'], df_final['TIME_PERIOD'].str[:4], df_final['SEXO']]).agg({'OBSERVACIONES': 'mean'}).reset_index()
            df_final.rename(columns={
                'TERRITORIO': 'ter',
                'TIME_PERIOD': 'per',
                'SEXO': 'grupo',
                'OBSERVACIONES': 'vd'
            }, inplace=True)

            sexo_etq = {
                "Hombres": "Masculina",
                "Mujeres": "Femenina",
            }

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio].copy()
                df_final_filtrado['grupo'] = df_final_filtrado['grupo'].map(sexo_etq)
                df_final_filtrado.sort_values(by=['grupo', 'per'], inplace=True)
                df_final_filtrado.to_csv(
                    f'output_files/tasa_paro_sexos_{territorio.lower().replace(" ", "_")}.csv', sep=';',
                    index=False, encoding='utf8')

        # endregion



        # region sector público (listo)

        # 59.- empleo registrado en adm. pub. educ. y sanidad
        if fila.id_indicador == 47:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_47_empleo_registrado.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
                SELECT DISTINCT TIME_PERIOD AS per, TERRITORIO as ter, SUM(OBSERVACIONES) as vd FROM df
                WHERE (ACTIVIDAD_ECONOMICA = "Administración pública y defensa; seguridad social obligatoria" OR
                ACTIVIDAD_ECONOMICA = "Educación" OR
                ACTIVIDAD_ECONOMICA = "Actividades sanitarias y de servicios sociales")
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
                AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010
                GROUP BY TIME_PERIOD, TERRITORIO
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_admin_pub_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 60.- empleo registrado en ayuntamientos y cabildos
        if fila.id_indicador == 179:
            # leer el archivo
            df = pd.read_csv("descargados/1_6_179_emp_reg_ayu_cab.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, MEDIDAS AS grupo, OBSERVACIONES AS vd FROM df  
            WHERE TIME_PERIOD NOT LIKE "% %"
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
            ORDER BY MEDIDAS, TERRITORIO, TIME_PERIOD;
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(f'output_files/empleo_registrado_aytos_cabildos_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')


        # endregion



        # region empresa y entorno regulatorio (listo)

        # 61.- Empresas inscritas en la seguridad social (por sectores)
        if fila.id_indicador == 158:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_158_empr_ss_islas_istac.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, ACTIVIDAD_ECONOMICA AS grupo, OBSERVACIONES AS vd FROM df 
            WHERE TIME_PERIOD NOT LIKE "%/%"
            AND ACTIVIDAD_ECONOMICA <> "Total"
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
            AND CAST(TIME_PERIOD AS UNSIGNED) = 2023;
            """
            df_final = sqldf(query)

            dicc_sectores = {
                'Agricultura, ganadería, silvicultura y pesca': 'Agricultura',
                'Industria': 'Industria',
                'Construcción': 'Construcción',
                'Servicios': 'Servicios'
            }
            df_final['grupo'] = df_final['grupo'].map(dicc_sectores)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/empresas_inscritas_ss_sectores_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 62.- empresas inscritas en la seguridad social
        if fila.id_indicador == 158:
            # leer el archivo
            df = pd.read_csv("descargados/1_5_158_empr_ss_islas_istac.csv", sep=';', encoding='utf8')

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT TERRITORIO AS ter, TIME_PERIOD AS per, OBSERVACIONES AS vd FROM df
            WHERE TIME_PERIOD NOT LIKE "%/%"
            AND ACTIVIDAD_ECONOMICA = "Total"
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
            AND CAST(TIME_PERIOD AS UNSIGNED) >= 2010;
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/empresas_inscritas_ss_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # 63.- Indice de Confianza Empresarial Armonizado
        if fila.id_indicador == 160:
            # leer el archivo
            px = pyaxis.parse('descargados/1_2_160_ind_conf_empr_arm_istac.px', encoding='ISO-8859-1')
            df = pd.DataFrame(px['DATA'])

            # transformar el archivo
            pass

            # subirlo a saoresearch
            df.to_sql(name=fila.archivo, con=sao_research_connection, index=False, if_exists='replace')

            # adaptarlo a la gráfica
            query = """
            SELECT Islas AS ter, Periodos AS per, `DATA` AS vd FROM df WHERE Indicadores = "ICEA"
            """
            df_final = sqldf(query)

            for territorio in df_final['ter'].unique():
                df_final_filtrado = df_final[df_final['ter'] == territorio]
                df_final_filtrado.to_csv(
                    f'output_files/indice_confianza_empresarial_{territorio.lower().replace(" ", "_")}.csv', sep=';', index=False, encoding='utf8')

        # endregion

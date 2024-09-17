from funciones_graficas import *
import pandas as pd
import json
import sqlalchemy as sqlal

pd.options.display.max_columns = 50

# funciones globales
def mayusculas_por_palabra(input_string):
    """
    Toma un string y devuelve otro string con la primera letra de cada palabra en mayúscula.

    Parámetros:
    - input_string (str): El string de entrada.

    Retorna:
    - str: Un string con la primera letra de cada palabra en mayúscula.
    """
    return ' '.join(word.capitalize() for word in input_string.split())

# conexión a SAO Research
sao_research_connection = sqlal.create_engine("mysql+pymysql://saoresearch:4Tg66a$r@87.106.125.96:3306/sao_research")

# leer archivo input_graficas
df_graficas = pd.read_excel('input_files/graficas.xlsx', sheet_name='islas')

# leer archivo colores
colores = json.load(open('config/colores.json'))

indicadores_concretos = [5,6]
indicadores_desde = 0

if len(indicadores_concretos) == 0:
    indicadores_concretos = df_graficas['id'].tolist()

if indicadores_desde > 0:
    indicadores_concretos = [indicador for indicador in indicadores_concretos if indicador >= indicadores_desde]
    print(f'Empezando a procesar {len(indicadores_concretos)} indicadores')

codigo_archivos = {'tenerife': 'TF', 'la_palma': 'LP', 'la_gomera': 'LG', 'el_hierro': 'EH',
                   'gran_canaria': 'GC', 'fuerteventura': 'FV', 'lanzarote': 'LZ'}

for indice, fila in df_graficas.iterrows():
    if fila.id in indicadores_concretos:

        # region gráficas poblacion

        # 1.- Población residente (islas TF / LP / LG / EH)
        pass

        # 1.- Población residente (islas GC / LZ / FTV + provincia Las Palmas)
        pass

        # 1.- Población residente

        if fila.id == 1:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/poblacion_total_{clave}.csv', sep=';', encoding='utf8').iloc[::-1]

                print(df_tf)

                grafico_barras(eje_x=df_tf['per'].astype(str),
                               eje_y=df_tf['vd'] / 1000,
                               titulo=fila.titulo,
                               subtitulo=fila.subtitulo,
                               territorio=df_tf['ter'].tolist()[0],
                               color_primario=colores[fila.seccion][0],
                               escala_x=2,
                               escala_y=1,
                               nombre_archivo=f'{valor}_{fila.codigo}',
                               mostrar_valores=False
                               )

        # 2.- Población residente por nacionalidad

        if fila.id == 2:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(F'output_files/poblacion_nacionalidad_{clave}.csv', sep=';', encoding='utf8')

                grafico_barras_apiladas(eje_x=df_tf['per'],
                                        eje_y=df_tf['vd'] / 1000,
                                        grupo=df_tf['grupo'],
                                        titulo=fila.titulo,
                                        subtitulo=fila.subtitulo,
                                        territorio=df_tf['ter'].tolist()[0],
                                        colores=[colores[fila.seccion][0], colores[fila.seccion][1]],
                                        escala_x=1.5,
                                        escala_y=1,
                                        nombre_archivo=f'{valor}_{fila.codigo}',
                                        escala_eje_y=1.3,
                                        posicion_leyenda={'yanchor': 'top', 'y': 0.95, 'xanchor': 'left', 'x': 0.5}
                                        )

        # 3.- Nacimientos y defunciones

        if fila.id == 3:
            for clave, valor in codigo_archivos.items():
                df_tf_nac = pd.read_csv(f'output_files/nacimientos_{clave}.csv', sep=';', encoding='utf8').drop(['ter'], axis=1)
                df_tf_def = pd.read_csv(f'output_files/defunciones_{clave}.csv', sep=';', encoding='utf8')

                df_tf = df_tf_nac.join(df_tf_def, lsuffix='_nac', rsuffix='_def').drop(['per_nac'], axis=1)
                df_tf['vd_sv'] = df_tf['vd_nac'] - df_tf['vd_def']
                df_tf = df_tf.melt(id_vars=['ter', 'per_def'], var_name='grupo', value_name='vd')
                df_tf = df_tf.rename(columns={"per_def": "per"})

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=df_tf['vd'],
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].tolist()[0],
                                         colores=[colores[fila.seccion][0], colores[fila.seccion][1], colores[fila.seccion][2]],
                                         escala_x=2,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.3,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.0, 'xanchor': 'left', 'x': 0.4},
                                         etiquetas_medidas={
                                             'vd_nac': 'Nacimientos',
                                             'vd_def': 'Defunciones',
                                             'vd_sv': 'Crecimiento vegetativo'
                                         },
                                         ticks="",
                                         )

        # 4.- Saldo migratorio

        if fila.id == 4:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/saldo_migratorio_{clave}.csv', sep=';', encoding='utf8')

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=df_tf['vd'],
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].tolist()[0],
                                         colores=[colores[fila.seccion][1], colores[fila.seccion][0]],
                                         escala_x=2,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.3,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.4},
                                         etiquetas_medidas={
                                             'Saldo exterior con otras CC.AA.': 'Saldo migratorio CCAA',
                                             'Saldo exterior con el extranjero': 'Saldo migratorio extranjero'},
                                         ticks=""
                                         )

        # 5.- Pirámide poblacional 2010 (ISTAC)
        # 6.- Pirámide poblacional 2022 (ISTAC)

        # 5.- Pirámide poblacional 2010 (INE)

        if fila.id == 5:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/piramide_poblacion_2010_ine_{clave}.csv', sep=';', encoding='utf8')
                df_tf = df_tf[::-1]
                max_eje_y = None if clave != 'el_hierro' else 1
                grafico_barras_colores_horizontal(eje_x=df_tf['per'].astype(str).tolist(),
                                                  eje_y=df_tf['vd'] / 1000,
                                                  colores=df_tf['grupo'].tolist(),
                                                  titulo=fila.titulo,
                                                  subtitulo=fila.subtitulo,
                                                  territorio=df_tf['ter'].tolist()[0],
                                                  colores_dict={'Población en edad de trabajar': colores[fila.seccion][0],
                                                                'Población dependiente': colores[fila.seccion][2]},
                                                  escala_x=1.2,
                                                  escala_y=1,
                                                  nombre_archivo=f'{valor}_{fila.codigo}',
                                                  escala_eje_y=1.3,
                                                  posicion_leyenda={'yanchor': 'top', 'y': 1.0, 'xanchor': 'left', 'x': 0.45},
                                                  margin_r=50,
                                                  max_eje_y=max_eje_y
                                                  )

        # 6.- Pirámide poblacional 2023 (INE)

        if fila.id == 6:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/piramide_poblacion_2023_ine_{clave}.csv', sep=';', encoding='utf8')
                df_tf = df_tf[::-1]
                max_eje_y = None if clave != 'el_hierro' else 1
                grafico_barras_colores_horizontal(eje_x=df_tf['per'].astype(str).tolist(),
                                                  eje_y=df_tf['vd'] / 1000,
                                                  colores=df_tf['grupo'].tolist(),
                                                  titulo=fila.titulo,
                                                  subtitulo=fila.subtitulo,
                                                  territorio=df_tf['ter'].tolist()[0],
                                                  colores_dict={'Población en edad de trabajar': colores[fila.seccion][0],
                                                                'Población dependiente': colores[fila.seccion][2]},
                                                  escala_x=1.2,
                                                  escala_y=1,
                                                  nombre_archivo=f'{valor}_{fila.codigo}',
                                                  escala_eje_y=1.3,
                                                  posicion_leyenda={'yanchor': 'top', 'y': 0.99, 'xanchor': 'left',
                                                                    'x': 0.5},
                                                  margin_r=50,
                                                  max_eje_y=max_eje_y
                                                  )

        # 7.- Índice de envejecimiento

        if fila.id == 7:

            inicio_eje_y_especificos = {
                'fuerteventura': 0.06,
                'lanzarote': 0.08,
                'gran_canaria': 0.08
            }

            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/indice_envejecimiento_{clave}.csv', sep=';', encoding='utf8')
                df_can = pd.read_csv('output_files/indice_envejecimiento_canarias.csv', sep=';', encoding='utf8')

                df_total = pd.concat([df_tf, df_can], axis=0, ignore_index=True)

                if clave in inicio_eje_y_especificos:
                    inicio_eje_y_actual = inicio_eje_y_especificos[clave]
                else:
                    inicio_eje_y_actual = 0.12

                grafico_lineas_doble_relleno(eje_x=extraer_unicos_ordenados(df_total['per'].astype(str).tolist()),
                                             eje_y=df_total['vd'][df_total['ter'] != "Canarias"],
                                             eje_y_secundario=df_total['vd'][df_total['ter'] == "Canarias"],
                                             color_primario=colores[fila.seccion][0],
                                             color_secundario=colores[fila.seccion][2],
                                             titulo=fila.titulo,
                                             subtitulo=fila.subtitulo,
                                             territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                             escala_x=2,
                                             escala_y=0.9,
                                             nombre_archivo=f'{valor}_{fila.codigo}',
                                             medida_y=f"Índice de envejecimiento {df_tf['ter'][0]}",
                                             medida_y_secundario="Índice de envejecimiento Canarias",
                                             inicio_eje_y=inicio_eje_y_actual,
                                             posicion_leyenda={'yanchor': 'top', 'y': 0.95, 'xanchor': 'left', 'x': 0.5},
                                             margin_r=10,
                                             tickformat='.0%'
                                             )

        # 8.- Tasa de dependencia

        if fila.id == 8:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/tasa_dependencia_total_{clave}.csv', sep=';', encoding='utf8')

                # region antiguo
                # df_tf['ter'] = df_tf['ter'].apply(mayusculas_por_palabra)
                #
                # df_poblacion = pd.read_sql("""
                # SELECT * FROM `1_1_1_pob_sexo_edad` pse
                # WHERE SEXO = "Total" AND
                # (TERRITORIO = "Tenerife" OR
                # TERRITORIO = "El Hierro" OR
                # TERRITORIO = "La Gomera" OR
                # TERRITORIO = "La Palma" OR
                # TERRITORIO = "Lanzarote" OR
                # TERRITORIO = "Fuerteventura" OR
                # TERRITORIO = "Gran Canaria")
                # AND
                # (EDAD = "De 15 a 64 años" OR
                # EDAD = "15 años" OR
                # EDAD = "Menor de 15 años" OR
                # EDAD = "65 años o más")
                # """, con=sao_research_connection)
                #
                # df_poblacion = df_poblacion.pivot_table(index=['TERRITORIO', 'TIME_PERIOD'], columns='EDAD', values='OBSERVACIONES', fill_value=0, aggfunc='sum').reset_index()
                #
                # df_poblacion['men_16'] = df_poblacion['Menor de 15 años'] + df_poblacion['15 años']
                # df_poblacion['may_15_men_64'] = df_poblacion['De 15 a 64 años'] - df_poblacion['15 años']
                # df_poblacion['may_64'] = df_poblacion['65 años o más']
                #
                # df_poblacion = df_poblacion[['TERRITORIO', 'TIME_PERIOD', 'men_16', 'may_15_men_64', 'may_64']]
                #
                # df_poblacion['tasa_dep_16'] = df_poblacion['men_16'] / df_poblacion['may_15_men_64']
                # df_poblacion['tasa_dep_64'] = df_poblacion['may_64'] / df_poblacion['may_15_men_64']
                #
                # df_poblacion = df_poblacion[['TERRITORIO', 'TIME_PERIOD', 'tasa_dep_16', 'tasa_dep_64']]
                # df_poblacion.columns = ['ter', 'per', 'Tasa de dependencia de la población menor de 16 años',
                #                         'Tasa de dependencia de la población mayor de 64 años']
                #
                # df_tf = pd.merge(df_tf, df_poblacion, how='inner', left_on=['per', 'ter'], right_on=['per', 'ter'])
                # df_tf.to_csv(f'tasa_depend_{clave}.csv', sep=';', index=False, encoding='utf8')

                grafico_barras_apiladas_y_lineas(eje_x=df_tf['per'].astype(str),
                                                 eje_y_barras=[df_tf['Tasa de dependencia']],
                                                 eje_y_lineas=[df_tf['Tasa de dependencia de la población menor de 16 años'].tolist(),
                                                               df_tf['Tasa de dependencia de la población mayor de 64 años'].tolist()
                                                               ],
                                                 titulo=fila.titulo,
                                                 subtitulo=fila.subtitulo,
                                                 territorio=df_tf['ter'].tolist()[0],
                                                 colores_barras=[colores[fila.seccion][1]],
                                                 colores_lineas=[colores[fila.seccion][0], colores[fila.seccion][2]],
                                                 nombres_medidas_barras=['Tasa de dependencia'],
                                                 nombres_medidas_lineas=['Tasa de dependencia de la población menor de 16 años',
                                                                         'Tasa de dependencia de la población mayor de 64 años'],
                                                 escala_x=2,
                                                 escala_y=0.9,
                                                 nombre_archivo=f'{valor}_{fila.codigo}',
                                                 lineas_a_eje_y_secundario=False,
                                                 tickformat='.0%',
                                                 mostrar_leyenda=False,
                                                 margin_t=125
                                                 )

        # 9.- Tasa bruta de natalidad

        if fila.id == 9:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/tasa_bruta_natalidad_{clave}.csv', sep=';', encoding='utf8')
                df_can = pd.read_csv('output_files/tasa_bruta_natalidad_canarias.csv', sep=';', encoding='utf8')

                df_total = pd.concat([df_tf, df_can], axis=0, ignore_index=True)

                grafico_lineas_doble_relleno(eje_x=extraer_unicos_ordenados(df_total['per'].astype(str).tolist()),
                                             eje_y=df_total['vd'][df_total['ter'] != "CANARIAS"],
                                             eje_y_secundario=df_total['vd'][df_total['ter'] == "CANARIAS"],
                                             titulo=fila.titulo,
                                             subtitulo=fila.subtitulo,
                                             territorio=df_tf['ter'].tolist()[0],
                                             color_primario=colores[fila.seccion][0],
                                             color_secundario=colores[fila.seccion][2],
                                             escala_x=2,
                                             escala_y=0.9,
                                             nombre_archivo=f'{valor}_{fila.codigo}',
                                             medida_y=f"Tasa Bruta de Natalidad {df_tf['ter'][0]}",
                                             medida_y_secundario="Tasa Bruta de Natalidad Canarias",
                                             inicio_eje_y=4,
                                             escala_eje_y=1.05,
                                             posicion_leyenda={'yanchor': 'top', 'y': 1.0, 'xanchor': 'left', 'x': 0.65},
                                             margin_r=10
                                             )

        # endregion

        # region gráficas ciclo económico

        # 10.- PIB corriente

        if fila.id == 10:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/pib_corriente_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de euros', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.6,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 11.- PIB per cápita corriente

        if fila.id == 11:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/pib_per_capita_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Euros por habitante', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.6,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 12.- ÍndicePIB per cápita corriente --isla-- / Canarias

        if fila.id == 12:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/indice_pib_per_capita_canarias_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras(eje_x=df_tf['per'].astype(str),
                               eje_y=df_tf['vd'],
                               inicio_eje_y=50,
                               titulo=fila.titulo,
                               subtitulo=fila.subtitulo,
                               territorio=df_tf['ter'].tolist()[0],
                               color_primario=colores[fila.seccion][0],
                               escala_x=2.2,
                               escala_y=1,
                               mostrar_valores=False,
                               nombre_archivo=f'{valor}_{fila.codigo}'
                               )

        # 13.- ÍndicePIB per cápita corriente --isla-- / España

        if fila.id == 13:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/indice_pib_per_capita_españa_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras(eje_x=df_tf['per'].astype(str),
                               eje_y=df_tf['vd'],
                               inicio_eje_y=50,
                               titulo=fila.titulo,
                               subtitulo=fila.subtitulo,
                               territorio=df_tf['ter'].tolist()[0],
                               color_primario=colores[fila.seccion][0],
                               escala_x=2.2,
                               escala_y=1,
                               mostrar_valores=False,
                               nombre_archivo=f'{valor}_{fila.codigo}'
                               )

        # NUEVA 2023 -- PRODUCTIVIDAD
        if fila.id == 135:
            for clave, valor in codigo_archivos.items():

                df_tf = pd.read_csv(f'output_files/productividad_total_{clave}.csv', sep=';',
                                    encoding='utf8')
                for columna in df_tf.columns.tolist():
                    if columna not in ['per', 'Canarias', 'España', 'ter']:
                        valor_territorio = columna
                    else:
                        pass
                grafico_varias_lineas(eje_x=df_tf['per'].astype(str),
                                      eje_y=[df_tf['España'],
                                             df_tf['Canarias'],
                                             df_tf[valor_territorio]],
                                      escala_eje_y=1.1,
                                      inicio_eje_y=15000,
                                      titulo=fila.titulo,
                                      subtitulo=fila.subtitulo,
                                      territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                      colores=[colores[fila.seccion][0],
                                               colores[fila.seccion][1],
                                               colores[fila.seccion][2]],
                                      nombres_medidas=['España', 'Canarias', valor_territorio],
                                      posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.3},
                                      escala_x=1.25,
                                      escala_y=1,
                                      nombre_archivo=f'{valor}_{fila.codigo}',
                                      angulo_etq_x=0,
                                      tickformat=','
                                      )

        # 14.- VAB Agricultura

        if fila.id == 14:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/vab_agricultura_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de euros', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.15},
                                     escala_x=1.2,
                                     escala_y=1,
                                     angulo_etq_x=270,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 15.- VAB Construcción

        if fila.id == 15:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/vab_construccion_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de euros', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.15},
                                     escala_x=1.2,
                                     escala_y=1,
                                     angulo_etq_x=270,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 16.- VAB Industria

        if fila.id == 16:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/vab_industria_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de euros', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.15},
                                     escala_x=1.2,
                                     escala_y=1,
                                     angulo_etq_x=270,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 17.- VAB Servicios

        if fila.id == 17:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/vab_servicios_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de euros', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.15},
                                     escala_x=1.2,
                                     escala_y=1,
                                     angulo_etq_x=270,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 18.- Estructura del VAB 2010

        if fila.id == 18:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/estructura_vab_2010_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_sectores(eje_x=df_tf['grupo'].astype(str).apply(mayusculas_por_palabra),
                                 eje_y=df_tf['vd'],
                                 titulo=fila.titulo,
                                 subtitulo=fila.subtitulo,
                                 territorio=df_tf['ter'].tolist()[0],
                                 color_primario=[colores[fila.seccion][4],
                                                 colores[fila.seccion][2],
                                                 colores[fila.seccion][3],
                                                 colores[fila.seccion][0]],
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=f'{valor}_{fila.codigo}',
                                 )

        # 19.- Estructura del VAB 2023

        if fila.id == 19:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/estructura_vab_2023_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_sectores(eje_x=df_tf['grupo'].astype(str).apply(mayusculas_por_palabra),
                                 eje_y=df_tf['vd'],
                                 titulo=fila.titulo,
                                 subtitulo=fila.subtitulo,
                                 territorio=df_tf['ter'].tolist()[0],
                                 color_primario=[colores[fila.seccion][4],
                                                 colores[fila.seccion][2],
                                                 colores[fila.seccion][3],
                                                 colores[fila.seccion][0]],
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=f'{valor}_{fila.codigo}',
                                 )

        # endregion

        # region gráficas agricultura

        # 20.- VAB y empleo en Agricultura

        if fila.id == 20:
            for clave, valor in codigo_archivos.items():

                df_tf = pd.read_csv(f'output_files/vab_empleo_agricultura_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_varias_lineas(eje_x=df_tf['per'].astype(str),
                                      eje_y=[df_tf['vd1'],
                                             df_tf['vd2']],
                                      escala_eje_y=1.3,
                                      centrar_eje_y_en=0,
                                      titulo=fila.titulo,
                                      subtitulo=fila.subtitulo,
                                      territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                      colores=[colores[fila.seccion][0],
                                               colores[fila.seccion][2]],
                                      nombres_medidas=['VAB Agricultura', 'Empleo Agricultura'],
                                      posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                      escala_x=1.6,
                                      escala_y=1,
                                      margin_r=60,
                                      nombre_archivo=f'{valor}_{fila.codigo}',
                                      angulo_etq_x=0
                                      )

        # 21.- Empleo Registrado Agricultura

        if fila.id == 21:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_agricultura_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y= df_tf['vd'] / 1000 if clave == "tenerife" or clave == "gran_canaria" else df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=1,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de personas' if clave == "tenerife" or clave == "gran_canaria" else 'Personas', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.6,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 22.- Superficie cultivada

        if fila.id == 22:

            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/superficie_cultivada_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                if clave == 'la_palma':
                    escala_eje_y2_actual = 1.9
                else:
                    escala_eje_y2_actual = 1.4

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     escala_eje_y_secundario=escala_eje_y2_actual,
                                     centrar_eje_y_secundario_en=0,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Hectáreas', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.3},
                                     escala_x=1.6,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 23.- Producción agrícola

        if fila.id == 23:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/produccion_agricola_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=2,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Toneladas', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.6,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 24.- Exportación de plátanos

        if fila.id == 24:
            for clave, valor in codigo_archivos.items():
                try:
                    df_tf = pd.read_csv(f'output_files/exportacion_platanos_{clave}.csv', sep=';', encoding='utf8')

                    df_tf['tma'] = df_tf['vd'].pct_change() * 100

                    grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                         eje_y=df_tf['vd'],
                                         escala_eje_y=1.2,
                                         eje_y_secundario=df_tf['tma'],
                                         centrar_eje_y_secundario_en=1,
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         color_primario=colores[fila.seccion][1],
                                         color_secundario=colores[fila.seccion][0],
                                         nombres_medidas=['Toneladas', 'Tasa de variación anual'],
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                         escala_x=1.6,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         margin_l=0,
                                         margin_r=0,
                                         )
                except Exception as e:
                    print(f'La gráfica {valor}_{fila.codigo} no se pudo realizar: ', e)

        # endregion

        # region gráficas industria

        # 25.- VAB y empleo en el sector de la industria

        if fila.id == 25:
            for clave, valor in codigo_archivos.items():

                df_tf = pd.read_csv(f'output_files/vab_empleo_industria_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_varias_lineas(eje_x=df_tf['per'].astype(str),
                                      eje_y=[df_tf['vd1'],
                                             df_tf['vd2']],
                                      escala_eje_y=1.3,
                                      centrar_eje_y_en=0,
                                      titulo=fila.titulo,
                                      subtitulo=fila.subtitulo,
                                      territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                      colores=[colores[fila.seccion][0],
                                               colores[fila.seccion][2]],
                                      nombres_medidas=['VAB Industria', 'Empleo Industria'],
                                      posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                      escala_x=1.6,
                                      escala_y=1,
                                      margin_r=60,
                                      nombre_archivo=f'{valor}_{fila.codigo}',
                                      angulo_etq_x=0
                                      )

        # 26.- Empleo Registrado Industria

        if fila.id == 26:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_industria_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y= df_tf['vd'] / 1000 if clave == "tenerife" or clave == "gran_canaria" else df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.3,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de personas' if clave == "tenerife" or clave == "gran_canaria" else 'Personas', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.08, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 27.- Energía eléctrica disponible

        if fila.id == 27:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/energia_electrica_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['MWh', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.08, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # endregion

        # region gráficas construccion

        # 28.- VAB y empleo en el sector de la Construcción

        if fila.id == 28:
            for clave, valor in codigo_archivos.items():

                df_tf = pd.read_csv(f'output_files/vab_empleo_construccion_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_varias_lineas(eje_x=df_tf['per'].astype(str),
                                      eje_y=[df_tf['vd1'],
                                             df_tf['vd2']],
                                      escala_eje_y=1.3,
                                      centrar_eje_y_en=0,
                                      titulo=fila.titulo,
                                      subtitulo=fila.subtitulo,
                                      territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                      colores=[colores[fila.seccion][0],
                                               colores[fila.seccion][2]],
                                      nombres_medidas=['VAB Construcción', 'Empleo Construcción'],
                                      posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                      escala_x=1.6,
                                      escala_y=1,
                                      margin_r=60,
                                      nombre_archivo=f'{valor}_{fila.codigo}',
                                      angulo_etq_x=0
                                      )

        # 29.- Empleo Registrado Construcción

        if fila.id == 29:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_construccion_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y= df_tf['vd'] / 1000 if clave == "tenerife" or clave == "gran_canaria" else df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de personas' if clave == "tenerife" or clave == "gran_canaria" else 'Personas', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0
                                     )

        # 30.- Consumo de cemento

        if fila.id == 30:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/consumo_cemento_{clave}.csv', sep=';', encoding='utf8')

                grafico_barras(eje_x=df_tf['per'].astype(str),
                               eje_y=df_tf['vd'],
                               titulo=fila.titulo,
                               subtitulo=fila.subtitulo,
                               territorio=df_tf['ter'].tolist()[0],
                               color_primario=colores[fila.seccion][0],
                               escala_x=2,
                               escala_y=1,
                               mostrar_valores=False,
                               nombre_archivo=f'{valor}_{fila.codigo}'
                               )

        # endregion

        # region gráficas turismo

        # 32.- Turistas nacionales e internacionales

        if fila.id == 32:

            for clave, valor in codigo_archivos.items():
                try:
                    df_tf = pd.read_csv(f'output_files/turistas_nacionales_internacionales_{clave}.csv',
                                    sep=';', encoding='utf8')

                    df_tf = df_tf.sort_values(by=['grupo', 'per'])
                    df_tf['tma'] = df_tf.groupby('grupo')['vd'].pct_change() * 100
                    # df_tf['tma'] = df_tf['vd'].pct_change() * 100

                    # df_tf['tma'].replace([np.inf, -np.inf], np.nan, inplace=True)
                    lista_nac = df_tf[df_tf['grupo'] == 'Nacionales']['vd'] / 1000
                    lista_internac = df_tf[df_tf['grupo'] == 'Internacionales']['vd'] / 1000

                    lista_tma_nac = df_tf[df_tf['grupo'] == 'Nacionales']['tma']
                    lista_tma_internac = df_tf[df_tf['grupo'] == 'Internacionales']['tma']

                    grafico_barras_apiladas_y_lineas(eje_x=df_tf['per'].astype(str),
                                                     grupo=df_tf['grupo'],
                                                     eje_y_barras=[lista_internac.to_list(), lista_nac.to_list()],
                                                     eje_y_lineas=[lista_tma_internac.to_list(), lista_tma_nac.to_list()],
                                                     inicio_eje_y=0,
                                                     escala_eje_y=1.4,
                                                     centrar_eje_y_secundario_en=50,
                                                     titulo=fila.titulo,
                                                     subtitulo=fila.subtitulo,
                                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                                     colores_barras=[colores[fila.seccion][1], colores[fila.seccion][3]],
                                                     colores_lineas=[colores[fila.seccion][2], colores[fila.seccion][0]],
                                                     nombres_medidas_barras=None,
                                                     nombres_medidas_lineas=['Nacionales tasa', 'Internacionales tasa'],
                                                     posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left',
                                                                       'x': 0.01},
                                                     escala_x=1.4,
                                                     escala_y=1,
                                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                                     tickformat=',')
                except Exception as e:
                    print(f'error para {clave}: ', e)

        # 33.- Cruceristas

        if fila.id == 33:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/cruceristas_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                df_tf['tma'].replace([np.inf, -np.inf], np.nan, inplace=True)

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'] / 1000,
                                     escala_eje_y=1.3,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     )

        # 34.- Turistas según país de procedencia

        if fila.id == 34:
            for clave, valor in codigo_archivos.items():
                try:
                    df_tf = pd.read_csv(f'output_files/turistas_segun_pais_{clave}.csv', sep=';',
                                        encoding='utf8')

                    grafico_barras_agrupadas(eje_x=df_tf['grupo'].astype(str).tolist(),
                                             eje_y=df_tf['vd'] / 1000,
                                             grupo=df_tf['per'].tolist(),
                                             titulo=fila.titulo,
                                             subtitulo=fila.subtitulo,
                                             territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                             colores=[colores[fila.seccion][0],
                                                      colores[fila.seccion][2]],
                                             escala_x=2.5,
                                             escala_y=1,
                                             nombre_archivo=f'{valor}_{fila.codigo}',
                                             escala_eje_y=1.1,
                                             posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.4},
                                             etiquetas_medidas={
                                                 2010: 2010,
                                                 2023: 2023
                                             })
                except Exception as e:
                    print(f'error para {clave}: ', e)

        # 35.- Gasto de los turistas internacionales

        if fila.id == 35:
            for clave, valor in codigo_archivos.items():
                try:

                    df_tf = pd.read_csv(f'output_files/gasto_turistas_internacionales_{clave}.csv',
                                        sep=';', encoding='utf8')

                    df_tf['tma'] = df_tf['vd'].pct_change() * 100

                    df_tf['tma'].replace([np.inf, -np.inf], np.nan, inplace=True)

                    grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                         eje_y=df_tf['vd'] / 1000000,
                                         escala_eje_y=1.3,
                                         eje_y_secundario=df_tf['tma'],
                                         centrar_eje_y_secundario_en=40,
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         color_primario=colores[fila.seccion][1],
                                         color_secundario=colores[fila.seccion][0],
                                         nombres_medidas=['Millones de euros', 'Tasa de variación anual'],
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left',
                                                           'x': 0.25},
                                         escala_x=1.7,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         )
                except Exception as e:
                    print(f'error para {clave}: ', e)

        # 36.- Gasto medio por turista

        if fila.id == 36:
            for clave, valor in codigo_archivos.items():
                try:

                    df_tf = pd.read_csv(f'output_files/gasto_medio_turista_{clave}.csv', sep=';',
                                        encoding='utf8')

                    df_tf['tma'] = df_tf['vd'].pct_change() * 100

                    df_tf['tma'].replace([np.inf, -np.inf], np.nan, inplace=True)

                    grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                         eje_y=df_tf['vd'],
                                         escala_eje_y=1.3,
                                         eje_y_secundario=df_tf['tma'],
                                         centrar_eje_y_secundario_en=0,
                                         escala_eje_y_secundario=1.5,
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         color_primario=colores[fila.seccion][1],
                                         color_secundario=colores[fila.seccion][0],
                                         nombres_medidas=['Millones de euros', 'Tasa de variación anual'],
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left',
                                                           'x': 0.25},
                                         escala_x=1.7,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         )
                except Exception as e:
                    print(f'error para {clave}: ', e)

        # 37.- Número de plazas

        if fila.id == 37:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/numero_plazas_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=df_tf['vd'] / 1000,
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         colores=[colores[fila.seccion][0],
                                                  colores[fila.seccion][2]],
                                         escala_x=1.75,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.1,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.3},
                                         etiquetas_medidas={
                                             'Hoteles': 'Hoteles',
                                             'Apartamentos turísticos': 'Apartamentos turísticos'
                                         })

        # 38.- Tasa de ocupación por plazas

        if fila.id == 38:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/tasa_ocupacion_plazas_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=df_tf['vd'],
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         colores=[colores[fila.seccion][0],
                                                  colores[fila.seccion][2]],
                                         escala_x=1.75,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.1,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.3},
                                         etiquetas_medidas={
                                             'Hoteles': 'Hoteles',
                                             'Apartamentos turísticos': 'Apartamentos turísticos'
                                         })

        # 391.- Pernoctaciones de los turistas internacionales

        if fila.id == 391:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/pernoctaciones_turistas_internac_{clave}.csv', sep=';',
                                    encoding='utf8')

                if clave == 'el_hierro' or clave == 'la_gomera' or clave == 'la_palma':
                    datos = df_tf['vd'] / 1000
                else:
                    datos = df_tf['vd'] / 1000000
                print(df_tf)

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=datos,
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         colores=[colores[fila.seccion][0],
                                                  colores[fila.seccion][2]],
                                         escala_x=1.6,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.1,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.5},
                                         etiquetas_medidas={
                                             'Hoteles': 'Hoteles',
                                             'Apartamentos turísticos': 'Apartamentos turísticos'
                                         })

        # 392.- Pernoctaciones de los turistas nacionales

        if fila.id == 392:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/pernoctaciones_turistas_nac_{clave}.csv', sep=';',
                                    encoding='utf8')

                if clave == 'el_hierro' or clave == 'la_gomera' or clave == 'la_palma':
                    datos = df_tf['vd'] / 1000
                else:
                    datos = df_tf['vd'] / 1000000
                print(df_tf)

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=datos,
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         colores=[colores[fila.seccion][0],
                                                  colores[fila.seccion][2]],
                                         escala_x=1.6,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.1,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.5},
                                         etiquetas_medidas={
                                             'Hoteles': 'Hoteles',
                                             'Apartamentos turísticos': 'Apartamentos turísticos'
                                         })

        # 401.- Estancia media de los turistas internacionales

        if fila.id == 401:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/estancia_media_turistas_internac_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=df_tf['vd'],
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         colores=[colores[fila.seccion][0],
                                                  colores[fila.seccion][2]],
                                         escala_x=1.6,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.1,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.5},
                                         etiquetas_medidas={
                                             'Hotel': 'Hoteles',
                                             'Apartamentos turísticos': 'Apartamentos turísticos'
                                         })

        # 402.- Estancia media de los turistas nacionales

        if fila.id == 402:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/estancia_media_turistas_nac_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=df_tf['vd'],
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         colores=[colores[fila.seccion][0],
                                                  colores[fila.seccion][2]],
                                         escala_x=1.6,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.1,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.5},
                                         etiquetas_medidas={
                                             'Hotel': 'Hoteles',
                                             'Apartamentos turísticos': 'Apartamentos turísticos'
                                         })

        # endregion

        # region gráficas comercio

        # 41.- Índice de Confianza del Consumidor

        if fila.id == 41:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/indice_confiaza_consumidor_{clave}.csv', sep=';', encoding='utf8')

                grafico_barras(eje_x=df_tf['per'].astype(str),
                               eje_y=df_tf['vd'],
                               titulo=fila.titulo,
                               subtitulo=fila.subtitulo,
                               territorio=df_tf['ter'].tolist()[0],
                               color_primario=colores[fila.seccion][0],
                               escala_x=2,
                               escala_y=1,
                               mostrar_valores=False,
                               nombre_archivo=f'{valor}_{fila.codigo}'
                               )

        # 42.- Empleo registrado del sector comercial

        if fila.id == 42:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_comercio_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras(eje_x=df_tf['per'].astype(str),
                               eje_y=df_tf['vd'],
                               titulo=fila.titulo,
                               subtitulo=fila.subtitulo,
                               territorio=df_tf['ter'].tolist()[0],
                               color_primario=colores[fila.seccion][0],
                               escala_x=2,
                               escala_y=1,
                               mostrar_valores=False,
                               nombre_archivo=f'{valor}_{fila.codigo}'
                               )

        # 43.- Matriculación de vehículos según tipología

        if fila.id == 43:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/matriculacion_vehiculos_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_total = df_tf.groupby('per')['vd'].sum().reset_index()

                df_total['tma'] = df_total['vd'].pct_change() * 100

                lista_ciclo = df_tf[df_tf['grupo'] == 'Ciclomotores']['vd']
                lista_turi = df_tf[df_tf['grupo'] == 'Turismos']['vd']
                lista_moto = df_tf[df_tf['grupo'] == 'Motocicletas']['vd']
                lista_ve_es = df_tf[df_tf['grupo'] == 'Vehículos especiales']['vd']
                lista_rest = df_tf[df_tf['grupo'] == 'Resto de automóviles']['vd']
                lista_remo = df_tf[df_tf['grupo'] == 'Remolques y semirremolques']['vd']

                grafico_barras_apiladas_y_lineas(eje_x=df_total['per'].astype(str),
                                                 grupo=df_tf['grupo'],
                                                 eje_y_barras=[lista_turi, lista_moto, lista_rest, lista_ciclo,
                                                               lista_ve_es, lista_remo],
                                                 eje_y_lineas=[df_total['tma']],
                                                 inicio_eje_y=0,
                                                 escala_eje_y=1.4,
                                                 centrar_eje_y_secundario_en=0,
                                                 titulo=fila.titulo,
                                                 subtitulo=fila.subtitulo,
                                                 territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                                 colores_barras=[colores[fila.seccion][2], colores[fila.seccion][0],
                                                                 colores[fila.seccion][5], colores[fila.seccion][3],
                                                                 colores[fila.seccion][1], colores[fila.seccion][4]],
                                                 colores_lineas=[colores[fila.seccion][0]],
                                                 nombres_medidas_barras=['Turismos', 'Motocicletas',
                                                                         'Resto de automóviles', 'Ciclomotores',
                                                                         'Vehículos especiales',
                                                                         'Remolques y semirremolques'],
                                                 nombres_medidas_lineas=['Tasa de variación anual'],
                                                 posicion_leyenda={'yanchor': 'top', 'y': 1.13, 'xanchor': 'left',
                                                                   'x': 0.05},
                                                 escala_x=2,
                                                 escala_y=1,
                                                 nombre_archivo=f'{valor}_{fila.codigo}',
                                                 tickformat=',')

        # endregion

        # region gráficas transporte

        # 44.- Pasajeros llegados por vía aérea

        if fila.id == 44:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/pasajeros_via_aerea_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'] / 1000,
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0
                                     )

        # 45.- Transporte marítimo de pasajeros

        if fila.id == 45:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/transporte_maritimo_pasajeros_{clave}.csv', sep=';', encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'] / 1000,
                                     escala_eje_y=1.3,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left',
                                                       'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0
                                     )

        # 46.- Transporte marítimo de mercancías

        if fila.id == 46:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/transporte_maritimo_mercancias_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'] / 1000,
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=0,
                                     escala_eje_y_secundario=1.4,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de TN', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left',
                                                       'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0
                                     )

        # endregion

        # region gráficas servicios

        # 47.- VAB y empleo en el sector Servicios

        if fila.id == 47:
            for clave, valor in codigo_archivos.items():

                df_tf = pd.read_csv(f'output_files/vab_empleo_servicios_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_varias_lineas(eje_x=df_tf['per'].astype(str),
                                      eje_y=[df_tf['vd1'],
                                             df_tf['vd2']],
                                      escala_eje_y=1.3,
                                      centrar_eje_y_en=0,
                                      titulo=fila.titulo,
                                      subtitulo=fila.subtitulo,
                                      territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                      colores=[colores[fila.seccion][0],
                                               colores[fila.seccion][2]],
                                      nombres_medidas=['VAB Servicios', 'Empleo Servicios'],
                                      posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                      escala_x=1.6,
                                      escala_y=1,
                                      margin_r=60,
                                      nombre_archivo=f'{valor}_{fila.codigo}',
                                      angulo_etq_x=0
                                      )

        # 48.- Empleo Registrado Servicios

        if fila.id == 48:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_servicios_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y= df_tf['vd'] / 1000 if clave == "tenerife" or clave == "gran_canaria" else df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     centrar_eje_y_secundario_en=1,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles de personas' if clave == "tenerife" or clave == "gran_canaria" else 'Personas', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.06, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 49.- Empleo Registrado Hostelería

        if fila.id == 49:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_hosteleria_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barras(eje_x=df_tf['per'].astype(str),
                               eje_y=df_tf['vd'],
                               escala_eje_y=1.2,
                               titulo=fila.titulo,
                               subtitulo=fila.subtitulo,
                               territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                               color_primario=colores[fila.seccion][1],
                               escala_x=1.75,
                               escala_y=1,
                               nombre_archivo=f'{valor}_{fila.codigo}',
                               margin_l=0,
                               mostrar_valores=False,
                               margin_r=0
                               )

        # endregion

        # region gráficas mercado laboral

        # 50.- Afiliados a la Seguridad Social

        if fila.id == 50:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/afiliados_ss_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'] / 1000,
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     escala_eje_y_secundario=1.4,
                                     centrar_eje_y_secundario_en=1,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.06, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=2,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 51.- Ocupados

        if fila.id == 51:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/ocupados_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf['tma'] = df_tf['vd'].pct_change() * 100

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.2,
                                     eje_y_secundario=df_tf['tma'],
                                     escala_eje_y_secundario=1.4,
                                     centrar_eje_y_secundario_en=1,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Miles', 'Tasa de variación anual'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.06, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=2,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 52.- Empleo registrado por sectores

        if fila.id == 52:
            for clave, valor in codigo_archivos.items():

                df_tf = pd.read_csv(f'output_files/empleo_registrado_sectores_tv_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_varias_lineas(eje_x=df_tf['per'].astype(str),
                                      eje_y=[df_tf['Agricultura'],
                                             df_tf['Industria'],
                                             df_tf['Construcción'],
                                             df_tf['Servicios']],
                                      escala_eje_y=1.1,
                                      centrar_eje_y_en=0,
                                      titulo=fila.titulo,
                                      subtitulo=fila.subtitulo,
                                      territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                      colores=[colores[fila.seccion][0],
                                               colores[fila.seccion][1],
                                               colores[fila.seccion][2],
                                               colores[fila.seccion][3]],
                                      nombres_medidas=['Agricultura', 'Industria', 'Construcción', 'Servicios'],
                                      posicion_leyenda={'yanchor': 'top', 'y': 1.15, 'xanchor': 'left', 'x': 0.45},
                                      escala_x=2,
                                      escala_y=1,
                                      nombre_archivo=f'{valor}_{fila.codigo}',
                                      angulo_etq_x=0,
                                      tickformat='.0%'
                                      )

        # 53.- Estructura del empleo registrado en --isla-- 2010

        if fila.id == 53:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_sectores_2010_{clave}.csv', sep=';',
                                    encoding='utf8')

                isla = df_tf['ter'].tolist()[0]

                grafico_sectores(eje_x=df_tf['grupo'].astype(str).apply(mayusculas_por_palabra),
                                 eje_y=df_tf['vd'],
                                 titulo=f'{fila.titulo[:36]}{isla}{fila.titulo[44:]}',
                                 mostrar_subtitulo=False,
                                 territorio=df_tf['ter'].tolist()[0],
                                 color_primario=[colores[fila.seccion][0],
                                                 colores[fila.seccion][6],
                                                 colores[fila.seccion][4],
                                                 colores[fila.seccion][5]],
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=f'{valor}_{fila.codigo}',
                                 )

        # 54.- Estructura del empleo registrado en --isla-- 2023

        if fila.id == 54:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_sectores_2023_{clave}.csv', sep=';',
                                    encoding='utf8')

                isla = df_tf['ter'].tolist()[0]

                grafico_sectores(eje_x=df_tf['grupo'].astype(str).apply(mayusculas_por_palabra),
                                 eje_y=df_tf['vd'],
                                 titulo=f'{fila.titulo[:36]}{isla}{fila.titulo[44:]}',
                                 mostrar_subtitulo=False,
                                 territorio=df_tf['ter'].tolist()[0],
                                 color_primario=[colores[fila.seccion][0],
                                                 colores[fila.seccion][6],
                                                 colores[fila.seccion][4],
                                                 colores[fila.seccion][5]],
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=f'{valor}_{fila.codigo}',
                                 )

        # 55.- Poblacion activa y tasa de actividad

        if fila.id == 55:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/activos_tasa_actividad_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd1'],
                                     escala_eje_y=1.03,
                                     inicio_eje_y=0,
                                     eje_y_secundario=df_tf['vd2'],
                                     escala_eje_y_secundario=1.15,
                                     centrar_eje_y_secundario_en=50,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Población activa', 'Tasa de actividad'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 56.- Tasa de actividad masculina y femenina

        if fila.id == 56:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/tasa_actividad_sexos_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=df_tf['vd'],
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         colores=[colores[fila.seccion][0],
                                                  colores[fila.seccion][2]],
                                         escala_x=2,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.1,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.4},
                                         etiquetas_medidas={
                                             'Masculina': 'Masculina',
                                             'Femenina': 'Femenina'
                                         })

        # 57.- Población parada y tasa de paro

        if fila.id == 57:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/parados_tasa_paro_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd1'],
                                     escala_eje_y=1.1,
                                     inicio_eje_y=0,
                                     eje_y_secundario=df_tf['vd2'],
                                     escala_eje_y_secundario=1.1,
                                     centrar_eje_y_secundario_en=16,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Parados', 'Tasa de paro'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 58.- Tasa de paro masculina y femenina

        if fila.id == 58:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/tasa_paro_sexos_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                         eje_y=df_tf['vd'],
                                         grupo=df_tf['grupo'].tolist(),
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                         colores=[colores[fila.seccion][0],
                                                  colores[fila.seccion][2]],
                                         escala_x=2,
                                         escala_y=1,
                                         nombre_archivo=f'{valor}_{fila.codigo}',
                                         escala_eje_y=1.1,
                                         posicion_leyenda={'yanchor': 'top', 'y': 1.0, 'xanchor': 'left', 'x': 0.4},
                                         etiquetas_medidas={
                                             'Masculina': 'Masculina',
                                             'Femenina': 'Femenina'
                                         })

        # endregion

        # region gráficas sector público

        # 59.- Empleo registrado en Administraciones Públicas, Educación y Sanidad

        if fila.id == 59:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_admin_pub_{clave}.csv', sep=';',
                                    encoding='utf8')
                df_tf['tma'] = df_tf['vd'].pct_change() * 100
                print(df_tf)

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['vd'],
                                     escala_eje_y=1.1,
                                     inicio_eje_y=0,
                                     eje_y_secundario=df_tf['tma'],
                                     escala_eje_y_secundario=1.35,
                                     centrar_eje_y_secundario_en=0,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Empleo público', 'Tasa de variación'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.25},
                                     escala_x=1.5,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # 60.- Empleo registrado Ayuntamientos y Cabildos

        if fila.id == 60:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empleo_registrado_aytos_cabildos_{clave}.csv', sep=';',
                                    encoding='utf8')

                df_tf = df_tf.pivot_table(index=['ter', 'per'], columns='grupo',
                                                        values='vd', fill_value=0,
                                                        aggfunc='sum').reset_index()

                grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                     eje_y=df_tf['Puesto de trabajo'],
                                     escala_eje_y=1.3,
                                     inicio_eje_y=0,
                                     eje_y_secundario=df_tf['Puesto de trabajo por 1.000 habitantes'],
                                     escala_eje_y_secundario=1.35,
                                     centrar_eje_y_secundario_en=2,
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     color_primario=colores[fila.seccion][1],
                                     color_secundario=colores[fila.seccion][0],
                                     nombres_medidas=['Empleo en Ayuntamientos y Cabildos',
                                                      'Empleo por cada cien mil habitantes'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.15},
                                     escala_x=2,
                                     escala_y=1,
                                     nombre_archivo=f'{valor}_{fila.codigo}',
                                     margin_l=0,
                                     margin_r=0,
                                     )

        # endregion

        # region gráficas empresa y entorno regulatorio

        # 61.- Porcentaje de empresas por sector de actividad (--isla--)

        if fila.id == 61:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empresas_inscritas_ss_sectores_{clave}.csv', sep=';',
                                    encoding='utf8')

                isla = df_tf['ter'].tolist()[0]

                grafico_sectores(eje_x=df_tf['grupo'].astype(str),
                                 eje_y=df_tf['vd'],
                                 titulo=f'{fila.titulo} ({isla})',
                                 mostrar_subtitulo=False,
                                 territorio=df_tf['ter'].tolist()[0],
                                 color_primario=[colores[fila.seccion][3],
                                                 colores[fila.seccion][2],
                                                 colores[fila.seccion][1],
                                                 colores[fila.seccion][0]],
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=f'{valor}_{fila.codigo}',
                                 )

        # 62.- Empresas inscritas en la Seguridad Social

        if fila.id == 62:
            for clave, valor in codigo_archivos.items():
                df_tf = pd.read_csv(f'output_files/empresas_inscritas_ss_{clave}.csv', sep=';',
                                    encoding='utf8').iloc[::-1]

                grafico_barras(eje_x=df_tf['per'].astype(str),
                               eje_y= df_tf['vd'] / 1000 if clave == "tenerife" or clave == "gran_canaria" else df_tf['vd'],
                               titulo=fila.titulo,
                               subtitulo=fila.subtitulo,
                               territorio=df_tf['ter'].tolist()[0],
                               color_primario=colores[fila.seccion][0],
                               escala_x=2,
                               escala_y=1,
                               mostrar_valores=False,
                               nombre_archivo=f'{valor}_{fila.codigo}'
                               )

        # 63.- Índice de Confianza Empresarial Armonizado en Tenerife (ICEA)

        if fila.id == 63:
            for clave, valor in codigo_archivos.items():

                df_tf = pd.read_csv(f'output_files/indice_confianza_empresarial_{clave}.csv', sep=';',
                                    encoding='utf8')

                grafico_varias_lineas(eje_x=df_tf['per'].astype(str),
                                      eje_y=[df_tf['vd']],
                                      escala_eje_y=1.3,
                                      centrar_eje_y_en=90,
                                      titulo=fila.titulo,
                                      subtitulo=fila.subtitulo,
                                      territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                      colores=[colores[fila.seccion][0]],
                                      nombres_medidas=['ICEA'],
                                      posicion_leyenda={'yanchor': 'top', 'y': 1.15, 'xanchor': 'left', 'x': 0.45},
                                      escala_x=2.5,
                                      escala_y=1,
                                      nombre_archivo=f'{valor}_{fila.codigo}',
                                      margin_b=110,
                                      angulo_etq_x=270
                                      )

        # endregion

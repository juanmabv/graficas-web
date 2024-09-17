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

indicadores_concretos = [135]
indicadores_desde = 0

if len(indicadores_concretos) == 0:
    indicadores_concretos = df_graficas['id'].tolist()

if indicadores_desde > 0:
    indicadores_concretos = [indicador for indicador in indicadores_concretos if indicador >= indicadores_desde]
    print(f'Empezando a procesar {len(indicadores_concretos)} indicadores')

codigo_archivos = {'las_palmas': 'LPGC'}

for indice, fila in df_graficas.iterrows():
    if fila.id in indicadores_concretos:

        # region gráficas poblacion

        # 1.- Población residente (islas TF / LP / LG / EH)
        pass

        # 1.- Población residente (islas GC / LZ / FTV + provincia Las Palmas)
        pass

        # 1.- Población residente

        if fila.id == 1:
            df_tf = pd.read_csv(f'output_files/poblacion_total_35_las_palmas.csv', sep=';',
                                encoding='utf8').iloc[::-1]

            print(df_tf)

            grafico_barras(eje_x=df_tf['per'].astype(str),
                           eje_y=df_tf['vd'] / 1000,
                           titulo=fila.titulo,
                           subtitulo=fila.subtitulo,
                           territorio=df_tf['ter'].tolist()[0],
                           color_primario=colores[fila.seccion][0],
                           escala_x=2,
                           escala_y=1,
                           nombre_archivo=f'LPGC_{fila.codigo}',
                           mostrar_valores=False
                           )

        # 2.- Población residente por nacionalidad

        if fila.id == 2:
            df_tf = pd.read_csv(F'output_files/poblacion_nacionalidad_35_las_palmas.csv', sep=';', encoding='utf8')

            grafico_barras_apiladas(eje_x=df_tf['per'],
                                    eje_y=df_tf['vd'] / 1000,
                                    grupo=df_tf['grupo'],
                                    titulo=fila.titulo,
                                    subtitulo=fila.subtitulo,
                                    territorio=df_tf['ter'].tolist()[0],
                                    colores=[colores[fila.seccion][0], colores[fila.seccion][1]],
                                    escala_x=1.5,
                                    escala_y=1,
                                    nombre_archivo=f'LPGC_{fila.codigo}',
                                    escala_eje_y=1.3,
                                    posicion_leyenda={'yanchor': 'top', 'y': 0.95, 'xanchor': 'left', 'x': 0.5}
                                    )

        # 3.- Nacimientos y defunciones

        if fila.id == 3:
            df_tf_nac = pd.read_csv(f'output_files/nacimientos_las_palmas.csv', sep=';', encoding='utf8').drop(['ter'], axis=1)
            df_tf_def = pd.read_csv(f'output_files/defunciones_las_palmas.csv', sep=';', encoding='utf8')

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
                                     nombre_archivo=f'LPGC_{fila.codigo}',
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
            df_tf = pd.read_csv(f'output_files/saldo_migratorio_las_palmas.csv', sep=';', encoding='utf8')

            grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                     eje_y=df_tf['vd'],
                                     grupo=df_tf['grupo'].tolist(),
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].tolist()[0],
                                     colores=[colores[fila.seccion][1], colores[fila.seccion][0]],
                                     escala_x=2,
                                     escala_y=1,
                                     nombre_archivo=f'LPGC_{fila.codigo}',
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
            df_tf = pd.read_csv(f'output_files/piramide_poblacion_2010_ine_35_las_palmas.csv', sep=';', encoding='utf8')
            df_tf = df_tf[::-1]

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
                                              nombre_archivo=f'LPGC_{fila.codigo}',
                                              escala_eje_y=1.3,
                                              posicion_leyenda={'yanchor': 'top', 'y': 1.0, 'xanchor': 'left', 'x': 0.45},
                                              margin_r=50
                                              )

        # 6.- Pirámide poblacional 2023 (INE)

        if fila.id == 6:
            df_tf = pd.read_csv(f'output_files/piramide_poblacion_2023_ine_35_las_palmas.csv', sep=';', encoding='utf8')
            df_tf = df_tf[::-1]

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
                                              nombre_archivo=f'LPGC_{fila.codigo}',
                                              escala_eje_y=1.3,
                                              posicion_leyenda={'yanchor': 'top', 'y': 0.99, 'xanchor': 'left',
                                                                'x': 0.5},
                                              margin_r=50
                                              )

        # 7.- Índice de envejecimiento

        if fila.id == 7:
            df_tf = pd.read_csv(f'output_files/indice_envejecimiento_las_palmas.csv', sep=';', encoding='utf8')
            df_can = pd.read_csv('output_files/indice_envejecimiento_canarias.csv', sep=';', encoding='utf8')

            df_total = pd.concat([df_tf, df_can], axis=0, ignore_index=True)

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
                                         nombre_archivo=f'LPGC_{fila.codigo}',
                                         medida_y="Índice de envejecimiento Las Palmas",
                                         medida_y_secundario="Índice de envejecimiento Canarias",
                                         inicio_eje_y=0,
                                         posicion_leyenda={'yanchor': 'top', 'y': 0.95, 'xanchor': 'left', 'x': 0.2},
                                         margin_r=10,
                                         tickformat='.0%'
                                         )

        # 8.- Tasa de dependencia

        if fila.id == 8:
            df_tf = pd.read_csv(f'output_files/tasa_dependencia_total_las_palmas.csv', sep=';', encoding='utf8')
            df_tf['ter'] = df_tf['ter'].apply(mayusculas_por_palabra)

            grafico_barras_apiladas_y_lineas(eje_x=df_tf['per'].astype(str),
                                             eje_y_barras=[df_tf['Tasa de dependencia'] / 100],
                                             eje_y_lineas=[df_tf['Tasa de dependencia de la población menor de 16 años'] / 100,
                                                           df_tf['Tasa de dependencia de la población mayor de 64 años'] / 100
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
                                             nombre_archivo=f'LPGC_{fila.codigo}',
                                             lineas_a_eje_y_secundario=False,
                                             tickformat='.0%',
                                             mostrar_leyenda=False,
                                             margin_t=125
                                             )

        # 9.- Tasa bruta de natalidad

        if fila.id == 9:
            df_tf = pd.read_csv(f'output_files/tasa_bruta_natalidad_las_palmas.csv', sep=';', encoding='utf8')

            grafico_lineas_doble_relleno(eje_x=extraer_unicos_ordenados(df_tf['per'].astype(str).tolist()),
                                         eje_y=df_tf['Tasa Bruta de Natalidad Las Palmas'],
                                         eje_y_secundario=df_tf['Tasa Bruta de Natalidad Canarias'],
                                         titulo=fila.titulo,
                                         subtitulo=fila.subtitulo,
                                         territorio='Las Palmas',
                                         color_primario=colores[fila.seccion][0],
                                         color_secundario=colores[fila.seccion][2],
                                         escala_x=2,
                                         escala_y=0.9,
                                         nombre_archivo=f'LPGC_{fila.codigo}',
                                         medida_y="Tasa Bruta de Natalidad Las Palmas",
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
            df_tf = pd.read_csv(f'output_files/pib_corriente_las_palmas.csv', sep=';', encoding='utf8')

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 11.- PIB per cápita corriente

        if fila.id == 11:
            df_tf = pd.read_csv(f'output_files/pib_per_capita_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 12.- ÍndicePIB per cápita corriente --isla-- / Canarias

        if fila.id == 12:
            df_tf = pd.read_csv(f'output_files/indice_pib_per_capita_canarias_las_palmas.csv', sep=';',
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
                           nombre_archivo=f'LPGC_{fila.codigo}'
                           )

        # 13.- ÍndicePIB per cápita corriente --isla-- / España

        if fila.id == 13:
            df_tf = pd.read_csv(f'output_files/indice_pib_per_capita_españa_las_palmas.csv', sep=';',
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
                           nombre_archivo=f'LPGC_{fila.codigo}'
                           )

        # NUEVA 2023 -- PRODUCTIVIDAD
        if fila.id == 135:

            df_tf = pd.read_csv(f'output_files/productividad_total_las_palmas.csv', sep=';',
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
                                  nombre_archivo=f'LPGC_{fila.codigo}',
                                  angulo_etq_x=0,
                                  tickformat=','
                                  )

        # 14.- VAB Agricultura

        if fila.id == 14:
            df_tf = pd.read_csv(f'output_files/vab_agricultura_las_palmas.csv', sep=';', encoding='utf8')

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 15.- VAB Construcción

        if fila.id == 15:
            df_tf = pd.read_csv(f'output_files/vab_construccion_las_palmas.csv', sep=';',
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 16.- VAB Industria

        if fila.id == 16:
            df_tf = pd.read_csv(f'output_files/vab_industria_las_palmas.csv', sep=';',
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 17.- VAB Servicios

        if fila.id == 17:
            df_tf = pd.read_csv(f'output_files/vab_servicios_las_palmas.csv', sep=';',
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 18.- Estructura del VAB 2010

        if fila.id == 18:
            df_tf = pd.read_csv(f'output_files/estructura_vab_2010_las_palmas.csv', sep=';',
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
                             nombre_archivo=f'LPGC_{fila.codigo}',
                             )

        # 19.- Estructura del VAB 2023

        if fila.id == 19:
            df_tf = pd.read_csv(f'output_files/estructura_vab_2023_las_palmas.csv', sep=';',
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
                             nombre_archivo=f'LPGC_{fila.codigo}',
                             )

        # endregion

        # region gráficas agricultura

        # 20.- VAB y empleo en Agricultura

        if fila.id == 20:
            df_tf = pd.read_csv(f'output_files/vab_empleo_agricultura_las_palmas.csv', sep=';',
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
                                  nombre_archivo=f'LPGC_{fila.codigo}',
                                  angulo_etq_x=0
                                  )

        # 21.- Empleo Registrado Agricultura

        if fila.id == 21:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_agricultura_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

            grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                 eje_y=df_tf['vd'] / 1000,
                                 escala_eje_y=1.2,
                                 eje_y_secundario=df_tf['tma'],
                                 centrar_eje_y_secundario_en=1,
                                 titulo=fila.titulo,
                                 subtitulo=fila.subtitulo,
                                 territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                 color_primario=colores[fila.seccion][1],
                                 color_secundario=colores[fila.seccion][0],
                                 nombres_medidas=['Miles de personas', 'Tasa de variación anual'],
                                 posicion_leyenda={'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.25},
                                 escala_x=1.6,
                                 escala_y=1,
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 22.- Superficie cultivada

        if fila.id == 22:
            df_tf = pd.read_csv(f'output_files/superficie_cultivada_las_palmas.csv', sep=';',
                                encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

            grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                 eje_y=df_tf['vd'],
                                 escala_eje_y=1.2,
                                 eje_y_secundario=df_tf['tma'],
                                 escala_eje_y_secundario=1.2,
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 23.- Producción agrícola

        if fila.id == 23:
            df_tf = pd.read_csv(f'output_files/produccion_agricola_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 24.- Exportación de plátanos

        if fila.id == 24:
            df_tf = pd.read_csv(f'output_files/exportacion_platanos_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # endregion

        # region gráficas industria

        # 25.- VAB y empleo en el sector de la industria

        if fila.id == 25:
            df_tf = pd.read_csv(f'output_files/vab_empleo_industria_las_palmas.csv', sep=';',
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
                                  nombre_archivo=f'LPGC_{fila.codigo}',
                                  angulo_etq_x=0
                                  )

        # 26.- Empleo Registrado Industria

        if fila.id == 26:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_industria_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

            grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                 eje_y=df_tf['vd'] / 1000,
                                 escala_eje_y=1.2,
                                 eje_y_secundario=df_tf['tma'],
                                 centrar_eje_y_secundario_en=0,
                                 escala_eje_y_secundario=1.3,
                                 titulo=fila.titulo,
                                 subtitulo=fila.subtitulo,
                                 territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                 color_primario=colores[fila.seccion][1],
                                 color_secundario=colores[fila.seccion][0],
                                 nombres_medidas=['Miles de personas', 'Tasa de variación anual'],
                                 posicion_leyenda={'yanchor': 'top', 'y': 1.08, 'xanchor': 'left', 'x': 0.25},
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 27.- Energía eléctrica disponible

        if fila.id == 27:
            df_tf = pd.read_csv(f'output_files/energia_electrica_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # endregion

        # region gráficas construccion

        # 28.- VAB y empleo en el sector de la Construcción

        if fila.id == 28:
            df_tf = pd.read_csv(f'output_files/vab_empleo_construccion_las_palmas.csv', sep=';',
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
                                  nombre_archivo=f'LPGC_{fila.codigo}',
                                  angulo_etq_x=0
                                  )

        # 29.- Empleo Registrado Construcción

        if fila.id == 29:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_construccion_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

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
                                 nombres_medidas=['Miles de personas', 'Tasa de variación anual'],
                                 posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.25},
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0
                                 )

        # 30.- Consumo de cemento

        if fila.id == 30:
            df_tf = pd.read_csv(f'output_files/consumo_cemento_las_palmas.csv', sep=';', encoding='utf8')

            grafico_barras(eje_x=df_tf['per'].astype(str),
                           eje_y=df_tf['vd'],
                           titulo=fila.titulo,
                           subtitulo=fila.subtitulo,
                           territorio=df_tf['ter'].tolist()[0],
                           color_primario=colores[fila.seccion][0],
                           escala_x=2,
                           escala_y=1,
                           mostrar_valores=False,
                           nombre_archivo=f'LPGC_{fila.codigo}'
                           )

        # 31.- Hipotecas Constituidas

        if fila.id == 31:
            df_tf = pd.read_csv(f'output_files/hipotecas_constituidas_las_palmas.csv', sep=';', encoding='utf8')

            grafico_barras(eje_x=df_tf['per'].astype(str),
                           eje_y=df_tf['vd'],
                           titulo=fila.titulo,
                           subtitulo=fila.subtitulo,
                           territorio=df_tf['ter'].tolist()[0],
                           color_primario=colores[fila.seccion][0],
                           escala_x=2,
                           escala_y=1,
                           mostrar_valores=False,
                           nombre_archivo=f'LPGC_{fila.codigo}'
                           )

        # endregion

        # region gráficas turismo

        # 32.- Turistas nacionales e internacionales

        if fila.id == 32:
            df_tf = pd.read_csv(f'output_files/turistas_nacionales_internacionales_las_palmas.csv',
                            sep=';', encoding='utf8')

            df_tf = df_tf.sort_values(by=['grupo', 'per'])
            df_tf['tma'] = df_tf.groupby('grupo')['vd'].pct_change() * 100
            # df_tf['tma'] = df_tf['vd'].pct_change() * 100

            # df_tf['tma'].replace([np.inf, -np.inf], np.nan, inplace=True)
            lista_nac = df_tf[df_tf['grupo'] == 'Nacionales']['vd'] / 1000
            lista_internac = df_tf[df_tf['grupo'] == 'Internacionales']['vd'] / 1000

            lista_tma_nac = df_tf[df_tf['grupo'] == 'Nacionales']['tma']
            lista_tma_internac = df_tf[df_tf['grupo'] == 'Internacionales']['tma']
            print(df_tf)

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
                                             nombre_archivo=f'LPGC_{fila.codigo}')

        # 33.- Cruceristas

        if fila.id == 33:
            df_tf = pd.read_csv(f'output_files/cruceristas_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100

            df_tf['tma'].replace([np.inf, -np.inf], np.nan, inplace=True)
            print(df_tf)

            grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                 eje_y=df_tf['vd'],
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 )

        # 34.- Turistas según país de procedencia

        if fila.id == 34:
            df_tf = pd.read_csv(f'output_files/turistas_segun_pais_las_palmas.csv', sep=';',
                                encoding='utf8')

            print(df_tf)
            orden_paises = ['Alemania', 'Bélgica', 'Países Nórdicos', 'Francia', 'Países Bajos', 'Irlanda', 'Italia',
                            'Reino Unido', 'Otros países', 'Resto de España']
            df_tf['grupo'] = pd.Categorical(df_tf['grupo'], categories=orden_paises, ordered=True)
            df_tf = df_tf.sort_values(by=['per', 'grupo'])
            print(df_tf)

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
                                     nombre_archivo=f'LPGC_{fila.codigo}',
                                     escala_eje_y=1.1,
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.4},
                                     etiquetas_medidas={
                                         2010: 2010,
                                         2023: 2023
                                     })

        # 35.- Gasto de los turistas internacionales

        if fila.id == 35:
            df_tf = pd.read_csv(f'output_files/gasto_turistas_internacionales_las_palmas.csv',
                                sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100

            df_tf['tma'].replace([np.inf, -np.inf], np.nan, inplace=True)
            print(df_tf)

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 )

        # 37.- Número de plazas

        if fila.id == 37:
            df_tf = pd.read_csv(f'output_files/numero_plazas_las_palmas.csv', sep=';',
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
                                     nombre_archivo=f'LPGC_{fila.codigo}',
                                     escala_eje_y=1.1,
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.3},
                                     etiquetas_medidas={
                                         'Hoteles': 'Hoteles',
                                         'Apartamentos turísticos': 'Apartamentos turísticos'
                                     })

        # 38.- Tasa de ocupación por plazas

        if fila.id == 38:
            df_tf = pd.read_csv(f'output_files/tasa_ocupacion_plazas_las_palmas.csv', sep=';',
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
                                     nombre_archivo=f'LPGC_{fila.codigo}',
                                     escala_eje_y=1.1,
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.3},
                                     etiquetas_medidas={
                                         'Hoteles': 'Hoteles',
                                         'Apartamentos turísticos': 'Apartamentos turísticos'
                                     })

        # 39.- Pernoctaciones

        if fila.id == 391:
            df_tf = pd.read_csv(f'output_files/pernoctaciones_las_palmas.csv', sep=';',
                                encoding='utf8')

            # if clave == 'el_hierro' or clave == 'la_gomera' or clave == 'la_palma':
            #     datos = df_tf['vd'] / 1000
            # else:
            #     datos = df_tf['vd'] / 1000000

            grafico_barras_agrupadas(eje_x=df_tf['per'].astype(str).tolist(),
                                     eje_y=df_tf['vd'] / 1000000,
                                     grupo=df_tf['grupo'].tolist(),
                                     titulo=fila.titulo,
                                     subtitulo=fila.subtitulo,
                                     territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                     colores=[colores[fila.seccion][0],
                                              colores[fila.seccion][2]],
                                     escala_x=1.6,
                                     escala_y=1,
                                     nombre_archivo=f'LPGC_{fila.codigo}',
                                     escala_eje_y=1.1,
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.5},
                                     etiquetas_medidas={
                                         'Hoteles': 'Hoteles',
                                         'Apartamentos turísticos': 'Apartamentos turísticos'
                                     })

        # 40.- Estancia media

        if fila.id == 401:
            df_tf = pd.read_csv(f'output_files/estancia_media_las_palmas.csv', sep=';',
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
                                     nombre_archivo=f'LPGC_{fila.codigo}',
                                     escala_eje_y=1.1,
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.5},
                                     etiquetas_medidas={
                                         'Hoteles': 'Hoteles',
                                         'Apartamentos turísticos': 'Apartamentos turísticos'
                                     })

        # endregion

        # region gráficas comercio

        # 43.- Matriculación de vehículos según tipología

        if fila.id == 43:
            df_tf = pd.read_csv(f'output_files/matriculacion_vehiculos_las_palmas.csv', sep=';',
                                encoding='utf8')

            df_total = df_tf.groupby('per')['vd'].sum().reset_index()

            df_total['tma'] = df_total['vd'].pct_change() * 100

            lista_ciclo = df_tf[df_tf['grupo'] == 'Ciclomotores']['vd']
            lista_turi = df_tf[df_tf['grupo'] == 'Turismos']['vd']
            lista_moto = df_tf[df_tf['grupo'] == 'Motocicletas']['vd']
            lista_ve_es = df_tf[df_tf['grupo'] == 'Vehículos especiales']['vd']
            lista_rest = df_tf[df_tf['grupo'] == 'Resto de automóviles']['vd']
            lista_remo = df_tf[df_tf['grupo'] == 'Remolques y semirremolques']['vd']
            print(df_total)

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
                                             nombre_archivo=f'LPGC_{fila.codigo}')

        # endregion

        # region gráficas transporte

        # 44.- Pasajeros llegados por vía aérea

        if fila.id == 44:
            df_tf = pd.read_csv(f'output_files/pasajeros_via_aerea_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0
                                 )

        # 45.- Transporte marítimo de pasajeros

        if fila.id == 45:
            df_tf = pd.read_csv(f'output_files/transporte_maritimo_pasajeros_las_palmas.csv', sep=';', encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0
                                 )

        # 46.- Transporte marítimo de mercancías

        if fila.id == 46:
            df_tf = pd.read_csv(f'output_files/transporte_maritimo_mercancias_las_palmas.csv', sep=';',
                                encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0
                                 )

        # endregion

        # region gráficas servicios

        # 47.- VAB y empleo en el sector Servicios

        if fila.id == 47:
            df_tf = pd.read_csv(f'output_files/vab_empleo_servicios_las_palmas.csv', sep=';',
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
                                  nombre_archivo=f'LPGC_{fila.codigo}',
                                  angulo_etq_x=0
                                  )

        # 48.- Empleo Registrado Servicios

        if fila.id == 48:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_servicios_las_palmas.csv', sep=';',
                                encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

            grafico_barra_lineas(eje_x=df_tf['per'].astype(str),
                                 eje_y=df_tf['vd'] / 1000,
                                 escala_eje_y=1.2,
                                 eje_y_secundario=df_tf['tma'],
                                 centrar_eje_y_secundario_en=1,
                                 titulo=fila.titulo,
                                 subtitulo=fila.subtitulo,
                                 territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                                 color_primario=colores[fila.seccion][1],
                                 color_secundario=colores[fila.seccion][0],
                                 nombres_medidas=['Miles de personas', 'Tasa de variación anual'],
                                 posicion_leyenda={'yanchor': 'top', 'y': 1.06, 'xanchor': 'left', 'x': 0.25},
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 49.- Empleo Registrado Hostelería

        if fila.id == 49:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_hosteleria_las_palmas.csv', sep=';',
                                encoding='utf8')

            df_tf['tma'] = df_tf['vd'].pct_change() * 100
            print(df_tf)

            grafico_barras(eje_x=df_tf['per'].astype(str),
                           eje_y=df_tf['vd'],
                           escala_eje_y=1.2,
                           titulo=fila.titulo,
                           subtitulo=fila.subtitulo,
                           territorio=df_tf['ter'].apply(mayusculas_por_palabra).tolist()[0],
                           color_primario=colores[fila.seccion][1],
                           escala_x=1.75,
                           escala_y=1,
                           nombre_archivo=f'LPGC_{fila.codigo}',
                           margin_l=0,
                           mostrar_valores=False,
                           margin_r=0
                           )

        # endregion

        # region gráficas mercado laboral

        # 50.- Afiliados a la Seguridad Social

        if fila.id == 50:
            df_tf = pd.read_csv(f'output_files/afiliados_ss_las_palmas.csv', sep=';',
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 51.- Ocupados

        if fila.id == 51:
            df_tf = pd.read_csv(f'output_files/ocupados_las_palmas.csv', sep=';',
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 52.- Empleo registrado por sectores

        if fila.id == 52:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_sectores_tv_las_palmas.csv', sep=';',
                                encoding='utf8')

            grafico_varias_lineas(eje_x=df_tf['per'].astype(str),
                                  eje_y=[df_tf['Agricultura'],
                                         df_tf['Industria'],
                                         df_tf['Construcción'],
                                         df_tf['Servicios']],
                                  escala_eje_y=1.3,
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
                                  nombre_archivo=f'LPGC_{fila.codigo}',
                                  angulo_etq_x=0,
                                  tickformat='.0%'
                                  )

        # 53.- Estructura del empleo registrado en --isla-- 2010

        if fila.id == 53:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_sectores_2010_las_palmas.csv', sep=';',
                                encoding='utf8')

            isla = df_tf['ter'].tolist()[0]

            grafico_sectores(eje_x=df_tf['grupo'].astype(str).apply(mayusculas_por_palabra),
                             eje_y=df_tf['vd'],
                             titulo=f'{fila.titulo[:36]}{isla}{fila.titulo[44:]}',
                             mostrar_subtitulo=False,
                             territorio=df_tf['ter'].tolist()[0],
                             color_primario=[colores[fila.seccion][6],
                                             colores[fila.seccion][5],
                                             colores[fila.seccion][4],
                                             colores[fila.seccion][0]],
                             escala_x=1.5,
                             escala_y=1,
                             nombre_archivo=f'LPGC_{fila.codigo}',
                             )

        # 54.- Estructura del empleo registrado en --isla-- 2023

        if fila.id == 54:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_sectores_2023_las_palmas.csv', sep=';',
                                encoding='utf8')

            isla = df_tf['ter'].tolist()[0]

            grafico_sectores(eje_x=df_tf['grupo'].astype(str).apply(mayusculas_por_palabra),
                             eje_y=df_tf['vd'],
                             titulo=f'{fila.titulo[:36]}{isla}{fila.titulo[44:]}',
                             mostrar_subtitulo=False,
                             territorio=df_tf['ter'].tolist()[0],
                             color_primario=[colores[fila.seccion][6],
                                             colores[fila.seccion][5],
                                             colores[fila.seccion][4],
                                             colores[fila.seccion][0]],
                             escala_x=1.5,
                             escala_y=1,
                             nombre_archivo=f'LPGC_{fila.codigo}',
                             )

        # 55.- Poblacion activa y tasa de actividad

        if fila.id == 55:
            df_tf = pd.read_csv(f'output_files/activos_tasa_actividad_las_palmas.csv', sep=';',
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 56.- Tasa de actividad masculina y femenina

        if fila.id == 56:
            df_tf = pd.read_csv(f'output_files/tasa_actividad_sexos_las_palmas.csv', sep=';',
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
                                     nombre_archivo=f'LPGC_{fila.codigo}',
                                     escala_eje_y=1.1,
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.05, 'xanchor': 'left', 'x': 0.4},
                                     etiquetas_medidas={
                                         'Hombres': 'Masculina',
                                         'Mujeres': 'Femenina'
                                     })

        # 57.- Población parada y tasa de paro

        if fila.id == 57:
            df_tf = pd.read_csv(f'output_files/parados_tasa_paro_las_palmas.csv', sep=';',
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # 58.- Tasa de paro masculina y femenina

        if fila.id == 58:
            df_tf = pd.read_csv(f'output_files/tasa_paro_sexos_las_palmas.csv', sep=';',
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
                                     nombre_archivo=f'LPGC_{fila.codigo}',
                                     escala_eje_y=1.1,
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.0, 'xanchor': 'left', 'x': 0.4},
                                     etiquetas_medidas={
                                         'Hombres': 'Masculina',
                                         'Mujeres': 'Femenina'
                                     })

        # endregion

        # region gráficas sector público

        # 59.- Empleo registrado en Administraciones Públicas, Educación y Sanidad

        if fila.id == 59:
            df_tf = pd.read_csv(f'output_files/empleo_registrado_admin_pub_las_palmas.csv', sep=';',
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
                                 nombre_archivo=f'LPGC_{fila.codigo}',
                                 margin_l=0,
                                 margin_r=0,
                                 )

        # endregion

        # region gráficas empresa y entorno regulatorio

        # 61.- Porcentaje de empresas por sector de actividad (--isla--)

        if fila.id == 61:
            df_tf = pd.read_csv(f'output_files/empresas_inscritas_ss_sectores_las_palmas.csv', sep=';',
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
                             nombre_archivo=f'LPGC_{fila.codigo}',
                             )

        # 62.- Empresas inscritas en la Seguridad Social

        if fila.id == 62:
            df_tf = pd.read_csv(f'output_files/empresas_inscritas_ss_las_palmas.csv', sep=';',
                                encoding='utf8')

            grafico_barras(eje_x=df_tf['per'].astype(str),
                           eje_y=df_tf['vd'] / 1000,
                           titulo=f'{fila.titulo} en Las Palmas 2012-2023',
                           subtitulo=fila.subtitulo,
                           territorio=df_tf['ter'].tolist()[0],
                           color_primario=colores[fila.seccion][0],
                           escala_x=1.75,
                           escala_y=1,
                           mostrar_valores=False,
                           nombre_archivo=f'LPGC_{fila.codigo}'
                           )

        # endregion

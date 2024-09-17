import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots


# region funciones generales
def dividir_titulo(titulo, longitud_max=60):
    """Divide un título en dos líneas si supera una longitud máxima."""
    if len(titulo) <= longitud_max:
        return titulo
    # Intenta dividir en el espacio más cercano a la mitad, sin cortar palabras
    punto_de_corte = titulo[:longitud_max].rfind(' ')
    if punto_de_corte != -1:
        return titulo[:punto_de_corte] + '<br>' + titulo[punto_de_corte + 1:]
    else:
        return titulo[:longitud_max] + '<br>' + titulo[longitud_max:]


def extraer_unicos_ordenados(lista_original):
    elementos_unicos = []
    elementos_vistos = set()
    for elemento in lista_original:
        if elemento not in elementos_vistos:
            elementos_unicos.append(elemento)
            elementos_vistos.add(elemento)
    return elementos_unicos


# endregion

# region función gráfico de barras
def grafico_barras(eje_x=['a', 'b', 'c', 'd'],
                   mostrar_eje_x=True,
                   eje_y=[1, 2, 3, 4],
                   inicio_eje_y=0,
                   mostrar_eje_y=True,
                   escala_eje_y=1.2,
                   titulo='Título gráfica prueba título',
                   subtitulo='Unidad de medida',
                   territorio="territorio",
                   fuente='',
                   color_primario='red',
                   nombre_medida='medida 1',
                   titulo_eje_y=False,
                   fondo_imagen='white',
                   fondo_grafica='white',
                   formato_imagen='svg',
                   escala_x=1.5,
                   escala_y=1,
                   nombre_archivo=None,
                   estimacion=False,
                   texto_estimacion="* Valor estimados a partir de los datos de periodos anteriores",
                   margin_l=0,
                   margin_r=0,
                   margin_t=None,
                   margin_b=None,
                   zoom=480,
                   mostrar_valores=True
                   ):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_xaxes(type='category')

    # Primera traza para las barras con nombre dinámico
    fig.add_trace(
        go.Bar(
            x=eje_x,
            y=eje_y,
            marker_color=color_primario,
            name=nombre_medida,  # Nombre dinámico para la leyenda
            orientation='v'
        ),
        secondary_y=False,
    )

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Actualizaciones de la configuración de la gráfica
    if estimacion:
        nota_estimacion = dict(xref='paper',
                               yref='paper',
                               x=-0.025,
                               y=-0.075,
                               xanchor='left',
                               yanchor='top',
                               text=texto_estimacion,
                               showarrow=False,
                               font=dict(size=10, color="black"))
    else:
        nota_estimacion = dict(text=" ", showarrow=False)
    fig.update_layout(dict(title={
        'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
        'y': 0.95,
        'x': 0.05,
        'xanchor': 'left',
        'yanchor': 'top'
    },
        xaxis_visible=mostrar_eje_x,
        yaxis_visible=mostrar_eje_y,
        paper_bgcolor=fondo_imagen,
        plot_bgcolor=fondo_grafica,
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        yaxis_tickformat=',',
        separators=',.',
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=-0.025,
            y=-0.05,
            xanchor='left',
            yanchor='top',
            text=fuente,
            showarrow=False,
            font=dict(size=10, color="black")
        ),
            nota_estimacion
        ],
        margin=margenes
    ))
    # Ajustar el rango del eje y
    if escala_eje_y is not None:
        fig.update_yaxes(range=[inicio_eje_y, max(eje_y) * escala_eje_y])

    # Configuración de títulos de eje y basada en el parámetro mostrar_en_titulo
    if titulo_eje_y:
        fig.update_yaxes(title_text=nombre_medida, secondary_y=False)
    else:
        fig.update_yaxes(title_text="", secondary_y=False)

    # Dibujar las líneas de cuadrícula en el eje y primario
    fig.update_yaxes(showgrid=True, secondary_y=False, griddash="dash", gridcolor="grey")

    # Dibujar la línea de los ejes
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")

    # Añadir anotaciones de texto sobre cada barra
    if mostrar_valores:
        for i, (x, y) in enumerate(zip(eje_x, eje_y)):
            fig.add_annotation(x=x, y=y, text=str(y), showarrow=False, xanchor='center', yanchor='bottom',
                               yshift=10, font=dict(size=10, color="black"))

    # fig.update_yaxes(autorange=True)

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_barras.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'
    fig.write_image(nombre_archivo,
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )
    # fig.show()


# endregion

# region función gráfico de barras con línea
def grafico_barra_lineas(eje_x=['a', 'b', 'c', 'd'],
                         mostrar_eje_x=True,
                         eje_y=[1, 2, 3, 4],
                         inicio_eje_y=0,
                         mostrar_eje_y=True,
                         escala_eje_y=1.2,
                         eje_y_secundario=[np.nan, 5, 6, 4],
                         escala_eje_y_secundario=1.2,
                         mostrar_eje_y_secundario=True,
                         mostrar_linea_cero_secundario=True,
                         centrar_eje_y_secundario_en=0,
                         titulo='Título gráfica prueba título',
                         subtitulo='unidad de medida 1 y Tasa de variación anual (escala derecha)',
                         territorio="territorio",
                         fuente='',
                         color_primario='grey',
                         color_secundario='red',
                         nombres_medidas=['medida 1', 'medida 2'],
                         titulos_eje_y=False,
                         posicion_leyenda={'yanchor': 'top', 'y': 1.04, 'xanchor': 'left', 'x': 0.5},
                         fondo_imagen='white',
                         fondo_grafica='white',
                         formato_imagen='svg',
                         escala_x=1.5,
                         escala_y=1,
                         angulo_etq_x=None,
                         nombre_archivo=None,
                         margin_l=0,
                         margin_r=0,
                         margin_t=None,
                         margin_b=None,
                         zoom=480
                         ):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Primera traza para las barras con nombre dinámico
    fig.add_trace(
        go.Bar(
            x=eje_x,
            y=eje_y,
            marker_color=color_primario,
            name=nombres_medidas[0],  # Nombre dinámico para la leyenda
            orientation='v'
        ),
        secondary_y=False,
    )

    # Condición para añadir la segunda traza solo si se debe mostrar el eje y secundario
    if mostrar_eje_y_secundario:
        # Segunda traza para la línea con nombre dinámico
        fig.add_trace(
            go.Scatter(
                x=eje_x,
                y=eje_y_secundario,
                marker_color=color_secundario,
                name=nombres_medidas[1],  # Nombre dinámico para la leyenda
                mode='lines+markers'
            ),
            secondary_y=True,
        )

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Actualizaciones de la configuración de la gráfica
    fig.update_layout(dict(title={
        'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
        'y': 0.95,
        'x': 0.05,
        'xanchor': 'left',
        'yanchor': 'top'
    },
        xaxis_visible=mostrar_eje_x,
        yaxis_visible=mostrar_eje_y,
        paper_bgcolor=fondo_imagen,
        plot_bgcolor=fondo_grafica,
        legend=dict(title='',
                    orientation='h',
                    **posicion_leyenda),  # Aplicar la posición de la leyenda dinámicamente
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        yaxis_tickformat=',',
        separators=',.',
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=-0.025,
            y=-0.05,
            xanchor='left',
            yanchor='top',
            text=fuente,
            showarrow=False,
            font=dict(size=10, color="black")
        )],
        margin=margenes
    ))

    # Mostrar u ocultar los títulos de los ejes y
    fig.update_yaxes(title_text=nombres_medidas[0], secondary_y=False)
    if mostrar_eje_y_secundario:
        fig.update_yaxes(title_text=nombres_medidas[1], secondary_y=True, showgrid=True)
    else:
        fig.update_yaxes(secondary_y=True, showgrid=False, visible=False)

    # Ajustar el rango del eje y
    if escala_eje_y is not None:
        fig.update_yaxes(range=[inicio_eje_y, max(eje_y) * escala_eje_y])

    # Ajustar el rango del eje secundario de y para centrar en el valor especificado
    if centrar_eje_y_secundario_en is not None and escala_eje_y_secundario is not None:
        max_value = int(np.nanmax(eje_y_secundario))
        min_value = int(np.nanmin(eje_y_secundario))
        max_range = max(max_value - centrar_eje_y_secundario_en, centrar_eje_y_secundario_en - min_value)
        fig.update_yaxes(range=[(centrar_eje_y_secundario_en - max_range) * escala_eje_y_secundario,
                                (centrar_eje_y_secundario_en + max_range) * escala_eje_y_secundario],
                         secondary_y=True)

    # Condición para añadir la línea de 0 en el eje Y secundario
    if mostrar_eje_y_secundario and mostrar_linea_cero_secundario:
        # Añadir una línea de referencia horizontal en el punto 0 del eje Y secundario
        fig.add_hline(y=0, line_dash="solid", line_color="gray", line_width=0.75, secondary_y=True)

    # Configuración de títulos de eje y basada en el parámetro mostrar_en_titulo
    if titulos_eje_y:
        fig.update_yaxes(title_text=nombres_medidas[0], secondary_y=False)
        if mostrar_eje_y_secundario:
            fig.update_yaxes(title_text=nombres_medidas[1], secondary_y=True)
    else:
        if mostrar_eje_y_secundario:
            fig.update_yaxes(title_text="", secondary_y=True)
        fig.update_yaxes(title_text="", secondary_y=False)

    # Dibujar las líneas de cuadrícula en el eje y primario
    fig.update_yaxes(showgrid=True, secondary_y=False, griddash="dash", gridcolor="grey")

    # Dibujar la línea de los ejes
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside", tickangle=angulo_etq_x)

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_barras_linea.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    fig.write_image(nombre_archivo,
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )

    # fig.show()


# endregion

# region función gráfico de barras apiladas
def grafico_barras_apiladas(eje_x=['a', 'b', 'c', 'd'],
                            mostrar_eje_x=True,
                            eje_y=[1, 2, 3, 4, 2, 3, 4, 5, 7, 9, 2, 3],
                            grupo=['a', 'a', 'a', 'a', 'b', 'b', 'b', 'b', 'c', 'c', 'c', 'c'],
                            inicio_eje_y=0,
                            mostrar_eje_y=True,
                            escala_eje_y=1.2,
                            titulo='Título gráfica prueba título',
                            subtitulo='Unidad de medida',
                            territorio="territorio",
                            fuente='',
                            colores=['red', 'blue', 'green'],
                            nombres_medidas=None,
                            posicion_leyenda={'yanchor': 'top', 'y': 1.04, 'xanchor': 'left', 'x': 0.5},
                            titulo_eje_y=False,
                            fondo_imagen='white',
                            fondo_grafica='white',
                            formato_imagen='svg',
                            escala_x=1.5,
                            escala_y=1,
                            nombre_archivo=None,
                            fuente_x=-0.025,
                            fuente_y=-0.2,
                            margin_l=60,
                            margin_r=0,
                            margin_t=None,
                            margin_b=100,
                            zoom=480,
                            ):
    if nombres_medidas is None:
        nombres_medidas = extraer_unicos_ordenados(grupo)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    datos_agrupados = {g: [] for g in nombres_medidas}
    for g, y in zip(grupo, eje_y):
        datos_agrupados[g].append(y)

    # Generar la lista de sumas de todos los elementos con el mismo índice
    sumas_por_indice = [sum(values) for values in zip(*datos_agrupados.values())]

    # Encontrar el valor máximo de la lista de sumas
    maximo_valor = max(sumas_por_indice)

    # Añadir trazas para cada grupo de datos
    for nombre, datos in datos_agrupados.items():
        fig.add_trace(
            go.Bar(
                x=eje_x[:len(datos)],
                y=datos,
                name=nombre,
                marker_color=colores[nombres_medidas.index(nombre)],
            ),
            secondary_y=False,
        )

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # # Preparar los datos agrupados por 'grupo'
    # datos_agrupados = {g: [] for g in nombres_medidas}
    # for g, y in zip(grupo, eje_y):
    #     datos_agrupados[g].append(y)
    #
    # # Añadir trazas para cada grupo de datos
    # for nombre, datos in datos_agrupados.items():
    #     fig.add_trace(
    #         go.Bar(
    #             x=eje_x,
    #             y=datos,
    #             name=nombre,  # Nombre dinámico para la leyenda
    #             marker_color=colores[nombres_medidas.index(nombre)],
    #         ),
    #         secondary_y=False,
    #     )

    # Configuración de la gráfica para barras apiladas
    fig.update_layout(barmode='stack')

    # La mayoría de la configuración se mantiene igual
    fig.update_layout(dict(title={
        'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
        'y': 0.95,
        'x': 0.05,
        'xanchor': 'left',
        'yanchor': 'top'
    },
        xaxis_visible=mostrar_eje_x,
        yaxis_visible=mostrar_eje_y,
        paper_bgcolor=fondo_imagen,
        plot_bgcolor=fondo_grafica,
        legend=dict(title='',
                    orientation='h',
                    **posicion_leyenda),  # Aplicar la posición de la leyenda dinámicamente
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        yaxis_tickformat=',',
        separators=',.',
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=fuente_x,
            y=fuente_y,
            xanchor='left',
            yanchor='top',
            text=fuente,
            showarrow=False,
            font=dict(size=10, color="black")
        )],
        margin=margenes
    ))

    # Ajustes adicionales como en la función original
    if escala_eje_y is not None:
        fig.update_yaxes(range=[inicio_eje_y, maximo_valor * escala_eje_y])

    if titulo_eje_y:
        fig.update_yaxes(title_text=",".join(nombres_medidas), secondary_y=False)

    fig.update_yaxes(showgrid=True, secondary_y=False, griddash="dash", gridcolor="grey")
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside", tickvals=eje_x,
                     ticktext=eje_x if mostrar_eje_x else [], tickangle=270)

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_barras_apiladas.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    fig.write_image(nombre_archivo,
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )

    # fig.show()


# endregion

# region gráfico de barras agrupadas
def grafico_barras_agrupadas(eje_x=['a', 'b', 'c', 'd'],
                             mostrar_eje_x=True,
                             eje_y=[1, 2, 3, 4, 2, -3, 4, -5, 7, -9, 2, 3],
                             grupo=['a', 'a', 'a', 'a', 'b', 'b', 'b', 'b', 'c', 'c', 'c', 'c'],
                             inicio_eje_y=0,
                             mostrar_eje_y=True,
                             escala_eje_y=1.1,
                             titulo='Título gráfica prueba título',
                             subtitulo='Unidad de medida',
                             territorio="territorio",
                             fuente='',
                             colores=['red', 'blue', 'green'],
                             nombres_medidas=None,
                             posicion_leyenda={'yanchor': 'top', 'y': 1.09, 'xanchor': 'left', 'x': 0.5},
                             titulo_eje_y=False,
                             fondo_imagen='white',
                             fondo_grafica='white',
                             formato_imagen='svg',
                             escala_x=1.5,
                             escala_y=1,
                             nombre_archivo=None,
                             margin_l=60,
                             margin_r=0,
                             margin_t=None,
                             margin_b=None,
                             etiquetas_medidas={'a': 'etq_a', 'b': 'etq_b', 'c': 'etq_c'},
                             ticks="outside",
                             zoom=480
                             ):
    if nombres_medidas is None:
        nombres_medidas = extraer_unicos_ordenados(grupo)
        for nombres in nombres_medidas:
            nombres_medidas[nombres_medidas.index(nombres)] = etiquetas_medidas[nombres]

    for valor in grupo:
        grupo[grupo.index(valor)] = etiquetas_medidas[valor]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    datos_agrupados = {g: [] for g in nombres_medidas}
    for g, y in zip(grupo, eje_y):
        datos_agrupados[g].append(y)

    # Generar la lista de sumas de todos los elementos con el mismo índice
    sumas_por_indice = [sum(values) for values in zip(*datos_agrupados.values())]

    # Encontrar el valor máximo de la lista de sumas
    maximo_valor = max(sumas_por_indice)

    # Añadir trazas para cada grupo de datos
    for nombre, datos in datos_agrupados.items():
        fig.add_trace(
            go.Bar(
                x=eje_x[:len(datos)],
                y=datos,
                name=nombre,
                marker_color=colores[nombres_medidas.index(nombre)],
            ),
            secondary_y=False,
        )

    # Configuración de la gráfica para barras agrupadas
    fig.update_layout(barmode='group')

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # La mayoría de la configuración se mantiene igual
    fig.update_layout(dict(title={
        'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
        'y': 0.95,
        'x': 0.05,
        'xanchor': 'left',
        'yanchor': 'top'
    },
        xaxis=dict(
            tickmode='array',
            tickvals=[i for i in range(len(eje_x))],
            ticktext=eje_x,
            visible=mostrar_eje_x
        ),
        yaxis_visible=mostrar_eje_y,
        paper_bgcolor=fondo_imagen,
        plot_bgcolor=fondo_grafica,
        legend=dict(title='',
                    orientation='h',
                    **posicion_leyenda),  # Aplicar la posición de la leyenda dinámicamente
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        yaxis_tickformat=',',
        separators=',.',
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=0,
            y=-0.05,
            xanchor='left',
            yanchor='top',
            text=fuente,
            showarrow=False,
            font=dict(size=10, color="black")
        )],
        margin=margenes
    ))

    if titulo_eje_y:
        fig.update_yaxes(title_text=",".join(nombres_medidas), secondary_y=False)

    fig.update_yaxes(showgrid=True, secondary_y=False, griddash="dash", gridcolor="grey")
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks=ticks)

    if escala_eje_y is not None:
        if np.nanmin(eje_y) < 0:
            inicio_eje_y = np.nanmin(eje_y)
            fig.update_xaxes(showline=False)
            fig.add_hline(y=0, line_dash="solid", line_color="gray")

        else:
            pass
        if min(eje_y) * escala_eje_y > 0:
            inicio = inicio_eje_y
        else:
            inicio = min(eje_y) * escala_eje_y
        fig.update_yaxes(range=[inicio, max(eje_y) * escala_eje_y])

    # Guardar imagen o mostrar
    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_barras_agrupadas.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    fig.write_image(nombre_archivo,
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )

    # fig.show()


# endregion

# region gráfico de barras dos colores horizontal
def grafico_barras_colores_horizontal(eje_x=['a', 'b', 'c', 'd'],
                                      mostrar_eje_x=True,
                                      eje_y=[1, 2, 3, 4],
                                      inicio_eje_y=0,
                                      mostrar_eje_y=True,
                                      escala_eje_y=1.2,
                                      titulo='Título gráfica prueba título',
                                      subtitulo='Unidad de medida',
                                      territorio="territorio",
                                      fuente='',
                                      colores=['grupo1', 'grupo2', 'grupo2', 'grupo1'],
                                      # Lista de grupos para las barras
                                      colores_dict={'grupo1': 'red', 'grupo2': 'blue'},
                                      # Diccionario de colores para cada grupo
                                      posicion_leyenda={'yanchor': 'top', 'y': 1.06, 'xanchor': 'left', 'x': 0.5},
                                      fondo_imagen='white',
                                      fondo_grafica='white',
                                      formato_imagen='svg',
                                      escala_x=1.5,
                                      escala_y=1,
                                      nombre_archivo=None,
                                      margin_l=200,
                                      margin_r=0,
                                      margin_t=None,
                                      margin_b=None,
                                      zoom=480,
                                      max_eje_y=None
                                      ):

    if max_eje_y is not None:
        max_eje_y = max_eje_y
    else:
        max_eje_y = max(eje_y)

    fig = make_subplots()

    eje_x = eje_x[::-1]
    eje_y = eje_y[::-1]

    legend_shown = set()

    # Añadir barras al gráfico manteniendo el orden original
    for i, (x, y, grupo) in enumerate(zip(eje_x, eje_y, colores)):
        show_legend = grupo not in legend_shown  # Mostrar leyenda solo si el grupo aún no se ha mostrado
        if show_legend:
            legend_shown.add(grupo)  # Marcar este grupo como mostrado

        fig.add_trace(
            go.Bar(
                y=[x],  # Usar un elemento de lista para mantener la estructura
                x=[y],  # Usar un elemento de lista para mantener la estructura
                marker_color=colores_dict[grupo],  # Color según el grupo
                name=f'{grupo}',
                # Evitar repetición de nombres en la leyenda
                orientation='h',  # Orientación horizontal
                showlegend=show_legend
                # Mostrar leyenda solo para el primer elemento de cada grupo
            )
        )

        # márgenes de la gráfica
        margenes = {'l': margin_l,
                    'r': margin_r,
                    't': margin_t,
                    'b': margin_b}

        margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Configuración del layout de la gráfica
    fig.update_layout(dict(title={
        'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
        'y': 0.95,
        'x': 0.05,
        'xanchor': 'left',
        'yanchor': 'top'
    },
        yaxis_visible=mostrar_eje_x,
        xaxis_visible=mostrar_eje_y,
        paper_bgcolor=fondo_imagen,
        plot_bgcolor=fondo_grafica,
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        legend=dict(title='',
                    orientation='v',
                    **posicion_leyenda),  # Aplicar la posición de la leyenda dinámicamente
        xaxis_tickformat=',',
        separators=',.',
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=0,
            y=-0.05,
            xanchor='left',
            yanchor='top',
            text=fuente,
            showarrow=False,
            font=dict(size=10, color="black")
        )],
        margin=margenes
    ))

    # Ajustar rango del eje Y, si es necesario
    if escala_eje_y is not None:
        fig.update_xaxes(range=[inicio_eje_y, max_eje_y * escala_eje_y])

    # Configuración de título del eje Y
    fig.update_xaxes(title_text="")

    # Añadir líneas de cuadrícula y configurar la apariencia de los ejes
    fig.update_xaxes(showgrid=True, griddash="dash", gridcolor="grey")
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="")

    if len(set(colores)) == 1:
        fig.update_layout(showlegend=False)

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_barras_colores_horizontal.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    # Guardar imagen o mostrar
    fig.write_image(nombre_archivo,
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )

    # fig.show()


# endregion

# region gráfico de barras dos colores vertical
def grafico_barras_colores_vertical(eje_x=['a', 'b', 'c', 'd'],
                                    mostrar_eje_x=True,
                                    eje_y=[1, 2, 3, 4],
                                    inicio_eje_y=0,
                                    mostrar_eje_y=True,
                                    escala_eje_y=1.2,
                                    titulo='Título gráfica prueba título',
                                    subtitulo='Unidad de medida',
                                    territorio="territorio",
                                    fuente='Fuente: Elaboración Corporación 5. Prueba (datos de ejemplo)',
                                    colores=['grupo1', 'grupo2', 'grupo2', 'grupo1'],  # Lista de grupos para las barras
                                    colores_dict={'grupo1': 'red', 'grupo2': 'blue'},
                                    # Diccionario de colores para cada grupo
                                    posicion_leyenda={'yanchor': 'top', 'y': 1.06, 'xanchor': 'left', 'x': 0.5},
                                    fondo_imagen='white',
                                    fondo_grafica='white',
                                    formato_imagen='svg',
                                    escala_x=1.5,
                                    escala_y=1,
                                    nombre_archivo=None,
                                    margin_l=60,
                                    margin_r=0,
                                    margin_t=None,
                                    margin_b=None,
                                    zoom=480
                                    ):
    fig = make_subplots()

    eje_x = eje_x[::-1]
    eje_y = eje_y[::-1]

    legend_shown = set()

    # Añadir barras al gráfico manteniendo el orden original
    for i, (x, y, grupo) in enumerate(zip(eje_x, eje_y, colores)):
        show_legend = grupo not in legend_shown  # Mostrar leyenda solo si el grupo aún no se ha mostrado
        if show_legend:
            legend_shown.add(grupo)  # Marcar este grupo como mostrado

        fig.add_trace(
            go.Bar(
                x=[x],  # Usar un elemento de lista para mantener la estructura
                y=[y],  # Usar un elemento de lista para mantener la estructura
                marker_color=colores_dict[grupo],  # Color según el grupo
                name=f'{grupo}',
                # Evitar repetición de nombres en la leyenda
                orientation='v',  # Orientación vertical
                showlegend=show_legend
                # Mostrar leyenda solo para el primer elemento de cada grupo
            )
        )

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Configuración del layout de la gráfica
    fig.update_layout(dict(title={
        'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
        'y': 0.95,
        'x': 0.05,
        'xanchor': 'left',
        'yanchor': 'top'
    },
        xaxis_visible=mostrar_eje_x,
        yaxis_visible=mostrar_eje_y,
        paper_bgcolor=fondo_imagen,
        plot_bgcolor=fondo_grafica,
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        legend=dict(title='',
                    orientation='h',
                    **posicion_leyenda),  # Aplicar la posición de la leyenda dinámicamente
        yaxis_tickformat=',',
        separators=',.',
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=0,
            y=-0.05,
            xanchor='left',
            yanchor='top',
            text=fuente,
            showarrow=False,
            font=dict(size=10, color="black")
        )],
        margin=margenes
    ))

    # Ajustar rango del eje Y, si es necesario
    if escala_eje_y is not None:
        fig.update_yaxes(range=[inicio_eje_y, max(eje_y) * escala_eje_y])

    # Configuración de título del eje Y
    fig.update_yaxes(title_text="")

    # Añadir líneas de cuadrícula y configurar la apariencia de los ejes
    fig.update_yaxes(showgrid=True, griddash="dash", gridcolor="grey")
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")

    if len(set(colores)) == 1:
        fig.update_layout(showlegend=False)

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_barras_colores_vertical.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    # Guardar imagen o mostrar
    fig.write_image(nombre_archivo,
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )

    # fig.show()


# endregion

# region gráfico de líneas con relleno
def grafico_lineas_doble_relleno(eje_x=['a', 'b', 'c', 'd'],
                                 mostrar_eje_x=True,
                                 eje_y=[1, 2, 3, 4],
                                 medida_y="medida 1",
                                 inicio_eje_y=0,
                                 mostrar_eje_y=True,
                                 escala_eje_y=1.2,
                                 eje_y_secundario=[3, 5, 1, 4],
                                 medida_y_secundario="medida 2",
                                 mostrar_eje_y_secundario=True,
                                 centrar_eje_y_secundario_en=0,
                                 titulo='Título gráfica prueba título',
                                 subtitulo='unidad de medida 1 y Tasa de variación anual (escala derecha)',
                                 territorio="territorio",
                                 fuente='',
                                 color_primario='grey',
                                 color_secundario='red',
                                 nombres_medidas=None,
                                 titulos_eje_y=False,
                                 posicion_leyenda={'yanchor': 'top', 'y': 1.04, 'xanchor': 'left', 'x': 0.5},
                                 fondo_imagen='white',
                                 fondo_grafica='white',
                                 formato_imagen='svg',
                                 escala_x=1.5,
                                 escala_y=1,
                                 nombre_archivo=None,
                                 margin_l=60,
                                 margin_r=0,
                                 margin_t=None,
                                 margin_b=None,
                                 zoom=480,
                                 tickformat=','
                                 ):
    eje_y_secundario_ok = [a - b for a, b in zip(eje_y_secundario, eje_y)]

    df = pd.concat([
        pd.DataFrame({'x': eje_x, 'y': eje_y, 'color': ['color1' for i in eje_y]}),
        pd.DataFrame({'x': eje_x, 'y': eje_y_secundario_ok, 'color': ['color2' for i in eje_y_secundario]})
    ],
        ignore_index=True, axis=0)
    fig = px.area(df, x='x', y='y', color='color', color_discrete_map={'color1': 'white', 'color2': 'white'},
                  pattern_shape="color", pattern_shape_sequence=['', '|'])

    # Primera traza transformada a línea para eje_y
    fig.add_trace(
        go.Scatter(
            x=eje_x,
            y=eje_y,
            marker_color=color_primario,
            name=medida_y,
            mode='lines+markers'
        ),
    )

    # Segunda traza para la línea eje_y_secundario, si se debe mostrar
    if mostrar_eje_y_secundario:
        fig.add_trace(
            go.Scatter(
                x=eje_x,
                y=eje_y_secundario,
                marker_color=color_secundario,
                name=medida_y_secundario,
                mode='lines+markers'
            ),
        )

    for trace in fig.data:
        if trace.name in ['color1', 'color2']:
            trace.showlegend = False

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Actualizaciones de la configuración de la gráfica
    fig.update_layout({
        'title': {
            'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
            'y': 0.95,
            'x': 0.05,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        'xaxis_visible': mostrar_eje_x,
        'yaxis_visible': mostrar_eje_y,
        'paper_bgcolor': fondo_imagen,
        'plot_bgcolor': fondo_grafica,
        'legend': {
            'title': '',
            'orientation': 'h',
            **posicion_leyenda
        },
        'font': {
            'family': "Arial, sans-serif",
            'size': 14,
            'color': "black"
        },
        'yaxis_tickformat': tickformat,
        'separators': ',.',
        'annotations': [{
            'xref': 'paper',
            'yref': 'paper',
            'x': 0,
            'y': -0.05,
            'xanchor': 'left',
            'yanchor': 'top',
            'text': fuente,
            'showarrow': False,
            'font': {'size': 10, 'color': "black"}
        }],
        'margin': margenes
    })

    # Ajustar el rango del eje y
    if escala_eje_y is not None:
        fig.update_yaxes(range=[inicio_eje_y, max(np.nanmax(eje_y), np.nanmax(eje_y_secundario)) * escala_eje_y],
                         secondary_y=False)

    # Añadir una línea de referencia horizontal en el punto 0 del eje Y
    fig.add_hline(y=0, line_dash="solid", line_color="gray")

    # Dibujar las líneas de cuadrícula en el eje y
    fig.update_yaxes(showgrid=True, griddash="dash", gridcolor="grey")

    # Dibujar la línea de los ejes
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")

    # Configuración de títulos de eje y basada en el parámetro titulos_eje_y
    if titulos_eje_y:
        fig.update_yaxes(title_text=nombres_medidas[0])
        if mostrar_eje_y_secundario:
            fig.update_yaxes(title_text=nombres_medidas[1])
    else:
        fig.update_yaxes(title_text="")

    fig.update_xaxes(range=[-0.25, len(eje_x) - 0.75], title_text="")

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_barras_colores_vertical.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    fig.write_image(nombre_archivo, scale=4, width=zoom * escala_x, height=zoom * escala_y, engine='kaleido')

    # fig.show() # Descomentar para mostrar la gráfica en un entorno interactivo


# endregion

# region gráfico de líneas doble
def grafico_lineas_doble(eje_x=['a', 'b', 'c', 'd'],
                         mostrar_eje_x=True,
                         eje_y=[1, -2, 3, -4],
                         inicio_eje_y=None,
                         mostrar_eje_y=True,
                         escala_eje_y=1.2,
                         eje_y_secundario=[3, -5, -1, 4],
                         mostrar_eje_y_secundario=True,
                         centrar_eje_y_en=0,
                         titulo='Título gráfica prueba título',
                         subtitulo='unidad de medida 1 y Tasa de variación anual (escala derecha)',
                         territorio="territorio",
                         fuente='Fuente: Elaboración Corporación 5. Prueba (datos de ejemplo)',
                         color_primario='grey',
                         color_secundario='red',
                         nombres_medidas=['medida 1', 'medida 2'],
                         titulos_eje_y=False,
                         posicion_leyenda={'yanchor': 'top', 'y': 1.04, 'xanchor': 'left', 'x': 0.5},
                         fondo_imagen='white',
                         fondo_grafica='white',
                         formato_imagen='svg',
                         escala_x=1.5,
                         escala_y=1,
                         margin_l=0,
                         margin_r=0,
                         margin_t=None,
                         margin_b=None,
                         zoom=480
                         ):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Primera traza transformada a línea para eje_y
    fig.add_trace(
        go.Scatter(
            x=eje_x,
            y=eje_y_secundario,
            marker_color=color_primario,
            name=nombres_medidas[0],
            mode='lines+markers'
        ),
    )

    # Segunda traza para la línea eje_y_secundario, si se debe mostrar
    if mostrar_eje_y_secundario:
        fig.add_trace(
            go.Scatter(
                x=eje_x,
                y=eje_y,
                marker_color=color_secundario,
                name=nombres_medidas[1],
                mode='lines+markers'
            ),
        )

    for trace in fig.data:
        if trace.name in ['color1', 'color2']:
            trace.showlegend = False

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Actualizaciones de la configuración de la gráfica
    fig.update_layout({
        'title': {
            'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
            'y': 0.95,
            'x': 0.05,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        'xaxis_visible': mostrar_eje_x,
        'yaxis_visible': mostrar_eje_y,
        'paper_bgcolor': fondo_imagen,
        'plot_bgcolor': fondo_grafica,
        'legend': {
            'title': '',
            'orientation': 'h',
            **posicion_leyenda
        },
        'font': {
            'family': "Arial, sans-serif",
            'size': 14,
            'color': "black"
        },
        'yaxis_tickformat': ',',
        'separators': ',.',
        'annotations': [{
            'xref': 'paper',
            'yref': 'paper',
            'x': 0,
            'y': -0.05,
            'xanchor': 'left',
            'yanchor': 'top',
            'text': fuente,
            'showarrow': False,
            'font': {'size': 10, 'color': "black"}
        }],
        'margin': margenes
    })

    # Ajustar el rango del eje secundario de y para centrar en el valor especificado
    max_value = int(np.nanmax(eje_y_secundario))
    min_value = int(np.nanmin(eje_y_secundario))
    max_range = max([max_value - centrar_eje_y_en, centrar_eje_y_en - min_value])
    if centrar_eje_y_en is not None:
        fig.update_yaxes(range=[(centrar_eje_y_en - max_range) * escala_eje_y,
                                centrar_eje_y_en + max_range * escala_eje_y],
                         secondary_y=False)

    if inicio_eje_y is not None:
        fig.update_yaxes(range=[inicio_eje_y, centrar_eje_y_en + max_range * escala_eje_y])

    # Añadir una línea de referencia horizontal en el punto 0 del eje Y
    fig.add_hline(y=0, line_dash="solid", line_color="gray")

    # Dibujar las líneas de cuadrícula en el eje y
    fig.update_yaxes(showgrid=True, griddash="dash", gridcolor="grey")

    # Dibujar la línea de los ejes
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_xaxes(showline=False)

    # Configuración de títulos de eje y basada en el parámetro titulos_eje_y
    if titulos_eje_y:
        fig.update_yaxes(title_text=nombres_medidas[0])
        if mostrar_eje_y_secundario:
            fig.update_yaxes(title_text=nombres_medidas[1])
    else:
        fig.update_yaxes(title_text="")

    fig.update_xaxes(range=[-0.25, len(eje_x) - 0.75], title_text="")

    fig.write_image(f'imagenes/prueba/prueba_lineas_doble.{formato_imagen}', scale=4, width=zoom * escala_x,
                    height=zoom * escala_y, engine='kaleido')

    # fig.show()


# endregion

# region gráfico de varias líneas
def grafico_varias_lineas(eje_x=['a', 'b', 'c', 'd'],
                          mostrar_eje_x=True,
                          eje_y=[[1, 2, 3, 4], [2, -3, 4, -5], [7, -9, 2, 3]],
                          inicio_eje_y=None,
                          mostrar_eje_y=True,
                          escala_eje_y=1.1,
                          centrar_eje_y_en=0,
                          angulo_etq_x=None,
                          titulo='Título gráfica prueba título',
                          subtitulo='Unidad de medida',
                          territorio="territorio",
                          fuente='',
                          colores=['red', 'blue', 'green'],
                          nombres_medidas=['medida 1', 'medida 2', 'medida 3'],
                          posicion_leyenda={'yanchor': 'top', 'y': 1.04, 'xanchor': 'left', 'x': 0.5},
                          titulo_eje_y=False,
                          fondo_imagen='white',
                          fondo_grafica='white',
                          formato_imagen='svg',
                          escala_x=1.5,
                          escala_y=1,
                          margin_l=60,
                          margin_r=0,
                          margin_t=None,
                          margin_b=None,
                          zoom=480,
                          tickformat='outside',
                          nombre_archivo=None):
    fig = make_subplots()

    # Añadir trazas para cada conjunto de datos como líneas
    for datos, color, nombre in zip(eje_y, colores, nombres_medidas):
        fig.add_trace(
            go.Scatter(
                x=eje_x,
                y=datos,
                name=nombre,
                mode='lines+markers',
                line=dict(color=color),
            )
        )

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Configuración de la gráfica para varias líneas
    fig.update_layout(
        title={
            'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
            'y': 0.95,
            'x': 0.05,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        xaxis=dict(
            tickmode='array',
            tickvals=[i for i, _ in enumerate(eje_x)],
            ticktext=eje_x,
            visible=mostrar_eje_x
        ),
        yaxis=dict(
            visible=mostrar_eje_y
        ),
        paper_bgcolor=fondo_imagen,
        plot_bgcolor=fondo_grafica,
        legend=dict(title='',
                    orientation='h',
                    **posicion_leyenda),
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        yaxis_tickformat=tickformat,
        separators=',.',
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=0,
            y=-0.05,
            xanchor='left',
            yanchor='top',
            text=fuente,
            showarrow=False,
            font=dict(size=10, color="black")
        )],
        margin=margenes
    )

    if titulo_eje_y:
        fig.update_yaxes(title_text=",".join(nombres_medidas))

    fig.update_yaxes(showgrid=True, griddash="dash", gridcolor="grey")
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")
    if angulo_etq_x is None:
        fig.update_xaxes(showline=False)
    else:
        fig.update_xaxes(showline=True, tickangle=angulo_etq_x)

    # Ajustar el rango del eje secundario de y para centrar en el valor especificado
    max_value = float(np.nanmax([np.nanmax(sublista) for sublista in eje_y]))
    print(max_value)
    min_value = float(np.nanmin([np.nanmin(sublista) for sublista in eje_y]))
    print(min_value)
    max_range = np.nanmax([max_value - centrar_eje_y_en, centrar_eje_y_en - min_value])
    if centrar_eje_y_en is not None:
        fig.update_yaxes(range=[(centrar_eje_y_en - max_range) * escala_eje_y,
                                centrar_eje_y_en + max_range * escala_eje_y],
                         secondary_y=False)

    if inicio_eje_y is not None:
        fig.update_yaxes(range=[inicio_eje_y, centrar_eje_y_en + max_range * escala_eje_y])

    # Añadir una línea de referencia horizontal en el punto 0 del eje Y
    fig.add_hline(y=0, line_dash="solid", line_color="gray", line_width=0.75)

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_lineas_varias.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    # Guardar imagen o mostrar
    fig.write_image(nombre_archivo,
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )


# endregion

# region gráfica barras apiladas y líneas
def grafico_barras_apiladas_y_lineas(eje_x=['a', 'b', 'c', 'd'],
                                     mostrar_eje_x=True,
                                     grupo=['a', 'a', 'a', 'a', 'b', 'b', 'b', 'b', 'c', 'c', 'c', 'c'],
                                     eje_y_barras=[[1, 2, 3, 4]],  # Datos para las barras
                                     eje_y_lineas=[[5, 3, 4, 7], [6, 5, 3, 2]],  # Datos para las líneas
                                     lineas_a_eje_y_secundario=True,
                                     inicio_eje_y=0,
                                     mostrar_eje_y=True,
                                     escala_eje_y=1.1,
                                     centrar_eje_y_secundario_en=0,
                                     eje_y_secundario_empieza_en=None,
                                     titulo='Título gráfica combinada',
                                     subtitulo='unidad de medida 1 y Tasa de variación anual (escala derecha)',
                                     territorio="territorio",
                                     fuente='',
                                     colores_barras=['red', 'blue', 'green'],
                                     colores_lineas=['black', 'purple'],
                                     nombres_medidas_barras=['medida 1', 'medida 2', 'medida 3'],
                                     nombres_medidas_lineas=['medida A', 'medida B'],
                                     posicion_leyenda={'yanchor': 'top', 'y': 1.04, 'xanchor': 'left', 'x': 0.33},
                                     titulo_eje_y=False,
                                     fondo_imagen='white',
                                     fondo_grafica='white',
                                     formato_imagen='svg',
                                     escala_x=1.5,
                                     escala_y=1,
                                     margin_l=60,
                                     margin_r=0,
                                     margin_t=None,
                                     margin_b=None,
                                     nombre_archivo=None,
                                     tickformat='outside',
                                     zoom=480,
                                     mostrar_leyenda=True):

    if nombres_medidas_barras is None:
        nombres_medidas_barras = extraer_unicos_ordenados(grupo)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras apiladas
    for datos, color, nombre in zip(eje_y_barras, colores_barras, nombres_medidas_barras):
        fig.add_trace(
            go.Bar(x=eje_x, y=datos, name=nombre, marker_color=colores_barras[nombres_medidas_barras.index(nombre)]),
            secondary_y=False,
        )

    # Líneas en el eje y secundario
    for datos, color, nombre in zip(eje_y_lineas, colores_lineas, nombres_medidas_lineas):
        fig.add_trace(
            go.Scatter(x=eje_x, y=datos, name=nombre, mode='lines+markers', line=dict(color=color)),
            secondary_y=lineas_a_eje_y_secundario,
        )

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Configuraciones comunes
    fig.update_layout(
        barmode='stack',
        title={
            'text': f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
            'y': 0.95,
            'x': 0.05,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        xaxis=dict(
            tickmode='array',
            tickvals=[i for i, _ in enumerate(eje_x)],
            ticktext=eje_x,
            visible=mostrar_eje_x
        ),
        paper_bgcolor=fondo_imagen,
        plot_bgcolor=fondo_grafica,
        yaxis_visible=mostrar_eje_y,
        font=dict(family="Arial, sans-serif", size=14, color="black"),
        separators=',.',
        annotations=[dict(xref='paper', yref='paper', x=0, y=-0.05, xanchor='left', yanchor='top',
                          text=fuente, showarrow=False, font=dict(size=10, color="black"))],
        margin=margenes,
        yaxis_tickformat=tickformat
    )

    if mostrar_leyenda:
        fig.update_layout(legend=dict(title='', orientation='h', **posicion_leyenda))
    else:
        fig.update_layout(showlegend=False)

    if titulo_eje_y:
        fig.update_yaxes(title_text=",".join(nombres_medidas_barras), secondary_y=False)

    fig.update_yaxes(showgrid=True, griddash="dash", gridcolor="grey", secondary_y=False)
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside", secondary_y=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside", secondary_y=False)
    fig.update_xaxes(showline=True, linewidth=2, linecolor="grey", ticks="outside")

    # Ajustar el tamaño del eje y primario
    if escala_eje_y is not None:
        suma_eje_y = [sum(valores) for valores in zip(*eje_y_barras)]

        fig.update_yaxes(range=[inicio_eje_y, max(suma_eje_y) * escala_eje_y])

    # Ajustar el rango del eje y secundario
    if escala_eje_y is not None:
        fig.update_yaxes(
            range=[inicio_eje_y, int(np.nanmax([np.nanmax(sublista) for sublista in eje_y_lineas])) * escala_eje_y],
            secondary_y=True)

    # Ajustar el rango del eje secundario de y para centrar en el valor especificado
    max_value = int(np.nanmax([np.nanmax(sublista) for sublista in eje_y_lineas]))
    min_value = int(np.nanmin([np.nanmin(sublista) for sublista in eje_y_lineas]))
    max_range = np.nanmax([max_value - centrar_eje_y_secundario_en, centrar_eje_y_secundario_en - min_value])
    if centrar_eje_y_secundario_en is not None:
        fig.update_yaxes(range=[(centrar_eje_y_secundario_en - max_range) * escala_eje_y,
                                centrar_eje_y_secundario_en + max_range * escala_eje_y],
                         secondary_y=True)

    if eje_y_secundario_empieza_en is not None:
        fig.update_yaxes(range=[eje_y_secundario_empieza_en, max_value * escala_eje_y],
                         secondary_y=True)

    # Añadir una línea de referencia horizontal en el punto 0 del eje Y secundario
    # opciones para line_dash: solid, dot, dash, longdash, dashdot, longdashdot
    fig.add_hline(y=0, line_dash="solid", line_color="gray", line_width=0.75, secondary_y=True)

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_barras_apiladas_y_lineas.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    fig.write_image(nombre_archivo, scale=4, width=zoom * escala_x,
                    height=zoom * escala_y, engine='kaleido')

    # fig.show()


# endregion

# region gráfico de sectores
def grafico_sectores(eje_x=['a', 'b', 'c', 'd'],
                     eje_y=[1, 2, 3, 4],
                     titulo='Título gráfica prueba título',
                     subtitulo='Unidad de medida',
                     mostrar_subtitulo=True,
                     territorio="territorio",
                     fuente='',
                     color_primario=['red', 'pink', 'grey', 'orange'],
                     nombre_medida='medida 1',
                     titulo_eje_y=False,
                     fondo_imagen='white',
                     fondo_grafica='white',
                     formato_imagen='svg',
                     escala_x=1.5,
                     escala_y=1,
                     margin_l=60,
                     margin_r=60,
                     margin_t=None,
                     margin_b=None,
                     zoom=480,
                     nombre_archivo=None
                     ):
    fig = go.Figure(go.Pie(labels=eje_x, values=eje_y, pull=[0.05] * len(eje_x), marker_colors=color_primario))

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    if mostrar_subtitulo is True:
        fig.update_layout(
            title_text=f'<b>{dividir_titulo(titulo)}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
            title_x=0.05,
            title_y=0.95,
            paper_bgcolor=fondo_imagen,
            plot_bgcolor=fondo_grafica,
            font=dict(family="Arial, sans-serif", size=14, color="black"),
            annotations=[dict(xref='paper', yref='paper', x=0, y=-0.05, xanchor='left', yanchor='top',
                              text=fuente, showarrow=False, font=dict(size=10, color="black"))],
            margin=margenes
        )
    else:
        fig.update_layout(
            title_text=f'<b>{dividir_titulo(titulo, 70)}</b><br><span style="font-size: 13px;"></span>',
            title_x=0.05,
            title_y=0.95,
            paper_bgcolor=fondo_imagen,
            plot_bgcolor=fondo_grafica,
            font=dict(family="Arial, sans-serif", size=14, color="black"),
            annotations=[dict(xref='paper', yref='paper', x=0, y=-0.05, xanchor='left', yanchor='top',
                              text=fuente, showarrow=False, font=dict(size=10, color="black"))],
            margin=margenes
        )

    if nombre_archivo is None:
        nombre_archivo = f'imagenes/prueba/prueba_sectores.{formato_imagen}'
    else:
        nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'

    fig.write_image(nombre_archivo,
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )



    # fig.show()


# endregion

# region gráfico de línea sin ejes
def grafico_linea_simple(eje_x=['a', 'b', 'c', 'd'],
                         eje_y=[1, -2, 3, -4],
                         color_primario='red',
                         formato_imagen='svg',
                         escala_x=1.5,
                         escala_y=1,
                         margin_l=0,
                         margin_r=0,
                         margin_t=0,
                         margin_b=0,
                         zoom=480
                         ):
    fig = go.Figure()

    # Añade una única línea al gráfico
    fig.add_trace(
        go.Scatter(
            x=eje_x,
            y=eje_y,
            mode='lines',
            line_color=color_primario,
            line_width=4
        )
    )

    # márgenes de la gráfica
    margenes = {'l': margin_l,
                'r': margin_r,
                't': margin_t,
                'b': margin_b}

    margenes = {clave: valor for clave, valor in margenes.items() if valor is not None}

    # Elimina todos los ejes y títulos
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=margenes
    )

    fig.write_image(f'imagenes/prueba/prueba_linea_simple.{formato_imagen}',
                    scale=4,
                    width=zoom * escala_x,
                    height=zoom * escala_y,
                    engine='kaleido'
                    )

    # fig.show()


# endregion

# region probar funciones

grafico_barras()
# grafico_barra_lineas()
# grafico_barras_apiladas()
# grafico_barras_agrupadas()
# grafico_barras_colores_horizontal()
# grafico_barras_colores_vertical()
# grafico_lineas_doble_relleno()
# grafico_lineas_doble()
# grafico_varias_lineas()
# grafico_barras_apiladas_y_lineas()
# grafico_sectores()
# grafico_linea_simple()

# endregion

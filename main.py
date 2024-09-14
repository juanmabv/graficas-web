import requests
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


from io import StringIO

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
        'text': f'<b>{titulo}</b><br><span style="font-size: 13px;">({subtitulo}. {territorio})</span>',
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
    print("Gráfica generada")

    # if nombre_archivo is None:
    #     nombre_archivo = f'imagenes/prueba/prueba_barras.{formato_imagen}'
    # else:
    #     nombre_archivo = f'imagenes/{nombre_archivo}.{formato_imagen}'
    # fig.write_image(nombre_archivo,
    #                 scale=4,
    #                 width=zoom * escala_x,
    #                 height=zoom * escala_y,
    #                 engine='kaleido'
    #                 )
    # # fig.show()
    # print(f"Imagen guardada como {nombre_archivo}.{formato_imagen}")
    fig.write_html("afil_ss_canarias.html", include_plotlyjs='cdn')


if __name__ == "__main__":
    datos = pd.read_csv("afiliados_ss_canarias.csv", sep=";", encoding="utf-8")

    print(datos)

    grafico_barras(
        eje_x=datos['per'].astype(str),
        eje_y=datos['vd'],
        inicio_eje_y=50,
        titulo="Titulo",
        subtitulo="subtitulo",
        territorio=datos['ter'].tolist()[0],
        color_primario="red",
        escala_x=2.2,
        escala_y=1,
        mostrar_valores=False,
        nombre_archivo="afiliados_ss_canarias",
        formato_imagen="png",
    )

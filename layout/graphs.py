import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
import json
from lxml import etree

def Hogares_encuestados(df):
    geojson_data = json.loads(df.to_json())

    # Separar los datos en dos: válidos y NaN
    df_validos = df[df["value"].notna()]
    df_nan = df[df["value"].isna()]

    # Capa 1: datos válidos
    fig = px.choropleth_mapbox(
        df_validos,
        geojson=geojson_data,
        locations="NOMBRE_DPT",
        featureidkey="properties.NOMBRE_DPT",
        color="value", ###["#FCE3EC", "#F6A5BC", "#E75B84", "#D72266", "#BE0C4D"]
        color_continuous_scale=["#F2A6BF", "#F38CA9", "#E75B84", "#D72266", "#BE0C4D"],
        mapbox_style="carto-positron",
        center={"lat": 4, "lon": -72},
        zoom=4.35,
        opacity=1,
        labels={'color': 'Valores'},
        hover_name="NOMBRE_DPT",
        hover_data={"value": True, "NOMBRE_DPT": False}  # Muestra solo 'value'
    )

    fig.update_traces(
        hovertemplate="<b>%{location}</b><br>Hogares: %{z}<extra></extra>"
    )
    
    # Capa 2: datos con NaN (color fijo, ej: gris claro)
    fig.add_trace(go.Choroplethmapbox(
        geojson=geojson_data,
        locations=df_nan["NOMBRE_DPT"],
        z=[0]*len(df_nan),  # dummy z values
        featureidkey="properties.NOMBRE_DPT",
        colorscale=[[0, "lightgrey"], [1, "lightgrey"]],
        showscale=False,
        marker_line_width=0,
        name="",  # <-- Quita "trace 1"
        hovertemplate="<b>%{location}</b><br><br>Sin datos<extra></extra>"
    ))

    # Estilo del mapa y márgenes
    fig.update_traces(marker_line_width=0, marker_line_color="white")

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(
            x=0.85,       
            y=0.5,        
            len=0.9,      
            thickness=20, 
            bgcolor='rgba(255,255,255,0)',
            outlinewidth=1
        )
    )

    return fig

def clasificacion_hogares(df):

    conteo = df[["pobre", "directorio"]].groupby("pobre").count()["directorio"]

    fig = go.Figure(go.Pie(
        labels=conteo.index,
        values=conteo.values,
        hole=0.5,
        textinfo='percent',
        textposition='outside',
        hovertemplate="<b>%{label}</b><br>%{value} hogares<extra></extra>",
        insidetextorientation='radial',
        marker=dict(colors=["#9F9F9F", "#BE0C4D"]),
    ))

    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        legend=dict(
            orientation="h",       # Horizontal
            yanchor="bottom",
            y=-0.3,                # Just below the chart
            xanchor="center",
            x=0.5                  # Centered horizontally
        )
    )

    return fig


def icons(fig,valor):
    """
    Crea un SVG modificado de la imagen 'Mujer.svg' con un gradiente de color
    que cambia de opaco a transparente de abajo hacia arriba.
    """

    tree = etree.parse(f'assets/svg/{fig}.svg')
    root = tree.getroot()

    # Crear el gradiente con cambio brusco (de abajo hacia arriba)
    if fig in ["rural", "urbano"]:
        grad = etree.Element('linearGradient', id="fade", x1="0%", y1="0%", x2="100%", y2="0%")
    else:
        grad = etree.Element('linearGradient', id="fade", x1="0%", y1="100%", x2="0%", y2="0%")

    color = "#E691AA" if fig == "Mujer" else "#CD3E64" if fig == "Hombre" else "#000000"
    
    stop1 = etree.Element('stop', offset=f"{valor}%", style=f"stop-color: {color}; stop-opacity:1")  # Parte inferior completamente opaca
    stop2 = etree.Element('stop', offset=f"{valor + 1}%", style="stop-color: #E3E3E3; stop-opacity:1")
    stop3 = etree.Element('stop', offset="100%", style="stop-color: #E3E3E3; stop-opacity:1")  # Parte superior completamente transparente (cambio inmediato)
    grad.extend([stop1, stop2, stop3])

    # Añadir el gradiente a los <defs> del SVG
    defs = root.find('{http://www.w3.org/2000/svg}defs')
    if defs is None:
        defs = etree.SubElement(root, 'defs')
    defs.append(grad)

    # Buscar el <path> y el <text> y aplicar el gradiente
    for path in root.findall(".//{http://www.w3.org/2000/svg}path"):
        path.set('fill', 'url(#fade)')  # Aplicamos el gradiente al path

    # Modificar el texto dentro del <tspan>
    for tspan in root.findall(".//{http://www.w3.org/2000/svg}tspan"):
        if tspan.text == "100%":  # Si el texto original es "100%", lo reemplazamos
            tspan.text = f"{valor}%"  # Reemplaza con el texto que desees
            
    tree.write(f'assets/icons/{fig}_modificada.svg')

def grupo_etario(df):

    conteo = df["Grupo Etario"].value_counts() 

    fig = go.Figure(go.Pie(
            labels=conteo.index,
            values=conteo.values,
            textinfo='percent',
            hovertemplate="<b>%{label}</b><br>%{value} personas<extra></extra>",
            textfont=dict(color='white'),
            marker=dict(colors=["#808080","#9F9F9F", "#841442","#BE0C4D"]),
            rotation=120, 
        ))

    fig.update_layout(
            margin=dict(t=50, b=50, l=50, r=50)
        )

    return fig

def salario(df):

    # Obtener valores y etiquetas
    valores_absolutos = df["INGRESOS BRUTO"].value_counts()
    valores_porcentuales = df["INGRESOS BRUTO"].value_counts(normalize=True)

    etiquetas = valores_absolutos.index[::-1]
    valores = valores_porcentuales.values[::-1]
    totales = valores_absolutos.values[::-1]

    # Crear gráfico
    fig = go.Figure(go.Bar(
        y = etiquetas,
        x = valores,
        orientation='h',
        text = [f"{v:.1%}" for v in valores],  # Mostrar porcentaje en las barras
        textposition='auto',
        textfont=dict(color='white'),
        hovertemplate="<b>%{y}</b><br>%{customdata} personas<extra></extra>",
        customdata=totales.reshape(-1, 1),  # Pasamos el total como customdata
        marker=dict(color=["#808080","#9F9F9F", "#841442","#BE0C4D"]),
    ))

    fig.update_layout(
        xaxis_title="Porcentaje",
        yaxis_title="Rango de Ingreso",
        plot_bgcolor='white',    # Fondo del área del gráfico
        paper_bgcolor='white',   # Fondo del "papel"
        )

    return fig
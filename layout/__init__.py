from dash import html, dcc
from .header import header, seccion_hogares
from .graphs import Hogares_encuestados, clasificacion_hogares,icons
import pandas as pd
import geopandas as gpd

hogares = pd.read_parquet("database/Hogares.parquet")
mapa_dptos = gpd.read_file("database/DptosColombia.geo.json")
hogares["Departamentos"] = hogares["Departamentos"].replace({
    "BOGOTA": "SANTAFE DE BOGOTA D.C",
    "NORTE SANTANDER" : "NORTE DE SANTANDER",
    "VALLE" : "VALLE DEL CAUCA"
})

# Paso 1: conteo de personas por departamento
conteo = (
    hogares.groupby("Departamentos")["directorio"]
    .count()
    .sort_values(ascending=False)
    .rename("value")
    .reset_index()
)

# Paso 2: merge partiendo de mapa_dptos para preservar tipo GeoDataFrame
resultado = mapa_dptos.merge(
    conteo,
    how="left",
    left_on="NOMBRE_DPT",
    right_on="Departamentos"
)

rural = round((hogares.groupby("Zona")["directorio"].count()/len(hogares["directorio"].unique())).iloc[0] * 100,1)
urbano = round((hogares.groupby("Zona")["directorio"].count()/len(hogares["directorio"].unique())).iloc[1] * 100,1)

def crear_layout():
    return html.Div([
        ### Header
        header(),

        ### Contenedor de 2 columnas
        html.Div([
            ### Columna 1
            html.Div( 
                    ### Contenido
                    [seccion_hogares(hogares),
                     
                    html.Div([
                        ### Columna 1
                        html.Div([
                            html.P("Hogares encuestados por departamento",className="titulos"),
                            dcc.Graph(figure=Hogares_encuestados(resultado),id="Mapa")],className="columna-izquierda",style={"flex": 0.6}),

                        ### Columna 2
                        html.Div([html.P("Hogares encuestados",className="titulos"),
                                  html.P(f"{len(hogares.directorio.unique()):,}".replace(",", "."),className="textos"),
                                  
                                  html.P("Clasificación de hogares",className="titulos"),
                                  dcc.Graph(figure=clasificacion_hogares(hogares),id="clas_hog"),

                                  html.P("Division por zona rural y urbana",className="titulos"),
                                  html.Div([
                                    ### Columna 1
                                    icons("rural", rural),
                                    html.Div([html.Img(src="assets/icons/rural_modificada.svg", style={"width": "100%"})],className="columna-izquierda",style={"flex" : 0.5,"margin-left" : "5%","margin-top" : "1%"}),

                                    ### Columna 2
                                    icons("urbano", urbano),
                                    html.Div([html.Img(src="assets/icons/urbano_modificada.svg", style={"width": "100%"})],className="columna-derecha",style={"flex" : 0.5,"margin-top" : "9%"})
                            ], className="contenedor-columnas", style= {"padding" : 0,"gap": "3%"})],className="columna-derecha",style={"flex": 0.4}) 
                        ], className="contenedor-columnas", style= {"padding" : 0, "margin-top" : "2%","gap": "3%"})], 
                    className="columna-izquierda"
                    ),

            ### Columna 2
            html.Div( 
                    ### Contenido
                    [html.P("Contenido de la columna derecha")],
                    className="columna-derecha"
                    )
        ], className="contenedor-columnas")
    ])



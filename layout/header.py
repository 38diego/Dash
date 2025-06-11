from dash import html, dcc

def header():
    return html.Div([
        html.H1("POBREZA MONETARIA Y DESIGUALDAD 2023", id="titulo-principal")
    ], id="encabezado-principal")

def seccion_hogares(df):
    return html.Div(
        [
            html.H1("Hogares", id = "titulo-hogares"),
            dcc.Dropdown(
                options=df["Departamentos"].unique(),
                id="dropdown"
            )
        ],
        id="container-hogares"
    )



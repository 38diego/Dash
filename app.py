from dash import Dash
from layout import crear_layout

# Crear la app
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Esto permite desplegarla en Heroku o Render

# Asignar el layout principal
app.layout = crear_layout()

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Cargar los datos
file_path = 'LLamados2024.csv'
data = pd.read_csv(file_path, sep=';')

# Agrupar los datos por la columna "dadopor" y contar la cantidad de atenciones
grouped_df = data.groupby('dadopor').size().reset_index(name='cantidad_atenciones')

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Layout del Dashboard
app.layout = html.Div([
    html.H1("Administrativos v/s Cantidad de pacientes contactados", style={'textAlign': 'center'}),
    
    # Dropdown para seleccionar nombre
    html.Label("Seleccionar un nombre:"),
    dcc.Dropdown(
        id='nombre-dropdown',
        options=[{'label': nombre, 'value': nombre} for nombre in grouped_df['dadopor'].unique()],
        placeholder="Seleccione un nombre",
        clearable=True
    ),
    
    # Dropdown para seleccionar categoría de cantidad de atenciones
    html.Label("Seleccionar una categoría de cantidad de atenciones:"),
    dcc.Dropdown(
        id='cantidad-dropdown',
        options=[
            {'label': 'Entre 0 a 4000', 'value': '0-4000'},
            {'label': 'Entre 4001 a 8000', 'value': '4001-8000'},
            {'label': 'Entre 8001 en adelante', 'value': '8001+'}
        ],
        placeholder="Seleccione una categoría",
        clearable=True
    ),
    
    # Gráfica
    dcc.Graph(id='bar-chart')
])

# Callback para actualizar el gráfico
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('nombre-dropdown', 'value'),
     Input('cantidad-dropdown', 'value')]
)
def update_chart(nombre_seleccionado, cantidad_seleccionada):
    df_filtrado = grouped_df
    
    if nombre_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['dadopor'] == nombre_seleccionado]
    
    if cantidad_seleccionada:
        if cantidad_seleccionada == '0-4000':
            df_filtrado = df_filtrado[df_filtrado['cantidad_atenciones'] <= 4000]
        elif cantidad_seleccionada == '4001-8000':
            df_filtrado = df_filtrado[(df_filtrado['cantidad_atenciones'] > 4000) & (df_filtrado['cantidad_atenciones'] <= 8000)]
        elif cantidad_seleccionada == '8001+':
            df_filtrado = df_filtrado[df_filtrado['cantidad_atenciones'] > 8000]
    
    df_filtrado = df_filtrado.sort_values(by='cantidad_atenciones')
    
    fig = px.bar(
        df_filtrado,
        x='dadopor',
        y='cantidad_atenciones',
        title='Cantidad Total de Atenciones por Dadopor'
    )
    
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
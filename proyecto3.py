import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Cargar los datos
file_path = 'LLamados2024.csv'
data = pd.read_csv(file_path, sep=';')

# Crear columna 'mes' desde la columna 'fecha'
data['mes'] = pd.to_datetime(data['fecha'], format='%d-%m-%Y', errors='coerce').dt.month_name()

# Filtrar las filas con estado "anulada" y agregar una columna de conteo
data['horas_anuladas'] = (data['estado'] == 'anulada').astype(int)

# Agrupar los datos por la columna "dadopor" y contar la cantidad de atenciones
grouped_df = data.groupby('dadopor').size().reset_index(name='cantidad_atenciones')

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Layout del Dashboard
app.layout = html.Div([
    html.H1("Dashboard de Contactos y Anulaciones", style={'textAlign': 'center'}),
    
    # Sección: Administrativos v/s Pacientes Contactados
    html.Div([
        html.H2("Administrativos v/s Cantidad de Pacientes Contactados"),
        html.Label("Seleccionar un nombre:"),
        dcc.Dropdown(
            id='nombre-dropdown',
            options=[{'label': nombre, 'value': nombre} for nombre in grouped_df['dadopor'].unique()],
            placeholder="Seleccione un nombre",
            clearable=True
        ),
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
        dcc.Graph(id='bar-chart'),
    ], style={'marginBottom': '50px'}),

    # Sección: Médicos v/s Horas Anuladas
    html.Div([
        html.H2("Médicos v/s Horas Anuladas"),
        html.Label("Seleccionar un médico:"),
        dcc.Dropdown(
            id='medico-dropdown',
            options=[
                {'label': 'Todos', 'value': 'todos'}
            ] + [{'label': medico, 'value': medico} for medico in data['Medico'].unique()],
            placeholder="Seleccione un médico",
            clearable=True
        ),
        html.Label("Seleccionar dado por:"),
        dcc.Dropdown(
            id='dadopor-dropdown',
            options=[{'label': tipo, 'value': tipo} for tipo in data['dadopor'].unique()],
            placeholder="Seleccione el tipo de personal",
            clearable=True
        ),
        html.Label("Seleccionar mes:"),
        dcc.Dropdown(
            id='mes-dropdown',
            options=[{'label': mes, 'value': mes} for mes in data['mes'].dropna().unique()],
            placeholder="Seleccione un mes",
            clearable=True
        ),
        dcc.Graph(id='medicos-bar-chart'),
    ]),
])

# Callback para actualizar el gráfico Administrativos v/s Pacientes
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
    
    fig = px.bar(
        df_filtrado,
        x='dadopor',
        y='cantidad_atenciones',
        title='Cantidad Total de Atenciones por Dadopor'
    )
    return fig

# Callback para actualizar el gráfico Médicos v/s Horas Anuladas
@app.callback(
    Output('medicos-bar-chart', 'figure'),
    [Input('medico-dropdown', 'value'),
     Input('dadopor-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def update_medicos_chart(medico_seleccionado, dado_por_seleccionado, mes_seleccionado):
    df_filtrado = data
    
    if medico_seleccionado and medico_seleccionado != 'todos':
        df_filtrado = df_filtrado[df_filtrado['Medico'] == medico_seleccionado]
    
    if dado_por_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['dadopor'] == dado_por_seleccionado]
    
    if mes_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes_seleccionado]
    
    df_resumen = df_filtrado.groupby('Medico')['horas_anuladas'].mean().reset_index()
    df_resumen = df_resumen.sort_values(by='horas_anuladas')
    
    fig = px.bar(
        df_resumen,
        x='Medico',
        y='horas_anuladas',
        title='Promedio de Horas Anuladas por Médico',
        labels={'Medico': 'Médico', 'horas_anuladas': 'Promedio de Horas Anuladas'}
    )
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)

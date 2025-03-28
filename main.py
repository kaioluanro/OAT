import pandas as pd
import time
from datetime import datetime
import asyncio
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

#==============

timeframe=0.5

app = Dash(__name__)
#df=constructor_ohlc(get_data_exchange(limit=400,timeframe=1,exchange='bitget'))
# Layout da aplicação
app.layout = html.Div([
    dcc.Graph(id='live-graph',
              style={
            'width': '99%',  # Largura do gráfico (80% da largura do contêiner)
            'height': '80vh',  # Altura do gráfico (500 pixels)
            'margin': 'auto',  # Centraliza o gráfico horizontalmente
            'border': '1px solid #ddd',  # Adiciona uma borda ao gráfico
            'borderRadius': '10px',  # Borda arredondada
            'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)',  # Sombra ao redor do gráfico
            'background':'#00000'
        }),  # Gráfico Plotly
    dcc.Interval(
        id='interval-component',
        interval=(60 * 300)*timeframe,  # Atualizar a cada 1 minuto (em milissegundos)
        n_intervals=0  # Contador de intervalos
    )
])

# Callback para atualizar o gráfico
@app.callback(
    Output('live-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def atualizar_grafico(n):

    df=pd.read_csv('test_sinais.csv')
    
    # Criar o gráfico de candlestick
    fig = go.Figure()
    
    # Adicionar candlesticks
    fig.add_trace(go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlestick',
        increasing_line_color= "#ffffff", decreasing_line_color= "#4f4b48"
    ))

    # Adicionar a SMA 8
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['sma1'],
        mode='lines',
        name=f'SMA 8',
        line=dict(color='orange', width=1)
    ))
    
    # Adicionar a SMA 20
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['sma2'],
        mode='lines',
        name=f'SMA 20',
        line=dict(color='blue', width=2)
    ))
    
    # Adicionar a SMA 40
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['sma3'],
        mode='lines',
        name=f'SMA 40',
        line=dict(color='purple', width=2)
    ))
    
    # Adicionar a SMA 200
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['sma4'],
        mode='lines',
        name=f'SMA 200',
        line=dict(color='white', width=3)
    ))
    
    #Bar Volume
    #fig.add_trace(go.Bar(x=df['time'], y=df['volume']))
    
    # Adiciona o Trem da 8:20 indicador
    fig.add_trace(go.Scatter(x=df['time'],y=df['compra_price'], mode='markers', marker_color='rgba(212, 255, 0, 1)'))
    fig.add_trace(go.Scatter(x=df['time'],y=df['venda_price'], mode='markers', marker_color='rgba(255, 0, 123, 1)'))
    
    # Adiciona o Elephant indicador
    fig.add_trace(go.Scatter(x=df['time'],y=df['compra_price_elephant'], mode='markers', marker_color='#2ae5b2'))
    fig.add_trace(go.Scatter(x=df['time'],y=df['venda_price_elephant'], mode='markers', marker_color='#ac0fe0'))
    
    
    # Configurações do layout
    fig.update_layout(
        title={
        'text': 'Gráfico Personalizado',
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': '#d50421'}  # Título vermelho
        },
        plot_bgcolor='#000000',  # Fundo do gráfico preto
        paper_bgcolor='#000000',  # Fundo externo preto
        xaxis={
        'title': 'Data',
        'title_font': {'color': '#d50421'},  # Título do eixo X vermelho
        'tickfont': {'color': '#d50421'},  # Rótulos do eixo X vermelhos
        'showgrid': False,  # Desativa as grades do eixo X
        'linecolor': '#4f4b48'  # Linha do eixo cinza
        },
        yaxis={
            'title': 'Preço',
            'title_font': {'color': '#d50421'},  # Título do eixo Y vermelho
            'tickfont': {'color': '#d50421'},  # Rótulos do eixo Y vermelhos
            'showgrid': False,  # Desativa as grades do eixo Y
            'linecolor': '#4f4b48'  # Linha do eixo cinza
        }
    )

    return fig
    
app.run(debug=True)


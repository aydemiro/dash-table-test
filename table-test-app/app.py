from dash import Dash, dcc, html, dash_table

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive CSV Explorer"),

    # 1. File Upload Component
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select CSV File')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),

    # 2. Results Container for the Interactive Table
    html.Div(id='output-data-upload'),
])

if __name__ == '__main__':
    app.run_server(debug=True)

import numpy as np
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

mydata = "Rhona_data.csv"
df = pd.read_csv(mydata,index_col=False)
# Calculate mean scores by ethnicity and rank the top five attributes
df.drop(['id', 'Age Category'], axis=1, inplace=True)

app = dash.Dash(__name__)
server = app.server

# External stylesheet for Google Fonts
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap',
        'rel': 'stylesheet'
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={'fontFamily': 'Roboto, sans-serif', 'marginTop': '20px'}, children=[
    html.H1("Top Factors that Minorities Look for in Employment (data simulated)", style={'textAlign': 'center', 'color': '#034f84'}),
    html.Br(),
    html.Br(),
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around'}, children=[
        html.Div([
            html.Label("Select Ethnicity:", style={'color': '#034f84'}),
            dcc.Dropdown(
                id='ethnicity-dropdown',
                options=[{'label': eth, 'value': eth} for eth in df['Ethnicity'].unique()] + [{'label': 'All', 'value': 'All'}],
                value='All',
                style={'width': '300px'}  # Widen the dropdown
            ),
        ]),
        html.Div([
            html.Label("Select Gender:", style={'color': '#034f84'}),
            dcc.Dropdown(
                id='gender-dropdown',
                options=[{'label': gender, 'value': gender} for gender in df['Gender'].unique()] + [{'label': 'All', 'value': 'All'}],
                value='All',
                style={'width': '200px'}  # Widen the dropdown
            ),
        ]),
    ]),
    html.Br(),
    html.Div(style={'width': '90%', 'margin': '0 auto'}, children=[
        html.Label("Select Age Range:", style={'color': '#034f84'}),
        html.Div([
            dcc.RangeSlider(
                id='age-slider',
                min=df['Age'].min(),
                max=df['Age'].max(),
                step=1,
                marks={i: str(i) for i in range(df['Age'].min(), df['Age'].max()+1, 5)},
                value=[df['Age'].min(), df['Age'].max()]
            ),
        ], style={'width': '80%'}),  # Make the range slider more narrow
        html.Div(id='age-range-output', style={'marginTop': '10px', 'color': '#034f84'})
    ]),
    html.Br(),
    html.Br(),
    html.Div(id='top-five-list', style={'marginTop': '20px'})
])

def get_top_five_attributes_by_filters(df, ethnicity, age_range, gender):
    filtered_df = df.copy()
    
    if ethnicity != 'All':
        filtered_df = filtered_df[filtered_df['Ethnicity'] == ethnicity]
    if gender != 'All':
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    
    filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]
    
    mean_scores = filtered_df.drop(columns=['Age']).mean(numeric_only=True)
    # Rescale the scores
    max_score = mean_scores.max()
    mean_scores = mean_scores * (100 / max_score)
    top_five_df = mean_scores.sort_values(ascending=False).head(5)
    return top_five_df.reset_index().rename(columns={'index': 'Attribute', 0: 'Score'})

@app.callback(
    Output('top-five-list', 'children'),
    [
        Input('ethnicity-dropdown', 'value'),
        Input('age-slider', 'value'),
        Input('gender-dropdown', 'value')
    ]
)
def update_top_five_list(selected_ethnicity, selected_age_range, selected_gender):
    top_five_df = get_top_five_attributes_by_filters(df, selected_ethnicity, selected_age_range, selected_gender)
    top_five_list = [html.H3(f"Top Five Attributes for {selected_gender} aged {selected_age_range[0]}-{selected_age_range[1]} {selected_ethnicity}", style={'color': '#034f84'})]
    for i, row in top_five_df.iterrows():
        top_five_list.append(html.P(f"{i+1}. {row['Attribute']}: {row['Score']:.1f}", style={'color': '#034f84'}))

    return top_five_list

@app.callback(
    Output('age-range-output', 'children'),
    [Input('age-slider', 'value')]
)
def display_age_range(selected_age_range):
    return f"Selected Age Range: {selected_age_range[0]} - {selected_age_range[1]}"


if __name__ == '__main__':
    app.run_server(port=8051, debug=True)

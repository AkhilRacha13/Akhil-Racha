import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px

# Read data into a DataFrame
df = pd.read_csv("Python Exercise Data.csv")

# Parse dates in the DataFrame
df["Start"] = pd.to_datetime(df["Start Time"])
df["End"] = pd.to_datetime(df["End Time"])

# Create a Dash app instance
app = dash.Dash(__name__)

# Define color mapping for states
state_colors = {"Stopped": "orangered", "Idle": "blue", "Working": "green"}

# Define the layout of your Dash app
app.layout = html.Div([
    html.Div([
        html.Div([  # Sidebar for filters
            dcc.Dropdown(
                id='machine-dropdown',
                options=[
                    {'label': machine_id, 'value': machine_id}
                    for machine_id in df['MachineID'].unique()
                ],
                value=list(df['MachineID'].unique()),  # Set default to all MachineIDs
                multi=True  # Allow multiple selections
            ),
            dcc.Dropdown(
                id='state-dropdown',
                options=[
                    {'label': state, 'value': state}
                    for state in df['State'].unique()
                ],
                value=list(df['State'].unique()),  # Set default to all States
                multi=True  # Allow multiple selections
            ),
        ], className='sidebar'),  # Add a CSS class to style the sidebar
    ], style={'position': 'fixed', 'width': '20%', 'height': '100%', 'overflow': 'scroll'}),  # Fix sidebar position

    html.Div([  # Place all the charts in the same div
        html.H1("Machine State Visualization"),
        dcc.Graph(id='state-pie-chart'),
        dcc.Graph(id='state-timeline'),
        dcc.Graph(id='state-bar-chart'),
        dcc.Graph(id='state-line-chart')
    ], style={'margin-left': '25%', 'margin-top': '20px'}),  # Adjust margin to align with filters

])

# Define callbacks to update graphs based on user interactions
@app.callback(
    Output('state-pie-chart', 'figure'),
    [Input('machine-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_pie_chart(selected_machines, selected_states):
    filtered_df = df[(df['MachineID'].isin(selected_machines)) & (df['State'].isin(selected_states))]
    state_counts = filtered_df['State'].value_counts()
    # Define custom colors for the pie chart
    custom_colors = {
        'Stopped': 'orangered',
        'Idle': 'blue',
        'Working': 'green'
    }

    fig = go.Figure(data=[go.Pie(
        labels=state_counts.index,
        values=state_counts.values,
        marker=dict(colors=[custom_colors[state] for state in state_counts.index])
    )])
    
    fig.update_layout(title_text=f'State Distribution for Machines ({", ".join(selected_machines)})')
    return fig   

@app.callback(
    Output('state-timeline', 'figure'),
    [Input('machine-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_timeline(selected_machines, selected_states):
    filtered_df = df[(df['MachineID'].isin(selected_machines)) & (df['State'].isin(selected_states))]

    # Create a timeline chart using Plotly Express
    timeline_fig = px.timeline(
        filtered_df,
        x_start=filtered_df["Start"],
        x_end=filtered_df["End"],
        y="MachineID",
        color="State",
        title="Machine Activity Timeline",
        color_discrete_map=state_colors  # Use color mapping
    )

    # Customize the appearance
    timeline_fig.update_yaxes(autorange="reversed")  # Reverse the order of MachineIDs
    timeline_fig.update_yaxes(fixedrange=True)  # Lock/disable the vertical zoom
    timeline_fig.update_xaxes(
        rangemode="tozero", showspikes=True, spikethickness=1, spikesnap="cursor", showline=True, showgrid=False
    )
    timeline_fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=True, thickness=0.05, bgcolor="lightgray"))
    )

    # Update the x-axis range to show the end timeline by default
    timeline_fig.update_layout(
        xaxis=dict(
            range=[filtered_df["End"].max() - pd.Timedelta(hours=1), filtered_df["End"].max()]
        )
    )

    return timeline_fig

@app.callback(
    Output('state-bar-chart', 'figure'),
    [Input('machine-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_bar_chart(selected_machines, selected_states):
    filtered_df = df[(df['MachineID'].isin(selected_machines)) & (df['State'].isin(selected_states))]
    filtered_df["Duration"] = (filtered_df["End"] - filtered_df["Start"]).dt.total_seconds() / 3600  # Duration in hours

    # Create a bar plot using Plotly Express
    bar_fig = px.bar(
        filtered_df,
        x="MachineID",
        y="Duration",
        color="State",
        title="Machine State Duration",
        color_discrete_map=state_colors  # Use color mapping
    )

    # Customize the appearance
    bar_fig.update_yaxes(title="Duration (Hours)")
    bar_fig.update_xaxes(title="Machine ID")
    bar_fig.update_layout(legend_title="State")

    return bar_fig

@app.callback(
    Output('state-line-chart', 'figure'),
    [Input('machine-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_line_chart(selected_machines, selected_states):
    filtered_df = df[(df['MachineID'].isin(selected_machines)) & (df['State'].isin(selected_states))]
    filtered_df["Duration"] = (filtered_df["End"] - filtered_df["Start"]).dt.total_seconds() / 3600  # Duration in hours

    # Create a line chart to show a trend
    line_fig = px.line(
        filtered_df,
        x='Start',
        y='Duration',
        color='State',
        title='Duration Trend Over Time',
        line_shape='linear',
        color_discrete_map=state_colors  # Use color mapping
    )

    # Customize the appearance
    line_fig.update_yaxes(title='Duration (Hours)')
    line_fig.update_xaxes(title='Time')

    return line_fig

if __name__ == '__main__':
    app.run_server(debug=True)
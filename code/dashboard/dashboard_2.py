import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pymongo
import pandas as pd
import plotly.express as px

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["smarthome"]
collection = db["iot"]

# Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(
    style={"backgroundColor": "#f0f8ff", "padding": "20px"},  # Light background
    children=[
        html.H1(
            "CPC 357 Assignment 2: Smart Indoor Air Quality Monitoring",
            style={"textAlign": "center", "color": "#333"},  # Center title
        ),
      
        # Date range picker
        html.Div(
            style={"textAlign": "center", "marginBottom": "20px"},
            children=[
                html.Label(
                    "Select Date Range:",
                    style={"display": "block", "marginBottom": "8px", "fontSize": "16px"},
                ),
                dcc.DatePickerRange(
                    id="date-picker",
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    style={"width": "auto", "padding": "5px", "fontSize": "14px"},
                ),
            ],
        ),
      
        # Dropdown to select sensors
        html.Div(
            style={"textAlign": "center", "marginBottom": "20px"},
            children=[
                html.Label(
                    "Select Sensors:",
                    style={"display": "block", "marginBottom": "8px", "fontSize": "16px"},
                ),
                dcc.Dropdown(
                    id="sensor-dropdown",
                    options=[
                        {"label": "Temperature", "value": "temperature"},
                        {"label": "Humidity", "value": "humidity"},
                        {"label": "Gas", "value": "gas"},
                    ],
                    value=["temperature", "humidity", "gas"],  # Default selected
                    multi=True,
                    placeholder="Select sensors to display",
                ),
            ],
        ),
      
        # Chart type toggle
        html.Div(
            style={"textAlign": "center", "marginBottom": "20px"},
            children=[
                html.Label(
                    "Select Chart Type:",
                    style={"display": "block", "marginBottom": "8px", "fontSize": "16px"},
                ),
                dcc.RadioItems(
                    id="chart-type",
                    options=[
                        {"label": "Line Chart", "value": "line"},
                        {"label": "Bar Chart", "value": "bar"},
                    ],
                    value="line",
                    labelStyle={"margin-right": "10px"},
                ),
            ],
        ),
      
        dcc.Interval(id="interval", interval=300000, n_intervals=0),  # Auto-refresh every 5 minutes
        dcc.Graph(id="live-graph"),
      
        # Footer for names
        html.Footer(
            style={"textAlign": "left", "marginTop": "40px", "fontSize": "14px", "color": "#666"},
            children=[
                html.P("Developed by:"),
                html.P("1. Nurul Najwa binti Mat Aris"),
                html.P("2. Nur Iffah Izzah binti Noor Hasim"),
            ],
        ),
    ],
)

@app.callback(
    Output("live-graph", "figure"),
    [
        Input("interval", "n_intervals"),
        Input("sensor-dropdown", "value"),
        Input("chart-type", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)

def update_graph(n_intervals, selected_sensors, chart_type, start_date, end_date):
  
    # Fetch the latest data from MongoDB
    query = {}
    if start_date and end_date:
        query["timestamp"] = {"$gte": start_date, "$lte": end_date}
    cursor = collection.find(query).sort("timestamp", -1).limit(50)  # Get the last 50 entries
    data = list(cursor)

    if data and selected_sensors:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])  # Convert timestamp to datetime
        df = pd.concat(
            [df.drop(["data"], axis=1), df["data"].apply(eval)]
        )  # Flatten 'data' field

        # Define the figure based on selected chart type
        if chart_type == "line":
            fig = px.line(
                df,
                x="timestamp",
                y=selected_sensors,
                labels={"value": "Sensor Value", "timestamp": "Time"},
                title="Real-time Sensor Data",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
        elif chart_type == "bar":
            fig = px.bar(
                df,
                x="timestamp",
                y=selected_sensors,
                barmode="group",
                labels={"value": "Sensor Value", "timestamp": "Time"},
                title="Real-time Sensor Data",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )

        fig.update_layout(
            title={"x": 0.5},  # Center the graph title
            xaxis_title="Time",  # X-axis title
            yaxis_title="Sensor Value",  # Y-axis title
            hovermode="x unified",  # Unified hover tooltip
            legend_title="Sensors",  # Legend title
        )

    else:
        fig = px.line(title="No Data Available")
        fig.update_layout(
            title={"x": 0.5},  # Center the title for consistency
        )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)

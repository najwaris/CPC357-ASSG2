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
        html.P(
            [
                "Developed by:",
                html.Br(),
                "1. Nurul Najwa binti Mat Aris",
                html.Br(),
                "2. Nur Iffah Izzah binti Noor Hasim",
            ],
            style={"textAlign": "center", "fontSize": "18px", "color": "#666"},
        ),
        
        # Dropdown to select sensors
        html.Div(
            style={"textAlign": "center", "marginBottom": "20px"},
            children=[
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
                )
            ],
        ),
        
        dcc.Interval(id="interval", interval=300000, n_intervals=0),  # Auto-refresh every 5 minutes
        dcc.Graph(id="live-graph"),
    ],
)

@app.callback(
    Output("live-graph", "figure"),
    [Input("interval", "n_intervals"), Input("sensor-dropdown", "value")],
)

def update_graph(n_intervals, selected_sensors):
    
    # Fetch the latest data from MongoDB
    cursor = collection.find().sort("timestamp", -1).limit(50)  # Get the last 50 entries
    data = list(cursor)

    if data and selected_sensors:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])  # Convert timestamp to datetime
        df = pd.concat(
            [df.drop(["data"], axis=1), df["data"].apply(eval)]
        )  # Flatten 'data' field

        # Define figure with selected sensors
        fig = px.line(
            df,
            x="timestamp",
            y=selected_sensors,
            labels={"value": "Sensor Value", "timestamp": "Time"},
            title="Real-time Sensor Data",
            color_discrete_sequence=px.colors.qualitative.Set2,  # Custom color palette
        )

        # Add annotations for max values of each selected sensor
        for sensor in selected_sensors:
            max_value = df[sensor].max()
            max_time = df.loc[df[sensor].idxmax(), "timestamp"]
            fig.add_annotation(
                x=max_time,
                y=max_value,
                text=f"Max {sensor.capitalize()}: {max_value:.2f}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
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

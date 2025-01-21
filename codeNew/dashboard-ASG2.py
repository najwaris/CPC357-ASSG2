import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pymongo
import pandas as pd
import plotly.express as px
from dash import dash_table

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["smarthome"]
collection = db["iot"]

# Dash app
app = dash.Dash(__name__)

# App layout
# Dash app layout
app.layout = html.Div(
    style={"backgroundColor": "#939be1", "padding": "20px"},  # Light background
    children=[
        html.H1(
            "CPC 357 Assignment 2: Smart Indoor Air Quality Monitoring",
            style={"textAlign": "center", "color": "#333"},  # Center title
        ),
        dcc.Interval(id="interval", interval=300000, n_intervals=0),  # Auto-refresh every 5 minutes
        dcc.Graph(id="dht11-graph"),
        
        # DHT11 Table with Background
        html.Div(
            style={
                "backgroundColor": "#ffffff",  # White background
                "padding": "15px",  # Padding inside the div
                "borderRadius": "10px",  # Rounded corners
                "marginTop": "20px",  # Space above the div
                "marginBottom": "20px",  # Space below the div
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",  # Subtle shadow for aesthetic
            },
            children=[
                html.H3(
                    "DHT11 Sensor Data (Temperature and Humidity)",
                    style={
                        "textAlign": "center", 
                        "color": "#333", 
                        "marginBottom": "10px"  # Reduced space between title and table
                    },
                ),
                dash_table.DataTable(
                    id="dht11-table",
                    style_table={
                        'height': '300px', 
                        'overflowY': 'auto',
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'whiteSpace': 'normal',
                    },
                ),
            ],
        ),
        
        dcc.Graph(id="mq2-graph"),
        
        # MQ2 Table with Background
        html.Div(
            style={
                "backgroundColor": "#ffffff",  # White background
                "padding": "15px",  # Padding inside the div
                "borderRadius": "10px",  # Rounded corners
                "marginTop": "20px",  # Space above the div
                "marginBottom": "20px",  # Space below the div
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",  # Subtle shadow for aesthetic
            },
            children=[
                html.H3(
                    "MQ2 Sensor Data (Gas)",
                    style={
                        "textAlign": "center", 
                        "color": "#333", 
                        "marginBottom": "10px"  # Reduced space between title and table
                    },
                ),
                dash_table.DataTable(
                    id="mq2-table",
                    style_table={
                        'height': '300px', 
                        'overflowY': 'auto',
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'whiteSpace': 'normal',
                    },
                ),
            ],
        ),
        
        # Footer for names
        html.Footer(
            html.Div(
                style={"textAlign": "left", "marginTop": "40px", "fontSize": "14px", "color": "#333"},
                children=[
                    html.H4("Developed by:"),
                    html.P("1. Nurul Najwa binti Mat Aris - 158560"),
                    html.P("2. Nur Iffah Izzah binti Noor Hasim - 157150"),
                ],
            ),
        ),
    ],
)

@app.callback(
    [Output("dht11-graph", "figure"), Output("mq2-graph", "figure"), Output("dht11-table", "data"), Output("mq2-table", "data")],
    [
        Input("interval", "n_intervals"),
    ],
)
def update_graph(n_intervals):
    # Fetch the latest data from MongoDB
    query = {}
    cursor = collection.find(query).sort("timestamp", -1).limit(50)  # Get the last 50 entries
    data = list(cursor)

    if data:
        df = pd.DataFrame(data)
        # Ensure the timestamp is properly extracted and converted to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])  # Convert timestamp to datetime
        
        # Flatten 'data' field and ensure correct column names
        df = pd.concat([df.drop(["data"], axis=1), df["data"].apply(eval).apply(pd.Series)], axis=1)
        
        # Create separate graphs for DHT11 and MQ2
        dht11_data = df[["timestamp", "Humidity", "Temperature"]]  # DHT11 data
        mq2_data = df[["timestamp", "Gas"]]  # MQ2 data

        # Plot DHT11 data
        dht11_fig = px.line(
            dht11_data,
            x="timestamp",
            y=["Humidity", "Temperature"],  # Select temperature and humidity for graph
            labels={"value": "Sensor Value", "timestamp": "Time"},
            title="DHT11 Data (Temperature and Humidity)",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )

        # Plot MQ2 data
        mq2_fig = px.line(
            mq2_data,
            x="timestamp",
            y="Gas",
            labels={"value": "Sensor Value", "timestamp": "Time"},
            title="MQ2 Data (Gas)",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )

        # Update layout for both graphs
        dht11_fig.update_layout(
            title={"x": 0.5},  # Center the graph title
            xaxis_title="Time",  # X-axis title
            yaxis_title="Sensor Value",  # Y-axis title
            hovermode="x unified",  # Unified hover tooltip
            legend_title="Sensors",  # Legend title
        )

        mq2_fig.update_layout(
            title={"x": 0.5},  # Center the graph title
            xaxis_title="Time",  # X-axis title
            yaxis_title="Sensor Value",  # Y-axis title
            hovermode="x unified",  # Unified hover tooltip
            legend_title="Sensors",  # Legend title
        )

        # Calculate the total number of data points
        humidity_count = dht11_data["Humidity"].count()
        temperature_count = dht11_data["Temperature"].count()
        gas_count = mq2_data["Gas"].count()

        # Prepare table data for DHT11 and MQ2
        dht11_table_data = dht11_data.to_dict("records")
        mq2_table_data = mq2_data.to_dict("records")

        # Add total data counts to the table as the last row
        dht11_table_data.append(
            {"timestamp": "Total Data:", "Humidity": f"{humidity_count} data", "Temperature": f"{temperature_count} data"}
        )
        mq2_table_data.append(
            {"timestamp": "Total Data:", "Gas": f"{gas_count} data"}
        )

    else:
        dht11_fig = px.line(title="No DHT11 Data Available")
        mq2_fig = px.line(title="No MQ2 Data Available")
        dht11_table_data = [{"timestamp": "Total Data:", "Humidity": "0 data", "Temperature": "0 data"}]
        mq2_table_data = [{"timestamp": "Total Data:", "Gas": "0 data"}]

    return dht11_fig, mq2_fig, dht11_table_data, mq2_table_data


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)

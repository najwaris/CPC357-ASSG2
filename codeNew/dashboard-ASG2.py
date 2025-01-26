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
                    style={"textAlign": "center", "color": "#333", "marginBottom": "10px"},
                ),
                dash_table.DataTable(
                    id="dht11-table",
                    style_table={'height': '300px', 'overflowY': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px', 'whiteSpace': 'normal'},
                ),
            ],
        ),
        
        dcc.Graph(id="mq2-graph"),
        
        # MQ2 Table with Background
        html.Div(
            style={
                "backgroundColor": "#ffffff",
                "padding": "15px",
                "borderRadius": "10px",
                "marginTop": "20px",
                "marginBottom": "20px",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
            },
            children=[
                html.H3(
                    "MQ2 Sensor Data (Gas)",
                    style={"textAlign": "center", "color": "#333", "marginBottom": "10px"},
                ),
                dash_table.DataTable(
                    id="mq2-table",
                    style_table={'height': '300px', 'overflowY': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px', 'whiteSpace': 'normal'},
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
    [Input("interval", "n_intervals")],
)
def update_graph(n_intervals):
    # Fetch the latest data from MongoDB
    cursor = collection.find().sort("timestamp", -1)  # Get the latest entries
    data = list(cursor)

    if data:
        df = pd.DataFrame(data)

        # Separate timestamps for graph and table
        df["timestamp_graph"] = pd.to_datetime(df["timestamp"], utc=True)
        df["timestamp_table"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("Asia/Kuala_Lumpur").dt.strftime("%Y/%m/%d %H:%M:%S")

        # Flatten 'data' field
        df = pd.concat([df.drop(["data"], axis=1), df["data"].apply(eval).apply(pd.Series)], axis=1)
        
        # Create separate dataframes for DHT11 and MQ2
        dht11_data = df[["timestamp_table", "timestamp_graph", "Humidity", "Temperature"]]
        mq2_data = df[["timestamp_table", "timestamp_graph", "Gas"]]

        # Create graphs
        dht11_fig = px.line(
            dht11_data,
            x="timestamp_graph",
            y=["Humidity", "Temperature"],
            labels={"value": "Sensor Value", "timestamp": "Time"},
            title="DHT11 Data (Temperature and Humidity)",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )

        mq2_fig = px.line(
            mq2_data,
            x="timestamp_graph",
            y="Gas",
            labels={"value": "Sensor Value", "timestamp": "Time"},
            title="MQ2 Data (Gas)",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )

        dht11_fig.update_layout(title={"x": 0.5}, xaxis_title="Time", yaxis_title="Sensor Value", hovermode="x unified", legend_title="Sensors")
        mq2_fig.update_layout(title={"x": 0.5}, xaxis_title="Time", yaxis_title="Sensor Value", hovermode="x unified", legend_title="Sensors")

        # Prepare table data
        dht11_table_data = dht11_data[["timestamp_table", "Humidity", "Temperature"]].to_dict("records")
        mq2_table_data = mq2_data[["timestamp_table", "Gas"]].to_dict("records")

        # Add total data counts
        dht11_table_data.append({"timestamp_table": "Total Data:", "Humidity": f"{len(dht11_data)} data", "Temperature": f"{len(dht11_data)} data"})
        mq2_table_data.append({"timestamp_table": "Total Data:", "Gas": f"{len(mq2_data)} data"})

    else:
        dht11_fig = px.line(title="No DHT11 Data Available")
        mq2_fig = px.line(title="No MQ2 Data Available")
        dht11_table_data = [{"timestamp_table": "Total Data:", "Humidity": "0 data", "Temperature": "0 data"}]
        mq2_table_data = [{"timestamp_table": "Total Data:", "Gas": "0 data"}]

    return dht11_fig, mq2_fig, dht11_table_data, mq2_table_data


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)

from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
from asset_list import asset_list
from helpers_seasonality import *

import datetime as dt
from datetime import date
import yfinance as yf

app = Dash(
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)
server = app.server

# Add inline styles to ensure dropdowns appear above content
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .dash-dropdown .Select-menu-outer {
                z-index: 9999 !important;
            }
            .DayPicker, .SingleDatePicker_picker, .DateRangePicker_picker {
                display: none !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

title = html.H1(children='SEASONALITY', style={'textAlign': 'center'})
subtitle = dcc.Markdown("""
    **Analyze Historical Trends and Patterns in Asset Prices**  
    🔗 [Learn More About Seasonality in Finance](https://www.investopedia.com/terms/s/seasonality.asp)
    """,
                        style={
                            "textAlign": "center",
                            "color": "lightgray",
                            "fontSize": "18px",
                            "marginTop": "0.5rem",
                            "transition": "color 0.3s, transform 0.3s",
                            "cursor": "pointer"
                        },
                        className="subtitle-markdown")

asset_dropdown = dcc.Dropdown(options=[{
    'label': asset.get("name"),
    'value': asset.get("ticker")
} for asset in asset_list],
                              id="ticker",
                              className="ticker",
                              value="TSLA")

date_range_picker = dcc.DatePickerRange(
    id='date-range',
    className="date-range",
    min_date_allowed=date(1995, 8, 5),
    max_date_allowed=dt.datetime.today(),
    start_date=date(2020, 8, 5),
    end_date=dt.date.today(),
    display_format='DD/MM/YYYY',
    with_portal=False,
    with_full_screen_portal=False,
    calendar_orientation='horizontal',
    is_RTL=False,
    clearable=False,
    # Disable the calendar and force manual input
    show_outside_days=False,
    initial_visible_month=None,
    reopen_calendar_on_clear=False,
    first_day_of_week=0,
    stay_open_on_select=False,
    updatemode='singledate',
)

sector = html.H4(id="sector", children="")

input_div = html.Div(id="input-div",
                     children=[
                         asset_dropdown,
                         date_range_picker,
                     ])

info_div = html.Div(id="info-div", children=[sector])

mention_footer = html.A(
    "Blackswan Quants",
    href='https://www.linkedin.com/company/106626489/admin/dashboard/',
    target="_blank")
footer = html.Div(id="footer", children=mention_footer)

app.layout = html.Div(
    style={
        'height': '100vh',
        'overflow': 'hidden'
    },
    children=[
        # HEADER
        html.Header([title, subtitle], className="header"),

        # MAIN CONTENT
        html.Div(className="content",
                 children=[
                     input_div,
                     html.Div(className="content-graph",
                              children=[
                                  dcc.Graph(id="graph",
                                            figure=False,
                                            config={'displayModeBar': False}),
                                  dcc.Graph(id="volume-graph",
                                            figure=False,
                                            config={'displayModeBar': False})
                              ]),
                 ]),
        info_div,
        footer
    ])


@callback(
    Output('graph', 'figure'),
    Output("volume-graph", "figure"),
    Input("ticker", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_graph(ticker, start_date, end_date):
    print("ciao!")

    start_date = start_date[0:4] + "-01-01"
    end_date = end_date[0:4] + "-12-31"

    stock = yf.Tickers(ticker)
    sector = stock.tickers[ticker].info["sector"]

    data = calculate_seasonality(start_date, end_date, ticker)
    volume_data = volume_seasonality(start_date, end_date, ticker)

    volume_figure = px.bar(volume_data,
                           x=volume_data.index,
                           y=volume_data.columns.to_list())
    volume_figure.update_xaxes(
        ticktext=[
            "Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept",
            "Oct", "Nov", "Dec"
        ],
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    years = data.columns.to_list()

    print(years)
    print(data.index)

    # Create line chart with custom styling
    figure = px.line(data, y=years)

    figure.update_xaxes(ticktext=[
        "Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept",
        "Oct", "Nov", "Dec"
    ],
                        tickvals=[
                            "01-January", "01-February", "01-March",
                            "01-April", "01-May", "01-June", "01-July",
                            "01-August", "01-September", "01-October",
                            "01-November", "01-December"
                        ])

    # Apply styling to both charts
    template = {
        "layout": {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {
                "color": "#ffffff"
            },
            "xaxis": {
                "gridcolor": "rgba(255,255,255,0.1)"
            },
            "yaxis": {
                "gridcolor": "rgba(255,255,255,0.1)"
            }
        }
    }

    # Style volume figure
    volume_figure.update_layout(xaxis_title=None,
                                yaxis_title=None,
                                legend_title_text='Volume',
                                template=template,
                                margin=dict(l=30, r=30, t=30, b=30),
                                legend=dict(orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1))

    # Style main figure
    figure.update_layout(xaxis_title=None,
                         yaxis_title=None,
                         legend_title_text='Years',
                         template=template,
                         margin=dict(l=30, r=30, t=30, b=30),
                         legend=dict(orientation="h",
                                     yanchor="bottom",
                                     y=1.02,
                                     xanchor="right",
                                     x=1))

    return figure, volume_figure


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)

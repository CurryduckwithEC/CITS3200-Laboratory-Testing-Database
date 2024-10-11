# See official docs at https://dash.plotly.com
# pip install dash pandas
import dash
from dash import Dash, dcc, html, Input, Output, ctx, callback, State, callback_context
import plotly.express as px
import pandas as pd
import sys
import io
import base64
import dash_bootstrap_components as dbc
import dash_table

from datahandler import retrieve_entry_data, change_path, commit_new_entry, retrieve_test_specs, retrieve_filtered_data, change_key, delete_entry_by_test, delete_test_by_test
from parser import parse_workbook

css_cdn = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"]
js_cdn = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"]

app = Dash(__name__, external_stylesheets=css_cdn, external_scripts=js_cdn)
css_cdn = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"]
js_cdn = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"]

app = Dash(__name__, external_stylesheets=css_cdn, external_scripts=js_cdn, use_pages=True, pages_folder="")

# Set default port
port = 18019
if len(sys.argv) > 2:
    port = int(sys.argv[2])

# Read path off command line arguments
change_path(sys.argv[1])
# Read the key from arguments
key_value = None
if len(sys.argv) > 3:
    key_value = sys.argv[3]

# Change key value if not None
if key_value is not None and key_value != "":
    change_key(key_value)
else:
    key_value = None

#print("Key is:", keyValue)

# Used for data download
df_combined = retrieve_entry_data()
df_test_ids = pd.DataFrame(df_combined["test_id"]).drop_duplicates()

# Used as list to display tests in admin page
df_test_specs = retrieve_test_specs()
df_test_specs["availability_type"] = df_test_specs["availability_type"].map({True: "public", False:"private"})

graphs = dbc.Container(
    children=[
        html.Link(
        rel='stylesheet',
        href='api/styles.css'
        ),
        html.Div(
            id="app-container",
            children=[
                dbc.Row(
                    [
                    dbc.Col(
                        html.Div(
                            id = "filters_sidebar",
                            style={
                                    "backgroundColor": "lightGrey",
                                    "padding": "5px",
                                    "width": "inherit",
                                    "position": "fixed",
                                    "top": 0,
                                    "bottom": 0,
                                    "overflow-y": "scroll",
                                },
                            children = [
                                html.H1("Filters"),
                                html.Div(
                                    dbc.Accordion(
                                        [
                                            dbc.AccordionItem(
                                                [
                                                    # Have to go back and put in actual values used in DB
                                                    # Format Value:Label
                                                    dcc.Checklist(["All"], [], id="checkall_test_checklist", inline=True),
                                                    html.H2("Drainage"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Drained":"Drained", 
                                                            "Undrained":"Undrained"},
                                                        value=["Drained", "Undrained"],
                                                        id="drainage_checklist",
                                                        inline=True
                                                    ),
                                                    html.Br(),
                                                    
                                                    html.H2("Shearing"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Compression":"Compression", 
                                                            "Extension":"Extension"},
                                                        value=["Compression", "Extension"],
                                                        id="shearing_checklist",
                                                        inline=True
                                                    ),
                                                    html.Br(),
                                                    
                                                    html.H2("Anisotropy"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Isotropic":"Isotropic", 
                                                            "Anisotropic":"Anisotropic"},
                                                        value=["Isotropic", "Anisotropic"],
                                                        id="anisotropy_checklist",
                                                        inline=True
                                                    ),
                                                    dcc.RangeSlider(
                                                        0.3,
                                                        1,
                                                        step=None,
                                                        value=[0.3,1.0], 
                                                        id="anisotropy_slider",
                                                        tooltip={"placement": "bottom"}
                                                    ),
                                                    "Min:",
                                                    dcc.Input(id="anisotropy_min_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0.3, max=1.0, value=0,  step=0.005),
                                                    "Max:",
                                                    dcc.Input(id="anisotropy_max_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0.3, max=1.0, value=1.0,  step=0.005),
                                                    html.Br(),

                                                    html.H2("Consolidation"),
                                                    html.P(id="consolidation_value"),
                                                    dcc.RangeSlider(
                                                        10,
                                                        1500,
                                                        step=1,
                                                        marks={
                                                            10: "10",
                                                            300: "300",
                                                            600: "600",
                                                            900: "900",
                                                            1200: "1200",
                                                            1500: "1500"
                                                        },
                                                        value=[10,1500], 
                                                        id="consolidation_slider",
                                                        tooltip={"placement": "bottom"}
                                                    ),
                                                    "Min:",
                                                    dcc.Input(id="consolidation_min_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=1500, value=0),
                                                    "Max:",
                                                    dcc.Input(id="consolidation_max_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=1500, value=1500),
                                                    html.Br(),

                                                    html.H2("Availability"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Public":"Public", 
                                                            "Confidential":"Confidential"},
                                                        value=["Public", "Confidential"],
                                                        id="availability_checklist",
                                                        inline=True
                                                    )
                                                ],
                                                title="Test",
                                            ),
                                            dbc.AccordionItem(
                                                [   
                                                    dcc.Checklist(["All"], [], id="checkall_sample_checklist", inline=True),
                                                    html.H2("Density"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Loose":"Loose",
                                                            "Dense":"Dense"},
                                                        value=["Loose", "Dense"],
                                                        id="density_checklist",
                                                        inline=True
                                                    ),
                                                    html.Br(),

                                                    html.H2("Plasticity"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Plastic":"Plastic",
                                                            "Non-plastic":"Non-plastic",
                                                            "Unknown":"Unknown"},
                                                        value=["Plastic", "Non-plastic","Unknown"],
                                                        id="plasticity_checklist",
                                                        inline=True
                                                    ),
                                                    html.Br(),

                                                    html.H2("PSD"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Clay":"Clay",
                                                            "Sand":"Sand",
                                                            "Silt":"Silt"},
                                                        value=["Clay","Sand","Silt"],
                                                        id="psd_checklist",
                                                        inline=True
                                                    ),
                                                ],
                                                title="Sample",
                                            ),
                                            dbc.AccordionItem(
                                                [
                                                    html.H2("Axial Strain"),
                                                    #html.P(id="axial_value"),
                                                    dcc.RangeSlider(
                                                        0,
                                                        0.4,
                                                        step=0.001,
                                                        value=[0,0.4], 
                                                        marks={
                                                            0: "0",
                                                            0.1: "0.1",
                                                            0.2: "0.2",
                                                            0.3: "0.3",
                                                            0.4: "0.4"
                                                        },
                                                        id='axial_slider',
                                                        tooltip={"placement": "bottom"}
                                                    ),
                                                    "Min:",
                                                    dcc.Input(id="axial_min_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=0.4, value=0, step=0.001),
                                            
                                                    "Max:",
                                                    dcc.Input(id="axial_max_value", className="filter_input_number", style={"width":"30%"},  type="number",  min=0, max=0.4, value=0, step=0.001),
                                                    
                                                    html.H2("Volumetric Strain"),
                                                    dcc.RangeSlider(
                                                        0,
                                                        0.4,
                                                        step=0.001,
                                                        value=[0,0.4], 
                                                        marks={
                                                            0: "0",
                                                            0.1: "0.1",
                                                            0.2: "0.2",
                                                            0.3: "0.3",
                                                            0.4: "0.4"
                                                        },
                                                        id='volumetric_slider',
                                                        tooltip={"placement": "bottom"}
                                                    ),
                                                    "Min:",
                                                    dcc.Input(id="vol_min_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=0.4, value=0, step=0.001),
                                                    "Max:",
                                                    dcc.Input(id="vol_max_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=0.4, value=0.4, step=0.001),
                                                    html.Br(),
                                                    
                                                    html.H2("p'"),
                                                    #html.P(id="p_value"),
                                                    dcc.RangeSlider(
                                                        0,
                                                        7000,
                                                        step=None,
                                                        value=[0,7000], 
                                                        id='p_slider',
                                                        tooltip={"placement": "bottom"}
                                                    ), 
                                                    "Min:",
                                                    dcc.Input(id="p_min_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=7000, value=0),
                                                    "Max:",
                                                    dcc.Input(id="p_max_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=7000, value=7000),
                                                    html.Br(),

                                                    html.H2("Induced PWP"),
                                                    #html.P(id="pwp_value"),
                                                    dcc.RangeSlider(
                                                        0,
                                                        7000,
                                                        step=None,
                                                        value=[0,7000], 
                                                        id='pwp_slider',
                                                        tooltip={"placement": "bottom"}
                                                    ),
                                                    "Min:",
                                                    dcc.Input(id="pwp_min_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=7000, value=0),
                                                    "Max:",
                                                    dcc.Input(id="pwp_max_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=7000, value=7000),
                                                    html.Br(),
                                                    
                                                    html.H2("Deviator stress (q)"),
                                                    #html.P(id="q_value"),
                                                    dcc.RangeSlider(
                                                        0,
                                                        7000,
                                                        step=None,
                                                        value=[0,7000], 
                                                        id='q_slider',
                                                        tooltip={"placement": "bottom"}
                                                    ),
                                                    "Min:",
                                                    dcc.Input(id="q_min_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=7000, value=0),
                                                    "Max:",
                                                    dcc.Input(id="q_max_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0, max=7000, value=7000),
                                                    html.Br(),
                                                    
                                                    html.H2("Void Ratio (e)"),
                                                    #html.P(id="e_value"),
                                                    dcc.RangeSlider(
                                                        0.3,
                                                        3,
                                                        step=0.01,
                                                        marks={
                                                            0.3: "0.3",
                                                            0.5: "0.5",
                                                            1.0: "1.0",
                                                            1.5: "1.5",
                                                            2.0: "2.0",
                                                            2.5: "2.5",
                                                            3.0: "3.0"
                                                        },
                                                        value=[0.3,3], 
                                                        id='e_slider',
                                                        tooltip={"placement": "bottom"}
                                                    ),
                                                    "Min:",
                                                    dcc.Input(id="e_min_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0.3, max=3, value=0, step=0.01),
                                                    "Max:",
                                                    dcc.Input(id="e_max_value", className="filter_input_number", style={"width":"30%"},  type="number", min=0.3, max=3, value=3, step=0.01),
                                                                                                        
                                                    ],
                                                    title="Variables",
                                                ),
                                               
                                                dbc.AccordionItem(
                                                    [
                                                        html.H3("Upload Data (.xlsx)"),
                                                        dcc.Upload(
                                                            id="upload-data",
                                                            children=html.Div(
                                                                [
                                                                    "Drag and Drop or ",
                                                                    html.A("Select Files"),
                                                                ]
                                                            ),
                                                            style={
                                                                "width": "100%",
                                                                "height": "60px",
                                                                "lineHeight": "60px",
                                                                "borderWidth": "1px",
                                                                "borderStyle": "dashed",
                                                                "borderRadius": "5px",
                                                                "textAlign": "center",
                                                                "margin": "10px",
                                                            },
                                                            accept=".xlsx",
                                                            multiple=True
                                                        ),
                                                        # Refresh Button 
                                                        html.Button(
                                                            "Refresh Page", 
                                                            id="refresh-button", 
                                                            n_clicks=0, 
                                                            style={
                                                                'margin': '10px', 
                                                                'background-color': '#4CAF50', 
                                                                'color': 'white', 
                                                                'border': 'none', 
                                                                'padding': '10px 20px',
                                                                'text-align': 'center',
                                                                'text-decoration': 'none',
                                                                'display': 'inline-block',
                                                                'font-size': '16px',
                                                                'cursor': 'pointer'
                                                            }
                                                        ),
                                                        html.Div(id="upload-status"),
                                                    ],
                                                    title="Upload",
                                                ),
                                            ],
                                            always_open=True,
                                            flush=True,
                                        )
                                    ),
                                ],
                            ),
                            width=3,
                        ),
                    
                        dbc.Col([
                            html.Div(
                                id="dashboard",
                                children = [
                                dcc.Graph(id="axial_deviator_fig"),
                                dcc.Graph(id="axial_pwp_fig"), 
                                dcc.Graph(id="q_p_fig"),
                                dcc.Graph(id="axial_vol_fig"), 
                                dcc.Graph(id="e_logp_fig"),
                                dcc.Graph(id="stress_ratio_axial_fig")
                            ]
                        )
                    ], width=9, 
                    ),
                    ],
                )
            ]
        ),
    ],
    fluid=True,
)

admin = dbc.Container(children=[
    html.Br(),
    html.Div([
        html.H3("Upload Data (.xlsx)"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                [
                    "Drag and Drop or ",
                    html.A("Select Files"),
                ]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },

            accept=".xlsx",
            multiple = True
        ),
        html.Div(id="upload-status"),
        html.Button(
            "Refresh Page", 
            id="refresh-table-button", 
            n_clicks=0, 
            style={
                'margin': '10px', 
                'background-color': '#4CAF50', 
                'color': 'white', 
                'border': 'none', 
                'padding': '10px 20px',
                'text-align': 'center',
                'text-decoration': 'none',
                'display': 'inline-block',
                'font-size': '16px',
                'cursor': 'pointer', 
            }
        ),
        html.Br(),
        html.Br(),
        html.H3("Current Database"),
        dash_table.DataTable(
            id="data-table",
            columns=[
                {"name": "Test ID", "id":"test_id"},
                {"name": "File Name", "id": "filename"},
                {"name": " ", "id": "download"},
                {"name": "Delete", "id": "delete"}    
            ],  # Define columns
                data = [
                  {
                      "test_id": row["test_id"],
                   "filename":row["test_file_name"],
                   "download": "Download",
                   "delete": "Delete"
                   }
                  for _, row in df_test_specs.iterrows()],  # Convert dataframe to dictionary
                style_table={'overflowX': 'auto'},  # Allow horizontal scrolling
                style_header={
                    'backgroundColor': 'lightgrey',
                    'font_size': '16px',
                    'fontWeight': 'bold',
                    'fontFamily': 'helveticaneue',
                },
                style_cell = {
                    'textAlign': 'left',
                    'padding': '10px',
                    'font_family': 'helveticaneue',
                    'font_size': '16px',
                    #'border': '1px solid black',
                    'margin': '20px'
                }
            ),
        dcc.Download(id="download-csv"),
    ], 
    style={"margin-bottom": "50px"}),
])

dash.register_page("graphs", path='/', layout=graphs)
dash.register_page("admin", layout=admin)
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Graphs", href=dash.page_registry['graphs']['path'])),
        dbc.NavItem(dbc.NavLink("Admin", href=dash.page_registry['admin']['path'])),
        dbc.NavItem(dbc.NavLink("axial_deviator", href="#axial_deviator_fig", external_link=True)),
        dbc.NavItem(dbc.NavLink("axial_pwp", href="#axial_pwp_fig", external_link=True)),
        dbc.NavItem(dbc.NavLink("q_p", href="#q_p_fig", external_link=True)),
        dbc.NavItem(dbc.NavLink("axial_vol", href="#axial_vol_fig", external_link=True)),
        dbc.NavItem(dbc.NavLink("e_logp", href="#e_logp_fig", external_link=True)),
        dbc.NavItem(dbc.NavLink("stress_ratio_axial", href="#stress_ratio_axial_fig", external_link=True)),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
            ],
            nav=True,
            in_navbar=True,
            label="More",
            direction="start",
        ),
    ],
    brand="DatabaseApp",
    brand_href="#",
    color="primary",
    sticky="top",
    dark=True,
)

app.layout = dbc.Container(
    children=[
        navbar,
        dash.page_container,
    ],
    fluid=True,
)

@app.callback(
    [
        Output("density_checklist", "value"),
        Output("plasticity_checklist", "value"),
        Output("psd_checklist", "value")
     ],
    [
        Input("checkall_sample_checklist", "value"),
        Input("density_checklist", "value"),
        Input("plasticity_checklist", "value"),
        Input("psd_checklist", "value")
    ]
)
def toggle_checklists(all_value, density_value, plasticity_value, psd_value):
    density_options = ["Loose", "Dense"]
    plasticity_options = ["Plastic", "Non-plastic", "Unknown"]
    psd_options = ["Clay", "Sand", "Silt"]

    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if input_id == "checkall_sample_checklist":
        if "All" in all_value:
            return density_options, plasticity_options, psd_options
        else:
            return [], [], []
    return density_value, plasticity_value, psd_value

@app.callback(
    [
        Output("drainage_checklist", "value"),
        Output("shearing_checklist", "value"),
        Output("anisotropy_checklist", "value"),
        Output("availability_checklist", "value"),
    ],
    [
        Input("checkall_test_checklist", "value"),
        Input("drainage_checklist", "value"),
        Input("shearing_checklist", "value"),
        Input("anisotropy_checklist", "value"),
        Input("availability_checklist", "value"),
    ]
)
def toggle_test_checklists(all_value, drainage_value, shearing_value, anisotropy_value, availability_value):
    drainage_options = ["Drained", "Undrained"]
    shearing_options = ["Compression", "Extension"]
    anisotropy_options = ["Isotropic", "Anisotropic"]
    availability_options = ["Public", "Confidential"]

    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if input_id == "checkall_test_checklist":
        if "All" in all_value:
            return drainage_options, shearing_options, anisotropy_options, availability_options
        else:
            return [], [], [], []
    return drainage_value, shearing_value, anisotropy_value, availability_value


def sync_slider_callback(min_id, max_id, slider):
    @app.callback(
    [
        Output(min_id,"value"),
        Output(max_id,"value"),
        Output(slider,"value")    
    ],    
    [
        Input(min_id,"value"),
        Input(max_id,"value"),
        Input(slider,"value")
    ]   
)
    def sync_slider(start, end, slider):
        trigger_id = ctx.triggered_id

        min_value = start if trigger_id == min_id else slider[0]
        max_value = end if trigger_id == max_id else slider[1]
        slider_value = slider if trigger_id == slider else [min_value, max_value]

        return min_value, max_value, slider_value

sync_slider_callback("consolidation_min_value", "consolidation_max_value", "consolidation_slider")
sync_slider_callback("anisotropy_min_value", "anisotropy_max_value", "anisotropy_slider")
sync_slider_callback("axial_min_value", "axial_max_value", "axial_slider")
sync_slider_callback("vol_min_value", "vol_max_value", "volumetric_slider")    
sync_slider_callback("p_min_value", "p_max_value", "p_slider")
sync_slider_callback("pwp_min_value", "pwp_max_value", "pwp_slider")
sync_slider_callback("q_min_value", "q_max_value", "q_slider")
sync_slider_callback("e_min_value", "e_max_value", "e_slider")




@app.callback(
    Output('upload-status', 'children'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename')
    ]
)
def handle_upload(content, filename):

    # Handling Electron initialisation
    if content == None:
        return
  
    try:
        excel_base64 = content[0].split(',')[1]
        decoded = base64.b64decode(excel_base64)
      
        file = io.BytesIO(decoded)
        specs, df = parse_workbook(file)

        # commit the new entry to database
        commit_new_entry(specs, df, filename[0])
    except Exception as e:
        print(f"Error parsing file {filename}: {str(e)}")
        return None, f"Error parsing file {filename}: {str(e)}"
    
    return f"{filename[0]} committed succesfully."

    

def parse_contents(contents, filename):
    # This function parses and processes the uploaded file contents.
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        
        specs, df = parse_workbook(decoded)
        return df
    except Exception as e:
        print(f"Error parsing file {filename}: {str(e)}")
        return None

@app.callback(
    Output("data-table", "data"),
    Input("refresh-table-button", "n_clicks")
)
def update_table(n_clicks):
    df_test_specs = retrieve_test_specs()
    data = [
        {"test_id": row["test_id"],
            "filename": row["test_file_name"],
            "download": "Download"}
        for _, row in df_test_specs.iterrows()]
    return data


@app.callback(
    [
        Output("axial_deviator_fig", "figure"),
        Output("axial_pwp_fig", "figure"), 
        Output("q_p_fig", "figure"),
        Output("axial_vol_fig", "figure"), 
        Output("e_logp_fig", "figure"), 
        Output("stress_ratio_axial_fig", "figure"),
    ],
    [
        Input("drainage_checklist", "value"),
        Input("shearing_checklist", "value"),
        Input("anisotropy_checklist", "value"),
        Input("anisotropy_slider", "value"),
        Input("consolidation_slider", "value"),
        Input("availability_checklist", "value"),
        Input("density_checklist","value"),
        Input("plasticity_checklist", "value"),
        Input("psd_checklist","value"),
        Input("axial_slider", "value"),
        Input("p_slider", "value"), 
        Input("pwp_slider", "value"), 
        Input("q_slider", "value"),
        Input("e_slider", "value"),
        Input('refresh-button', 'n_clicks'),
        Input("checkall_sample_checklist", "value"),
        Input("checkall_test_checklist", "value")
    ]
)
def update_figure(selected_drainage, selected_shearing, checked_anisotropy, selected_anisotropy, selected_consolidation, selected_availability, selected_density, selected_plasticity, selected_psd,
                  selected_axial, selected_p, selected_pwp, selected_q, selected_e, click, selected_all_sample, selected_all_test):
    
    # Check if filters and data are properly initialized
    print(f"Selected filters: {selected_drainage}, {selected_shearing}, {selected_anisotropy}, {selected_consolidation}, {selected_availability},{selected_density},{selected_plasticity},{selected_psd}")
    if(checked_anisotropy == ['Isotropic']):
        selected_anisotropy = [0.5, 0.5]
    if(checked_anisotropy == ['Anisotropic']):
        selected_anisotropy = [0.3, 0.495]
    df_filtered = retrieve_filtered_data(
        drainage_types=selected_drainage,
        shearing_types=selected_shearing,
        anisotropy_range=selected_anisotropy,
        consolidation_range=selected_consolidation,
        availability_types=selected_availability,
        density_types=selected_density,
        plasticity_types=selected_plasticity,
        psd_types = selected_psd
    )
    
    #if not df_filtered:
    #    print("No data after filtering")
    #    return {}, {}, {}, {}, {}, {}
    
    print(f"Filtered DataFrame: {df_filtered.shape}")  # Debugging log to see if data is passed to the figure generation
    
    if df_filtered.empty:
        print("Filtered dataframe is empty.")
        return {}, {}, {}, {}, {}, {}


    # Filter the data further by the sliders (axial strain, p, pwp, q, and e)
    filtered_df= df_filtered[
        (df_filtered["axial_strain"] >= selected_axial[0]) &
        (df_filtered["axial_strain"] <= selected_axial[1]) &
        (df_filtered["p"] >= selected_p[0]) &
        (df_filtered["p"] <= selected_p[1]) &
        (df_filtered["shear_induced_pwp"] >= selected_pwp[0]) &
        (df_filtered["shear_induced_pwp"] <= selected_pwp[1]) &
        (df_filtered["deviator_stress"] >= selected_q[0]) &
        (df_filtered["deviator_stress"] <= selected_q[1]) &
        (df_filtered["void_ratio"] >= selected_e[0]) &
        (df_filtered["void_ratio"] <= selected_e[1])
    ]

    if filtered_df.empty:
        print("Filtered dataframe is empty after applying the sliders.")
        return {}, {}, {}, {}, {}, {}

    #print(filtered_df.head())
    # Deviator Stress (q) & Mean effective stress (p') VS Axial Strain 
    axial_deviator_fig = px.line(
        filtered_df, 
        x="axial_strain", 
        y=["deviator_stress", "p"], 
        color="test_id", 
        title="Deviator Stress, q and Mean Effective Stress (kPa), p' vs. Axial Strain (%)").update_layout(
            xaxis_title="Axial Strain",
            yaxis_title="Deviator Stress, q & Mean Effective Stress, p'"
        ).update_layout(showlegend=False)

    # Shear induced PWP VS Axial Strain
    axial_pwp_fig = px.line(
        filtered_df, 
        x="axial_strain", 
        y="shear_induced_pwp",
        color="test_id", 
        title="Shear Induced Pore Pressure (kPa) vs. Axial Strain (%)").update_layout(
            xaxis_title="Axial Strain",
            yaxis_title="Shear Induced Pore Pressure"
        ).update_layout(showlegend=False)
    
    # Deviator Stress (q) VS Mean effective stress (p')
    q_p_fig = px.line(
        filtered_df, 
        x="p", 
        y="deviator_stress",
        color="test_id", 
        title="Deviator Stress, q (kPa) vs. Mean Effective Stress, p' (kPa)").update_layout(
            xaxis_title="Mean Effective Stress, p'",
            yaxis_title="Deviator stress, q"
        ).update_layout(showlegend=False)
    
    ### Volumetric Strain VS Axial Strain
    axial_vol_fig = px.line(
        filtered_df, 
        x="axial_strain", 
        y="vol_strain",
        color="test_id", 
        title="Volumetric Stress (%) vs. Axial Strain (%)").update_layout(
            xaxis_title="Axial Strain",
            yaxis_title="Volumetric Strain"
        ).update_layout(showlegend=False)
    
    ### e VS log(p')
    e_logp_fig = px.line(
        filtered_df, 
        x="p", 
        y="void_ratio",
        color="test_id", 
        title="Void ratio, e vs. log(p')", 
        log_x = True).update_layout(
            xaxis_title="log(p')",
            xaxis = dict(range=[0,4]),
            yaxis_title="Void Ratio, e"
        ).update_layout(showlegend=False)
    
    ### Stress ratio (p'/q) vs. Axial Strain
    stress_ratio_axial_fig = px.line(
        filtered_df, 
        x="axial_strain", 
        y=filtered_df["deviator_stress"]/filtered_df["p"],
        color="test_id", 
        title="Stress Ratio, q/p' vs. Axial Strain").update_layout(
            xaxis_title="Axial Strain",
            yaxis_title="Stress Ratio"
        ).update_layout(showlegend=False)
    

    return axial_deviator_fig, axial_pwp_fig, q_p_fig, axial_vol_fig, e_logp_fig, stress_ratio_axial_fig


import io 
from dash.dependencies import Input, Output
import base64

def create_excel_file(df, specs):
    output = io.BytesIO()
    transposed_specs = pd.DataFrame(specs.T) # Transpose specifications to match format of required Excel sheet
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer: 
        transposed_specs.to_excel(writer, index=True, header=False, sheet_name="Shearing", startrow=0, startcol=0)
        df.to_excel(writer, index=False, sheet_name="Shearing", startrow=len(transposed_specs)+2)
    output.seek(0)
    return output.getvalue()

@app.callback(
    Output("download-csv", "data"),
    Input("data-table", "active_cell"),
    prevent_initial_call=True
)
def download_csv(active_cell):
    if active_cell: 

        clicked_column = active_cell["column"] # Identify which column has been clicked 

        if clicked_column == 2: # Download column has been clicked 
            row_idx = active_cell["row"] # Index of clicked row
            selected_test = df_test_specs.iloc[row_idx]["test_id"] # Corresponding test ID 

            test_df = df_combined[df_combined["test_id"]==selected_test] # Dataframe of selected test 
            test_specs = df_test_specs[df_test_specs["test_id"]==selected_test] # Specifications of selected test 
            test_filename = test_specs["test_file_name"][row_idx] # Original file name

            # Drop unnecessary columns 
            test_df_d = test_df.drop(columns=["entry_id", "test_id"]) 
            test_specs_d = test_specs.drop(columns=["test_id", "test_value_id", "sample_value_id", "test_value_id_1", "test_file_name", "test_value_id", "sample_value_id_1"])

            # Rename columns to match required format of Excel sheet 
            test_df_d.columns = test_df_d.columns.str.replace('_', ' ')
            test_df_d.rename(columns={'p': "p'", 'vol strain': 'volumetric strain'}, inplace=True)
            test_specs_d.columns = test_specs_d.columns.str.replace('_', ' ')
            test_specs_d.columns = test_specs_d.columns.str.replace('type', '')

            file = create_excel_file(test_df_d, test_specs_d)

            return dcc.send_bytes(file, f"{test_filename}")

@app.callback(
    Output("data-table", "data", allow_duplicate=True),
    Input("data-table", "active_cell"),
    State("data-table", "data"),
    prevent_initial_call=True
)
def update_data_table_on_delete(active_cell, current_data):
    if active_cell and active_cell["column_id"] == "delete":
        row_idx = active_cell["row"]
        test_id_to_delete = current_data[row_idx]["test_id"]

        # Delete entry from the database
        delete_entry_by_test(test_id=test_id_to_delete)
        delete_test_by_test(test_id=test_id_to_delete)

        # Update DataTable by removing the deleted entry
        updated_data = [row for row in current_data if row["test_id"] != test_id_to_delete]

        return updated_data

    return dash.no_update

@app.callback(
    [
        Output("axial_deviator_fig", "figure", allow_duplicate=True),
        Output("axial_pwp_fig", "figure", allow_duplicate=True),
        Output("q_p_fig", "figure", allow_duplicate=True),
        Output("axial_vol_fig", "figure", allow_duplicate=True),
        Output("e_logp_fig", "figure", allow_duplicate=True),
        Output("stress_ratio_axial_fig", "figure", allow_duplicate=True),
    ],
    [
        Input("drainage_checklist", "value"),
        Input("shearing_checklist", "value"),
        Input("anisotropy_checklist", "value"),
        Input("anisotropy_slider", "value"),
        Input("consolidation_slider", "value"),
        Input("availability_checklist", "value"),
        Input("density_checklist", "value"),
        Input("plasticity_checklist", "value"),
        Input("psd_checklist", "value"),
        Input("axial_slider", "value"),
        Input("p_slider", "value"),
        Input("pwp_slider", "value"),
        Input("q_slider", "value"),
        Input("e_slider", "value"),
        Input("refresh-button", "n_clicks"),
    ],
    prevent_initial_call=True
)
def update_graphs_based_on_filters(selected_drainage, selected_shearing, checked_anisotropy, selected_anisotropy, selected_consolidation, selected_availability,
                                   selected_density, selected_plasticity, selected_psd, selected_axial, selected_p, selected_pwp,
                                   selected_q, selected_e, refresh_click):
    # Filter the data based on the inputs
    if(checked_anisotropy == ['Isotropic']):
        selected_anisotropy = [0.5, 0.5]
    if(checked_anisotropy == ['Anisotropic']):
        selected_anisotropy = [0.3, 0.495]
    df_filtered = retrieve_filtered_data(
        drainage_types=selected_drainage,
        shearing_types=selected_shearing,
        anisotropy_range=selected_anisotropy,
        consolidation_range=selected_consolidation,
        availability_types=selected_availability,
        density_types=selected_density,
        plasticity_types=selected_plasticity,
        psd_types=selected_psd
    )

    # Create the graphs with the filtered data
    axial_deviator_fig = px.line(df_filtered, x="axial_strain", y=["deviator_stress", "p"])
    axial_pwp_fig = px.line(df_filtered, x="axial_strain", y="shear_induced_pwp")
    q_p_fig = px.line(df_filtered, x="p", y="deviator_stress")
    axial_vol_fig = px.line(df_filtered, x="axial_strain", y="vol_strain")
    e_logp_fig = px.line(df_filtered, x="p", y="void_ratio", log_x=True)
    stress_ratio_axial_fig = px.line(df_filtered, x="axial_strain", y=df_filtered["deviator_stress"] / df_filtered["p"])

    return axial_deviator_fig, axial_pwp_fig, q_p_fig, axial_vol_fig, e_logp_fig, stress_ratio_axial_fig






app.run_server(port=port, debug=True)
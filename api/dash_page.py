# See official docs at https://dash.plotly.com
# pip install dash pandas
import dash
from dash import Dash, dcc, html, Input, Output, ctx, callback, State
import plotly.express as px
import pandas as pd
import sys
import io
import base64
import dash_bootstrap_components as dbc
import dash_table

from datahandler import retrieve_entry_data, change_path, commit_new_entry, retrieve_test_specs
from parser import parse_workbook

app = Dash(__name__, use_pages=True, pages_folder="")

# Set default port
port = 18019
if len(sys.argv) > 2:
    port = int(sys.argv[2])

# Read path off command line arguments
change_path(sys.argv[1])


df_combined = retrieve_entry_data()
df_test_specs = retrieve_test_specs()
df_test_specs["availability_type"] = df_test_specs["availability_type"].map({True: "public", False:"private"})
#df_test_ids = pd.DataFrame(df_combined["test_id"]).drop_duplicates()


graphs = dbc.Container(
    children=[
        html.Div(
            id="app-container",
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                id="filters-sidebar",
                                style={
                                    "backgroundColor": "lightGrey",
                                    "padding": "5px",
                                    "width": "inherit",
                                    "position": "fixed",
                                    "top": 0,
                                    "bottom": 0,
                                    "overflow-y": "scroll",
                                },
                                children=[
                                    html.H1("Filters"),
                                    html.Div(
                                        dbc.Accordion(
                                            [
                                            
                                                dbc.AccordionItem(
                                                    [
                                                        html.H3("Drainage"),
                                                        dcc.Checklist(
                                                            options={
                                                                "Drained": "Drained",
                                                                "Undrained": "Undrained",
                                                            },
                                                            value=["Drained", "Undrained"],
                                                            id="drainage_checklist",
                                                            inline=True,
                                                        ),
                                                        html.H3("Shearing"),
                                                        dcc.Checklist(
                                                            options={
                                                                "Compression": "Compression",
                                                                "Extension": "Extension",
                                                            },
                                                            value=["Compression", "Extension"],
                                                            id="shearing_checklist",
                                                            inline=True,
                                                        ),
                                                        html.H3("Anisotropy"),
                                                        dcc.Checklist(
                                                            options={
                                                                "Isotropic": "Isotropic",
                                                                "Anisotropic": "Anisotropic",
                                                            },
                                                            value=["Isotropic", "Anisotropic"],
                                                            id="anisotropy_checklist",
                                                            inline=True,
                                                        ),
                                                        dcc.RangeSlider(
                                                            0.3,
                                                            1,
                                                            step=None,
                                                            value=[0.3, 1.0],
                                                            id="anisotropy_slider",
                                                            tooltip={
                                                                "placement": "bottom",
                                                                "always_visible": True,
                                                            },
                                                        ),
                                                        "Min Value:",
                                                        dcc.Input(
                                                            id="anisotropy_min_value",
                                                            type="number",
                                                            min=0,
                                                            max=1.0,
                                                            value=1.0,
                                                            step=0.05,
                                                            style={'width': '70px'}
                                                        ),
                                                        "Max Value:",
                                                        dcc.Input(
                                                            id="anisotropy_max_value",
                                                            type="number",
                                                            min=0,
                                                            max=1.0,
                                                            value=0,
                                                            step=0.05,
                                                            style={'width': '70px'}
                                                        ),
                                                        html.H3("Consolidation"),
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
                                                                1500: "1500",
                                                            },
                                                            value=[10, 1500],
                                                            id="consolidation_slider",
                                                            tooltip={
                                                                "placement": "bottom",
                                                                "always_visible": True,
                                                            },
                                                        ),
                                                        "Min Value:",
                                                        dcc.Input(
                                                            id="consolidation_min_value",
                                                            type="number",
                                                            min=0,
                                                            max=1500,
                                                            value=1500,
                                                            style={'width': '70px'}
                                                        ),
                                                        "Max Value:",
                                                        dcc.Input(
                                                            id="consolidation_max_value",
                                                            type="number",
                                                            min=0,
                                                            max=1500,
                                                            value=0,
                                                            style={'width': '70px'}
                                                        ),
                                                        html.H3("Availability"),
                                                        dcc.Checklist(
                                                            options={
                                                                "Public": "Public",
                                                                "Confidential": "Confidential",
                                                            },
                                                            value=["Public", "Confidential"],
                                                            id="availability_checklist",
                                                            inline=True,
                                                        ),
                                                    ],
                                                    title="Test",
                                                ),
                                                dbc.AccordionItem(
                                                    [
                                                        html.H3("Density"),
                                                        dcc.Checklist(
                                                            options={
                                                                "Loose": "Loose",
                                                                "Dense": "Dense",
                                                            },
                                                            value=["Loose", "Dense"],
                                                            id="density_checklist",
                                                            inline=True,
                                                        ),
                                                        html.H3("Plasticity"),
                                                        dcc.Checklist(
                                                            options={
                                                                "Plastic": "Plastic",
                                                                "Non-plastic": "Nonplastic",
                                                                "Unknown": "Unknown",
                                                            },
                                                            value=[
                                                                "Plastic",
                                                                "Non-plastic",
                                                                "Unknown",
                                                            ],
                                                            id="plasticity_checklist",
                                                            inline=True,
                                                        ),
                                                        html.H3("PSD"),
                                                        dcc.Checklist(
                                                            options={
                                                                "Clay": "Clay",
                                                                "Sand": "Sand",
                                                                "Silt": "Silt",
                                                            },
                                                            value=["Clay", "Sand", "Silt"],
                                                            id="psd_checklist",
                                                            inline=True,
                                                        ),
                                                    ],
                                                    title="Sample",
                                                ),
                                                dbc.AccordionItem(
                                                    [
                                                        html.H3("Axial Strain Filter"),
                                                        html.P(id="axial_value"),
                                                        dcc.RangeSlider(
                                                            0,
                                                            0.5,
                                                            step=0.05,
                                                            marks={
                                                                0.0: "0.0",
                                                                0.1: "0.1",
                                                                0.2: "0.2",
                                                                0.3: "0.3",
                                                                0.4: "0.4",
                                                                0.5: "0.5",
                                                            },
                                                            value=[0, 0.5],
                                                            id="axial_slider",
                                                            tooltip={
                                                                "placement": "bottom",
                                                                "always_visible": True,
                                                            },
                                                        ),
                                                        "Min Value:",
                                                        dcc.Input(
                                                            id="axial_min_value",
                                                            type="number",
                                                            min=0,
                                                            max=0.5,
                                                            value=0,
                                                            step=0.05,
                                                            style={'width': '70px'}
                                                        ),
                                                        "Max Value:",
                                                        dcc.Input(
                                                            id="axial_max_value",
                                                            type="number",
                                                            min=0,
                                                            max=0.5,
                                                            value=0.5,
                                                            step=0.05,
                                                            style={'width': '70px'}
                                                        ),
                                                        html.H3("p' Filter"),
                                                        html.P(id="p_value"),
                                                        dcc.RangeSlider(
                                                            0,
                                                            500,
                                                            step=None,
                                                            value=[0, 500],
                                                            id="p_slider",
                                                            tooltip={
                                                                "placement": "bottom",
                                                                "always_visible": True,
                                                            },
                                                        ),
                                                        "Min Value:",
                                                        dcc.Input(
                                                            id="p_min_value",
                                                            type="number",
                                                            min=0,
                                                            max=500,
                                                            value=0,
                                                            style={'width': '70px'}
                                                        ),
                                                        "Max Value:",
                                                        dcc.Input(
                                                            id="p_max_value",
                                                            type="number",
                                                            min=0,
                                                            max=500,
                                                            value=500,
                                                            style={'width': '70px'}
                                                        ),
                                                        html.H3("Induced PWP Filter"),
                                                        html.P(id="pwp_value"),
                                                        dcc.RangeSlider(
                                                            0,
                                                            500,
                                                            step=None,
                                                            value=[0, 500],
                                                            id="pwp_slider",
                                                            tooltip={
                                                                "placement": "bottom",
                                                                "always_visible": True,
                                                            },
                                                        ),
                                                        "Min Value:",
                                                        dcc.Input(
                                                            id="pwp_min_value",
                                                            type="number",
                                                            min=0,
                                                            max=500,
                                                            value=0,
                                                            style={'width': '70px'}
                                                        ),
                                                        "Max Value:",
                                                        dcc.Input(
                                                            id="pwp_max_value",
                                                            type="number",
                                                            min=0,
                                                            max=500,
                                                            value=500,
                                                            style={'width': '70px'}
                                                        ),
                                                        html.H3("Deviator stress (q) Filter"),
                                                        html.P(id="q_value"),
                                                        dcc.RangeSlider(
                                                            0,
                                                            500,
                                                            step=None,
                                                            value=[0, 500],
                                                            id="q_slider",
                                                            tooltip={
                                                                "placement": "bottom",
                                                                "always_visible": True,
                                                            },
                                                        ),
                                                        "Min Value:",
                                                        dcc.Input(
                                                            id="q_min_value",
                                                            type="number",
                                                            min=0,
                                                            max=500,
                                                            value=0,
                                                            style={'width': '70px'}
                                                        ),
                                                        "Max Value:",
                                                        dcc.Input(
                                                            id="q_max_value",
                                                            type="number",
                                                            min=0,
                                                            max=500,
                                                            value=500,
                                                            style={'width': '70px'}
                                                        ),
                                                        html.H3("Void Ratio (e) Filter"),
                                                        html.P(id="e_value"),
                                                        dcc.RangeSlider(
                                                            0,
                                                            1,
                                                            step=0.01,
                                                            marks={
                                                                0.0: "0.0",
                                                                0.2: "0.2",
                                                                0.4: "0.4",
                                                                0.6: "0.6",
                                                                0.8: "0.8",
                                                                1.0: "1.0",
                                                            },
                                                            value=[0, 1],
                                                            id="e_slider",
                                                            tooltip={
                                                                "placement": "bottom",
                                                                "always_visible": True,
                                                            },
                                                        ),
                                                        "Min Value:",
                                                        dcc.Input(
                                                            id="e_min_value",
                                                            type="number",
                                                            min=0,
                                                            max=1,
                                                            value=0,
                                                            step=0.1,
                                                            style={'width': '70px'}
                                                        ),
                                                        "Max Value:",
                                                        dcc.Input(
                                                            id="e_max_value",
                                                            type="number",
                                                            min=0,
                                                            max=1,
                                                            value=1,
                                                            step=0.1,
                                                            style={'width': '70px'}
                                                        ),
                                                    ],
                                                    title="Variables",
                                                ),
                                               
                                                dbc.AccordionItem(
                                                    [
                                                        
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
                        dbc.Col(
                            children=[
                                html.Div(
                                    id="dashboard",
                                    children=[
                                        dcc.Graph(id="axial_deviator_fig"),
                                        dcc.Graph(id="axial_pwp_fig"),
                                        dcc.Graph(id="q_p_fig"),
                                        dcc.Graph(id="axial_vol_fig"),
                                        dcc.Graph(id="e_logp_fig"),
                                        dcc.Graph(id="stress_ratio_axial_fig"),
                                    ],
                                ),
                            ], width=9,
                        ),
                    ]
                ),
            ]
        ),
    ],
    fluid=True,
)

admin = dbc.Container(children=[
    html.H1('This is our Admin page'),
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
        html.H3("Download CSV"),
        dash_table.DataTable(
            id="data-table",
            columns=[
                {"name": "File Name", "id": "filename"},
                {"name": "Test ID", "id":"test_id"},
                {"name": " ", "id": "download"}],  # Define columns
              data = [
                  {"filename":row["test_file_name"],
                   "test_id": row["test_id"],
                   "download": "Download"}
                  for _, row in df_test_specs.iterrows()],  # Convert dataframe to dictionary
                style_table={'overflowX': 'auto'},  # Allow horizontal scrolling
                style_cell={'textAlign': 'left'},  # Cell alignment
                style_header={
            'backgroundColor': 'lightgrey',
            'fontWeight': 'bold'
            }
            ),
        dcc.Download(id="download-csv"),
    ]),
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
sync_slider_callback("p_min_value", "p_max_value", "p_slider")
sync_slider_callback("pwp_min_value", "pwp_max_value", "pwp_slider")
sync_slider_callback("q_min_value", "q_max_value", "q_slider")
sync_slider_callback("e_min_value", "e_max_value", "e_slider")




@app.callback(
    Output('upload-status', 'children'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename')]
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
    [
        Output("axial_deviator_fig", "figure"),
        Output("axial_pwp_fig", "figure"), 
        Output("q_p_fig", "figure"),
        Output("axial_vol_fig", "figure"), 
        Output("e_logp_fig", "figure"), 
        Output("stress_ratio_axial_fig", "figure")
    ],
    [
        Input("axial_slider", "value"), 
        Input("p_slider", "value"), 
        Input("pwp_slider", "value"), 
        Input("q_slider", "value"),
        Input("e_slider", "value"),
    ]
)
def update_figure(selected_axial, selected_p, selected_pwp, selected_q, selected_e):  
    global df_combined
    
    #print("update_figure called with selected values:")
    #print(f"Axial: {selected_axial}, p: {selected_p}, pwp: {selected_pwp}, q: {selected_q}, e: {selected_e}")

    if df_combined.empty:
        print("Global dataframe 'df_combined' is empty. Returning empty figures.")
        return {}, {}, {}, {}, {}, {}

    #print("df_combined before filtering:")
    #print(df_combined.head())

    filtered_df = df_combined[
        (df_combined["axial_strain"] >= selected_axial[0]) &
        (df_combined["axial_strain"] <= selected_axial[1]) &
        (df_combined["p"] >= selected_p[0]) &
        (df_combined["p"] <= selected_p[1]) &
        (df_combined["shear_induced_pwp"] >= selected_pwp[0]) &
        (df_combined["shear_induced_pwp"] <= selected_pwp[1]) &
        (df_combined["deviator_stress"] >= selected_q[0]) &
        (df_combined["deviator_stress"] <= selected_q[1]) &
        (df_combined["void_ratio"] >= selected_e[0]) &
        (df_combined["void_ratio"] <= selected_e[1])
    ]
    if filtered_df.empty:
        print("Filtered dataframe is empty after applying the filters.")
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
        )

    # Shear induced PWP VS Axial Strain
    axial_pwp_fig = px.line(
        filtered_df, 
        x="axial_strain", 
        y="shear_induced_pwp",
        color="test_id", 
        title="Shear Induced Pore Pressure (kPa) vs. Axial Strain (%)").update_layout(
            xaxis_title="Axial Strain",
            yaxis_title="Shear Induced Pore Pressure"
        )
    
    # Deviator Stress (q) VS Mean effective stress (p')
    q_p_fig = px.line(
        filtered_df, 
        x="p", 
        y="deviator_stress",
        color="test_id", 
        title="Deviator Stress, q (kPa) vs. Mean Effective Stress, p' (kPa)").update_layout(
            xaxis_title="Mean Effective Stress, p'",
            yaxis_title="Deviator stress, q"
        )
    
    ### Volumetric Strain VS Axial Strain
    axial_vol_fig = px.line(
        filtered_df, 
        x="axial_strain", 
        y="vol_strain",
        color="test_id", 
        title="Volumetric Stress (%) vs. Axial Strain (%)").update_layout(
            xaxis_title="Axial Strain",
            yaxis_title="Volumetric Strain"
        )
    
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
        )
    
    ### Stress ratio (p'/q) vs. Axial Strain
    stress_ratio_axial_fig = px.line(
        filtered_df, 
        x="axial_strain", 
        y=filtered_df["deviator_stress"]/filtered_df["p"],
        color="test_id", 
        title="Stress Ratio, q/p' vs. Axial Strain").update_layout(
            xaxis_title="Axial Strain",
            yaxis_title="Stress Ratio"
        )
    
    return axial_deviator_fig, axial_pwp_fig, q_p_fig, axial_vol_fig, e_logp_fig, stress_ratio_axial_fig



@app.callback(
    [
        Output("axial_value", "children"),
        Output("p_value", "children"),
        Output("pwp_value", "children"), 
        Output("q_value", "children"),
        Output("e_value", "children")
     ],
    [
        Input("axial_slider", "value"), 
        Input("p_slider", "value"), 
        Input("pwp_slider", "value"), 
        Input("q_slider", "value"),
        Input("e_slider", "value")]
     ,
     
)
def update_filters(selected_axial, selected_p, selected_pwp, selected_q, selected_e): 
    return f'Selected range: {selected_axial[0]} to {selected_axial[1]}', f'Selected range: {selected_p[0]} to {selected_p[1]}', f'Selected range: {selected_pwp[0]} to {selected_pwp[1]}', f'Selected range: {selected_q[0]} to {selected_q[1]}', f'Selected range: {selected_e[0]} to {selected_e[1]}'

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
    Input("data-table", "active_cell")
)
def download_csv(active_cell):
    if active_cell: 
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
        #return dcc.send_data_frame(test_df.to_csv, f"test_id_{selected_test}.csv")

app.run_server(port=port, debug=True)



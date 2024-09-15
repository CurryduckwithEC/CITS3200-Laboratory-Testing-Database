# See official docs at https://dash.plotly.com
# pip install dash pandas

from dash import Dash, dcc, html, Input, Output, ctx, callback
import plotly.express as px
import pandas as pd
import sys
import dash_bootstrap_components as dbc

from datahandler import retrieve_entry_data

app = Dash(__name__)

df_combined = retrieve_entry_data()
#print(df_combined)

app.layout = dbc.Container(
    children = [
        html.Div(
            id = "app-container",
            children = [  
                dbc.Row( 
                    [
                    dbc.Col(
                        html.Div(
                            id = "filters-sidebare",
                            style = {
                                "backgroundColor": "lightGrey",
                                "padding": "5px",
                                "position": "fixed"
                            },
                            children = [
                                html.H1("Filters"),
                                html.Div(
                                    
                                    dbc.Accordion(
                                        [
                                            dbc.AccordionItem(
                                                [
                                                    # Have to go back and put in actual values used in DB
                                                    # Format Label:Value
                                                    html.H2("Drainage"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Drained":"Drained", 
                                                            "Undrained":"Undrained"},
                                                        value=["Drained", "Undrained"],
                                                        id="drainage_checklist",
                                                        inline=True
                                                    ),
                                                    html.H2("Shearing"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Compression":"Compression", 
                                                            "Extension":"Extension"},
                                                        value=["Compression", "Extension"],
                                                        id="shearing_checklist",
                                                        inline=True
                                                    ),
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
                                                        tooltip={"placement": "bottom", "always_visible": True}
                                                    ),
                                                    "Min Value:",
                                                    dcc.Input(id="anisotropy_min_value", type="number", min=0, max=1.0, value=1.0, style={'width': '80px'}),
                                                    "Max Value:",
                                                    dcc.Input(id="anisotropy_max_value", type="number", min=0, max=1.0, value=0, style={'width': '80px'}),
                                                    
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
                                                        tooltip={"placement": "bottom", "always_visible": True}
                                                    ),
                                                    "Min Value:",
                                                    dcc.Input(id="consolidation_min_value", type="number", min=0, max=1500, value=1500, style={'width': '80px'}),
                                                    "Max Value:",
                                                    dcc.Input(id="consolidation_max_value", type="number", min=0, max=1500, value=0, style={'width': '80px'}),

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
                                                    html.H2("Density"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Loose":"Loose",
                                                            "Dense":"Dense"},
                                                        value=["Loose", "Dense"],
                                                        id="density_checklist",
                                                        inline=True
                                                    ),
                                                    html.H2("Plasticity"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Plastic":"Plastic",
                                                            "Non-plastic":"Nonplastic",
                                                            "Unknown":"Unknown"},
                                                        value=["Plastic", "Non-plastic","Unknown"],
                                                        id="plasticity_checklist",
                                                        inline=True
                                                    ),
                                                    html.H2("PSD"),
                                                    dcc.Checklist(
                                                        options={
                                                            "Clay":"Clay",
                                                            "Sand":"Sand",
                                                            "Silt":"Silt"},
                                                        value=["Clay", "Sand","Silt"],
                                                        id="psd_checklist",
                                                        inline=True
                                                    ),
                                                ],
                                                title="Sample",
                                            ),
                                            dbc.AccordionItem(
                                                [
                                                    html.H2("Axial Strain Filter"),
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
                                                            0.5: "0.5"
                                                        },
                                                        value=[0,0.5], 
                                                        id='axial_slider'
                                                    ),
                                                    "Min Value:",
                                                    dcc.Input(id="axial_min_value", type="number", min=0, max=0.5, value=0.5, style={'width': '80px'}),
                                                    "Max Value:",
                                                    dcc.Input(id="axial_max_value", type="number", min=0, max=0.5, value=0, style={'width': '80px'}),
                                                    
                                                    html.H2("p' Filter"),
                                                    html.P(id="p_value"),
                                                    dcc.RangeSlider(
                                                        0,
                                                        500,
                                                        step=None,
                                                        value=[0,500], 
                                                        id='p_slider'
                                                    ), 
                                                    html.H2("Induced PWP Filter"),
                                                    html.P(id="pwp_value"),
                                                    dcc.RangeSlider(
                                                        0,
                                                        500,
                                                        step=None,
                                                        value=[0,500], 
                                                        id='pwp_slider'
                                                    ),
                                                    html.H2("Deviator stress (q) Filter"),
                                                    html.P(id="q_value"),
                                                    dcc.RangeSlider(
                                                        0,
                                                        500,
                                                        step=None,
                                                        value=[0,500], 
                                                        id='q_slider'
                                                    ),

                                                    html.H2("Void Ratio (e) Filter"),
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
                                                            1.0: "1.0"
                                                        },
                                                        value=[0,1], 
                                                        id='e_slider'
                                                    ),
                                                    ],
                                                title="Variables",
                                            ),
                                        ],
                                        always_open=True, flush=True,
                                    )
                                ),
                                
                            ]
                        ), 
                        width=3
                    ),
                    dbc.Col(
                        html.Div(
                            id = "dashboard",
                            children = [
                                dcc.Graph(id="axial_deviator_fig"),
                                dcc.Graph(id="axial_pwp_fig"), 
                                dcc.Graph(id="q_p_fig"),
                                dcc.Graph(id="axial_vol_fig"), 
                                dcc.Graph(id="e_logp_fig"),
                                dcc.Graph(id="stress_ratio_axial_fig")
                            ]
                        ), width=9 
                    ),
                    ]
                )
            ]
        )
    ],
    fluid=True,
)

@app.callback(
    [
    Output("consolidation_min_value","value"),
    Output("consolidation_max_value","value"),
    Output("consolidation_slider","value")    
    ],    
    [
     Input("consolidation_min_value","value"),
     Input("consolidation_max_value","value"),
     Input("consolidation_slider","value")
    ]   
)
def sync_consol_slider(start, end, slider):
    trigger_id = ctx.triggered_id

    consolidation_min_value = start if trigger_id == "consolidation_min_value" else slider[0]
    consolidation_max_value = end if trigger_id == "consolidation_max_value" else slider[1]
    consolidation_slider_value = slider if trigger_id == "consolidation_slider" else [consolidation_min_value, consolidation_max_value]

    return consolidation_min_value, consolidation_max_value, consolidation_slider_value

@app.callback(
    [
    Output("anisotropy_min_value","value"),
    Output("anisotropy_max_value","value"),
    Output("anisotropy_slider","value")    
    ],    
    [
     Input("anisotropy_min_value","value"),
     Input("anisotropy_max_value","value"),
     Input("anisotropy_slider","value")
    ]   
)
def sync_aniso_slider(start, end, slider):
    trigger_id = ctx.triggered_id

    anisotropy_min_value = start if trigger_id == "anisotropy_min_value" else slider[0]
    anisotropy_max_value = end if trigger_id == "anisotropy_max_value" else slider[1]
    anisotropy_slider_value = slider if trigger_id == "anisotropy_slider" else [anisotropy_min_value, anisotropy_max_value]

    return anisotropy_min_value, anisotropy_max_value, anisotropy_slider_value

@app.callback(
    [
    Output("axial_min_value","value"),
    Output("axial_max_value","value"),
    Output("axial_slider","value")    
    ],    
    [
     Input("axial_min_value","value"),
     Input("axial_max_value","value"),
     Input("axial_slider","value")
    ]   
)
def sync_axial_slider(start, end, slider):
    trigger_id = ctx.triggered_id

    axial_min_value = start if trigger_id == "axial_min_value" else slider[0]
    axial_max_value = end if trigger_id == "axial_max_value" else slider[1]
    axial_slider_value = slider if trigger_id == "axial_slider" else [axial_min_value, axial_max_value]

    return axial_min_value, axial_max_value, axial_slider_value

@app.callback(
    [
    Output("axial_deviator_fig", "figure"),
    Output("axial_pwp_fig", "figure"), 
    Output("q_p_fig", "figure"),
    Output("axial_vol_fig", "figure"), 
    Output("e_logp_fig", "figure"), 
    Output("stress_ratio_axial_fig", "figure")
    ],
    [Input("axial_slider", "value"), 
     Input("p_slider", "value"), 
     Input("pwp_slider", "value"), 
     Input("q_slider", "value"),
     Input("e_slider", "value")
     ], 
     )
def update_figure(selected_axial, selected_p, selected_pwp, selected_q, selected_e):
    filtered_df = df_combined[
        (df_combined["axial_strain"]>=selected_axial[0]) & (df_combined["axial_strain"]<=selected_axial[1])
        & (df_combined["p"]>=selected_p[0]) & (df_combined["p"]<=selected_p[1])
        & (df_combined["shear_induced_pwp"]>=selected_pwp[0]) & (df_combined["shear_induced_pwp"]<=selected_pwp[1])
        & (df_combined["deviator_stress"]>=selected_q[0]) & (df_combined["deviator_stress"]<=selected_q[1])
        & (df_combined["void_ratio"]>=selected_e[0]) & (df_combined["void_ratio"]<=selected_e[1])]

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
        x="deviator_stress", 
        y="p",
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
        title="Void ratio, e vs. log(p')").update_layout(
            xaxis_title="log(p')",
            yaxis_title="Void Ratio, e"
        )
    
    ### Stress ratio (p'/q) vs. Axial Strain
    stress_ratio_axial_fig = px.line(
        filtered_df, 
        x="axial_strain", 
        y=filtered_df["p"]/filtered_df["deviator_stress"],
        color="test_id", 
        title="Stress Ratio, p'/q vs. Axial Strain").update_layout(
            xaxis_title="Axial Strain",
            yaxis_title="Stress Ratio"
        )
    
    return axial_deviator_fig, axial_pwp_fig, q_p_fig, axial_vol_fig, e_logp_fig, stress_ratio_axial_fig

@app.callback(
    [Output("axial_value", "children"),
     Output("p_value", "children"),
     Output("pwp_value", "children"), 
     Output("q_value", "children"),
     Output("e_value", "children")],
    [Input("axial_slider", "value"), 
     Input("p_slider", "value"), 
     Input("pwp_slider", "value"), 
     Input("q_slider", "value"),
     Input("e_slider", "value")]
     )
def update_filters(selected_axial, selected_p, selected_pwp, selected_q, selected_e): 
    return f'Selected range: {selected_axial[0]} to {selected_axial[1]}', f'Selected range: {selected_p[0]} to {selected_p[1]}', f'Selected range: {selected_pwp[0]} to {selected_pwp[1]}', f'Selected range: {selected_q[0]} to {selected_q[1]}', f'Selected range: {selected_e[0]} to {selected_e[1]}'

port = "18019"


if len(sys.argv) > 1:
    port = sys.argv[1]

app.run_server(port=port, debug=True)

from urllib.request import urlopen
import json
import plotly.express as px
import pandas as pd
import boto3
import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

def load_data():
    s3_client = boto3.client('s3', region_name='us-east-2')
    bucket_name = 'harshil-storage'
    probs_name = 'civil_war_prob.csv'
    response = s3_client.get_object(Bucket=bucket_name, Key=probs_name)
    probs = pd.read_csv(response.get('Body'))
    countries_name = 'countries.json'
    response = s3_client.get_object(Bucket=bucket_name, Key=countries_name)
    countries = json.load(response.get('Body'))
    return probs, countries

def create_map():
    probs, countries = load_data() 

    map = folium.Map(location=[40, 0], zoom_start=1.5)
    folium.TileLayer('cartodbpositron', name = "Light Map", control=False).add_to(map)
 
    folium.Choropleth(
        geo_data=countries,
        name='choropleth',
        data=probs,
        columns=['country_text_id', 'civil_war_prob'],
        key_on='feature.id',
        fill_color='Reds',
        fill_opacity=1,
        line_opacity=0.2,
        legend_name='Probability of Civil War (%)',
        smooth_factor=0).add_to(map)

    style_function = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}

    highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}

    select = folium.features.GeoJson(
        data = countries,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=['name', 'prob'],
            aliases=['Country:', 'Probability of Civil War (%):'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px; outline: none;")
        )
    )

    map.add_child(select)
    map.keep_in_front(select)
    folium.LayerControl().add_to(map)

    css = """
    <style>
    path.leaflet-interactive:focus {
        outline: none;
    }
    </style>
    """

    map.get_root().header.add_child(folium.Element(css))

    map_html = map._repr_html_()

    with st.container():
        components.html(map_html, height=400, width=800)
    
    
if __name__ == '__main__':
    left, right = st.columns([1, 3])
    with left:
        st.header('here goes drop down menu')
    with right:
        st.header('Probability of Civil War')
        create_map()
    
    
    




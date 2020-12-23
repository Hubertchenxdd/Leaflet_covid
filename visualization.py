import branca.colormap as cm
import folium
import geopandas
from matplotlib import pyplot as plt
import pandas as pd
import shapely
import datetime
import numpy as np
import re
from folium import plugins
import os


TPS_mean = pd.read_excel('TPS_mean.xlsx')
delta = pd.read_excel('delta.xlsx')
gdf = geopandas.read_file('hackathon.shp')
TPS_mean = gdf.merge(TPS_mean.dropna())


linear = cm.LinearColormap(
    ['red', 'yellow', 'green'],
    vmin=0.6, vmax=1,
)

def geojson_features(tps):
    print('> Creating GeoJSON features...')
    features = []
    for _, row in tps.iterrows():
        coordinates_arr = []
        temp = re.findall(r"\-?\d+\.?\d*", row['geometry'])
        for i in range(0, len(temp), 2):
            coordinates_arr.append([float(temp[i]), float(temp[i+1])])
        times_arr=[]
        for i in range(0,len(coordinates_arr)):#each feature has a 'times' property with the same length as the coordinates array#所以times要和坐标长度一样
            times_arr.append(row['DATE'])
        feature = {
            'type': 'Feature',
            'id':row['segmentID'],
            'geometry': {
                'type':'LineString',
                'coordinates': coordinates_arr
            },
            'properties': {
                'times': times_arr,
                'style': {
                    'color': linear(row['TPS_GP']),
                    'weight': 3
                    }
            }
        }
        features.append(feature)
    return features

# Observing TPS from February to June
features_tps = geojson_features(TPS_mean[(TPS_mean.DATE > '2020-02-01') & (TPS_mean.DATE < '2020-06-28')])
m = folium.Map([47.65, -122.12], tiles='Stamen Terrain', zoom_start=10)

linear.caption = 'Traffic Performance Score'
m.add_child(linear)

jsonfile={'type': 'FeatureCollection',
        'features': features_tps}

plugins.TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features_tps}
        , period='P1D'
        , add_last_point = False
        , auto_play = True
        , loop = True
        , max_speed = 7
        , loop_button = True

        , time_slider_drag_update=True
    ).add_to(m)
m.save(os.path.join('result', 'Overall.html'))

# Comparing TPS during different stages of covid-19
dual1 = TPS_mean[(TPS_mean.DATE > '2020-02-01') & (TPS_mean.DATE < '2020-03-01')]
dual2 = TPS_mean[(TPS_mean.DATE > '2020-02-29') & (TPS_mean.DATE < '2020-03-29')]
dual3 = TPS_mean[(TPS_mean.DATE > '2020-05-30') & (TPS_mean.DATE < '2020-06-28')]

dual_1 = geojson_features(dual1)
dual_2 = geojson_features(dual2)
dual_3 = geojson_features(dual3)

dualmap = plugins.DualMap([47.65, -122.12], tiles='Stamen Terrain', zoom_start=10)

plugins.TimestampedGeoJson({'type': 'FeatureCollection',
                            'features': dual_1}
                            , period='P1D'
                            , add_last_point = False
                            , auto_play = True
                            , loop = True
                            , max_speed = 7
                            , loop_button = True
                            , time_slider_drag_update=True).add_to(dualmap.m1)

plugins.TimestampedGeoJson({'type': 'FeatureCollection',
                            'features': dual_2}
                            , period='P1D'
                            , add_last_point = False
                            , auto_play = True
                            , loop = True
                            , max_speed = 1
                            , loop_button = True
                            , time_slider_drag_update=True).add_to(dualmap.m2)
dualmap.save(os.path.join('result', 'beginning.html'))

dualmap = plugins.DualMap([47.65, -122.12], tiles='Stamen Terrain', zoom_start=10)

plugins.TimestampedGeoJson({'type': 'FeatureCollection',
                            'features': dual_1}
                            , period='P1D'
                            , add_last_point = False
                            , auto_play = True
                            , loop = True
                            , max_speed = 7
                            , loop_button = True
                            , time_slider_drag_update=True).add_to(dualmap.m1)

plugins.TimestampedGeoJson({'type': 'FeatureCollection',
                            'features': dual_3}
                            , period='P1D'
                            , add_last_point = False
                            , auto_play = True
                            , loop = True
                            , max_speed = 1
                            , loop_button = True
                            , time_slider_drag_update=True).add_to(dualmap.m2)
dualmap.save(os.path.join('result', 'latter.html'))

# Visualizing change of TPS with landuse

linear_1 = cm.LinearColormap(
    ['red', 'yellow', 'green'],
    vmin = 0, vmax = 0.22,
)

def geojson_delta(tps):
    print('> Creating GeoJSON features...')
    features = []
    for _, row in tps.iterrows():
        coordinates_arr = []
        temp = re.findall(r"\-?\d+\.?\d*", row['geometry'])
        for i in range(0, len(temp), 2):
            coordinates_arr.append([float(temp[i]), float(temp[i+1])])
        times_arr=[]
        for i in range(0,len(coordinates_arr)):#each feature has a 'times' property with the same length as the coordinates array#所以times要和坐标长度一样
            times_arr.append(row['Date'])
        feature = {
            'type': 'Feature',
            'id':row['segmentID'],
            'geometry': {
                'type':'LineString',
                'coordinates': coordinates_arr
            },
            'properties': {
                'times': times_arr,
                'style': {
                    'color': linear_1(row['TPS']),
                    'weight': 3
                    }
            }
        }
        features.append(feature)
    return features
features_tps = geojson_delta(delta)

currentLandUse = geopandas.read_file('General_Land_Use.shp')
currentLandUse = currentLandUse[currentLandUse.geometry.notnull()]
currentLandUseWithoutRoad = currentLandUse[currentLandUse['MASTER_CAT'] != 'ROW']
targetArea = currentLandUseWithoutRoad[(currentLandUseWithoutRoad['CITY_NM'] == 'Clyde Hill') | (currentLandUseWithoutRoad['CITY_NM'] == 'Edmonds') | (currentLandUseWithoutRoad['CITY_NM'] == 'Brier') | (currentLandUseWithoutRoad['CITY_NM'] == 'Lake Forest Park') | (currentLandUseWithoutRoad['CITY_NM'] == 'Bothell') | (currentLandUseWithoutRoad['CITY_NM'] == 'Kenmore') | (currentLandUseWithoutRoad['CITY_NM'] == 'Seattle') | (currentLandUseWithoutRoad['CITY_NM'] == 'Bellevue') | (currentLandUseWithoutRoad['CITY_NM'] == 'Kirkland') | (currentLandUseWithoutRoad['CITY_NM'] == 'Burien') | (currentLandUseWithoutRoad['CITY_NM'] == 'Renton') | (currentLandUseWithoutRoad['CITY_NM'] == 'Redmond') | (currentLandUseWithoutRoad['CITY_NM'] == 'Shoreline') | (currentLandUseWithoutRoad['CITY_NM'] == 'Issaquah') | (currentLandUseWithoutRoad['CITY_NM'] == 'Mountlake Terrace') | (currentLandUseWithoutRoad['CITY_NM'] == 'Lynnwood') | (currentLandUseWithoutRoad['CITY_NM'] == 'Medina') | (currentLandUseWithoutRoad['CITY_NM'] == 'Mercer Island') | (currentLandUseWithoutRoad['CITY_NM'] == 'Tukwila') | (currentLandUseWithoutRoad['CITY_NM'] == 'Newcastle')]
targetArea= targetArea[(targetArea['MASTER_CAT'] != 'PROW') & (targetArea['MASTER_CAT'] != 'Water')]

def my_color_function(feature):
    """Maps low values to green and high values to red."""
    regionUse = feature['properties']['MASTER_CAT']
    if regionUse == 'Intensive Urban':
        return '#FF0000'
    elif regionUse == 'Urban Character Residential':
        return '#F38A0D'
    elif regionUse == 'Industrial':
        return '#6B4D93'
    elif regionUse == 'Active Open Space and Recreation':
        return '#17C7E3'
    elif regionUse == 'Public':
        return '#05C1F9'
    elif regionUse == 'Rural Character Residential':
        return '#BCBC33'
    elif regionUse == 'Agricultural Area':
        return '#48E317'
    elif regionUse == 'Mineral Resource Area':
        return '#926127'
    elif regionUse == 'Natural Preservation and Conservation':
        return '#9DF905'
    elif regionUse == 'Forest Lands':
        return '#50953D'
    elif regionUse == 'Tribal':
        return '#AA2121'
    else:
        return '#CECECE'

m = folium.Map([47.65, -122.12], tiles='Stamen Terrain', zoom_start=10)

linear_1.caption = 'Change of Traffic Performance Score'
m.add_child(linear_1)

jsonfile={'type': 'FeatureCollection',
        'features': features_tps}

folium.GeoJson(
    targetArea,
    style_function=lambda feature: {
        'fillColor': my_color_function(feature),
        'weight': 0,
        'fillOpacity': 0.7,
    }
).add_to(m)

plugins.TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features_tps}
        , period='P1w'
        , add_last_point = False
        , auto_play = True
        , loop = True
        , max_speed = 7
        , loop_button = True

        , time_slider_drag_update=True
    ).add_to(m)
m.save(os.path.join('result', 'delta.html'))

import json
import os
import urllib
from math import acos, asin, cos, degrees, pi, radians, sin, sqrt

import pandas as pd
from bokeh.io import show, export_svg
from bokeh.models import Arrow, ColumnDataSource, VeeHead, Label
from bokeh.plotting import figure
from bokeh.sampledata import us_states, us_counties
import bokeh.sampledata 
from bokeh.palettes import all_palettes
from bokeh.tile_providers import Vendors, get_provider
from bokeh.transform import cumsum
from pyproj import Transformer
import numpy as np


# Copied from powersimdata/input/scenario_grid.py
def column_name_provider():
    """Provides column names for data frame.
    :return: (*dict*) -- dictionary of data frame columns name.
    """
    col_name_sub = ["name", "interconnect_sub_id", "lat", "lon", "interconnect"]
    col_name_bus = [
        "bus_id",
        "type",
        "Pd",
        "Qd",
        "Gs",
        "Bs",
        "zone_id",
        "Vm",
        "Va",
        "baseKV",
        "loss_zone",
        "Vmax",
        "Vmin",
        "lam_P",
        "lam_Q",
        "mu_Vmax",
        "mu_Vmin",
    ]
    col_name_bus2sub = ["sub_id", "interconnect"]
    col_name_branch = [
        "from_bus_id",
        "to_bus_id",
        "r",
        "x",
        "b",
        "rateA",
        "rateB",
        "rateC",
        "ratio",
        "angle",
        "status",
        "angmin",
        "angmax",
        "Pf",
        "Qf",
        "Pt",
        "Qt",
        "mu_Sf",
        "mu_St",
        "mu_angmin",
        "mu_angmax",
    ]
    col_name_plant = [
        "bus_id",
        "Pg",
        "Qg",
        "Qmax",
        "Qmin",
        "Vg",
        "mBase",
        "status",
        "Pmax",
        "Pmin",
        "Pc1",
        "Pc2",
        "Qc1min",
        "Qc1max",
        "Qc2min",
        "Qc2max",
        "ramp_agc",
        "ramp_10",
        "ramp_30",
        "ramp_q",
        "apf",
        "mu_Pmax",
        "mu_Pmin",
        "mu_Qmax",
        "mu_Qmin",
    ]
    col_name = {
        "sub": col_name_sub,
        "bus": col_name_bus,
        "bus2sub": col_name_bus2sub,
        "branch": col_name_branch,
        "plant": col_name_plant,
    }
    return col_name


# Copied from powersimdata/input/scenario_grid.py
def column_type_provider():
    """Provides column types for data frame.
    :return: (*dict*) -- dictionary of data frame columns type.
    """
    col_type_sub = ["str", "int", "float", "float", "str"]
    col_type_bus = [
        "int",
        "int",
        "float",
        "float",
        "float",
        "float",
        "int",
        "float",
        "float",
        "float",
        "int",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
    ]
    col_type_bus2sub = ["int", "str"]
    col_type_branch = [
        "int",
        "int",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "int",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
    ]
    col_type_plant = [
        "int",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "int",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
        "float",
    ]
    col_type = {
        "sub": col_type_sub,
        "bus": col_type_bus,
        "bus2sub": col_type_bus2sub,
        "branch": col_type_branch,
        "plant": col_type_plant,
    }
    return col_type


# Copied from powersimdata/input/scenario_grid.py
def link(keys, values):
    """Creates hash table
    
    :param iterable keys: key.
    :param iterable values: value.
    :return: (*dict*).
    """
    return {k: v for k, v in zip(keys, values)}


# Adapated from postreise/plot/projection_helpers.py
def project_latlon_to_xy(df, from_columns, to_columns):
    """Projects coordinates from lat/lon to x/y for plotting.
    
    :param pandas.DataFrame df: data frame to project.
    :param tuple from_columns: tuple of (str, str), names of (lat, lon) columns in df.
    :param tuple to_columns: tuple of (str, str), names of (lat, lon) columns to add.
    :return: (*pandas.DataFrame*) -- projected branch data frame.
    """
    
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    lat, lon = df[from_columns[0]].to_numpy(), df[from_columns[1]].to_numpy()
    x, y = transformer.transform(lat, lon)
    assign_dict = {to_columns[0]: x, to_columns[1]: y}
    new_df = df.assign(**assign_dict)
    return new_df


# Copied from postreise/plot/plot_states.py
def download_states_json():
    """Downloads json file containing coordinates for U.S. state outlines.

    :return: (*str*) -- path to json file.
    """
    shapes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shapes")
    os.makedirs(shapes_path, exist_ok=True)
    json_filename = "state_shapes.json"
    filepath = os.path.join(shapes_path, json_filename)
    if not os.path.isfile(filepath):
        url_base = "https://besciences.blob.core.windows.net/us-shapefiles/"
        r = urllib.request.urlopen(f"{url_base}{json_filename}")
        with open(filepath, "wb") as f:
            f.write(r.read())
    return filepath


# Copied from postreise/plot/plot_states.py
def get_state_borders():
    """Get state borders as a dictionary of coordinate arrays.

    :return: (*dict*) -- dictionary with keys from the specified shapefile column,
        values are dict with keys of {"lat", "lon"}, values are coordinates, padded by
        nan values to indicate the end of each polygon before the start of the next one.
    """
    try:
        json_filepath = download_states_json()
        with open(json_filepath, "r") as f:
            us_states_dat = json.load(f)
    except Exception:
        # In case we can't get the json file, use the bokeh shapes
        us_states_dat = us_states.data
    return us_states_dat

def get_county_borders():
    """Get county borders as a dictionary of coordinate arrays.

    :return: (*dict*) -- dictionary with keys from the specified shapefile column,
        values are dict with keys of {"lat", "lon"}, values are coordinates, padded by
        nan values to indicate the end of each polygon before the start of the next one.
    """
    # try:
    #     json_filepath = download_states_json()
    #     with open(json_filepath, "r") as f:
    #         us_states_dat = json.load(f)
    # except Exception:
    #     # In case we can't get the json file, use the bokeh shapes
    #     us_states_dat = us_states.data
    us_counties_dat = us_counties.data
    return us_counties_dat

# Adapted from postreise/plot/plot_states.py
def plot_state_lines(bokeh_figure, state_list=None, colors=None, us_states_dat=None):
    """Plots US state borders and allows color coding by state,
        for example to represent different emissions goals.

    :param bokeh.plotting.figure.Figure bokeh_figure: bokeh figure to plot on.
    :param list state_list: list of us state abbreviations. None defaults to all.
    :param dict us_states_dat: dictionary of state border lats/lons. If None, get
        from :func:`postreise.plot.plot_states.get_state_borders`.
    """
    # Get state borders if necessary, and project lat/lon to "EPSG:3857" either way
    if us_states_dat is None:
        us_states_dat = get_state_borders()
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    if state_list is None:
        state_list = list(set(us_states_dat.keys()) - {"AK", "HI", "DC", "PR"})
    state_xys = [
        transformer.transform(us_states_dat[s]["lats"], us_states_dat[s]["lons"])
        for s in state_list
    ]
    all_state_xs, all_state_ys = zip(*state_xys)
    
    # Plot state patches
    if colors is None:
        colors = "white"
    if isinstance(colors, str):
        colors = [colors for s in state_list]
    state_patch_info = {
        "xs": all_state_xs,
        "ys": all_state_ys,
        "color": colors,
        "state_name": state_list,
    }
    patch = bokeh_figure.patches(
        "xs",
        "ys",
        source=ColumnDataSource(state_patch_info),
        fill_alpha=1,
        fill_color="color",
        line_color='#252525',#"gray",
    )

def plot_counties_lines(bokeh_figure, county_list=None, colors=None, us_counties_dat=None):
    """Plots US county borders and allows color coding by county,
        for example to represent different emissions goals.

    :param bokeh.plotting.figure.Figure bokeh_figure: bokeh figure to plot on.
    :param list state_list: list of us state abbreviations. None defaults to all.
    :param dict us_counties_dat: dictionary of county border lats/lons. If None, get
        from :func:`postreise.plot.plot_states.get_state_borders`.
    """
    # Get state borders if necessary, and project lat/lon to "EPSG:3857" either way
    if us_counties_dat is None:
        us_counties_dat = get_county_borders()
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    if county_list is None:
        county_list= []
        for key in us_counties_dat.keys():
            if us_counties_dat[key]["state"]=='tx':
                county_list.append(key)
        # county_list = list(set(us_counties_dat.keys()) - {"AK", "HI", "DC", "PR"})
    county_xys = [
        transformer.transform(us_counties_dat[s]["lats"], us_counties_dat[s]["lons"])
        for s in county_list
    ]
    all_county_xs, all_county_ys = zip(*county_xys)
    

    weather_zone = ['Coast', 'East', 'Far West', 'North', 'North Central', 'South', 'South Central', 'West']
    county_weather_zone = {}
    for county in county_list:
        county_weather_zone[us_counties_dat[county]["name"]]=-1
    df_zip_code = pd.read_csv(".\data\loadzone_by_zip.csv")
    df_dict_zip_county = pd.read_csv(".\data\ZIP-COUNTY-FIPS_2017-06.csv")
    for index, row in df_zip_code.iterrows():
        zip_tmp = row["Svc. Address Zip Code"]
        weather_zone_tmp = row["Weather Zone Name"]
        county_tmp = df_dict_zip_county.loc[df_dict_zip_county["ZIP"]==zip_tmp].copy()
        if not county_tmp.empty:
            county_name_tmp = county_tmp["COUNTYNAME"].values[0][0:-7]
            try:
                if  county_weather_zone[county_name_tmp]==-1:
                    county_weather_zone[county_name_tmp]= weather_zone.index(weather_zone_tmp)
            except:
                print(county_name_tmp+" is not in the list")
    
    # set weather zones by force
    exception_list = ["Trinity", "San Jacinto", "Liberty", "Jefferson", "Orange", "Hardin", "Polk", "Tyler", 'Jasper', 'Newton', 'Sabine',
                    'San Augustine', 'Shelby', 'Panola', 'Harrison', 'Gregg', 'Upshur', 'Camp', 'Marion', 'Cass', 'Morris', 'Bowie', 'Walker',
                    'El Paso', 'Hudspeth']
    for i in exception_list:
        county_weather_zone[i] = -1
    county_weather_zone["Montague"] = 3
    county_weather_zone["Frio"] = 5
    county_weather_zone["Montague"] = 3

    # Plot county patches
    colors_candidate = all_palettes['OrRd'][len(weather_zone)+1][0:len(weather_zone)+1]
    # colors_candidate = all_palettes['Greens'][len(weather_zone)][0:len(weather_zone)-1]+all_palettes['Viridis'][11][-2:]
    colors = [colors_candidate[county_weather_zone[us_counties_dat[s]["name"]]] if county_weather_zone[us_counties_dat[s]["name"]]>=0 else "grey" for s in county_list]
    county_patch_info = {
        "xs": all_county_xs,
        "ys": all_county_ys,
        "color": colors,
        "county_name": county_list,
    }
    patch = bokeh_figure.patches(
        "xs",
        "ys",
        source=ColumnDataSource(county_patch_info),
        fill_alpha=0.3,
        fill_color="color",
        line_color="white",
    )

def get_dataframes_from_mpc(mpc):
    """Parses a case struct to data frames, adds extra info.
    
    :param scipy.io.matlab.mio5_params.mat_struct mpc: matpower mpc.
    :return: (*tuple*) -- (branch data frame, bus data frame, plant data frame).
    """
    
    branch = pd.DataFrame(
        mpc.branch, columns=column_name_provider()["branch"], index=mpc.branchid
    )
    branch = branch.astype(
        link(column_name_provider()["branch"], column_type_provider()["branch"])
    )
    bus = pd.DataFrame(
        mpc.bus, columns=column_name_provider()["bus"], index=mpc.busid
    )
    bus = bus.astype(
        link(column_name_provider()["bus"], column_type_provider()["bus"])
    )
    plant = pd.DataFrame(
        mpc.gen, columns=column_name_provider()["plant"], index=mpc.genid
    )
    plant = plant.astype(
        link(column_name_provider()["plant"], column_type_provider()["plant"])
    )
    plant["type"] = mpc.genfuel
    sub = pd.DataFrame(
        mpc.sub, columns=column_name_provider()["sub"], index=mpc.subid
    )
    sub = sub.astype(
        link(column_name_provider()["sub"], column_type_provider()["sub"])
    )
    bus2sub = pd.DataFrame(
        mpc.bus2sub, columns=column_name_provider()["bus2sub"], index=mpc.busid
    )
    bus2sub = bus2sub.astype(
        link(column_name_provider()["bus2sub"], column_type_provider()["bus2sub"])
    )
    # Add coordinates to {bus, plant, branch} & zone_id to {plant}
    bus2coord = (
        pd.merge(
            bus2sub[["sub_id"]], sub[["lat", "lon"]], left_on="sub_id", right_index=True
        )
        .set_index(bus2sub.index)
        .drop(columns="sub_id")
        .to_dict()
    )
    bus = bus.assign(
        lat=[bus2coord["lat"][i] for i in bus.index],
        lon=[bus2coord["lon"][i] for i in bus.index],
    )
    branch = branch.assign(
        from_lat=[bus2coord["lat"][i] for i in branch.from_bus_id],
        from_lon=[bus2coord["lon"][i] for i in branch.from_bus_id],
        to_lat=[bus2coord["lat"][i] for i in branch.to_bus_id],
        to_lon=[bus2coord["lon"][i] for i in branch.to_bus_id],
    )
    plant = plant.assign(
        lat=[bus2coord["lat"][i] for i in plant.bus_id],
        lon=[bus2coord["lon"][i] for i in plant.bus_id],
        zone_id=[bus.loc[i, "zone_id"] for i in plant.bus_id],
    )
    
    return branch, bus, plant


def haversine(lat1, lon1, lat2, lon2):
    _AVG_EARTH_RADIUS_MILES = 3958.7613
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    lat = lat2 - lat1
    lon = lon2 - lon1
    d = (
        2
        * _AVG_EARTH_RADIUS_MILES
        * asin(sqrt(sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lon * 0.5) ** 2))
    )
    return d


def plot_ac_powerflow(bokeh_figure, pf, branch):
    # Constants
    color = '#4292c6'#'#969696'  #"#8B36FF" #('#252525', '#525252', '#737373', '#969696', '#bdbdbd', '#d9d9d9', '#f7f7f7')
    alpha = 0.5
    width_scale_factor = 1/5 ########################1 / 500
    min_arrow_size = 5
    power_flow_threshold = 500
    distance_threshold = 20
    
    # Append extra data to branch dataframe
    branch = branch.copy()
    branch["powerflow"] = pf
    branch["dist"] = branch.apply(
        lambda x: haversine(x.from_lat, x.from_lon, x.to_lat, x.to_lon), axis=1
    )
    branch["arrow_size"] = 0###########################################pf.abs() * width_scale_factor + min_arrow_size
    branch = project_latlon_to_xy(
        branch, ("from_lat", "from_lon"), ("from_x", "from_y")
    )
    branch = project_latlon_to_xy(
        branch, ("to_lat", "to_lon"), ("to_x", "to_y")
    )
    
    # Prepare for bokeh plotting
    branch_source = ColumnDataSource(
        {
            "xs": branch[["from_x", "to_x"]].values.tolist(),
            "ys": branch[["from_y", "to_y"]].values.tolist(),
            "width": np.sqrt(branch["powerflow"].abs()) * width_scale_factor, ###########branch["powerflow"].abs() * width_scale_factor,
        }
    )
    
    # Plot lines at proper width
    bokeh_figure.multi_line(
        "xs",
        "ys",
        source=branch_source,
        color=color,
        alpha=alpha,
        line_width="width"
    )
    
    # Plot arrows
    positive_arrows = branch.loc[
        (branch.powerflow > power_flow_threshold) & (branch.dist > distance_threshold)
    ]
    negative_arrows = branch.loc[
        (branch.powerflow < -power_flow_threshold) & (branch.dist > distance_threshold)
    ]
    # Swap direction of negative arrows
    negative_arrows.rename(
        {'from_x': 'to_x', 'to_x': 'from_x', 'to_y': 'from_y', 'from_y': 'to_y'}
    )
    arrows = pd.concat([positive_arrows, negative_arrows])
    # arrows.apply(
    #     lambda a: bokeh_figure.add_layout(
    #         Arrow(
    #             end=VeeHead(
    #                 line_color='black', 
    #                 fill_color='gray', 
    #                 line_width=2,
    #                 fill_alpha=0.5, 
    #                 line_alpha=0.5, 
    #                 size=a["arrow_size"]
    #             ),
    #             x_start=a["from_x"],
    #             y_start=a["from_y"],
    #             x_end=a["to_x"],
    #             y_end=a["to_y"],
    #             line_color=color, 
    #             line_alpha=0.7,
    #         )
    #     ),
    #     axis=1,
    # )


def plot_pies(bokeh_figure, pie_data):
    # Constants
    pie_scale = 30
    
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    for pie in pie_data:
        x, y = transformer.transform(
            pie["coordinates"]["lat"], pie["coordinates"]["lon"]
        )
        plot_data = pd.Series(pie).drop("coordinates").reset_index(name="value")
        plot_data.rename({"index": "source"}, axis=1, inplace=True)

        #plot_data["color"] = all_palettes['Category20c'][len(plot_data)] #["blue", "red", "green"]###################
        plot_data["color"] = ['#3182bd', '#6baed6']
        total_size = plot_data.value.sum()
        plot_data["angle"] = plot_data["value"] * 2 * pi / total_size
        # bokeh_figure.wedge(
        #     x=x,
        #     y=y,
        #     radius=(total_size * pie_scale),
        #     start_angle=cumsum("angle", include_zero=True),
        #     end_angle=cumsum("angle"),
        #     line_color="white",
        #     fill_color="color",
        #     source=plot_data,
        #     legend_field="source",
        #     alpha=0.7,
        # )
        bokeh_figure.annular_wedge(
            x=x,
            y=y,
            inner_radius = np.maximum((total_size * pie_scale)-25000, 3000),
            outer_radius= (total_size * pie_scale),
            start_angle=cumsum("angle", include_zero=True),
            end_angle=cumsum("angle"),
            line_color="white",
            fill_color="color",
            source=plot_data,
            legend_field="source",
            alpha=0.8,
        )

def plot_gens(bokeh_figure, pie_data, colors, legend = 1):
    # Constants
    pie_scale = 30
    
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    for pie in pie_data:
        x, y = transformer.transform(
            pie["coordinates"]["lat"], pie["coordinates"]["lon"]
        )
        plot_data = pd.Series(pie).drop("coordinates").reset_index(name="value")
        plot_data.rename({"index": "source"}, axis=1, inplace=True)

        #plot_data["color"] = all_palettes['Category20c'][len(plot_data)] #["blue", "red", "green"]###################
        plot_data["color"] = colors
        total_size = plot_data.value.sum()
        plot_data["angle"] = plot_data["value"] * 2 * pi / total_size
        # bokeh_figure.wedge(
        #     x=x,
        #     y=y,
        #     radius=(total_size * pie_scale),
        #     start_angle=cumsum("angle", include_zero=True),
        #     end_angle=cumsum("angle"),
        #     line_color="white",
        #     fill_color="color",
        #     source=plot_data,
        #     legend_field="source",
        #     alpha=0.7,
        # )
        if legend == 1:
            bokeh_figure.annular_wedge(
                x=x,
                y=y,
                #inner_radius = np.maximum((total_size * pie_scale)-25000, 3000),
                inner_radius = 0,
                outer_radius= (total_size * pie_scale),
                start_angle=cumsum("angle", include_zero=True),
                end_angle=cumsum("angle"),
                line_color="white",
                fill_color="color",
                source=plot_data,
                legend_field="source",
                alpha=0.8,
            )
        else:
            bokeh_figure.annular_wedge(
                x=x,
                y=y,
                #inner_radius = np.maximum((total_size * pie_scale)-25000, 3000),
                inner_radius = 0,
                outer_radius= (total_size * pie_scale),
                start_angle=cumsum("angle", include_zero=True),
                end_angle=cumsum("angle"),
                line_color="white",
                fill_color="color",
                source=plot_data,
                alpha=0.8,
            )

def plot_text(bokeh_figure, pie_data):
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    text_index = 0
    weather_zone = ['Far West', 'North', 'West', 'South', 'North Central', 'South Central', 'Coast', 'East']
    for pie in pie_data:
        x, y = transformer.transform(
            pie["coordinates"]["lat"], pie["coordinates"]["lon"]
        )
        mytext = Label(x=x, y=y, text=weather_zone[text_index], text_font_style="bold", text_font_size="16px", text_alpha=0.5)
        bokeh_figure.add_layout(mytext)
        text_index +=1

def plot_texas_powerflow(pf=None, branch=None, pie_data=None, background_map=False, text_data=None, colors = None):
    # Initialize figure
    bokeh_figure = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
        output_backend="webgl",
        sizing_mode="scale_height",
        match_aspect=True,
        x_range=(-11.9e6, -10.2e6), 
        y_range=(2.7e6, 4.4e6),
    )
    bokeh_figure.xgrid.visible = False
    bokeh_figure.ygrid.visible = False
    bokeh_figure.output_backend = "svg"###############
    if background_map:
        # Tiles for map background
        bokeh_figure.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
    
    plot_state_lines(bokeh_figure)
    plot_counties_lines(bokeh_figure)

    if pf is not None:
        plot_ac_powerflow(bokeh_figure, pf, branch)  
    
##    if pie_data is not None:
##        plot_pies(bokeh_figure, pie_data)
##        plot_text(bokeh_figure, text_data)
    if pie_data is not None:
        for i in range(len(pie_data)):
            if i == 3:
                plot_gens(bokeh_figure, pie_data[i], colors[i], 1)
            else:
                plot_gens(bokeh_figure, pie_data[i], colors[i], 0)
        plot_text(bokeh_figure, text_data)
    
    export_svg(bokeh_figure, filename="fig3.svg")
    show(bokeh_figure)
    a=0



def test_counties(pf=None, branch=None, pie_data=None, background_map=False):
    # Initialize figure
    bokeh_figure = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
        output_backend="webgl",
        sizing_mode="scale_height",
        match_aspect=True,
        x_range=(-11.9e6, -10.2e6), 
        y_range=(2.7e6, 4.4e6),
    )
    bokeh_figure.xgrid.visible = False
    bokeh_figure.ygrid.visible = False
    bokeh_figure.output_backend = "svg"###############
    if background_map:
        # Tiles for map background
        bokeh_figure.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
    
    plot_counties_lines(bokeh_figure)
    show(bokeh_figure)
    a=0



if __name__=="__main__":
    a=0
    test_counties()

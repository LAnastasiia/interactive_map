# File: Anastasiia_Lazorenko_interactive_map.py
import folium
import pandas
import geocoder
import csv
import re
import html
import os.path
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import ArcGIS


def get_coordinates(adress):
    """
    (str) -> (list)

    This function finds lattitude and longitude of given address using
    geocoder.

    Precondition: the address must be appropriate, so it can be found on map.

    >>>get_coordinates('Mountain View, CA')
    [37.3860517, -122.0838511]
    >>>get_coordinates('Russell Winkelaar's flat, Toronto, Ontario, Canada)
    None
    >>>get_coordinates(Lviv, Ukraine)
    [49.839683, 24.029717]
    """
    try:
        geolocator = ArcGIS()
        # Get location in appropriate form.
        location = geolocator.geocode(adress)
        # Get coordinates of address.
        coordinates = (location.latitude, location.longitude)
        # Return coordinatess as [longitude and lattitude] list.
        print(coordinates)
        return coordinates
    except GeocoderTimedOut:
        # TIME Error
        return get_coordinates(adress)


def convert_to_csv(list_path):
    """
    (str) -> (file)

    This function reads info from .list file (name of file is function's
    parameter) and writes transformed data into .csv file, named
    'film_data_test.csv'. Information, written to csv-file is following:
    year of film's release, titles (in some cases also episode name),
    location of shooting(filming).
    Precondition: this function is written for specific file - locations.list
    from http://www.imdb.com. It can be renamed on Your computer, but it's
    content shouldn't be changed.

    """
    check_loc = dict()
    # Open .list file to read from it
    with open(list_path, 'r', encoding='utf-8', errors='ignore') as film_file:

        # Skip everything before actual data.
        for line in film_file:
            if line.startswith("LOCATIONS"):
                film_file.readline()
                break

        # Create .csv file to write into it
        with open('film_data_test.csv', 'w', encoding='utf-8',
                  errors='ignore') as csv_file:
            # Create writer object.
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Year', 'Titles', 'Lattitude', 'Longitude'])

            # ['film_name, date', /'episode_name' 'location', /'details']
            data_l = [line.strip('\n').split('\t') for line in film_file]
            # Delete unuseful lines in the end of file.
            del data_l[-3:]
            # Get rid of empty strings('') in the data_list.
            data_list = [list(filter(None, data_line)) for data_line in data_l]

            for data_line in data_list:
                # Make titles in appropriate format by replacing year info.
                title = ''.join(re.sub(r'\(\d{4}\)', '', data_line[0]))
                title_r = ''.join(re.sub(r'\(\?{4}\)',
                                  '', title)).replace('\"', '')
                # Use html module to represent titles in html appropriately.
                title_res = html.escape(title_r, quote=True)
                # Extract year from data_line[0].
                year = ''.join(re.findall(r'\(\d{4}\)',
                               data_line[0])).strip('()')
                # Replace details, (given with address in brackets) with ''.
                address = ''.join(re.sub(r'\(.+\)', '', data_line[1]))
                # Find coordinates of address.
                loc = get_coordinates(address)
                # Solving the case, when details are given before address.
                while not loc:
                    ind = address.index(',')
                    address = address[(ind+2):]
                    loc = get_coordinates(address)
                # Check if this location wasn't used before.
                if loc in check_loc:
                    check_loc[loc] += '<br>' + title_res
                    title_res = check_loc[loc]
                else:
                    check_loc[loc] = title_res
                if year:
                    # Combine data into list to write into csv file.
                    data_csv = [year, title_res, float(loc[0]), float(loc[1])]
                else:
                    data_csv = [0, title_res, float(loc[0]), float(loc[1])]
                csv_writer.writerow(data_csv)


def get_year_data_csv(csv_path, year):
    """
    (str) -> (pandas.core.frame.DataFrame)

    This function reads info from csv-file (named 'film_data_test.csv') and
    returns data frame according to year value.
    """
    # Get ifo from csv_file.
    with open(csv_path, 'r', encoding='utf-8', errors='ignore'):
        # Read data from file into DataFrame.
        df = pandas.read_csv(csv_path, sep=',',
                             dtype={'Year': 'int64',
                                    'Titles': 'object',
                                    'Lattitude': 'float64',
                                    'Longitude': 'float64'})
        # Extract DataFrame, which suits us by the year value.
        data_by_year = df[df['Year'] == year]
        occur = df['Year'].value_counts()
        return data_by_year


def get_decade_data_csv(csv_path, decade):
    with open(csv_path, 'r', encoding='utf-8', errors='ignore'):
        # Read data from file into DataFrame.
        df = pandas.read_csv(csv_path, sep=',',
                             dtype={'Year': 'int64',
                                    'Titles': 'object',
                                    'Lattitude': 'float64',
                                    'Longitude': 'float64'})
        # Extract only DataFrame, which suits us by the decade value.
        min_year = 1950 + (decade * 10)
        max_year = 1950 + ((decade + 1) * 10)
        data_by_decade = df[(min_year < df['Year']) & (df['Year'] < max_year)]
        return data_by_decade


def create_map(data_frame, home_address, year):
    """
    (pandas.core.frame.DataFrame) -> (file)

    This function takes data frame and builds an interactive map
    (using folium library), according to given data. It also creates feature
    group of markers to point places of filming on map.
    """
    # Build a simple map.
    f_map = folium.Map(location=[49.839683, 24.029717],
                            tiles='openstreetmap',
                            zoom_start=10)
    home_location = list(get_coordinates(home_address))
    if home_location:
        home = folium.Marker(location=home_location,
                             popup="My location",
                             icon=folium.Icon(icon='home', color='red'))
        f_map.add_child(home)

    # Create feature group of markers to point/mark filming set by year.
    f_year_gr = folium.FeatureGroup(name="​Films_year_{}".format(year))

    # Iterate through rows of extracted data.
    for data_tuple in data_frame.itertuples():
        ltt = data_tuple[3]
        lng = data_tuple[4]
        ttl = data_tuple[2]
        # Add marker for each DataFrame row.
        f_year_gr.add_child(folium.Marker([ltt, lng],
                                          popup=ttl,
                                          icon=folium.Icon(icon='video')))
    f_map.add_child(f_year_gr)

    travel_layer = folium.TileLayer('Stamen Terrain')
    paint_layer = folium.TileLayer('Stamen Watercolor')
    beautiful_layer = folium.TileLayer('Mapbox Bright')

    mark_on_cklick = folium.ClickForMarker(popup="My Marker")
    f_map.add_child(mark_on_cklick)

    f_map.add_child(folium.GeoJson(data=open('world.json', 'r',
                                    encoding='utf-8-sig').read(),
                                    name='population',
                                    style_function=lambda x: {'fillColor': 'green'
                                    if x['properties']['POP2005'] < 10000000
                                    else 'orange'
                                    if ((10000000 <= x['properties']['POP2005'])
                                    and (x['properties']['POP2005'] < 20000000))
                                    else 'red'}))
    # Add map layers to give an option of map's look like.
    travel_layer.add_to(f_map)
    paint_layer.add_to(f_map)
    beautiful_layer.add_to(f_map)
    # Create Layer Controller.
    folium.LayerControl().add_to(f_map)
    # Save created map as .html file.
    f_map.save("result_film_map.html")


def get_input():
    try:
        year = int(input("Enter year of films, which You want to see on map:"))
        home_address = input("Enter Your city and country name, separated by\
commas:")
        list_file_path = input("Enter the name of .list file to read from \
(include the pass, if needed):")
        assert (1950 < year < 2019)
        assert (os.path.isfile(list_file_path))
        return [year, home_address, list_file_path]
    except ValueError:
        print("You entered wrong values, please check them and try again.")
    except AssertionError:
        print("Year value must be greater than 1949 and less than 2019.")
    except AssertionError:
        print("Entered filename must be valid for appropriate work of \
program. Please check it and try again.")
    except EOFError:
        print("Try again.")
    return 0


def give_output():
    """
    This function prints a message to user in order to inform him about
    succesfull result of program.
    """
    print("Done")
    print(" Your request was succesfully processed. Results are available in \
.html file, called 'result_film_map'. \n You can find this file in the \
directory of this program. Also You may find a file with .csv extension.\n \
Please, do not delete, remove, change or rename it to get this program \
working faster.")


def main():
    user_info = get_input()
    if not user_info:
        user_info = get_input()
    # Values from user.
    year = user_info[0]
    home_address = user_info[1]
    list_file_path = user_info[2]
    # File is rewritten to .csv only once, then it may be used to make
    #program faster.
    if not os.path.isfile('film_data_for_map.csv'):
        convert_to_csv(list_file_path)
    data_frames = get_year_data_csv('film_data_test.csv', year)
    create_map(data_frames, home_address, year)
    give_output()
main()

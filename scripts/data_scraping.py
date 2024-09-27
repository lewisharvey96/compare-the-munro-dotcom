import pandas as pd
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import time
import enchant
import matplotlib.pyplot as plt
import numpy as np

# ### Data Scraping of Munros and Routes from WalkHighlands
# https://www.walkhighlands.co.uk/munros/munros-a-z

base_url = "https://www.walkhighlands.co.uk"
# a2z_url = f"{base_url}/munros/munros-a-z"
# a2z_doc = requests.get(a2z_url).content

# +
# soup = BeautifulSoup(a2z_doc, 'html.parser')
# munro_paths = list(set([f"{base_url}/munros/{i.a.get('href')}" for i in soup.find_all('tr')])-set([a2z_url]))
# -

with open("munro_urls.txt") as f:
    munro_paths_text = f.read()
munro_paths = eval(munro_paths_text)

len(munro_paths), munro_paths[0], munro_paths[-1]


# ## Save each page and extract data for each munro
#  - Name
#  - Region
#  - Altidue
#  - Routes description links

# Get and store all the htmls

# +
def _save_munro_page_html(url):
    content = requests.get(url).content
    url_safe = url.split("/")[-1].lower().strip().replace("-", "_")
    filename = f'./html_pages/{url_safe}.html'
    with open(filename, 'wb') as f:
        f.write(content)

# for url in tqdm(munro_paths):
#     _save_munro_page_html(url)


# -

# Search through the html pages for data

def _get_data_from_munro(munro_url):
    url_safe = munro_url.split("/")[-1].lower().strip().replace("-", "_")
    filename = f'./html_pages/{url_safe}.html'
    with open(filename, 'rb') as f:
        test_munro_page = f.read()
    munro_soup = BeautifulSoup(test_munro_page, 'html.parser')
    name = munro_soup.title.text.split("-")[0].strip()
    region = [i.a.text for i in munro_soup.find_all('p') if "Region" in i.text][0]
    altitude = [int(i.text.split(" ")[1]) for i in munro_soup.find_all('p') if "Altitude" in i.text][0]
    route_links = [f"{base_url}/{i.a.get('href')}".strip() for i in munro_soup.find_all('p') if i.b and i.a if ('www' not in i.a.get('href', ''))]
    filtered_links = [
        i for i in route_links if (
            (
            ("breakfast" not in i) and ("hotels" not in i) and ("cottages" not in i) and ("hostels" not in i)
        ) or (
            ("mount-keen" in i) or ("ben-hope" in i)
        )
        ) and ((len(i.replace("//", "/").split("/"))>3))]
    return {
        "name":name,
        "region":region,
        "altitude":altitude,
        "page_link": munro_url,
        "route_links":filtered_links,
    }


munro_records = []
failed_munro_urls = []
for munro_url in tqdm(munro_paths):
    try:
        record = _get_data_from_munro(munro_url)
        munro_records.append(record)
    except:
        failed_munro_urls.append(munro_url)

[i for i in munro_records if not i["route_links"]], failed_munro_urls

# pd.DataFrame(munro_records).to_csv("all_munro_pages_data.csv",index=False)
munros_df = pd.read_csv('all_munro_pages_data.csv').sort_values("name")
munros_df["route_links"] = [eval(i) for i in munros_df["route_links"]]
munros_df.head()

# ## Extract data for each route
# -  RouteName
# -  Distance
# -  Time (min,max)
# -  Ascent
# -  Start Grid Ref
# -  Summits climbed
# -  Start point lat and lon
# -  User rating
# -  Grade
# -  Bog Factor

route_urls = list(set(munros_df.explode("route_links").route_links))
route_urls[0]

url


# +
def _save_route_page_html(url):
    content = requests.get(url.strip()).content
    url_safe = url.split("/")[-1].lower().strip().replace("-", "_").replace(".shtml", "")
    filename = f'./html_pages/routes/{url_safe}.html'
    with open(filename, 'wb') as f:
        f.write(content)

# for url in tqdm(route_urls):
#     _save_route_page_html(url)


# -

# #### Manually handle some tricky ones
#
# - The Lairig Ghru and Lairig an Laoigh aren't really direct routes so don't worry about them but leave this in with no munros explicity mentioned (handled above)
# - Manually parse the time min and max from Cairn toul and Bideinachoiresheasgaich since they are in an unusual format i.e. "12 hours or 3 days"

def _get_data_from_route(route_url):
    url_safe = route_url.split("/")[-1].lower().strip().replace("-", "_").replace(".shtml", "")
    filename = f'./html_pages/routes/{url_safe}.html'
    with open(filename, 'rb') as f:
        test_route_page = f.read()
    route_soup = BeautifulSoup(test_route_page, 'html.parser')
    
    route_name = route_soup.title.text.split(",")[0].strip()
    walk_stats = dict(zip([i.text for i in route_soup.find_all("dl")[0].find_all("dt")], [i.text for i in route_soup.find_all("dl")[0].find_all("dd")]))
    distance = float(walk_stats['Distance'].split("/")[0].strip().replace("km", ""))
    if route_name == 'Cairn Toul - Braeriach traverse (Walkhighlands)':
        time_min = float(13)
        time_max = float(16) # guess
    elif route_name == "Bidein a' Choire Sheasgaich and Lurg Mhòr (Walkhighlands)":
        time_min = float(16)
        time_max = float(19) # guess
    else:
        time_min = float(walk_stats['Time'].split("-")[0].strip())
        time_max = float(walk_stats['Time'].split("-")[1].replace("hours", "").strip())
    ascent = float(walk_stats['Ascent'].replace("m (Profile)", "").strip())
    start_grid_ref = walk_stats["Start Grid Ref"]
    def _parse_munros(_route_soup):
        try:
            return list(set([i.text for i in _route_soup.find_all("dl")[1]])-set(['Munro']))
        except:
            return []
    munros_climbed = _parse_munros(route_soup)
    start_lat, start_lon = [i.get('href') for i in route_soup.find_all('a') if i.text == 'Open in Google Maps'][0].split("/")[-2].split(",")
    ratings = []
    for i in route_soup.find_all("span"):
        try:
            potential_rating = eval(i.text)
            if 0 <= potential_rating <=5:
                ratings.append(potential_rating)
        except:
            ...
    ratings.remove(5)
    rating = ratings[0]
    grade = len([i for i in route_soup.find_all("div") if i.get("title") == 'Grade of Walk'][0].find_all("img"))
    bog_factor = len([i for i in route_soup.find_all("div") if i.get("title") == 'Bog Factor'][0].find_all("img"))
    
    return {
        "route_name":route_name, 
        "distance":distance, 
        "time_min":time_min, 
        "time_max":time_max, 
        "ascent":ascent, 
        "start_grid_ref":start_grid_ref, 
        "munros_climbed":munros_climbed, 
        "start_lat":start_lat, 
        "start_lon":start_lon, 
        "rating":rating, 
        "grade":grade, 
        "bog_factor":bog_factor,
        "route_page_link": route_url,
    }


# +
route_records = []
failed_route_records = []
for munro_record in tqdm(munro_records):
    name = munro_record["name"]
    for route_url in munro_record["route_links"]:
        try:
            record = _get_data_from_route(route_url)
            route_records.append({"name": name} | record)
        except:
            failed_route_records.append(route_url)

print(set(failed_route_records))
# -

# routes_df = pd.DataFrame(route_records)
# routes_df.to_csv("all_route_pages_data.csv",index=False)
routes_df = pd.read_csv('all_route_pages_data.csv').sort_values("name")
routes_df["munros_climbed"] = [eval(i) for i in routes_df["munros_climbed"]]
routes_df.head()

# #### Add Calorie estimate / energy usage feature
#
# Calories Burned = [Body Weight (in kg) x 0.0215 + (average speed (in km/h) x 0.0189) + (Total Elevation Gained (in meters) x 0.0001167)] x Distance Hiked (in km)

MET = 3 # for hiking
bodyweight_ref = 1
g = 9.8
human_body_eff = 0.2
joules_per_calorie = 4184

routes_df['time_median'] = routes_df[['time_min', 'time_max']].median(axis=1).values
d = routes_df
calories_ser = (d['time_median']*MET*bodyweight_ref)+((bodyweight_ref*g*d['ascent'])/(human_body_eff*joules_per_calorie))
routes_df['calories_per_kg'] = calories_ser

routes_df['number_of_munros'] = [len(i) for i in routes_df['munros_climbed']]

# +
# routes_df.to_csv("all_route_add_features.csv",index=False)
# -

plt.scatter(x=d['time_median'], y=d['ascent'], c=calories_ser, marker="^")
plt.colorbar(label='Calories per kg of bodyweight')
plt.xlabel('hours')
plt.ylabel('elevation gain (m)')
plt.grid(True, linestyle="--")

plt.scatter(x=d['ascent'], y=d['distance'], c=calories_ser, marker="^")
plt.colorbar(label='Calories per kg of bodyweight')
plt.xlabel('elevation gain (m)')
plt.ylabel('distance (km)')
plt.grid(True, linestyle="--")

x = routes_df['ascent']
y = routes_df['distance']
z = routes_df["calories_per_kg"]
plt.tricontourf(x, y, z)
plt.colorbar(label='Calories per kg of bodyweight')
plt.xlabel('elevation gain (m)')
plt.ylabel('distance (km)')
plt.scatter(x=d['ascent'], y=d['distance'], marker=".", color="black", label="Munro Route")
plt.legend()

x = routes_df['ascent']
y = routes_df['distance']
z = routes_df["time_median"]
plt.tricontourf(x, y, z)
plt.colorbar(label='hours to complete')
plt.xlabel('elevation gain (m)')
plt.ylabel('distance (km)')
plt.scatter(x=d['ascent'], y=d['distance'], marker=".", color="black", label="Munro Route")
plt.legend()



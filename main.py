from emailscraper import append_emails
from osm import query_osm_businesses
import os
from dotenv import load_dotenv
import json

# Load variables from .env file into environment
load_dotenv()


bT = Trondheim =  [63.430502,10.395053]
bB = Bergen =  [60.3913,5.3221]

# Access them just like Node.js
lat = float(os.getenv("LAT"))
lon = float(os.getenv("LON"))
r = float(os.getenv("RADIUS"))


b0 = query_osm_businesses(lat, lon, radius=r)

append_emails(b0)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(b0, f, ensure_ascii=False, indent=4)

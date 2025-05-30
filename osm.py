import requests
import time

def reverse_geocode(lat, lon):
    """Get a full address string from coordinates using Nominatim."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1
    }

    response = requests.get(url, params=params, headers={"User-Agent": "business-finder"})
    if response.status_code == 200:
        data = response.json()
        address = data.get("address", {})
        street = address.get("road", "")
        housenumber = address.get("house_number", "")
        city = address.get("city") or address.get("town") or address.get("village") or ""
        postcode = address.get("postcode", "")
        country = address.get("country", "")
        
        # Build the full address string
        parts = [part for part in [f"{housenumber} {street}".strip(), city, postcode, country] if part]
        return ", ".join(parts)
    else:
        return ""

def query_osm_businesses(lat, lon, radius=100):
    query = f"""
    [out:json];
    (
      node(around:{radius},{lat},{lon})["name"];
      way(around:{radius},{lat},{lon})["name"];
    );
    out center tags;
    """

    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query})

    if response.status_code != 200:
        print("Error fetching data:", response.status_code)
        return []

    data = response.json()
    results = []

    for element in data['elements']:
        tags = element.get('tags', {})
        website = tags.get("website") or tags.get("contact:website")
        email = tags.get("contact:email") or tags.get("email")

        if not website and not email:
            continue

        # Determine coordinates (node or way with center)
        if element['type'] == 'node':
            lat_, lon_ = element['lat'], element['lon']
        else:
            lat_, lon_ = element['center']['lat'], element['center']['lon']

        # Reverse geocode to get address string
        address_str = reverse_geocode(lat_, lon_)
        time.sleep(0.1)  # Respect Nominatim's rate limits

        business = {
            "name": tags.get("name"),
            "website": website,
            "email": [email],
            "address": address_str
        }

        results.append(business)

    return results



bT = Trondheim =  [63.430502,10.395053]
bB = Bergen =  [60.3913,5.3221]
       # in meters

def demo():
    businesses = query_osm_businesses(bT[0], bT[1])
    for b in businesses:
        print(b)

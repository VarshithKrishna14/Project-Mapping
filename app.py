#this file contains the entire data fetched from the NPI API for every MSA entered

#vivnovation_54 file contains the working code with map






import google.generativeai as genai
GEMINI_API_KEY = "AIzaSyC-_oUfWDeonZBi-hr_VD9q_lLRpmUdSlI" 
genai.configure(api_key=GEMINI_API_KEY)



from flask import Flask, render_template, request
import requests
import folium
import pandas as pd
import google.generativeai as genai

app = Flask(__name__)

# Load dataset once for efficiency
file_path = "Cleaned_ZIP_MSA.xlsx"
df = pd.read_excel(file_path, dtype={"ZIP": str})  


def get_zipcodes_for_msa(msa_name):
    """Extract ZIP codes from the dataset based on the given MSA."""
    matching_rows = df[df["MSA_Name"].str.contains(msa_name, case=False, na=False)]
    if matching_rows.empty:
        print(f"No ZIP codes found for MSA: {msa_name}")
        return []
    
    zip_codes = matching_rows["ZIP"].unique().tolist()
    #print(f"Extracted ZIP codes for {msa_name}: {zip_codes}")  # ✅ Debugging
    return zip_codes

def fetch_physicians(msa_name):
    """Fetch physician data from the NPI registry API based on ZIP codes."""
    
    physician_list = []  # Reset for fresh request

    # Step 1: Get ZIP codes for the entered MSA
    zip_codes = get_zipcodes_for_msa(msa_name)
    if not zip_codes:
        return []

    # Step 2: Query NPI API using ZIP codes
    for zip_code in zip_codes:
        api_url = f'https://npiregistry.cms.hhs.gov/api/?postal_code={zip_code}&limit=10&version=2.1'
        response = requests.get(api_url)

        if response.status_code != 200:
            print(f"Failed API Request for ZIP {zip_code} - Status Code: {response.status_code}")
            continue

        data = response.json()
        results = data.get("results", [])
        
        # if not results:
        #     print(f"ZIP {zip_code}: No physician data found.")
        #     continue

       # print(f"ZIP {zip_code}: {len(results)} results found.")  # ✅ Debugging

        # Step 3: Extract relevant data
        for result in results:
            if "addresses" in result and len(result["addresses"]) > 0:
                address = result["addresses"][0]
                lat = address.get("latitude")
                lon = address.get("longitude")

                # Fixing full address
                full_address = f"{address.get('address_1', '')}, {address.get('city', '')}, {address.get('state', '')} {address.get('postal_code', '')}"

                basic_info = result.get("basic", {})
                name = basic_info.get("organization_name", None)
                if not name:
                    first_name = basic_info.get("first_name", "Unknown")
                    last_name = basic_info.get("last_name", "Physician")
                    name = f"{first_name} {last_name}".strip()

                if lat and lon:
                    physician_list.append({
                        "name": name,
                        "address": full_address,
                        "lat": float(lat),
                        "lon": float(lon)
                    })
                
                #print(f"{msa_name} -> ZIP {zip_code}: {name} @ {full_address}")

    return find_physician_groups(physician_list)

def find_physician_groups(physicians):
    """Use Gemini AI to find Physician Groups (PGs) and return them."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    pg_list = []
    
    print("\n🔍 Finding Physician Groups using Gemini AI...\n")

    for physician in physicians:
        prompt = f"Find the physician group for {physician['name']} in {physician['address']}."
        
        try:
            response = model.generate_content(prompt)
            
            # Debugging: Print the full response
            print(f"📜 Gemini Raw Response: {response.text}")  

            pg_name = response.text.strip() if response.text else "Unknown PG"
        except Exception as e:
            print(f"⚠️ Gemini API Error: {str(e)}")
            pg_name = "Unknown PG"

        print(f"🩺 {physician['name']} ➝ PG: {pg_name}")  # ✅ Print Gemini output

        pg_list.append({
            "name": physician["name"],
            "pg": pg_name,
            "lat": physician["lat"],
            "lon": physician["lon"]
        })

    return pg_list

@app.route('/', methods=['GET', 'POST'])
def index():
    physician_groups = []  # Reset for fresh request

    if request.method == 'POST':
        msa_name = request.form.get('msa_name', '').strip()

        if msa_name:
            print(f"User entered MSA: {msa_name}")  
            physician_groups = fetch_physicians(msa_name)

    # Default map location (New York) if no results found
    lat_avg, lon_avg = 40.7128, -74.0060  
    if physician_groups:
        lat_avg = sum(pg["lat"] for pg in physician_groups) / len(physician_groups)
        lon_avg = sum(pg["lon"] for pg in physician_groups) / len(physician_groups)

    # Create Map
    map = folium.Map(location=[lat_avg, lon_avg], zoom_start=10)
    for pg in physician_groups:
        folium.Marker(
            location=[pg["lat"], pg["lon"]],
            popup=f"{pg['name']} (PG: {pg['pg']})",
            icon=folium.Icon(color='blue')
        ).add_to(map)

    map.save("static/map.html")

    return render_template("index.html", physician_groups=physician_groups)

if __name__ == '__main__':
    app.run(debug=True)

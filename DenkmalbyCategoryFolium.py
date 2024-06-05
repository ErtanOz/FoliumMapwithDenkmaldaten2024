import folium
from folium.plugins import MarkerCluster
import json

# Create a map centered around Cologne, Germany
m = folium.Map(location=[50.9375, 6.9603], zoom_start=12)

# Add a marker cluster to the map
marker_cluster = MarkerCluster().add_to(m)

# Add markers to the map
for feature in denkmaeler_data['features']:
    properties = feature['properties']
    coordinates = feature['geometry']['coordinates']
    
    # Popup content
    popup_content = f"""
    <strong>{properties.get("kurzbezeichnung")}</strong><br>
    <strong>Address:</strong> {properties.get("strasse")}<br>
    <strong>District:</strong> {properties.get("stadtbezirk")}<br>
    <strong>Category:</strong> {properties.get("kategorie")}<br>
    <strong>Year of Construction:</strong> {properties.get("baujahr")}<br>
    """
    if properties.get("foto") == 'ja' and properties.get("fotourl"):
        popup_content += f'<img src="{properties.get("fotourl")}" width="200px"><br>'
    
    # Create and add marker to the cluster
    folium.Marker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON stores coordinates as [longitude, latitude]
        popup=folium.Popup(popup_content, max_width=300)
    ).add_to(marker_cluster)

# Save the map to an HTML file
map_path = '/mnt/data/denkmaeler_map.html'
m.save(map_path)

# Create an enhanced HTML file with filter functionality
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Denkmaeler Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <style>
        #map {{ height: 90vh; }}
        #controls {{ height: 10vh; padding: 10px; background: #f4f4f4; }}
    </style>
</head>
<body>
    <div id="controls">
        <label for="filter">Filter by Category: </label>
        <select id="filter">
            <option value="all">All</option>
            {''.join([f'<option value="{category}">{category}</option>' for category in sorted(set(p['kategorie'] for p in (f['properties'] for f in denkmaeler_data['features'])))])}
        </select>
    </div>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
    <script>
        var map = L.map('map').setView([50.9375, 6.9603], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        var markerCluster = L.markerClusterGroup().addTo(map);
        
        var data = {json.dumps(denkmaeler_data)};

        function addMarkers(data) {{
            data.features.forEach(function(feature) {{
                var properties = feature.properties;
                var coordinates = feature.geometry.coordinates;

                var popupContent = `
                    <strong>${{properties.kurzbezeichnung}}</strong><br>
                    <strong>Address:</strong> ${{properties.strasse}}<br>
                    <strong>District:</strong> ${{properties.stadtbezirk}}<br>
                    <strong>Category:</strong> ${{properties.kategorie}}<br>
                    <strong>Year of Construction:</strong> ${{properties.baujahr}}<br>
                `;
                if (properties.foto === 'ja' && properties.fotourl) {{
                    popupContent += `<img src="${{properties.fotourl}}" width="200px"><br>`;
                }}
                
                var marker = L.marker([coordinates[1], coordinates[0]])
                    .bindPopup(popupContent);
                markerCluster.addLayer(marker);
            }});
        }}

        addMarkers(data);

        document.getElementById('filter').addEventListener('change', function(e) {{
            var category = e.target.value;
            markerCluster.clearLayers();
            if (category === 'all') {{
                addMarkers(data);
            }} else {{
                var filteredData = {{
                    "type": "FeatureCollection",
                    "features": data.features.filter(function(feature) {{
                        return feature.properties.kategorie === category;
                    }})
                }};
                addMarkers(filteredData);
            }}
        }});
    </script>
</body>
</html>
"""

# Write the enhanced HTML content to a file
enhanced_map_path = '/mnt/data/denkmaeler_enhanced_map.html'
with open(enhanced_map_path, 'w') as file:
    file.write(html_content)

enhanced_map_path

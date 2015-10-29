var geoJSON_layer = new L.geoJson();
$.getJSON('./js/convex-hull.json', function(data) {
    geoJSON_layer = L.geoJson(data, {
        'color': '#1e90ff',
        'width': 5,
        'opacity': 0.95,
        onEachFeature: function(feature, layer) {
            if (feature.properties) {
                layer.bindPopup(feature.properties['label']);
            }
        },
        pointToLayer: function (feature, latlng) {
            if (feature.properties) {
                switch (feature.properties.style) {
                    case "#1":
                        color = '#B22222';
                        break;
                    case "#2":
                        color = '#3D6D1C';
                        break;
                    default:
                        color = '#AC66AF';
                        break;
                }
                return new L.CircleMarker(latlng, {
                    radius: 5,
                    color: color,
                    weight: 1,
                    opacity: 0.8,
                    fillOpacity: 0.4
                });
            } else {
                return new L.CircleMarker(latlng, {
                    radius: 10,
                    color: '#123456',
                    weight: 1,
                    opacity: 0.8,
                    fillOpacity: 0.4
                });
            }
        },
    });
    var map = L.map('map', {
        'center': [48.7900, 44.8000],
        'zoom': 12,
        'layers': [
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            }),
            geoJSON_layer
        ]
    });
});

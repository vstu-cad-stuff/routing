var map = 0;
var geoJSON_layer = 0;

function load_data(data) {
  if (map) {
    map.removeLayer(geoJSON_layer);
  }
  $.getJSON('./data/' + data + '.json', function(data) {
      geoJSON_layer = L.geoJson(data, {
          style: function(feature) {
              if (feature.properties.color) {
                  color = feature.properties.color;
              } else {
                  color = '#123456';
              }
              return {
                  'color': color,
                  'width': 5,
                  'opacity': 0.95
              };
          },
          onEachFeature: function(feature, layer) {
              if (feature.properties) {
                  layer.bindPopup(feature.properties['label']);
              }
          },
          pointToLayer: function (feature, latlng) {
              if (feature.properties) {
                  if (feature.properties.color) {
                      color = feature.properties.color;
                  } else {
                      color = '#AC66AF';
                  }
                  return new L.CircleMarker(latlng, {
                      radius: 8,
                      color: color,
                      weight: 4,
                      opacity: 0.8,
                      fillOpacity: 0.8
                  });
              } else {
                  return new L.CircleMarker(latlng, {
                      radius: 8,
                      weight: 1,
                      opacity: 1,
                      fillOpacity: 0.35
                  });
              }
          },
      });
      if (map) {
        map.addLayer(geoJSON_layer);
      } else {
          map = L.map('map', {
            'center': [48.7900, 44.8000],
            'zoom': 12,
            'layers': [
                L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                }),
                geoJSON_layer
            ]
        });
      }
      map.fitBounds(geoJSON_layer);
  });
}

var map = 0;
var geoJSON_layer = 0;
var layer = 0;
var info = L.control();

function highlightFeature(e) {
  layer = e.target;
  layer.setStyle({
    weight: 8,
    color: '#000',
    dashArray: '',
    fillOpacity: 0.5,
    opacity: 0.6
  });
  if (!L.Browser.ie && !L.Browser.opera) {
    layer.bringToFront();
  }
  info.update(layer.feature.properties);
}

function resetHighlight(e) {
  geoJSON_layer.resetStyle(e.target);
  info.update();
}

function zoomToFeature(e) {
  map.fitBounds(e.target.getBounds());
}

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
          layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: zoomToFeature
          });
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
        var slider = L.control({position: 'bottomleft'});
        slider.onAdd = function (map) {
          this._div = L.DomUtil.create('div', 'slider');
          this._div.innerHTML = 
            '<button id="decrement" onclick="present(-1);"><</button>' + 
            '<h4 id="dataset">100 кластеров / 8 маршрутов</h4>' +
            '<button id="increment" onclick="present(+1);">></button>';
          return this._div;
        };
        slider.addTo(map);
        info.onAdd = function (map) {
          this._div = L.DomUtil.create('div', 'info');
          this._div.innerHTML = '<h4>Выбранный объект</h4>';
          this.update();
          return this._div;
        };
        info.update = function (props) {
          this._div.innerHTML = '<h4>Выбранный объект</h4>' + 
            (props ? '<b>' + props.label + '</b>' : '<b>--</b>');
        };
        info.addTo(map);
    }
    map.fitBounds(geoJSON_layer);
  });
}

var select_index = 0;
var distance_sum = 0;
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
          this._div.innerHTML = '<h4>Выбранны объект</h4>';
          this.update();
          return this._div;
        };
        info.update = function (props) {
          if (props) {
            regexp_n = /[0-9]{1,}/;
            regexp_a = /[a-zA-Z]{1,}/;
            route_num = parseInt(regexp_n.exec(props.label)) - 2;
            route_name = regexp_a.exec(props.label) + ' №' + (route_num + 1);
          }
          this._div.innerHTML = '<h4>Выбранный объект</h4>' +
            (props ? '<b>' + route_name + '</b>' : '<b>--</b>') +
            '<h4>Длина маршрута</h4>' +
            '<b>' + (props ? distances[select_index][route_num] + ' м' : '--') + '</b>' +
            '<h4>Суммарная длина</h4>' + '<b id="total_distance">' + distance_sum + ' м</b>';
        };
        info.addTo(map);
    }
    map.fitBounds(geoJSON_layer);
  });
}

function present(inc) {
  var data_list = [
      'result-100-8', 'result-100-10', 'result-100-12', 'result-100-14', 'result-100-16', 'result-100-18',
      'result-150-8', 'result-150-10', 'result-150-12', 'result-150-14', 'result-150-16', 'result-150-18',
      'result-200-8', 'result-200-10', 'result-200-12', 'result-200-14', 'result-200-16', 'result-200-18']
  select_index += inc;
  if (select_index < 0 ) {
    select_index = data_list.length-1;
  } else if (select_index > data_list.length-1) {
    select_index = 0;
  }
  distance_sum = 0;
  for (i = 0; i < distances[select_index].length; i++) {
    distance_sum += distances[select_index][i];
  }
  selected_name = data_list[select_index];
  load_data(data_list[select_index]);
  dataset.innerHTML = selected_name.substr(7, 3) + ' кластеров / ' +
    selected_name.substr(11, 3) + ' маршрутов';
  total_distance.innerHTML = distance_sum + ' м';
}
present(0);
var circles;
var layer;
var sec_layer;
var layergroup;
var counters = [0, 0, 0, 0, 0];
var markers = [];
var flows = [];
var map = L.map('map').setView([48.7941, 44.8009], 13);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
var color_lines  = [
    '#ff0000', '#00BB00', '#9966cc', '#8db600', '#d2691e'
];
var color_circle = [
    '#00308f', '#6666cc', '#5d8aa8', '#000000', '#003fc0',
    '#007ba7', '#0066ff', '#003153', '#909090', '#6495ed'
];

function CreateMarker(coord, label, color, id) {
    marker = L.circleMarker(coord, {
        color: color,
        radius: Math.log2(centers.length) * 10,
        opacity: 0.7,
        fillOpacity: 0.5
    }).bindLabel(label[0], {noHide: true}).addTo(map).bindPopup(label[1]);
    marker.on('click', onClick);
    return marker;
}

function draw() {
    circles = new L.FeatureGroup();
    for (i in centers) {
        lat = centers[i][0];
        lon = centers[i][1];
        ctr = centers[i][2];
        text = '<b>#' + ctr + '</b>; ' + lat + ', ' + lon + '<br>pop: ' + data[i][i];
        label = '#' + i + '<br>' + data[i][i];
        markers[i] = CreateMarker([lat, lon], [label, text], color_circle[ctr], i);
        circles.addLayer(markers[i]);
    }
    map.addLayer(circles);
    layer = new L.LayerGroup();
    layergroup = new L.LayerGroup();
    for (select = 0; select < 5; select++) {
        if (counters[select] != 0 ) {
            polyline = L.polyline(path[select], {
                color: color_lines[select],
                weight: 5, 
                smoothFactor: 1
            });
            polylineDecorator = L.polylineDecorator(polyline, {
                patterns: [{
                    offset: 25,
                    repeat: 100,
                    symbol: L.Symbol.arrowHead({
                        pixelSize: 15,
                        pathOptions: {color: color_lines[select], fillOpacity: 1, weight: 0}
                    })
                }]
            });
            layergroup = L.layerGroup([polyline, polylineDecorator]);
            layer.addLayer(layergroup);
        }
    }
    map.addLayer(layer);
}

function update_func() {
    checkboxes=['01', '02', '03', '04', '05']
    for (i = 0; i < 5; i++) {
        if (document.getElementById(checkboxes[i]).checked === true) {
            counters[i] = 1;
        } else {
            counters[i] = 0;
        }
    }
    if (map.hasLayer(circles)) {
        map.removeLayer(circles);
    }
    if (map.hasLayer(layer)) {
        map.removeLayer(layer);
    }
    draw();
}

function clear_path() {
    for (i = 0; i < 5; i++) {
        document.getElementById(checkboxes[i]).checked = false;
        counters[i] = 0;
    } 
    if (map.hasLayer(layer)) {
        map.removeLayer(layer);
    }
}

function clear_flow() {
    if (map.hasLayer(sec_layer)) {
        map.removeLayer(sec_layer);
    }
}

function onClick(e) {
    if (map.hasLayer(sec_layer)) {
        map.removeLayer(sec_layer);
    }
    sec_layer = new L.LayerGroup();
    layergroup = new L.LayerGroup();
    for (i in centers) {
        if (e.target == markers[i]) {
            for (j in data[i]) {
                if (i != j) {
                    polyline = L.polyline([[centers[i][0], centers[i][1]], [centers[j][0], centers[j][1]]],
                        {color: 'blue', weight: 3}).bindLabel('flow: ' + data[i][j], {noHide: true});
                    polylineDecorator = L.polylineDecorator(polyline, {
                        patterns: [{
                            offset: 25,
                            repeat: 100,
                            symbol: L.Symbol.arrowHead({
                                pixelSize: 10,
                                pathOptions: {color: 'blue', fillOpacity: 1, weight: 0}
                            })
                        }]
                    });
                    layergroup = L.layerGroup([polyline, polylineDecorator]);
                    sec_layer.addLayer(layergroup);
                }
            }
            break;
        }
    }
    map.addLayer(sec_layer);
}

draw();
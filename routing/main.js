var circles;
var layer;
var sec_layer;
var oth_layer;
var layergroup;
var counters = [0, 0, 0, 0, 0, 0];
var markers = [];
var route_count = 6;
var coords = [];
var map = L.map('map').setView([48.7941, 44.8009], 13);
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
var oth_color = '#7b36ec';
var color_lines  = [
    '#ff0000', '#00BB00', '#9966cc', '#8db600', '#d2691e', '#423189'
];
var color_circle = [
    '#00308f', '#6666cc', '#5d8aa8', '#000000', '#003fc0',
    '#007ba7', '#0066ff', '#003153', '#909090', '#6495ed'
];

function generate_circle() {
    var R = 0.005;
    coords.slice(0, coords.length);
    for (i = 0; i <= 180.0; i += ( 180.0 / 32)) {
        coords.push( new L.LatLng( R / 1.5 * ( -Math.cos( 2 * i * Math.PI / 179.0 ) + 1 ), 
                                   R * Math.sin( 2 * i * Math.PI / 179.0 ) ) );
    }
}

function sqrtn(x, n) {
    return Math.exp((1/n)*Math.log(x));
}

function CreateMarker(coord, label, color, id) {
    marker = L.circleMarker(coord, {
        color: color,
        radius: Math.log10(data[id][id]) * 1.5 * sqrtn(data[id][id], 4),
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
        text = '<b>#' + (ctr+1) + '</b>; ' + lat + ', ' + lon + '<br>pop: ' + data[i][i];
        label = '#' + (ctr+1) + '<br>' + data[i][i];
        markers[i] = CreateMarker([lat, lon], [label, text], color_circle[ctr], i);
        circles.addLayer(markers[i]);
    }
    map.addLayer(circles);
    layer = new L.LayerGroup();
    layergroup = new L.LayerGroup();
    for (select = 0; select < route_count; select++) {
        if (counters[select] != 0 ) {
            for ( i = 0; i < path[select].length - 1; i++ ) {
                j1 = path[select][i];
                j2 = path[select][i+1];
                polyline = L.polyline([[centers[j1][0], centers[j1][1]], [centers[j2][0], centers[j2][1]]], {
                    color: color_lines[select],
                    weight: Math.log10(data[j1][j2]) * 1.2, 
                    smoothFactor: 1
                }).bindLabel('flow: ' + data[j1][j2], {noHide: true});
                polylineDecorator = L.polylineDecorator(polyline, {
                    patterns: [{
                        offset: 25,
                        repeat: 100,
                        symbol: L.Symbol.arrowHead({
                            pixelSize: 10,
                            pathOptions: {color: color_lines[select], fillOpacity: 1, weight: 0}
                        })
                    }]
                });
                layergroup = L.layerGroup([polyline, polylineDecorator]);
                layer.addLayer(layergroup);
            }
        }
    }
    map.addLayer(layer);
}

function update_func() {
    checkboxes=['01', '02', '03', '04', '05', '06']
    for (i = 0; i < route_count; i++) {
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

function draw_other() {
    str = document.getElementById("input_box").value.split(" ");
    clear_other();
    oth_layer = new L.LayerGroup();
    layergroup = new L.LayerGroup();
    for ( i = 0; i < str.length - 1; i++ ) {
        j1 = parseInt(str[i]);
        j2 = parseInt(str[i+1]);
        polyline = L.polyline([[centers[j1][0], centers[j1][1]], [centers[j2][0], centers[j2][1]]], {
            color: oth_color,
            weight: Math.log10(data[j1][j2]) * 1.2, 
            smoothFactor: 1
        }).bindLabel('flow: ' + data[j1][j2], {noHide: true});
        polylineDecorator = L.polylineDecorator(polyline, {
            patterns: [{
                offset: 25,
                repeat: 100,
                symbol: L.Symbol.arrowHead({
                    pixelSize: 10,
                    pathOptions: {color: oth_color, fillOpacity: 1, weight: 0}
                })
            }]
        });
        layergroup = L.layerGroup([polyline, polylineDecorator]);
        oth_layer.addLayer(layergroup);
    }
    map.addLayer(oth_layer);
}

function clear_path() {
    for (i = 0; i < route_count; i++) {
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

function clear_other() {
    if (map.hasLayer(oth_layer)) {
        map.removeLayer(oth_layer);
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
                        {color: 'blue', weight: Math.log10(data[i][j]) * 1.2}).bindLabel('flow: ' + data[i][j], {noHide: true});
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
                } else {
                    var coords_list = [];
                    for (k = 0; k < coords.length; k++ ) {
                        coords_list.push( new L.LatLng( -coords[k].lat + centers[i][0], 
                                                        coords[k].lng + centers[i][1] ) );
                    }
                    polyline = L.polyline(coords_list,
                        {color: 'orange', weight: Math.log10(data[i][j]) * 1.2}).bindLabel('flow: ' + data[i][j], {noHide: true});
                    polylineDecorator = L.polylineDecorator(polyline, {
                        patterns: [{
                            offset: 10,
                            repeat: 25,
                            symbol: L.Symbol.arrowHead({
                                pixelSize: 10,
                                pathOptions: {color: 'orange', fillOpacity: 1, weight: 0}
                            })
                        }]
                    });
                }
                layergroup = L.layerGroup([polyline, polylineDecorator]);
                sec_layer.addLayer(layergroup);
            }
            break;
        }
    }
    map.addLayer(sec_layer);
}

generate_circle();
draw();
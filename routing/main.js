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

function getDinstance(a, b) {
    var rad = 6372795; // радиус сферы (Земли)
    var dlng = Math.abs(centers[a][1] - centers[b][1]) * Math.PI / 180.0;
    var lat1 = centers[a][0] * Math.PI / 180.0;
    var lat2 = centers[b][0] * Math.PI / 180.0;
    var p1 = Math.cos(lat2), p2 = Math.sin(dlng), p3 = Math.cos(lat1);
    var p4 = Math.sin(lat2), p5 = Math.sin(lat1), p6 = Math.cos(lat2);
    var p7 = Math.cos(dlng);
    var y = Math.sqrt(Math.pow(p1 * p2, 2) + Math.pow(p3 * p4 - p5 * p6 * p7, 2));
    var x = p5 * p4 + p3 * p6 * p7;
    return rad * Math.atan2(y, x);
}

function analyze(list) {
    var distance = 0, coast = 0;
    for (i = 0; i < list.length - 1; i++) {
        distance += getDinstance(list[i], list[i+1]);
        coast += data[list[i+1]][list[i]];
    }
    return coast / distance;
}

function draw() {
    circles = new L.FeatureGroup();
    for (i in centers) {
        lat = centers[i][0];
        lng = centers[i][1];
        ctr = centers[i][2];
        text = '<b>#' + (ctr+1) + '</b>; ' + lat + ', ' + lng + '<br>pop: ' + data[i][i];
        label = '#' + (ctr+1) + '<br>' + data[i][i];
        markers[i] = CreateMarker([lat, lng], [label, text], color_circle[ctr], i);
        circles.addLayer(markers[i]);
    }
    map.addLayer(circles);
    layer = new L.LayerGroup();
    layergroup = new L.LayerGroup();
    for (var j = 0; j < route_count; j++) {
        if (counters[j] != 0 ) {
            for ( i = 0; i < path[j].length - 1; i++ ) {
                var j1 = path[j][i];
                var j2 = path[j][i+1];
                polyline = L.polyline([[centers[j1][0], centers[j1][1]], [centers[j2][0], centers[j2][1]]], {
                    color: color_lines[j],
                    weight: Math.log10(data[j1][j2]) * sqrtn(data[j1][j2], 4), 
                    smoothFactor: 1
                }).bindLabel('flow: ' + data[j1][j2], {noHide: true});
                polylineDecorator = L.polylineDecorator(polyline, {
                    patterns: [{
                        offset: 25,
                        repeat: 100,
                        symbol: L.Symbol.arrowHead({
                            pixelSize: 10,
                            pathOptions: {color: color_lines[j], fillOpacity: 1, weight: 0}
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
    var route_list = [];
    str = document.getElementById("input_box").value.split(" ");
    for ( i = 0; i < str.length; i++ ) {
        route_list.push( parseInt( str[i] ) - 1 );
    }
    document.getElementById('value').innerHTML = analyze(route_list).toFixed(4);
    clear_other();
    oth_layer = new L.LayerGroup();
    layergroup = new L.LayerGroup();
    for ( i = 0; i < route_list.length - 1; i++ ) {
        j1 = route_list[i+0];
        j2 = route_list[i+1];
        polyline = L.polyline([[centers[j1][0], centers[j1][1]], [centers[j2][0], centers[j2][1]]], {
            color: oth_color,
            weight: Math.log10(data[j1][j2]) * sqrtn(data[j1][j2], 4), 
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
    var marker;
    if (map.hasLayer(sec_layer)) {
        map.removeLayer(sec_layer);
    }
    sec_layer = new L.LayerGroup();
    layergroup = new L.LayerGroup();
    for (i in centers) {
        if (e.target == markers[i]) {
            for (j in data[i]) {
                if (i != j) {
                    polyline = L.polyline([[centers[i][0], centers[i][1]], [centers[j][0], centers[j][1]]],{
                        color: 'blue', weight: Math.log10(data[i][j]) * sqrtn(data[i][j], 4)
                    }).bindLabel('flow: ' + data[i][j], {noHide: true});
                    polylineDecorator = L.polylineDecorator(polyline, {
                        patterns: [{
                            offset: 25,
                            repeat: 100,
                            symbol: L.Symbol.arrowHead({
                                pixelSize: 12,
                                pathOptions: {color: 'blue', fillOpacity: 1, weight: 0}
                            })
                        }]
                    });
                    layergroup = L.layerGroup([polyline, polylineDecorator]);
                    sec_layer.addLayer(layergroup);
                } else {
                    var myIcon = L.icon({
                        iconUrl: 'images/arrows.png',
                        iconSize: [48, 48],
                        iconAnchor: [48, 24],
                        labelAnchor: [0, -26] 
                    });
                    marker = L.marker([centers[i][0], centers[i][1]], {
                        icon: myIcon
                    }).bindLabel('inside: ' + data[i][j], {direction: left, offset: [50, -15]});
                    sec_layer.addLayer(marker);
                }

            }
            break;
        }
    }
    map.addLayer(sec_layer);
}

draw();
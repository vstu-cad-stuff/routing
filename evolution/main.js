var circles;
var layer;
var layergroup;
var route_num = 0;
var map = L.map('map').setView([48.7941, 44.8009], 13);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
var color_lines  = ['#423189', '#4c8931'];
var status_text  = ['before', 'after'];
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
    }).bindLabel(label, {noHide: true}).addTo(map);
    return marker;
}

function draw() {
    circles = new L.FeatureGroup();
    for (i in centers) {
        lat = centers[i][0];
        lon = centers[i][1];
        ctr = centers[i][2];
        label = '#' + i + '<br>' + data[i][i];
        marker = CreateMarker([lat, lon], label, color_circle[ctr], i);
        circles.addLayer(marker);
    }
    map.addLayer(circles);
    draw_other();
}

function draw_other() {
    str = routes[route_num];
    bf_status = route_num % 2;
    clear_other();
    document.getElementById('status').innerHTML = status_text[bf_status];
    document.getElementById('index').innerHTML = '#' + Math.floor( route_num / 2 );
    layer = new L.LayerGroup();
    layergroup = new L.LayerGroup();
    for ( i = 0; i < str.length - 1; i++ ) {
        j1 = str[i];
        j2 = str[i+1];
        polyline = L.polyline([[centers[j1][0], centers[j1][1]], [centers[j2][0], centers[j2][1]]], {
            color: color_lines[bf_status],
            weight: 5, 
            smoothFactor: 1
        });
        polylineDecorator = L.polylineDecorator(polyline, {
            patterns: [{
                offset: 25,
                repeat: 100,
                symbol: L.Symbol.arrowHead({
                    pixelSize: 10,
                    pathOptions: {color: color_lines[bf_status], fillOpacity: 1, weight: 0}
                })
            }]
        });
        layergroup = L.layerGroup([polyline, polylineDecorator]);
        layer.addLayer(layergroup);
    }
    map.addLayer(layer);
}

function clear_other() {
    if (map.hasLayer(layer)) {
        map.removeLayer(layer);
    }
}

function prev_route() {
    if ( route_num != 0 ) {
        route_num -= 1;
    }
    draw_other();
}

function next_route() {
    if ( route_num < routes.length ) {
        route_num += 1;
    }
    draw_other();
}

draw();
var circles;
var layer;
var layergroup;
var counters = [0, 0, 0, 0, 0]
var map = L.map('map').setView([48.7941, 44.8009], 13);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
var color_lines  = [
    '#ff0000', '#00BB00', '#0000ff', '#bb00ff', '#ffaa00'
];
var color_circle = [
    '#00308f', '#6666cc', '#5d8aa8', '#000000', '#003fc0',
    '#007ba7', '#0066ff', '#003153', '#909090', '#6495ed'
];
draw = function() {
    circles = new L.FeatureGroup();
    for (i in centers) {
        lat = centers[i][0];
        lon = centers[i][1];
        ctr = centers[i][2];
        circle = L.circleMarker([lat, lon], {
            color: color_circle[ctr],
            radius: Math.log2(centers.length) * 10,
            opacity: 0.7,
            fillOpacity: 0.5
        }).addTo(map).bindPopup('<b>' + ctr + '</b><br />' + lat + ', ' + lon);
        circles.addLayer(circle);
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
update_func = function() {
    checkboxes=['01', '02', '03', '04', '05']
    for (i = 0; i < 5; i++) {
        if (document.getElementById(checkboxes[i]).checked === true) {
            counters[i] = 1;
        } else {
            counters[i] = 0;
        }
    }
    clear();
    draw();
}
clear = function() {
    map.removeLayer(circles);
    map.removeLayer(layer);
}
draw();
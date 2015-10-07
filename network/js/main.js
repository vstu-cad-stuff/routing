var circles;
var markers = [];
var map = L.map('map').setView([48.7850, 44.8000], 13);
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
var circle_color = '#123456';

function CreateMarker(coord, label, color, id) {
    marker = L.circleMarker(coord, {
        color: color,
        radius: 3 + Math.pow(G[id][id], 1 / 2) * 2,
        opacity: 0.7,
        fillOpacity: 0.5
    }).bindLabel(label[0], {noHide: false}).addTo(map).bindPopup(label[1]);
    return marker;
}

function draw() {
    circles = new L.FeatureGroup();
    for (i in centers) {
        lat = centers[i][0];
        lng = centers[i][1];
        ctr = centers[i][2];
        text = '<b>Cluster #' + (ctr+1) + '</b>; Pop: ' + G[i][i] + '<br>' + lat + ', ' + lng;
        label = '#' + (ctr+1) + '<br>' + G[i][i];
        markers[i] = CreateMarker([lat, lng], [label, text], circle_color, i);
        circles.addLayer(markers[i]);
    }
    map.addLayer(circles);
}

draw();
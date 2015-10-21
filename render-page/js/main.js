var circle_color = '#123456';
var geoJSON_layer = new L.geoJson();
$.getJSON('./js/convex-hull.json', function(data) {
    geoJSON_layer = L.geoJson(data, {
        'color': '#1e90ff',
        'width': 5,
        'opacity': 0.95
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
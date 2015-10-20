var circle_color = '#123456';
var shell_color = '#d2691e';
var map = L.map('map').setView([48.7900, 44.8000], 13);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// var plot_data = JSON.parse(geodata);
// var line_style = {
//     "color": shell_color,
//     "weight": 5,
//     "opacity": 0.8
// };
alert(geodata['coordinates'][0]);
poly = L.geoJson(geodata);
alert(poly);
poly.addTo(map);

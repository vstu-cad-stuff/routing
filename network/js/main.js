var circles;
var routes;
var markers = [];
var network = [];
var circle_color = '#123456';
var route_colors = ['#239837', '#d2691e', '#ff69b4', '#1e90ff', '#483d8b'];
var slidebar = document.getElementById('slidebar');
var map = L.map('map').setView([48.7900, 44.8000], 13);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
slidebar.setAttribute('onChange', 'drawRoutes()');
slidebar.setAttribute('onMouseMove', 'drawRoutes()');

function getDistance(a, b) {
    // earth radius in meters
    var rad = 6372795.0;
    var dlng = Math.abs(centers[a][1] - centers[b][1]) * Math.PI / 180.0
    var lat1 = centers[a][0] * Math.PI / 180.0;
    var lat2 = centers[b][0] * Math.PI / 180.0;
    var p1 = Math.cos(lat2); var p2 = Math.sin(dlng);
    var p3 = Math.cos(lat1); var p4 = Math.sin(lat2);
    var p5 = Math.sin(lat1); var p6 = Math.cos(dlng);
    var y = Math.sqrt(Math.pow(p1 * p2, 2) + Math.pow(p3 * p4 - p5 * p1 * p6, 2));
    var x = p5 * p4 + p3 * p1 * p6
    return rad * Math.atan2(y, x)
}

function getPeople(a, b) {
    return G[a][b];
}

function getParamCounter(func, route) {
    var param = 0;
    for (index = 0; index < route.length - 1; index++) {
        param += func(route[index+0], route[index+1]);
    }
    return param;
}

function calculateRoute(iteration) {
    var routes = network[iteration];
    var total_distance = 0;
    var total_traffic = 0;
    for (index = 0; index < routes.length; index++) {
        var route = routes[index];
        total_distance += getParamCounter(getDistance, route);
        total_traffic += getParamCounter(getPeople, route);
    }
    return [total_distance, total_traffic];
}

function renderLegend(iteration) {
    var avg_route = document.getElementById('avg_route');
    var sum_route = document.getElementById('sum_route');
    var sum_traff = document.getElementById('sum_traff');
    result = calculateRoute(iteration)
    avg_route.innerHTML = (result[0] / network[iteration].length).toFixed(2) + ' m.';
    sum_route.innerHTML = (result[0]).toFixed(2) + ' m.';
    sum_traff.innerHTML = result[1] + ' p.';
}

function createMarker(coord, label, color, id) {
    marker = L.circleMarker(coord, {
        color: color,
        radius: 3 + Math.pow(getPeople(id, id), 1 / 2) * 2,
        opacity: 0.7,
        fillOpacity: 0.5
    }).bindLabel(label[0], {noHide: false}).addTo(map).bindPopup(label[1]);
    return marker;
}

function drawClusters() {
    circles = new L.FeatureGroup();
    for (i in centers) {
        lat = centers[i][0];
        lng = centers[i][1];
        ctr = centers[i][2];
        if (lat == 0 && lng == 0) {
            continue;
        }
        text = '<b>Cluster #' + (ctr+1) + '</b>; Pop: ' + getPeople(i, i) + '<br>' + lat + ', ' + lng;
        label = '#' + (ctr+1) + ' : ' + getPeople(i, i);
        markers[i] = createMarker([lat, lng], [label, text], circle_color, i);
        circles.addLayer(markers[i]);
    }
    map.addLayer(circles);
}

function drawRoutes() {
    if (map.hasLayer(routes)) {
        map.removeLayer(routes);
    }
    iteration = parseInt(slidebar.value);
    renderLegend(iteration);
    routes = new L.FeatureGroup();
    for (network_count = 0; network_count < network[iteration].length; network_count++) {
        for (index = 0; index < network[iteration][network_count].length - 1; index++) {
            p1 = network[iteration][network_count][index+0];
            p2 = network[iteration][network_count][index+1];
            c00 = centers[p1][0];
            c01 = centers[p1][1];
            c10 = centers[p2][0];
            c11 = centers[p2][1];
            polyline = L.polyline([[c00, c01], [c10, c11]], {
                color: route_colors[network_count],
                weight: 3 + Math.pow(getPeople(p1, p2), 1 / 4) * 2,
            }).bindLabel('flow: ' + getPeople(p1, p2), {noHide: true});
            polylineDecorator = L.polylineDecorator(polyline, {
                patterns: [{
                    offset: 25,
                    repeat: 100,
                    symbol: L.Symbol.arrowHead({
                        pixelSize: 12,
                        pathOptions: {
                            color: route_colors[network_count],
                            fillOpacity: 1,
                            weight: 1
                        }
                    })
                }]
            });
            var sublayer = L.layerGroup([polyline, polylineDecorator]);
            routes.addLayer(sublayer);
        }
    }
    map.addLayer(routes);
}

function selectRoute(index) {
    network = network_list[index];
    slidebar.max = network.length - 1;
    drawRoutes();
}

function renderList() {
    var count = network_list.length;
    var ul = document.getElementById('examples');
    while (ul.hasChildNodes()) {
        ul.removeChild(ul.lastChild);
    }
    for (index = 0; index < count; index++) {
        var li = document.createElement('li');
        var button = document.createElement('button');
        button.title = "Example route #" + ( index + 1 );
        button.setAttribute("onclick", "selectRoute(" + index + ")");
        button.innerHTML = "#" + ( index + 1 );
        li.appendChild(button);
        ul.appendChild(li);
    }
}

renderList();
drawClusters();
selectRoute(0);
var reload = 0;

function include(src) {
    var script = document.createElement('script');
    script.src = src;
    document.head.appendChild(script);
}

function loadData() {
    var radioButton = document.getElementsByName('cluster_count');
    var value = 0;
    for (i = 0; i < radioButton.length; i++) {
        if (radioButton[i].checked) {
            value = radioButton[i].value;
        }
    }
    var loadStr = './cluster'+value+'/data.js';
    include(loadStr);
    if ( reload != 0 ) {
        location.reload();
        reload = 0;
    } else {
        reload++;
    }
}

include('./centers.js');
loadData();
include('./main.js');
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
    include('./cluster'+value+'/centers.js');
    include('./cluster'+value+'/data.js');
    if ( reload != 0 ) {
        reload = 0;
        location.reload();
    } else {
        reload++;
    }
}

loadData();
include('./main.js');
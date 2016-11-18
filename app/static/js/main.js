function nextword(){
    $.get("/api/e/word/next", {timeStamp: new Date().getTime()},
        function (data, status) {
            $("#english").html(data['english']);
            $("#chinese").html(data['chinese']);
            $("#example").html(data['example']);
        });
}

$(document).ready(function() {
    $(".caption h3").click(function(){
        $(this).next().toggle(200);
    });
    $("#next").click(function(){nextword()});

    nextword();

    var myChart = echarts.init(document.getElementById('summary'));
    myChart.setOption({
        title: {
            text: 'Accumulate accuracy',
            x: 'center'
        },
        tooltip: {},
        legend: {
            data:[],
            x: 'left'
        },
        xAxis: {
            type: 'category',
            axisLine: {onZero: true},
            data: []
        },
        yAxis: {
            max: 100
        },
        series: [{
            type: 'line',
            symbolSize: 8,
            label: {
                normal: {
                    show: true,
                    position: 'top'
                }
            },
            data: []
        }]
    });

    $.get('/api/e/exercise/vintage').done(function (data) {
        myChart.setOption({
            xAxis: {
                data: data.date
            },
            series: [{
                data: data.accuracy
            }]
        });
    });

});
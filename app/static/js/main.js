function nextword(){
    $.get("/api/e/word/next", {timeStamp: new Date().getTime()},
        function (data, status) {
            //$("#newword .progress").hide();
            $("#english").html(data['english']);
            $("#chinese").html(data['chinese']);
            $("#example").html(data['example']);
            $("#book_title").html(data['book_title']);
            $("#lesson").html('Lesson ' + data['lesson'])
        });
}

$(document).ready(function() {

    $("#next").click(function(){nextword()});
    $("#error_words li").click(function(){
        if ($(this).find(".material-icons").html() == 'arrow_drop_up'){
            $(this).find(".material-icons").html("arrow_drop_down");
        }
        else {
            $(this).find(".material-icons").html("arrow_drop_up");
        }
    })
    //nextword();

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
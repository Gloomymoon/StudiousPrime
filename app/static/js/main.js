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
});
$(function() {
    /* city select */
    $("#drivCity,.input-group-addon").click(function() {
    var ul = $(".cityArea");
    if (ul.css("display") == "none") {
            ul.slideDown("fast");
        } else {
            ul.slideUp("fast");
        }
    });
    $(".cityArea li a").click(function() {
        var txt = $(this).text();
        $("#drivCity").val(txt);
        var value = $(this).attr("rel");
        $(".cityArea").hide();
    });
    $(document).click(function(e){
        if(e.target.id!='drivCity'){
            $(".cityArea").hide();
        }
    });
});
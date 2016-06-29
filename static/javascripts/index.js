$(function() {
	/* banner #main-slider */
    $('#main-slider').carousel({
        interval: 8000
    });

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

$("#benefit_ok").cxScroll({
	    direction:"bottom",
	    step:1,
	    accel:160,
	    speed:800,
	    time:4000,
	    auto:true,
	    prevBtn:false,
	    nextBtn:false,
	    safeLock:true
	});
    /* 受益车主上下滚动 */
    $("#klbusershow").cxScroll({
	    direction:"bottom",
	    step:1,
	    accel:160,
	    speed:500,
	    time:3000,
	    auto:true,
	    prevBtn:false,
	    nextBtn:false,
	    safeLock:true
	});
    /* 合作保险公司左右滚动 */
    $("#par_ok").cxScroll({
        direction:"right",
        step:1,
        accel:160,
        speed:800,
        time:4000,
        auto:true,
        prevBtn:false,
        nextBtn:false,
        safeLock:true
    });
    $('#indicatorContainer1').circleProgress({
        value: 0.4,
        size: 160,
        fill: {
            gradient: ["red", "red"]
        }
    });
    $('#indicatorContainer2').circleProgress({
        value: 0.6,
        size: 160,
        fill: {
            gradient: ["red", "red"]
        }
    });
    $('#indicatorContainer3').circleProgress({
        value: 0.8,
        size: 160,
        fill: {
            gradient: ["red", "red"]
        }
    });
    $('#indicatorContainer4').circleProgress({
        value: 1,
        size: 160,
        fill: {
            gradient: ["red", "red"]
        }
    });
    $('#show_num_hd').prop('number', 10).animateNumber({ number: 7543 },20000);
});
/* 受益车主上下滚动 */
    $("#benefit-okid").cxScroll({
	    direction:"bottom",
	    step:1,
	    accel:160,
	    speed:500,
	    time:3000,
	    auto:true,
	    prevBtn:false,
	    nextBtn:false,
	    safeLock:true
	});
    /* 合作保险公司左右滚动 */
    $("#partners-id").cxScroll({
        direction:"right",
        step:1,
        accel:160,
        speed:800,
        time:4000,
        auto:true,
        prevBtn:false,
        nextBtn:false,
        safeLock:true
    });
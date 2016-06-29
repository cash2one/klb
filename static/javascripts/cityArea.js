function animate() {
    $(".charts").each(function (i, item) {
        var a = parseInt($(item).attr("w"));
        $(item).animate({
            width: a + "%"
        }, 1000);
    });
}
function selectCity(id) {
    $("#cityArea2").empty();
    var p = 0;
    for (var i = 0; i < dictionary.length; i++) {
        if (dictionary[i]['pid'] == id) {
            p++;
            $("#cityArea2").append('<li fc="two"><a href="#" cararealiense="' + dictionary[i]['cararealiense'] + '" rel="' + dictionary[i]['id'] + '" onclick="setCity(this)">' + dictionary[i]['name'] + '</a></li>');
        }

    }

}
function setCity(d) {
    var txt = $(d).text();
    $("#drivCity").val(txt);
    var value = $(d).attr("rel");
    var cararealiense = $(d).attr("cararealiense");
    $("#cityCode").val(value);
    $("#licenseNo").val(cararealiense);
    $(".cityArea").hide();


}

function getBXlist(d) {
    var citycode = $(d).attr("citycode");
    var ownername = $(d).attr("ownername");
    var engine = $(d).attr("engine");
    var vin = $(d).attr("vin");
    var drivCity =  $(d).attr("drivCity");
    var licenseno = $(d).attr("licenseno");
    var key = encodeURIComponent($(d).attr("key"));
    var vehiclefgwcode = encodeURIComponent($(d).attr("vehiclefgwcode"));
    var value = encodeURIComponent($(d).text());
    window.location.href = "/web/pricing/4/?licenseno=" + licenseno + "&citycode=" + citycode + "&ownername=" + ownername + "&engine=" + engine + "&vin=" + vin + "&key=" + key + "&vehiclefgwcode=" + vehiclefgwcode + "&value=" + value + "&a=a"+"&drivCity="+drivCity;


}

$(function () {
    $('li[fc="0"]').remove();
    $('li[fc="one"]').remove();
    $('li[fc="two"]').remove();
    for (var i = 0; i < impCitys.length; i++) {
        $("#cityArea0").append('<li fc="0"><a href="javascript:void(0);" cararealiense="' + impCitys[i]['cararealiense'] + '" rel="' + impCitys[i]['id'] + '" onclick="setCity(this)">' + impCitys[i]['name'] + '</a></li>');
    }
    for (var i = 0; i < provinces.length; i++) {
        $("#cityArea1").append('<li fc="one"><a href="javascript:selectCity(' + provinces[i]['id'] + ');" rel="' + provinces[i]['id'] + '">' + provinces[i]['name'] + '</a></li>');
    }


    $("#drivCity,.input-group-addon").click(function () {

        var ul = $(".cityArea");
        if (ul.css("display") == "none") {
            ul.slideDown("fast");
        } else {
            ul.slideUp("fast");
        }

    });

    $("#action1").click(function () {
        var licenseNo = $.trim($("#licenseNo").val());
        var ownerName = $.trim($("#ownerName").val());
        var cityCode = $.trim($("#cityCode").val());
        var drivCity = $.trim($("#drivCity").val());

        var re = /^[\u4e00-\u9fa5]{1}[A-Z]{1}[A-Z_0-9]{5}$/;
        var xmre = /^[\u4e00-\u9fa5]{2,5}$/;
        if (cityCode == "") {
            layer.alert("请选择城市");
        } else if (licenseNo == "" || ownerName == "") {
            layer.alert("请输入完整的信息");
        } else if (licenseNo.search(re) == -1) {
            layer.alert("车牌号码不正确");
        } else if (ownerName.search(xmre) == -1) {
            layer.alert("车主姓名不正确");
        } else {
            $('#loading').modal('toggle');
            animate();
            var getdb = {
                "licenseNo": licenseNo,
                "ownerName": ownerName,
                "cityCode": cityCode
            };
            $.getJSON('/bxservice/VINIsSet/', getdb, function (j) {
                if (j.error == "0") {
                    window.location.href="/web/pricing/4/?id="+ j.data.id+"&time="+ String((new Date()).valueOf())+"&drivCity="+drivCity;
                } else {
                    $.post("/bxservice/getvin/", getdb, function (e) {

                        if (e.error == "1") {
                            window.location.href = "/web/pricing/2/?licenseno=" + e.data.licenseNo + "&ownername=" + e.data.ownerName + "&citycode=" + e.data.cityCode+"&drivCity="+drivCity;
                        } else {

                            var url = "http://chexian.sinosig.com/Partner/netVehicleModel.action?searchCode=" + e.data.vin_noen + "&searchType=1&encoding=utf-8&isSeats=1&pageSize=100";
                            $.ajax({
                                type: "get",
                                async: false,
                                url: url,
                                dataType: "jsonp",
                                success: function (data) {
                                    if (data.rows.length > 0) {
                                        $("#carlist").empty().append('<a href="javascript:void(0);" class="list-group-item disabled">请选择车型</a>');
                                        for (var i = 0; i < data.rows.length; i++) {
                                            $("#carlist").append('<a href="javascript:void(0);" onclick="getBXlist(this);" class="list-group-item" citycode="' + e.data.cityCode + '" ownername="' + e.data.ownerName + '" engine="' + e.data.engine + '" vin="' + e.data.vin + '" licenseno="' + e.data.licenseNo + '" key="' + data.rows[i].key + '" vehiclefgwcode="' + data.rows[i].vehicleFgwCode + '" drivCity="'+drivCity+'">' + data.rows[i].value + '</a>');
                                        }
                                        var w = $("body").width() / 1.5;
                                        var h = $('#carlist_b').height() + 10;
                                        $('#loading').modal('toggle');
                                        layer.open({
                                            type: 1,
                                            title: false,
                                            closeBtn: true,
                                            shadeClose: false,
                                            skin: 'layui-layer-rim',
                                            area: [w + 'px', h + 'px'],
                                            content: $('#carlist_b')
                                        });

                                    }
                                },
                                error: function () {
                                    alert('fail');
                                }
                            });

                            //window.location.href = "/web/pricing/2/?licenseNo=" + e.data.licenseNo + "&ownerName=" + e.data.ownerName + "&cityCode=" + e.data.cityCode + "&vin=" + e.data.vin + "&engine=" + e.data.engine;

                        }
                    }, "json");
                }
            });

        }

    });
});

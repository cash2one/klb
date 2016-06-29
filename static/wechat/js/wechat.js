var WeChat = new Framework7({modalButtonOk: "同意", modalButtonCancel: "不同意"});
var $$klb = Dom7;

var ZHDICT, ASDICT, YGDICT, DICT, BXGS;
var ZHACTION = false;
var ASACTION = false;
var YGACTION = false;
//点击触发事件
var Mclick = 1;
//配送城市
var C_DELIVERY_PROVINCE_P = "";//省
var C_DELIVERY_CITY_P = "";//市
//支付地址
var PAYURL = "";
//初始化算价要的值
var licenseno = "", citycode = "", ownername = "", engine = "", vin = "", key = "", vehiclefgwcode = "", value = "", action = "a", id = "";
var licensenoNew = "", openid = "";
var flag = "";
var timer = '';
var intedname = '';
var mainView = WeChat.addView('.view', {
    dynamicNavbar: true,
    smartSelectBackText: '返回',
    domCache: true
});
//WeChat.alert('卡来宝会保证您的信息安全，不会向他人泄露您的个人信息。如您无法认同此授权，请点击返回按钮，之后您将不能使用卡来宝进行车险相关的其他操作。', '以下操作将授权卡来宝通过第三方平台比对您投保所需的车辆信息。');

var mySwiper = WeChat.swiper('.swiper-container', {
    pagination: '.swiper-pagination',
    speed: 400,
});
//程序初始化的时候执行
$$klb(document).on('pageInit', function (e) {

    var page = e.detail.page;

    if (page.name == "bx-list") {
    }
    if (page.name == "car-info") {
    }
    if (page.name == "home") {

    }
});
$$klb(document).on('pageAfterAnimation', function (e) {
    var page = e.detail.page;
    if (page.name == "home") {
        ZHDICT = "";
        ASDICT = "";
        YGDICT = "";
        DICT = "";
        BXGS = "";
        ZHACTION = false;
        ASACTION = false;
        YGACTION = false;
        licenseno = "";
        citycode = "";
        ownername = "";
        engine = "";
        vin = "";
        key = "";
        vehiclefgwcode = "";
        value = "";
        action = "a";
        id = "";
        //$('[klb="hide"]').hide();
        //$('[klb="hide"]').find("input").val("");
        Mclick = 1;

    }
    if (page.name == "carlist") {
        ZHDICT = "";
        ASDICT = "";
        YGDICT = "";
        DICT = "";
        BXGS = "";
        Mclick = 1;
    }
    //保险列表页面
    if (page.name == "bx-list") {
        WeChat.hidePreloader();
        inputChang();
        if (ZHDICT == "" || ZHDICT == undefined) {
            if (ZHACTION == false) {
                AjaxBJList(licenseno, ownername, citycode, vin, engine, action, "zh", vehiclefgwcode, value, key, id);
            }
        }
        if (ASDICT == "" || ASDICT == undefined) {
            if (ASACTION == false) {
                AjaxBJList(licenseno, ownername, citycode, vin, engine, action, "as", vehiclefgwcode, value, key, id);
            }
        }
        if (YGDICT == "" || YGDICT == undefined) {
            if (YGACTION == false) {
                AjaxBJList(licenseno, ownername, citycode, vin, engine, action, "yg", vehiclefgwcode, value, key, id);
            }
        }

        btn_color_chang();
        //WeChat.accordionOpen("#accordion-tbfa");
        //点击选择价格触发事件
        selectJG();
        click_BXList();
        Mclick = 1;

    }
    if (page.name == "bx-detail") {
        btn_color_chang();
        inputChang();
        WeChat.closeModal();
        click_BXList();
        Mclick = 1;
        if (BXGS == 'zh') {
            $('a[klb="Go5"]').prop("href", "/wechat/pricing/7/?id=" + id + "&key=" + vin + "&bxgs=" + BXGS);
        } else {
            $('a[klb="Go5"]').prop("href", "/wechat/pricing/5/?id=" + id + "&key=" + vin + "&bxgs=" + BXGS);
        }
        for (var o in DICT) {
            if (DICT[o] == '0') {
                DICT[o] = '0.00';
            }
        }
        $("#detail_TotalPremium").text(DICT.TotalPremium);//保险合计
        $("#detail_BizPremium").text(DICT.BizPremium);//商险合计
        $("#detail_ForePremium").text(DICT.ForePremium);//交强险合计
        $("#detail_InsuranceGift").text(DICT.InsuranceGift);//保险公司礼品
        $("#detail_klbGift").text(DICT.klbGift);//卡来宝礼品
        $("#detail_bizPremium").text(DICT.bizPremium);//商业险总计
        $("#detail_VehicleLoss").text(DICT.VehicleLoss);//车辆损失险
        $("#detail_SanZhe").text(DICT.SanZhe);//车辆损失险
        $("#detail_DaoQiang").text(DICT.DaoQiang);//盗抢险
        $("#detail_ZeRenSJ").text(DICT.ZeRenSJ);//责任险（司机）
        $("#detail_ZeRenCK").text(DICT.ZeRenCK);//（乘客）
        $("#detail_BoLiPS").text(DICT.BoLiPS);//玻璃破险
        $("#detail_HuaHen").text(DICT.HuaHen);//划痕险
        $("#detail_ZiRan").text(DICT.ZiRan);//自燃险
        $("#detail_SheShui").text(DICT.SheShui);//涉水险
        $("#detail_BuJiMPZJ").text(DICT.BuJiMPZJ);//不计免赔总计
        $("#detail_BUJiCS").text(DICT.BUJiCS);//不计车损
        $("#detail_BuJiSZ").text(DICT.BuJiSZ);//不计三者
        $("#detail_BuJiDQ").text(DICT.BuJiDQ);//不计盗抢险
        $("#detail_BuJiSJ").text(DICT.BuJiSJ);//不计司机
        $("#detail_BuJiCK").text(DICT.BuJiCK);//不计乘客
        $("#detail_forcePremium").text(DICT.forcePremium);//交强总计
        $("#detail_forcePre").text(DICT.forcePre);//交强险
        $("#detail_VehTaxPremium").text(DICT.VehTaxPremium);// 车船税
        $("#detail_totalPremium").text(DICT.totalPremium);// 保险总计

    }
    if (page.name == "bx-FuDongBiz") {
        $('[klb="Gofore"]').click(function () {
            var ORDER_ID = $.trim($("#ORDER_ID").val());
            db = {
                'order_id': ORDER_ID,
                "M": "11"
            };
            IsRead(db);
            $('a[klb="Gofore"]').prop("href", "/wechat/pricing/8/?id=" + id + "&key=" + vin + "&bxgs=" + BXGS);

        });

    }
    if (page.name == "bx-FuDongForce") {
        $('[klb="Go5"]').click(function () {
            var ORDER_ID = $.trim($("#ORDER_ID").val());
            db = {
                'order_id': ORDER_ID,
                "M": "12"
            };
            IsRead(db);
            $('a[klb="Go5"]').prop("href", "/wechat/pricing/5/?id=" + id + "&key=" + vin + "&bxgs=" + BXGS);
        });

    }
    if (page.name == "bx-userinfo") {
        Mclick = 1;
        //C_DELIVERY_PROVINCE_P = "";
        AutoInsetInfo();
        CitySelect();

        $('[klb="bxgs-pay"]').click(function () {
            if (Mclick < 2) {
                var bxgs = $.trim($("#bxgs").val());
                var VINPAY = $.trim($("#vin-pay").val());
                var bxgs_type = $.trim($("#bxgs_type").val());
                var Session_ID = $.trim($("#Session_ID").val());
                var ORDER_ID = $.trim($("#ORDER_ID").val());
                var C_APP_NAME = $.trim($("#C_APP_NAME").val()); //投保人姓名
                var C_APP_IDENT_NO = $.trim($("#C_APP_IDENT_NO").val()); //投保人身份证号
                var C_APP_TEL = $.trim($("#C_APP_TEL").val()); //投保人电话
                var C_APP_ADDR = $.trim($("#C_APP_ADDR").val()); //投保人地址
                var C_APP_EMAIL = $.trim($("#C_APP_EMAIL").val()); // 投保人邮箱
                var C_INSRNT_NME = $.trim($("#C_INSRNT_NME").val()); //被保险人姓名
                intedname = C_INSRNT_NME;
                var C_INSRNT_IDENT_NO = $.trim($("#C_INSRNT_IDENT_NO").val()); // 被保险人身份证号
                var C_INSRNT_TEL = $.trim($("#C_INSRNT_TEL").val()); //被保险人电话
                var C_INSRNT_ADDR = $.trim($("#C_INSRNT_ADDR").val()); //被保险人地址
                var C_INSRNT_EMAIL = $.trim($("#C_INSRNT_EMAIL").val()); //被保险人邮箱
                var C_CONTACT_NAME = $.trim($("#C_CONTACT_NAME").val()); // 收件人姓名
                var C_CONTACT_TEL = $.trim($("#C_CONTACT_TEL").val()); //收件人电话
                var C_ADDRESS = $.trim($("#C_ADDRESS").val()); //收件地址
                var C_IDET_NAME = $.trim($("#C_INSRNT_NME").val()); // 行驶证车主
                var C_IDENT_NO = $.trim($("#C_INSRNT_IDENT_NO").val()); // 身份证号

                var C_DELIVERY_PROVINCE = $.trim($("#C_DELIVERY_PROVINCE").val());
                var C_DELIVERY_CITY = $.trim($("#C_DELIVERY_CITY").val());
                //var C_DELIVERY_DISTRICT = $.trim($("#C_DELIVERY_DISTRICT").val());
                var pam = {
                    "vin": VINPAY,
                    "bxgs_type": bxgs_type,
                    "Session_ID": Session_ID,
                    "ORDER_ID": ORDER_ID,
                    "C_APP_NAME": C_APP_NAME,
                    "C_APP_IDENT_NO": C_APP_IDENT_NO,
                    "C_APP_TEL": C_APP_TEL,
                    "C_APP_ADDR": C_APP_ADDR,
                    "C_APP_EMAIL": C_APP_EMAIL,
                    "C_INSRNT_NME": C_INSRNT_NME,
                    "C_INSRNT_IDENT_NO": C_INSRNT_IDENT_NO,
                    "C_INSRNT_TEL": C_INSRNT_TEL,
                    "C_INSRNT_ADDR": C_INSRNT_ADDR,
                    "C_INSRNT_EMAIL": C_INSRNT_EMAIL,
                    "C_CONTACT_NAME": C_CONTACT_NAME,
                    "C_CONTACT_TEL": C_CONTACT_TEL,
                    "C_ADDRESS": C_ADDRESS,
                    "C_IDET_NAME": C_IDET_NAME,
                    "C_IDENT_NO": C_IDENT_NO,
                    "C_DELIVERY_PROVINCE": C_DELIVERY_PROVINCE_P,
                    "C_DELIVERY_CITY": C_DELIVERY_CITY,
                    "C_DELIVERY_DISTRICT": "",
                    "bxgs": bxgs
                };
                var openidNEW = $("#openid").val();
                var db = {
                    "openid": openidNEW,
                    "order_id": ORDER_ID,
                    "bxgs": bxgs,
                    "flag": '1',
                    "ownername": C_INSRNT_NME,
                    "vin": VINPAY
                };
                Createorder(db);
                WeChat.showPreloader('正在与保险公司核对您的信息,请稍后......');

                $.ajax({
                    url: '/bxservice/ConfirmTouBao/',
                    type: "POST",
                    contentType: "application/x-www-form-urlencoded; charset=utf-8",
                    data: pam,
                    dataType: "json",
                    success: function (d) {
                        WeChat.hidePreloader();
                        if (d.data.error == "1") {
                            WeChat.addNotification({
                                title: '卡来宝车险',
                                message: d.data.msg
                            });
                            return False;
                        }
                        if (d.data.error == '2') {
                            prom()
                        }
                        else {

                            PAYURL = d.url;
                            mainView.router.loadPage("/wechat/pricing/6/");

                        }

                    },
                    error: function (xhr, err) {
                        WeChat.hidePreloader();
                        WeChat.addNotification({
                            title: '卡来宝车险',
                            message: "您的信息有误"
                        });
                    }
                });


                Mclick++;

            }

        });


    }
    if (page.name == "bx-bxgsweb") {
        $("#bxgs_website").attr("src", PAYURL);
        timer = setInterval("ReadCallBack()", 3000);

    }



    var pat1 = new RegExp("smart-select-radio");
    if(pat1.test(page.name)){
        $(".icon-back").remove();

    }

});

$$klb("#GetVin").click(function () {
    //mainView.router.loadPage("/wechat/pricing/3/");
    //return false;
    WeChat.confirm("以下操作将授权卡来宝通过第三方平台比对您投保所需的车辆信息。卡来宝会保证您的信息安全。", "卡来宝友情提示", function () {
        WeChat.showPreloader('正在验证您的信息......');
        var licenseNo = $$klb("#licenseNo").val();
        var ownerName = $$klb("#ownerName").val();
        var re = /^[\u4e00-\u9fa5]{1}[A-Z]{1}[A-Z_0-9]{5}$/;
        var xmre = /^[\u4e00-\u9fa5]{2,5}$/;

        if (ownerName == "") {
            WeChat.hidePreloader();
            ShowMsg('请正确填写车主姓名');
            return false;
        }
        if (licenseNo == "" || ownerName == "") {
            WeChat.hidePreloader();
            ShowMsg('请输入完整的信息');
            return false;
        }
        if (licenseNo.search(re) == -1) {
            WeChat.hidePreloader();
            ShowMsg('车牌号码不正确');
            return false;
        }
        if (ownerName.search(xmre) == -1) {
            WeChat.hidePreloader();
            ShowMsg('车主姓名不正确');
            return false;
        }
        var citycode = GetCityCode(licenseNo);
        if (citycode == "") {
            WeChat.hidePreloader();
            ShowMsg('车牌号码不正确');
            return false;
        }
        var getdb = {
            "licenseNo": licenseNo,
            "ownerName": ownerName,
            "cityCode": citycode
        };
        licensenoNew = licenseNo;
        openid = $("#openid").val();
        $.getJSON('/bxservice/VINIsSet/', getdb, function (j) {
            if (j.error == "0") {
                $("#id").val(j.data.id);
                var time = (new Date()).valueOf();
                id = j.data.id;
                mainView.router.loadPage("/wechat/pricing/3/?id=" + j.data.id + "&time=" + time);

            } else {

                if (!$("#engine").is(":hidden")) {
                    var Hiengine = $.trim($("#engine").val());
                    var Hivin = $.trim($("#vin").val());
                    if (Hiengine.length < 6) {
                        WeChat.hidePreloader();
                        ShowMsg('发动机号码不正确');
                        return false;
                    }
                    if (Hivin.length < 17) {
                        WeChat.hidePreloader();
                        ShowMsg('车架号不正确');
                        return false;
                    }
                    var HilicenseNo = $("#HilicenseNo").val();
                    var HiownerName = $("#HiownerName").val();
                    var HicityCode = $("#HicityCode").val();
                    alert(HicityCode);
                    alert(HiownerName);
                    alert(HilicenseNo);
                    if (HilicenseNo == "" && HiownerName == "" && HicityCode == "") {
                        WeChat.hidePreloader();
                        ShowMsg('系统错误，请刷新后重试!');
                        return false;
                    }
                    selectCarInfo(HilicenseNo, HicityCode, HiownerName, Hiengine, Hivin, Hivin);

                } else {
                    AjaxGo3(getdb);
                }

            }
        });
    },
        function(){
            mainView.router.loadPage("/wechat/pricing/1/");
        });


});

function ShowMsg(txt) {
    WeChat.addNotification({
        title: '卡来宝.车险',
        media: '<i class="fa fa-exclamation-circle"></i>',
        message: txt,
        hold: 5
    });
}
//点击选择车型后执行
function getBXlist(d) {
    citycode = $(d).attr("citycode");
    ownername = $(d).attr("ownername");
    engine = $(d).attr("engine");
    vin = $(d).attr("vin");
    licenseno = $(d).attr("licenseno");
    key = $(d).attr("key");
    vehiclefgwcode = $(d).attr("vehiclefgwcode");
    value = $(d).text();
    $("#carkey").val(key);
    $("#vehiclefgwcode").val(vehiclefgwcode);
    $("#value").val(value);
    if ($("#vin").is(":hidden")) {
        action = "a";
        $("#a").val("a");
    } else {
        action = "b";
        $("#a").val("b");
    }
    var Indb = {
        "key": key,
        "vehiclefgwcode": vehiclefgwcode,
        "value": value,
        "vin": vin,
        "engine": engine,
        "licenseno": licenseno,
        "ownername": ownername,
        "citycode": citycode,
        "a": action
    };
    $.getJSON("/bxservice/createvin/", Indb, function (e) {
        if (e.error == "1") {
            WeChat.alert(e.msg, "卡来宝友情提示");
            return false;
        } else {
            var NewURL = "/wechat/pricing/3/?licenseno=" + licenseno + "&citycode=" + citycode + "&ownername=" + ownername + "&engine=" + engine + "&vin=" + vin + "&key=" + encodeURIComponent(key) + "&vehiclefgwcode=" + encodeURIComponent(vehiclefgwcode) + "&value=" + encodeURIComponent(value) + "&a=a";
            mainView.router.loadPage(NewURL);
        }
    });

}
//截取字符串
function cutstr(str, len) {
    var str_length = 0;
    var str_len = 0;
    str_cut = new String();
    var a;
    str_len = str.length;
    for (var i = 0; i < str_len; i++) {
        a = str.charAt(i);
        str_length++;
        if (escape(a).length > 4) {
            //中文字符的长度经编码之后大于4
            str_length++;
        }
        str_cut = str_cut.concat(a);
        if (str_length >= len) {
            str_cut = str_cut.concat("");
            return str_cut;
        }
    }
    //如果给定字符串小于指定长度，则返回源字符串；
    if (str_length < len) {
        return str;
    }
}
//通过车牌获得城市代码

function GetCityCode(licenseNo) {
    var CityCode = "";
    //获取直辖市
    var ZXList = [
        {'cararealiense': "京", "id": "110100"},
        {'cararealiense': "津", "id": "120100"},
        {'cararealiense': "沪", "id": "310100"},
        {'cararealiense': "渝", "id": "500100"}
    ];

    var CitySubZX = cutstr(licenseNo, 2);
    var CitySub = cutstr(licenseNo, 3);

    for (var i = 0; i < ZXList.length; i++) {
        if (CitySubZX == ZXList[i].cararealiense) {
            CityCode = ZXList[i].id;
            break;
        }
    }
    if (CityCode == "") {
        for (var n = 0; n < dictionary.length; n++) {
            if (CitySub == dictionary[n].cararealiense) {
                CityCode = dictionary[n].id;
                break;
            }
        }
    }

    return CityCode;


}
function AjaxGo3(getdb) {
    jQuery.post("/bxservice/getvin/", getdb, function (e) {
        if (e.error == "1") {
            $('[klb="hide"]').show();
            WeChat.hidePreloader();
            $("#HilicenseNo").val(e.data.licenseNo);
            $("#HiownerName").val(e.data.ownerName);
            $("#HicityCode").val(e.data.cityCode);
            ShowMsg('请输入您的车架号和发动机号');
        } else {
            selectCarInfo(e.data.licenseNo, e.data.cityCode, e.data.ownerName, e.data.engine, e.data.vin, e.data.vin_noen);
        }
    }, "json");
}

function btn_color_chang() {
    $('[klb="bjmp"]').click(function () {
        var bjmp = $(this);
        bjmp.toggleClass("active");
    });
}

function selectJG() {
    var SANZHE = $('#JG-SANZHE');
    var SHIJI = $("#JG-SHIJI");
    var CHENGKE = $("#JG-CHENGKE");
    var HUAHEN = $("#JG-HUAHEN");
    var BOLI = $("#JG-BOLI");
    //三者
    SANZHE.bind('click', function (event) {

        var buttons = [
            {
                text: '5万',
                onClick: function () {
                    SANZHE.val("5万");
                    WeChat.closeModal();
                }
            },
            {
                text: '10万',
                onClick: function () {
                    SANZHE.val("10万");
                    WeChat.closeModal();
                }
            },
            {
                text: '20万',
                onClick: function () {
                    SANZHE.val("20万");
                    WeChat.closeModal();
                }
            },
            {
                text: '30万',
                onClick: function () {
                    SANZHE.val("30万");
                    WeChat.closeModal();
                }
            },
            {
                text: '50万',
                onClick: function () {
                    SANZHE.val("50万");
                    WeChat.closeModal();
                }
            },
            {
                text: '100万',
                onClick: function () {
                    SANZHE.val("100万");
                    WeChat.closeModal();
                }
            }
        ];
        WeChat.actions(buttons);
        event.stopPropagation();
        event.preventDefault();
        return false;

    });
    //司机
    SHIJI.bind("click", function (event) {
        var buttons = [
            {
                text: '1万',
                onClick: function () {
                    SHIJI.val("1万");
                    WeChat.closeModal();
                }
            },
            {
                text: '2万',
                onClick: function () {
                    SHIJI.val("2万");
                    WeChat.closeModal();
                }
            },
            {
                text: '3万',
                onClick: function () {
                    SHIJI.val("3万");
                    WeChat.closeModal();
                }
            },
            {
                text: '5万',
                onClick: function () {
                    SHIJI.val("5万");
                    WeChat.closeModal();
                }
            },
            {
                text: '10万',
                onClick: function () {
                    SHIJI.val("10万");
                    WeChat.closeModal();
                }
            },
            {
                text: '20万',
                onClick: function () {
                    SHIJI.val("20万");
                    WeChat.closeModal();
                }
            }
        ];
        WeChat.actions(buttons);
        event.stopPropagation();
        event.preventDefault();
        return false;
    });
    //乘客
    CHENGKE.bind("click", function (event) {
        var buttons = [
            {
                text: '1万',
                onClick: function () {
                    CHENGKE.val("1万");
                    WeChat.closeModal();
                }
            },
            {
                text: '2万',
                onClick: function () {
                    CHENGKE.val("2万");
                    WeChat.closeModal();
                }
            },
            {
                text: '3万',
                onClick: function () {
                    CHENGKE.val("3万");
                    WeChat.closeModal();
                }
            },
            {
                text: '5万',
                onClick: function () {
                    CHENGKE.val("5万");
                    WeChat.closeModal();
                }
            },
            {
                text: '10万',
                onClick: function () {
                    CHENGKE.val("10万");
                    WeChat.closeModal();
                }
            },
            {
                text: '20万',
                onClick: function () {
                    CHENGKE.val("20万");
                    WeChat.closeModal();
                }
            },
        ];
        WeChat.actions(buttons);
        event.stopPropagation();
        event.preventDefault();
        return false;
    });
    //划痕
    HUAHEN.bind("click", function (event) {
        var buttons = [
            {
                text: '1万',
                onClick: function () {
                    HUAHEN.val("1万");
                    WeChat.closeModal();
                }
            },
            {
                text: '2万',
                onClick: function () {
                    HUAHEN.val("2万");
                    WeChat.closeModal();
                }
            },
            {
                text: '3万',
                onClick: function () {
                    HUAHEN.val("3万");
                    WeChat.closeModal();
                }
            },
            {
                text: '5万',
                onClick: function () {
                    HUAHEN.val("5万");
                    WeChat.closeModal();
                }
            },
            {
                text: '10万',
                onClick: function () {
                    HUAHEN.val("10万");
                    WeChat.closeModal();
                }
            },
            {
                text: '20万',
                onClick: function () {
                    HUAHEN.val("20万");
                    WeChat.closeModal();
                }
            },
        ];
        WeChat.actions(buttons);
        event.stopPropagation();
        event.preventDefault();
        return false;
    });
    //玻璃
    BOLI.bind("click", function (event) {
        var buttons = [
            {
                text: '1万',
                onClick: function () {
                    BOLI.val("1万");
                    WeChat.closeModal();
                }
            },
            {
                text: '2万',
                onClick: function () {
                    BOLI.val("2万");
                    WeChat.closeModal();
                }
            },
            {
                text: '3万',
                onClick: function () {
                    BOLI.val("3万");
                    WeChat.closeModal();
                }
            },
            {
                text: '5万',
                onClick: function () {
                    BOLI.val("5万");
                    WeChat.closeModal();
                }
            },
            {
                text: '10万',
                onClick: function () {
                    BOLI.val("10万");
                    WeChat.closeModal();
                }
            },
            {
                text: '20万',
                onClick: function () {
                    BOLI.val("20万");
                    WeChat.closeModal();
                }
            }
        ];
        WeChat.actions(buttons);
        event.stopPropagation();
        event.preventDefault();
        return false;
    });
}

//保险公司报价(第一次默认推荐)
function AjaxBJList(Inlicenseno, Inownername, Incitycode, Invin, Inengine, Ina, Incompany, Invehiclefgwcode, Invalue, Incarkey, Inid) {
    var data = {
        "licenseno": Inlicenseno,
        "ownername": Inownername,
        "citycode": Incitycode,
        "vin": Invin,
        "engine": Inengine,
        "a": Ina,
        "carkey": Incarkey,
        "vehiclefgwcode": Invehiclefgwcode,
        "value": Invalue,
        "company": Incompany,
        "id": Inid,
        "time": String((new Date()).valueOf())
    };
    $.ajax({
        url: '/bxservice/PriceList/',
        type: "POST",
        contentType: "application/x-www-form-urlencoded; charset=utf-8",
        data: data,
        dataType: "json",
        success: function (d) {

            AddListDB(Incompany, d, Inid);
        },
        error: function (xhr, err) {
            $("#" + Incompany + "_logoimg").removeClass("wechat-opacity70");
            $("#" + Incompany + "_imgloading").hide();
            $("#" + Incompany + "_bxzj").removeClass("preloader");
            $("#" + Incompany + "_msg").html("<span style='color:red;'>系统异常,请稍后再试！</span>");
        }
    });
}
function AddListDB(bxgs, d, id) {
    switch (bxgs) {
        case "zh":
            ZHACTION = true;
            break;
        case "as":
            ASACTION = true;
            break;
        case "yg":
            YGACTION = true;
            break;
        default :
            ZHACTION = true;
            ASACTION = true;
            YGACTION = true;
            break;
    }
    $("#" + bxgs + "_logoimg").removeClass("wechat-opacity70");
    $("#" + bxgs + "_imgloading").hide();
    $("#" + bxgs + "_bxzj").removeClass("preloader");
    if (d.data.error == "1") {
        $("#" + bxgs + "_msg").html("<span style='color:red;'>" + d.data.msg + "</span>");
    } else {

        /**
         *
         * 这是返回成功报价信息
         *
         *
         *
         */


        $("#" + bxgs + "_msg").html("黄金会员每1200赠100");
        for (var o in d.data) {
            if (d.data[o] == '不支持') {
                $("#" + bxgs + "_bxzj").html("*" + d.data.TotalPremium);
                $("#beizhu").show();
                break;
            } else {
                $("#" + bxgs + "_bxzj").html("¥" + d.data.TotalPremium);
            }
        }

        $("#" + bxgs + "_url").attr("href", "/wechat/pricing/4/?");
        var db = d.data;
        db.bxgs = bxgs;
        db.licenseno = licensenoNew;
        db.openid = openid;
        db.CarId = id;
        CreateHistory(db);
        if (bxgs == "zh") {
            ZHDICT = d.data;
        }
        if (bxgs == "as") {
            ASDICT = d.data;
        }
        if (bxgs == "yg") {
            YGDICT = d.data;
        }
    }
}

function selectCarInfo(InlicenseNo, IncityCode, InownerName, Inengine, Invin, Invin_noen) {
    WeChat.hidePreloader();
    WeChat.showPreloader('正在查询车辆信息......');
    var url = "http://chexian.sinosig.com/Partner/netVehicleModel.action?searchCode=" + Invin_noen + "&searchType=1&encoding=utf-8&isSeats=1&pageSize=100";
    $.ajax({
        type: "get",
        async: false,
        url: url,
        dataType: "jsonp",
        success: function (data) {
            if (data.rows.length > 0) {

                var InHtml = $("#car_list_info ul");
                InHtml.empty();
                for (var i = 0; i < data.rows.length; i++) {
                    InHtml.append('<li>' +
                            //'<a licenseno="'+e.data.licenseNo+'" citycode="'+e.data.cityCode+'" ownername="' + e.data.ownerName + '" engine="' + e.data.engine + '" vin="' + e.data.vin + '" key="'+data.rows[i].key+'" vehiclefgwcode="'+data.rows[i].vehicleFgwCode+'" value="'+data.rows[i].value+'" href="/wechat/pricing/3/?licenseno=' + e.data.licenseNo + '&citycode=' + e.data.cityCode + '&ownername=' + e.data.ownerName + '&engine=' + e.data.engine + '&vin=' + e.data.vin + '&key=' + encodeURIComponent(data.rows[i].key) + '&vehiclefgwcode=' + encodeURIComponent(data.rows[i].vehicleFgwCode) + '&value=' + encodeURIComponent(data.rows[i].value) + '&a=a" class="item-link item-content">' +
                        '<a onclick="getBXlist(this);" licenseno="' + InlicenseNo + '" citycode="' + IncityCode + '" ownername="' + InownerName + '" engine="' + Inengine + '" vin="' + Invin + '" key="' + data.rows[i].key + '" vehiclefgwcode="' + data.rows[i].vehicleFgwCode + '" value="' + data.rows[i].value + '" href="#" class="item-link item-content">' +
                        '<div class="item-inner">' +
                        '<div class="item-title wechat_font12">' +
                        data.rows[i].value + '</div>' +
                        '</div>' +
                        '</a>' +
                        '</li>');

                }
                mainView.router.load({pageName: 'carlist'});
                WeChat.hidePreloader();

            }
        },
        error: function () {
            WeChat.alert("系统错误!", "卡来宝友情提示");
        }
    });
}

// 点击保险公司列表触发事件
function click_BXList() {
    $("#zh_url").bind("click", function () {
        DICT = ZHDICT;
        BXGS = "zh";
    });
    $("#as_url").bind("click", function () {
        DICT = ASDICT;
        BXGS = "as";
    });

    $("#yg_url").bind("click", function () {
        DICT = YGDICT;
        BXGS = "yg";
    });
}

function changTB_btn() {
    ASACTION = false;
    ZHACTION = false;
    YGACTION = false;
    $("#as_logoimg,#zh_logoimg,#yg_logoimg").addClass("wechat-opacity70");
    $("#as_imgloading,#zh_imgloading,#yg_imgloading").show();
    $("#as_bxzj,#zh_bxzj,#yg_bxzj").html("").addClass("preloader");
    $("#zh_url,#as_url,#yg_url").attr("href", "#");
    $("[id*='_msg']").html("正在为您报价，大概需要1分钟");
    WeChat.showTab('#tab1');
    ZHDICT = "";
    ASDICT = "";
    YGDICT = "";
    DICT = "";
    BXGS = "";
    changTB_action("as");
    changTB_action("zh");
    changTB_action("yg");

}

function changTB_action(Incompany) {

    var CHESHUN = $("#CHESHUN").val();
    var SANZHE = $("#SANZHE").val();
    var DAOQIANG = $("#DAOQIANG").val();
    var SHIJI = $("#SHIJI").val();
    var CHENGKE = $("#CHENGKE").val();

    var BOLI = $("#BOLI").val();
    var HUAHEN = $("#HUAHEN").val();
    var ZIRAN = $("#ZIRAN").val();
    var SHESHUI = $("#SHESHUI").val();

    var CHESHUN_BJ = $("#CHESHUN_BJ").is(':checked') ? 1 : 0;
    var SANZHE_BJ = $("#SANZHE_BJ").is(':checked') ? 1 : 0;
    var DAOQIANG_BJ = $("#DAOQIANG_BJ").is(':checked') ? 1 : 0;
    var SHIJI_BJ = $("#SHIJI_BJ").is(':checked') ? 1 : 0;
    var CHENGKE_BJ = $("#CHENGKE_BJ").is(':checked') ? 1 : 0;
    var FUJIA_BJ = $("#FUJIA_BJ").is(':checked') ? 1 : 0;
    var JIAOQIANG = $("#JIAOQIANG").is(':checked') ? 1 : 0;
    var licenseNo = licenseno;
    var ownerName = ownername;
    var cityCode = citycode;
    var vin = vin;
    var engine = engine;
    var action = action;
    var key = key;
    var vehicleFgwCode = vehiclefgwcode;
    var value = value;
    var id1 = id;

    var sendval = {
        "CHESHUN": CHESHUN,
        "SANZHE": SANZHE,
        "DAOQIANG": DAOQIANG,
        'SHIJI': SHIJI,
        "CHENGKE": CHENGKE,
        "BOLI": BOLI,
        "HUAHEN": HUAHEN,
        "ZIRAN": ZIRAN,
        "SHESHUI": SHESHUI,
        "CHESHUN_BJ": CHESHUN_BJ,
        "SANZHE_BJ": SANZHE_BJ,
        "DAOQIANG_BJ": DAOQIANG_BJ,
        "SHIJI_BJ": SHIJI_BJ,
        "CHENGKE_BJ": CHENGKE_BJ,
        "FUJIA_BJ": FUJIA_BJ,
        "JIAOQIANG": JIAOQIANG,
        "licenseno": licenseNo,
        "ownername": ownerName,
        "citycode": cityCode,
        "vin": vin,
        "engine": engine,
        "a": action,
        "carkey": key,
        "vehiclefgwcode": vehicleFgwCode,
        "value": value,
        "company": Incompany,
        "id": id1,
        "time": String((new Date()).valueOf()),
        "chang": "1"

    };
    $.ajax({
        url: '/bxservice/PriceList/',
        type: "POST",
        contentType: "application/x-www-form-urlencoded; charset=utf-8",
        data: sendval,
        dataType: "json",
        success: function (d) {
            AddListDB(Incompany, d, id);
        },
        error: function (xhr, err) {
            $("#" + Incompany + "_logoimg").removeClass("wechat-opacity70");
            $("#" + Incompany + "_imgloading").hide();
            $("#" + Incompany + "_bxzj").removeClass("preloader");
            $("#" + Incompany + "_msg").html("<span style='color:red;'>系统异常,请稍后再试！</span>");
        }

    });
}

function selectIsSet() {
    var CHESHUN = $("#CHESHUN").val();
    var SANZHE = $("#SANZHE").val();
    var DAOQIANG = $("#DAOQIANG").val();
    var SHIJI = $("#SHIJI").val();
    var CHENGKE = $("#CHENGKE").val();

    var BOLI = $("#BOLI").val();
    var HUAHEN = $("#HUAHEN").val();
    var ZIRAN = $("#ZIRAN").val();
    var SHESHUI = $("#SHESHUI").val();

    var CHESHUN_BJ = $("#CHESHUN_BJ").is(':checked') ? 1 : 0;
    var SANZHE_BJ = $("#SANZHE_BJ").is(':checked') ? 1 : 0;
    var DAOQIANG_BJ = $("#DAOQIANG_BJ").is(':checked') ? 1 : 0;
    var SHIJI_BJ = $("#SHIJI_BJ").is(':checked') ? 1 : 0;
    var CHENGKE_BJ = $("#CHENGKE_BJ").is(':checked') ? 1 : 0;
    var FUJIA_BJ = $("#FUJIA_BJ").is(':checked') ? 1 : 0;
    //车损
    if (CHESHUN == "0") {
        $("#FUJIAXIAN_UL").find("select").val("0").attr("disabled", true);
        $("#CHESHUN_BJ,#DAOQIANG_BJ").attr("checked", false).attr("disabled", true);
        $('[fc="CHESHUN"]').val("0").attr("disabled", true);
    } else if (CHESHUN == "1") {
        $("#FUJIAXIAN_UL").find("select,input").attr("disabled", false);
        $("#CHESHUN_BJ,#DAOQIANG_BJ").attr("disabled", false);
        $('[fc="CHESHUN"]').attr("disabled", false);
    }
    //司机
    if (SHIJI == "0") {
        $("#SHIJI_BJ").attr("checked", false).attr("disabled", true);
    } else {
        $("#SHIJI_BJ").attr("disabled", false);
    }
    //乘客
    if (CHENGKE == "0") {
        $("#CHENGKE_BJ").attr("checked", false).attr("disabled", true);
    } else {
        $("#CHENGKE_BJ").attr("disabled", false);
    }
    //三者
    if (SANZHE == "0") {
        $('[fc="SANZHE"]').attr("checked", false).attr("disabled", true);
    } else {
        $('[fc="SANZHE"]').attr("disabled", false);
    }
    //盗抢
    if (DAOQIANG == "0") {
        $('[fc="DAOQIANG"]').attr("checked", false).attr("disabled", true);
    } else {
        $('[fc="DAOQIANG"]').attr("disabled", false);
    }
    //附加不计免赔判断
    if (BOLI == 0 && HUAHEN == 0 && ZIRAN == 0 && SHESHUI == 0) {
        $('#FUJIA_BJ').attr("checked", false).attr("disabled", true);
    } else {
        $('#FUJIA_BJ').attr("disabled", false);
    }
}
function inputChang() {
    $("select,input").change(function () {
        selectIsSet();
    });

}
//自动填写表单
function AutoInsetInfo() {
    $('[fc*="tb_"]').keyup(function () {
        var fcname = $(this).attr("fc");
        var fcnameArr = fcname.split("_");
        var val = $(this).val();
        $('[fc="btb_' + fcnameArr[1] + '"]').val(val);
    });
}

//表单验证
function ShowMsgTop(content) {
    WeChat.addNotification({
        title: '卡来宝车险',
        message: content
    });
}

//城市联动
function CitySelect() {
    $("#C_DELIVERY_PROVINCE").empty();
    $("#C_DELIVERY_PROVINCE").append('<option value="" selected>请选择省</option>');
    for (var i = 0; i < impCitys.length; i++) {

        if (impCitys[i]['pid'] == "733") {
            impCitys[i]['id'] = impCitys[i]['id'] == '110100' ? "110000" : impCitys[i]['id'];
            impCitys[i]['id'] = impCitys[i]['id'] == '120100' ? "120000" : impCitys[i]['id'];
            impCitys[i]['id'] = impCitys[i]['id'] == '310100' ? "310000" : impCitys[i]['id'];
            impCitys[i]['id'] = impCitys[i]['id'] == '500100' ? "500000" : impCitys[i]['id'];
            $("#C_DELIVERY_PROVINCE").append('<option value="' + impCitys[i]['id'] + '">' + impCitys[i]['name'] + '</option>');
        }

    }

    for (var i = 0; i < provinces.length; i++) {
        $("#C_DELIVERY_PROVINCE").append('<option value="' + provinces[i]['id'] + '">' + provinces[i]['name'] + '</option>');
    }

    $("#C_DELIVERY_PROVINCE").change(function () {
        var citycode = $(this).val();
        C_DELIVERY_PROVINCE_P = citycode;
        var p = 0;
        $("#C_DELIVERY_CITY").empty();
        $("#C_DELIVERY_CITY").append(' <option value="" selected>请选择市/县</option>');
        for (var i = 0; i < dictionary.length; i++) {
            if (dictionary[i]['pid'] == citycode) {
                p++;

                $("#C_DELIVERY_CITY").append('<option value="' + dictionary[i]['id'] + '">' + dictionary[i]['name'] + '</option>');

            }
        }
        if (p > 0) {
            $("#C_DELIVERY_CITY_LI").show();
        } else {
            $("#C_DELIVERY_CITY_LI").hide();
        }


    });


}

function CreateHistory(db) {
    $.ajax({
        url: "/wechat/CreateHistory/",
        data: db,
        type: "post",
        dataType: "json",
        success: function (d) {
        },
        error: function () {
        }
    });
}
function IsRead(db) {
    $.ajax({
        url: '/bxservice/ConfirmFeiLv/',
        type: "POST",
        contentType: "application/x-www-form-urlencoded; charset=utf-8",
        data: db,
        dataType: "json",
        async: false,
        success: function (d) {
            if (d.data.error == '1') {
                flag = d.data.error;
                WeChat.alert(d.data.msg, "卡来宝友情提示");
            }
            else {
                flag = d.data.error;
            }
        },
        error: function (xhr, err) {
            $("#" + Incompany + "_logoimg").removeClass("wechat-opacity70");
            $("#" + Incompany + "_imgloading").hide();
            $("#" + Incompany + "_bxzj").removeClass("preloader");
            $("#" + Incompany + "_msg").html("<span style='color:red;'>系统异常,请稍后再试！</span>");
            return False;
        }
    });
}
function prom() {
    var Verify = prompt("请输入验证码", "");
    if (Verify) {
        var VINNEW = $.trim($("#vin-pay").val());
        var pam = {
            "Verify": Verify,
            "bxgs": "yg",
            "vin": VINNEW,
            "C_INSRNT_NME": intedname,
        };
        $.post('/bxservice/ConfirmTouBao/', pam, function (d) {
            if (d.data.error == "1") {
                WeChat.hidePreloader();
                WeChat.addNotification({
                    title: '卡来宝车险',
                    message: d.data.msg
                });
                //WeChat.alert(d.data.msg,"卡来宝友情提示");
            }
            if (d.data.error == "2") {
                prom();
            } else {
                PAYURL = d.url;
                mainView.router.loadPage("/wechat/pricing/6/");
            }

        }, "json");

    } else {
        prom();
    }
}
function ReadCallBack() {
    var Session_ID_NEW = $.trim($("#Session_ID").val());
    var bxgsnew = $.trim($("#bxgs").val());
    var db = {
        'Session_ID': Session_ID_NEW,
        "bxgs": bxgsnew
    };
    $.ajax({
        url: '/bxservice/GetCallBack/',
        type: "POST",
        contentType: "application/x-www-form-urlencoded; charset=utf-8",
        data: db,
        dataType: "json",
        success: function (d) {
            if (d.data.error == '1') {
            }
            else {
                clearInterval(timer);
                $('#pay_success').show();
                $('#bxgs_pay').hide();
                var openidnew = $("#openid").val();
                var order_id = d.data.orderno;
                var Bxgs = d.data.bxgs;
                var db = {
                    "openid": openidnew,
                    "order_id": order_id,
                    "bxgs": Bxgs,
                    "flag": '0'
                };
                Createorder(db);
                setTimeout("loadpricing()", 5000)

            }
        },
        error: function (xhr, err) {
            $("#" + Incompany + "_logoimg").removeClass("wechat-opacity70");
            $("#" + Incompany + "_imgloading").hide();
            $("#" + Incompany + "_bxzj").removeClass("preloader");
            $("#" + Incompany + "_msg").html("<span style='color:red;'>系统异常,请稍后再试！</span>");
            return False;
        }
    });
}
function loadpricing() {
    var openidnew = $("#openid").val();
    mainView.router.loadPage("/wechat/UserCenter/?openid=" + openidnew);
}
function Createorder(db) {

    $.ajax({
        url: '/wechat/CreateOrder/',
        type: "POST",
        contentType: "application/x-www-form-urlencoded; charset=utf-8",
        data: db,
        dataType: "json",
        success: function (d) {
        },
        error: function (xhr, err) {
        }
    });

}
$(function () {
    $("#K1").bind("change", function () {

        var K = $(this).val();
        $("#guohu").text(K == "1" ? "已过户" : "未过户");

        if (K == "1") {
            $('[klb="hide"]').show();
        } else {
            $('[klb="hide"]').hide();
        }
    });

});
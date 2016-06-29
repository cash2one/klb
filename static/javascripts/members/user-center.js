$(function () {
    //点击添加车辆
    $("#addcar_btn").on("click", function () {
        layer.open({
            type: 1,
            title: "添加车辆",
            closeBtn: 2,
            area: ['600px', '400px'],
            shadeClose: false,
            scrollbar: false,
            content: $('#addcar')
        });
    });

    $("#addcarbtn").on("click", function () {
        var chepai, carusername, vin, fadongji;
        chepai = $.trim($("#inputchepai").val());
        carusername = $.trim($("#carusername").val());
        vin = $.trim($("#inputvin").val());
        fadongji = $.trim($("#inputfadongji").val());
        var index = layer.load();
        $.post("/members/mycar/", {
            "chepai": chepai,
            "carusername": carusername,
            "vin": vin,
            "fadongji": fadongji,
            "a": "bind"
        }, function (e) {
            layer.close(index);
            if (e.error == 0) {
                window.location.href = "/members/mycar/";
            } else {
                layer.msg(e.msg, {icon: 5});
            }

        }, "json");

    });

    var util = {
        wait: 180,
        hsTime: function (that) {
            _this = this;

            if (_this.wait == 0) {
                $('#send_sms').removeAttr("disabled").val('重发短信验证码');
                _this.wait = 180;
            } else {
                var _this = this;
                $(that).attr("disabled", true).val('' + _this.wait + '秒后重新获取');
                _this.wait--;
                setTimeout(function () {
                    _this.hsTime(that);

                }, 1000);
            }
        }
    };
    //发送手机验证码验证
    $("#send_sms").on("click", function () {
        util.hsTime('#send_sms');
        //$("#phone_submit").removeAttr("disabled");
        var phone = $("#phone").val();
        var index = layer.load();
        $.post("/members/getvcode/", {"phone": phone}, function (e) {
            layer.close(index);
            if (e.error != 0) {
                layer.alert(e.msg, {icon: 2});
                util.wait = 0;
            } else {
                layer.alert(e.msg, {icon: 6});
            }
        }, "json");
    });
    //银行选择
    $("#bank_show ul li a").click(function () {
        $("#bank_show ul li").css({
            'border': "1px #999999 solid"
        });
        $(this).prev().prop("checked", true);
        $(this).parent().css({
            "border": "2px #ff0000 solid"
        });
    });
    //判断输入金钱是否正确
    $("#Amount").blur(function () {
        var Amount = $.trim($(this).val());
        var re = /^[0-9]{1}\d*(\.\d{1,2})?$/;
        if (!re.test(Amount)) {
            layer.tips('请输入正确的数字', '#Amount');
        }else{
            var BillNo = $("#BillNo").val();
            $.getJSON("/members/GetPayMD5Info/",{"BillNo":BillNo,"Amount":Amount},function(e){
                $("#MD5info").val(e.data.MD5info);
            });
        }
    });

    $("#pay_go").on("click",function(){
        var Amount = $.trim($("#Amount").val());
        var BillNo = $.trim($("#BillNo").val());
        var re = /^[0-9]{1}\d*(\.\d{1,2})?$/;
        if(!re.test(Amount)){
            layer.alert('请输入正确的金额');
        }else{
            $("#payform").submit();
            layer.confirm('登录网上银行充值', {
                btn: ['充值成功', '充值失败'],
                shade: false
            }, function () {
                window.location.href="/members/";
            }, function () {
                window.location.href="/members/pay/";
            });
        }

    });

});
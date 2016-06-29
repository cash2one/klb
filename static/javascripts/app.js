/* Smooth scrolling para anclas */
var click_one = false;
$(document).on('click', 'a.smooth', function (e) {
    e.preventDefault();
    var $link = $(this);
    var anchor = $link.attr('href');
    $('html, body').stop().animate({
        scrollTop: $(anchor).offset().top
    }, 1000);
});

/* Stick the menu */
$(function () {
    var sticky_navigation_offset_top = $('#sticky_navigation').offset().top + 40;
    var sticky_navigation = function () {
        var scroll_top = jQuery(window).scrollTop();
        if (scroll_top > sticky_navigation_offset_top) {
            jQuery('#sticky_navigation').stop(true).animate({
                    'padding': '5px 0;',
                    'min-height': '40px',
                    'opacity': '0.89'
                },
                500);
            jQuery('#sticky_navigation').css({
                'position': 'fixed',
                'top': 0,
                'left': 0
            });
        } else {
            jQuery('#sticky_navigation').stop(true).animate({
                    'padding': '20px 0;',
                    'min-height': '40px',
                    'opacity': 1
                },
                100);
            jQuery('#sticky_navigation').css({
                'position': 'relative'
            });
        }
    };

    sticky_navigation();

    jQuery(window).scroll(function () {
        sticky_navigation();
    });
});

jQuery(document).ready(function () {
    $('.nav').on('click mousedown mouseup touchstart touchmove', 'a.has_children', function () {
        if ($(this).next('ul').hasClass('open_t') && !$(this).parents('ul').hasClass('open_t')) {
            $('.open_t').removeClass('open_t');
            return false;
        }
        $('.open_t').not($(this).parents('ul')).removeClass('open_t');
        $(this).next('ul').addClass('open_t');
        return false;
    });
    $(document).on('click', ':not(.has_children, .has_children *)', function () {
        if ($('.open_t').length > 0) {
            $('.open_t').removeClass('open_t');
            $('.open_t').parent().removeClass('open');
            return false;
        }
    });

    // hide #back-top first
    $("#back-top").hide();

    // fade in #back-top
    $(function () {
        $(window).scroll(function () {
            if ($(this).scrollTop() > 100) {
                $('#back-top').fadeIn();
            } else {
                $('#back-top').fadeOut();
            }
        });

        // scroll body to 0px on click
        $('#back-top a').click(function () {
            $('body,html').animate({
                scrollTop: 0
            }, 500);
            return false;
        });
    });

});

$(function () {

    var util = {
        wait: 180,
        hsTime: function (that) {
            _this = this;

            if (_this.wait == 0) {
                $('#send_code').removeAttr("disabled").val('重发短信验证码');
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
    $("#send_code").click(function () {
        util.hsTime('#send_code');
        $("#phone_submit").removeAttr("disabled");
        var phone = $("#Mobile").val();
        $.post("/members/getvcode/", {"phone": phone}, function (e) {
            if (e.error != 0) {
                layer.alert(e.msg, {icon: 2});
                util.wait = 0;
            } else {
                layer.alert(e.msg, {icon: 6});
            }
        }, "json");
    });

    $("#phone_submit").click(function () {
        var Mobile = $.trim($("#Mobile").val());
        var ValidatedCode = $.trim($("#ValidatedCode").val());
        var Password = $.trim($("#Password").val());
        var InputConfirmPassword = $.trim($("#InputConfirmPassword").val());
        var RecomCode = $.trim($("#RecomCode").val());
        if (Mobile == "") {
            layer.tips('请输入手机号码', '#Mobile', {
                tips: [1, '#78BA32']
            });
            return false;
        }
        if (ValidatedCode == "") {
            layer.tips('请输入手机验证码', '#ValidatedCode');
            return false;
        }

        if (Password.length < 6) {

            layer.tips('密码不能少于6位', '#Password');
            return false;
        }
        if (InputConfirmPassword.length < 6) {

            layer.tips('密码不能少于6位', '#InputConfirmPassword');
            return false;
        }
        if (Password != InputConfirmPassword) {
            //layer.tips('两次密码输入不一致', '#Password',{tipsMore: true});
            layer.tips('两次密码输入不一致', '#InputConfirmPassword', {tipsMore: true});
            return false;
        }

        layer.load();
        $.post("/members/reg/", {
            "Mobile": Mobile,
            "ValidatedCode": ValidatedCode,
            "Password": Password,
            "InputConfirmPassword": InputConfirmPassword,
            "RecomCode": RecomCode,
            "action": "mobile"
        }, function (e) {

            if (e.error != 0) {
                layer.alert(e.msg, {icon: 2});
            } else {
                window.location.href = "/members/";
            }
            layer.closeAll('loading');
        }, "json");

    });
    //刷新验证码
    $("#new_validcode,#validcode_img").click(function () {
        layer.load();
        $("#validcode_img").attr("src", "/members/validcode/?a=" + (new Date()).valueOf());
        layer.closeAll('loading');
    });
    $("#email_submit").click(function () {
        var Email = $.trim($("#email").val());
        var Password = $.trim($("#Password_email").val());
        var InputConfirmPassword = $.trim($("#InputConfirmPassword_email").val());
        var RecomCode = $.trim($("#RecomCode_email").val());
        var ValidCode = $.trim($("#ValidCode_email").val());

        if (Email == "") {
            layer.tips('邮件不能为空', '#email');
            return false;
        }
        if (checkemail(Email) == false) {
            layer.tips('邮件格式不正确', '#email');
            return false;
        }
        if (Password.length < 6) {
            layer.tips('密码不能少于6位', '#Password_email');
            return false;
        }
        if (Password != InputConfirmPassword) {
            layer.tips('两次密码输入不一致', '#InputConfirmPassword_email');
            return false;
        }
        if (ValidCode == "") {
            layer.tips('验证码不能为空', '#ValidCode_email', {
                tips: 2
            });
            return false;
        }
        $.get("/members/validcode/", {"a": "check", "code": ValidCode}, function (e) {

            if (e.error == 1) {
                layer.tips('验证码不正确', '#ValidCode_email', {
                    tips: 2
                });
            } else {
                var db = {
                    "Email": Email,
                    "Password": Password,
                    "InputConfirmPassword": InputConfirmPassword,
                    "RecomCode": RecomCode,
                    "ValidCode": ValidCode,
                    "action": "email"
                };
                $.post("/members/reg/", db, function (m) {
                    if (m.error != 0) {
                        layer.alert(m.msg, {icon: 2});
                        $("#new_validcode").click();
                    } else {
                        window.location.href = "/members/";
                    }
                }, "json")
            }
        }, "json");
    });

    //#用户登录
    $("#login_email").click(function () {
        var username = $.trim($("#username_login").val());
        var password = $.trim($("#password_login").val());
        var next = $.trim($("#href_next").val());
        if (username == "") {
            layer.tips('用户名不能为空', '#username_login');
            return false;
        }
        if (password == "") {
            layer.tips('密码不能为空', '#password_login');
            return false;
        }
        var db = {
            "username": username,
            "password": password
        };
        var Index = layer.load();
        $.post("/members/login/?next="+next, db, function (e) {
            layer.close(Index);
            if (e.error != 0) {
                layer.alert(e.msg, {icon: 2});
            } else {

                if(e.url!=""){
                    window.location.href= e.url;
                }else{
                    window.location.href = "/members/";
                }

            }
        }, "json");
    });
    $("#copytxtbtn").zclip({
        path: '/static/javascripts/ZeroClipboard.swf',
        copy: $('#copytxtinput').val()
    });
    $("#qr_image").attr("src", "/members/qrcode/?s=" + $("#copytxtinput").val());
    //设置推荐码
    $("#set_tuijian_btn").bind("click", function (event) {
        $(this).hide();

        $(this).attr("hidden", "hidden");
        var code = $.trim($("#tuijian_code").val());
        if (code.length < 6) {
            layer.tips('推荐码不能少于6位,大于20位', '#tuijian_code', {
                tips: 2
            });
        } else if (/[\u4e00-\u9fa5]/g.test(code)) {
            layer.tips('推荐码不能包含汉字', '#tuijian_code', {
                tips: 2
            });
        } else if (!/[a-zA-Z0-9_]{6,40}$/g.test(code)) {
            layer.tips('推荐码只能是长度6到20的字母，数字', '#tuijian_code', {
                tips: 2
            });
        } else {
            layer.load(2);
            $.post("/members/tjcode/", {"code": code, "a": "set"}, function (e) {
                layer.closeAll();
                if (e.error != "0") {
                    layer.tips(e.msg, '#tuijian_code', {
                        tips: 2
                    });
                    event.stopPropagation();
                    return false;
                } else {
                    layer.alert(e.msg, {icon: 0});
                    $("#copytxtinput").val(e.data.url);
                    event.stopPropagation();
                    return false;
                }
                return false;
            }, "json");
        }
        $(this).show();
        return false;
    });

});



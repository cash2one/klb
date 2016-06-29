var WeChat = new Framework7();
var $$klb = Dom7;
var mainView = WeChat.addView('.view', {
    dynamicNavbar: true,
    smartSelectBackText: '返回',
    domCache: true
});

$$klb('#bind-btn').on('click', function () {
    var storedData = WeChat.formGetData('bind-form');
    var ReUserName = /^[\u4e00-\u9fa5]{2,4}$/;
    var RePwd = /^(\w){6,20}$/;
    var ReEmail = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
    var RePhone = /^1\d{10}$/;
    var ReIdCard =  /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
    if (storedData) {
        var username = (storedData.username).toString();
        var email = (storedData.email).toString();
        var password = (storedData.password).toString();
        var repassword = (storedData.repassword).toString();
        var phone = storedData.phone;
        var idcard = storedData.idcard;
        if(!ReUserName.test(username)){
            WeChat.alert('真实姓名格式错误', '卡来宝友情提示!');
        }else if(!ReEmail.test(email)){
            WeChat.alert('邮件地址格式格式错误', '卡来宝友情提示!');
        }else if(!RePwd.test(password)){
            WeChat.alert('密码格式为6到20位字母数字下划线', '卡来宝友情提示!');
        }else if(password!=repassword){
            WeChat.alert('两次密码不一致', '卡来宝友情提示!');
        }else if(!RePhone.test(phone)){
            WeChat.alert('手机号码格式格式错误', '卡来宝友情提示!');
        }else if(!ReIdCard.test(idcard)){
            WeChat.alert('身份证号码格式格式错误', '卡来宝友情提示!');
        }else{
            WeChat.showIndicator();
            $.post("/wechat/BindUserInfo/",storedData,function(e){
                WeChat.hideIndicator();
                WeChat.alert(e.msg, '卡来宝友情提示!');
                if(e.error!="1"){
                    $("#username_tag").val(username);
                    mainView.router.back();
                }

            },"json");
        }

    }
    else {
        alert('error');
    }
});

$$klb(document).on('pageAfterAnimation', function (e) {
    var page = e.detail.page;
    //alert(page.name);

});

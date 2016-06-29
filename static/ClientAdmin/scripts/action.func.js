/**
 * Created by fengchao on 15/11/5.
 */
function Login(){
    var username = $.trim($("#username").val());
    var password = $.trim($("#password").val());
    if(username=="" || password==""){
        $("#msg").html("用户名密码不能为空").show();
    }else{
        var index = layer.load(1);
        $("#msg").hide().html("");
        $.ajax({
            url:"/ClientAdmin/Login/",
            type:"post",
            dataType:"json",
            data:{"username":username,"password":password},
            success:function(e){
                layer.close(index);
                if(e.error=="0"){
                    window.location.href="/ClientAdmin/";
                }else{
                    $("#msg").html(e.msg).show();
                }
            },
            error:function(){
                $("#msg").html("系统异常，请稍后再试").show();
            }
        });
    }
}
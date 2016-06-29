var WeChat = new Framework7();
var $$klb = Dom7;
var mainView = WeChat.addView('.view', {
    dynamicNavbar: true,
    smartSelectBackText: '返回',
    domCache: true
});

$(".wechat-share-p15").hover(
    function () {
        var T = $(this).find("i");
        T.addClass("fa-spin");
    }, function () {
        var T = $(this).find("i");
        T.removeClass("fa-spin");
    });
$('.open-slider-modal').on('click', function () {
    var QrecodeURL = $("#QrecodeURL").val();
    var modal = WeChat.modal({
        title: '关注卡来宝',
        text: '长按图片识别二维码，关注卡来宝公众号',
        afterText: '<div>' +
        '<img src="' + QrecodeURL + '" height="200">' +
        '</div>',
        buttons: [
            {
                text: '我已关注'
            }
        ]
    })
    WeChat.swiper($$klb(modal).find('.swiper-container'), {pagination: '.swiper-pagination'});
});

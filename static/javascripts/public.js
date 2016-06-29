/**
 * Created by fengchao on 15/7/27.
 */
function AddFavorite(title, url) {
    try {
        window.external.addFavorite(url, title);
    }
    catch (e) {
        try {
            window.sidebar.addPanel(title, url, "");
        }
        catch (e) {
            alert("抱歉，您所使用的浏览器无法完成此操作。\n\n加入收藏失败，请使用Ctrl+D进行添加");
        }
    }
}
function checkemail(email){

  var reg = /^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/;
  ismail= reg.test(email);
  if(!ismail ) {
    return false
  }else{
      return true
  }
}

function copy_code(copyText)
    {
        if (window.clipboardData)
        {
            window.clipboardData.setData("Text", copyText)
        }
        else
        {
            var flashcopier = 'flashcopier';
            if(!document.getElementById(flashcopier))
            {
              var divholder = document.createElement('div');
              divholder.id = flashcopier;
              document.body.appendChild(divholder);
            }
            document.getElementById(flashcopier).innerHTML = '';
            var divinfo = '<embed src="/static/javascripts/_clipboard.swf" FlashVars="clipboard='+encodeURIComponent(copyText)+'" width="0" height="0" type="application/x-shockwave-flash"></embed>';
            document.getElementById(flashcopier).innerHTML = divinfo;
        }
      alert('copy成功！');
    }
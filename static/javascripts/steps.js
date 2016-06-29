$(function() {
       $(".brand_class li").each(function (i) {
        $(this).mouseenter(function () {
            $(this).find("div").stop().animate({ "top": -50 }, 300);
        })
        $(this).mouseleave(function () {
            $(this).find("div").stop().animate({ "top": 0 }, 300);
        })
    });

    /* 左侧 */
    var $menuL = $(".form-box-l");
        $menuL.mouseleave(function(){
            $(this).find("li").removeClass('maintainHover');
            $(this).find(".popover").css("display", "none");
        });
    
        $menuL.menuAim({
            activate: activateSubmenuL,
            deactivate: deactivateSubmenuL,
            submenuDirection: "right"
        });
        function activateSubmenuL(row) {
            var $row = $(row),
                submenuId = $row.data("submenuId"),
                $submenu = $("#" + submenuId),
                height = $menuL.outerHeight(),
                width = $menuL.outerWidth();
                var s1 = $submenu.selector + "";
                var str = s1.substring(9,s1.indexOf("-") + 3);
                console.log(str);
                ///第一次tab 下的li hover 后的layout 位置不正确，在此修正
                if (str < 6){
                   // Show the submenu
                    $submenu.css({
                        display: "block",
                        top: 44,
                        left: width,  // main should overlay submenu
                        height: height // padding for main dropdown's arrow
                    });
                } else {
                    // Show the submenu
                    $submenu.css({
                        display: "block",
                        top: 44,
                        left: width+530,  // main should overlay submenu
                        height: height // padding for main dropdown's arrow
                    });
                }
                // normal Show the submenu  
                /* $submenu.css({
                    display: "block",
                    top: 44,
                    left: width+530,  // main should overlay submenu
                    height: height // padding for main dropdown's arrow
                }); */
                $row.addClass("maintainHover");
        }

        function deactivateSubmenuL(row) {
            var $row = $(row),
                submenuId = $row.data("submenuId"),
                $submenu = $("#" + submenuId);
                $submenu.css("display", "none");
                $row.removeClass("maintainHover");
        }

        /* 右侧 */
        var $menuR = $(".form-box-r");
            $menuR.mouseleave(function(){
                $(this).find("li").removeClass('maintainHover');
                $(this).find(".popover").css("display", "none");
            });
        
            $menuR.menuAim({
                activate: activateSubmenuR,
                deactivate: deactivateSubmenuR,
                submenuDirection: "left"
            });
        function activateSubmenuR(row) {
            var $row = $(row),
                submenuId = $row.data("submenuId"),
                $submenu = $("#" + submenuId),
                height = $menuR.outerHeight(),
                width = $menuR.outerWidth();
                var s2 = $submenu.selector + "";
                var str = s2.substring(9,s2.indexOf("-") + 3);
                console.log(str);
                ///第一次tab 下的li hover 后的layout 位置不正确，在此修正
                if (str < 16 && str > 10){
                   // Show the submenu
                    $submenu.css({
                        display: "block",
                        top: 44,
                        left: width-1040,  // main should overlay submenu
                        height: height // padding for main dropdown's arrow
                    });
                } else {
                    // Show the submenu
                    $submenu.css({
                        display: "block",
                        top: 44,
                        left: width-530,  // main should overlay submenu
                        height: height // padding for main dropdown's arrow
                    });
                }

                // normal Show the submenu                
                /*$submenu.css({
                    display: "block",
                    top: 44,
                    left: width-530,  // main should overlay submenu
                    height: height // padding for main dropdown's arrow
                });*/
                $row.addClass("maintainHover");
        }

        function deactivateSubmenuR(row) {
            var $row = $(row),
                submenuId = $row.data("submenuId"),
                $submenu = $("#" + submenuId);
                $submenu.css("display", "none");
                $row.removeClass("maintainHover");
        }

        $(".form-box li").click(function(e) {
            e.stopPropagation();
        });

        $(document).click(function() {
            $(".popover").css("display", "none");
            $("li.maintainHover").removeClass("maintainHover");
        });

       /* 饼图调用 */
        $('.chart').easyPieChart({
            easing: 'easeOutBounce',
            onStep: function(from, to, percent) {
                $(this.el).find('.percent').text(Math.round(percent));
            }
        });

        var chart = window.chart = $('#chart01').data('easyPieChart');
        $('.pie_update').on('click', function() {
            chart.update(Math.random()*200-100);
        });
    
});
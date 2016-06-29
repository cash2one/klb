$(function() {
var $menuL = $("#form-box-l");
        $menuL.menuAim({
            activate: activateSubmenuL,
            deactivate: deactivateSubmenuL,
            submenuDirection: "right"
        });
        $menuL.css("margin-bottom",0)
        function activateSubmenuL(row) {
            var $row = $(row),
                submenuId = $row.data("submenuId"),
                $submenu = $("#" + submenuId),
                height = $menuL.outerHeight(),
                width = $menuL.outerWidth();

            // Show the submenu
            $submenu.css({
                display: "block",
                top: 4,
                left: width+110,  // main should overlay submenu
                height: height+25 // padding for main dropdown's arrow
            });
            $row.addClass("maintainHover");
        }

        function deactivateSubmenuL(row) {
            var $row = $(row),
                submenuId = $row.data("submenuId"),
                $submenu = $("#" + submenuId);
            $submenu.css("display", "none");
            $row.removeClass("maintainHover");
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
});
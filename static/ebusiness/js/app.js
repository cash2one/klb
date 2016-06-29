function GetVin() {
    var licenseNo_re = /^[\u4e00-\u9fa5]{1}[A-Z0-9]{6}$/gi;
    var ownerName_re = /^[\u4e00-\u9fa5]{2,5}$/gi;
    var ownerName = $.trim($("#ownerName").val());
    var licenseNo = $.trim($("#licenseNo").val());
    $("#vin").removeAttr("readonly");
    $("#engine").removeAttr("readonly");
    if (ownerName == "" && licenseNo == "") {
        return false;
    }
    var licenseNois = licenseNo_re.test(licenseNo);
    var ownerNameis = ownerName_re.test(ownerName);
    if (!licenseNois) {
        var licenseNo_msg = '<div class="alert alert-warning">' +
            '<button type="button" class="close" data-dismiss="alert">' +
            '<span aria-hidden="true">×</span>' +
            '<span class="sr-only">Close</span>' +
            '</button>' +
            '<strong>提示：</strong>' +
            '车牌号码格式错误!</div>';
        $("#sub-body").prepend(licenseNo_msg);
        $('#modal').modal('hide');
        return false;
    }

    if (!ownerNameis) {
        var licenseNo_msg = '<div class="alert alert-warning">' +
            '<button type="button" class="close" data-dismiss="alert">' +
            '<span aria-hidden="true">×</span>' +
            '<span class="sr-only">Close</span>' +
            '</button>' +
            '<strong>提示：</strong>' +
            '车主姓名格式错误!</div>';
        $("#sub-body").prepend(licenseNo_msg);
        $('#modal').modal('hide');
        return false;
    }

    if (licenseNois && ownerNameis) {


        var vin = $.trim($("#vin").val());
        var engine = $.trim($("#engine").val());

        if (ownerName == "" || licenseNo == "") {

            var msg = '<div class="alert alert-warning">' +
                '<button type="button" class="close" data-dismiss="alert">' +
                '<span aria-hidden="true">×</span>' +
                '<span class="sr-only">Close</span>' +
                '</button>' +
                '<strong>提示!</strong>' +
                '车牌号码车主姓名不能为空!</div>';
            $("#sub-body").prepend(msg);
            $('#modal').modal('hide');
        } else {
            $('#modal').modal('show', {backdrop: 'static'});
            var m1 = $("#vin").val();
            var m2 = $("#engine").val();
            if (m1 == "" && m2 == "") {
                var data = {"n1": licenseNo, "n2": ownerName, "a": "a1"};
                $.ajax({
                    url: '/ebusiness/GetVIN/',
                    type: "POST",
                    contentType: "application/x-www-form-urlencoded; charset=utf-8",
                    data: data,
                    dataType: "json", success: function (d) {
                        if (d.error == "1") {
                            $("#form-vin").show();
                            $("#form-engine").show();
                            $('#modal').modal('hide');
                            $("#sub-btn").attr("type", "submit");
                            $("#auto-vin-btn").attr("disabled", "disabled");
                        } else {
                            $("#form-vin").show();
                            $("#form-engine").show();
                            $("#vin").val(d.data.n1).attr("readonly", "readonly");
                            $("#auto-vin-btn").attr("disabled", "disabled");
                            $("#engine").val(d.data.n2).attr("readonly", "readonly");
                            $('#modal').modal('hide');
                            $("#sub-btn").attr("type", "submit");
                            // readonly="readonly"
                        }


                    },
                    error: function () {
                        $("#form-vin").show();
                        $("#form-engine").show();
                        $("#sub-btn").attr("type", "submit");
                        $('#modal').modal('hide');
                    }
                });
            } else {
                $("#form-vin").show();
                $("#form-engine").show();
                $("#sub-btn").attr("type", "submit");
                $('#modal').modal('hide');
            }

        }
    } else {
        $('#modal').modal('hide');
        $("#sub-btn").attr("type", "submit");
    }

}
function ShowVinInput() {
    $("#form-engine,#form-vin").show();
    $("#show-guohu").text("过户车");
}
function SetVinVal() {
    if ($.trim($("#ownerName").val()) == "" || $.trim($("#licenseNo").val()) == "") {
        $("#vin").val("").removeAttr("readonly");
        $("#engine").val("").removeAttr("readonly");
    }
    $("#auto-vin-btn").removeAttr("disabled");
}
$(function () {
    $("input[type='text']").blur(function () {
        this.value = this.value.toUpperCase();
    });
    $("#ownerName,#licenseNo").blur(function () {
        SetVinVal();
    });

    $("#sub-btn").click(function () {
        if ($("#sub-btn").attr("type") == "button") {
            GetVin();
        }
    });

});

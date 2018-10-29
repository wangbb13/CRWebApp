function main() {
    var map = new BMap.Map("auxiliary");
    var point = new BMap.Point(81.389641, 49.289662);
    map.centerAndZoom(point, 4);
    map.enableScrollWheelZoom(true);
    map.setMapStyle({
        style: "midnight"
    });
    var geoc = new BMap.Geocoder();

    map.addEventListener("click", function(e){
        //通过点击百度地图，可以获取到对应的point, 由point的lng、lat属性就可以获取对应的经度纬度
        var pt = e.point;
        geoc.getLocation(pt, function(rs){
            //addressComponents对象可以获取到详细的地址信息
            var addComp = rs.addressComponents;
            // var site = addComp.province + ", " + addComp.city + ", " + addComp.district + ", " + addComp.street + ", " + addComp.streetNumber;
            var site = addComp.city;
            //将对应的HTML元素设置值
            $("#city_name").val(site);
            $("#lng_val").val(pt.lng);
            $("#lat_val").val(pt.lat);
        });
    });
}

$(function () {
    main();
});

$("#add_btn").click(function () {
    var city_name = $("#city_name").val();
    if (city_name == "") {
        alert("城市名不能为空！");
        return;
    }
    var lng_val = $("#lng_val").val();
    if (lng_val == "") {
        alert("经度不能为空！");
        return;
    }
    var lat_val = $("#lat_val").val();
    if (lat_val == "") {
        alert("纬度不能为空！");
        return;
    }
    var no_val = $("#no_val").val();
    if (no_val == "") {
        alert("数值不能为空");
        return;
    }
    var add_data = {
        city: city_name,
        lng: lng_val,
        lat: lat_val,
        val: no_val
    };

    $.ajax({
        type: "POST",
        url: "/auxiliary/add/",
        data: add_data,
        success: function (resJson) {
            if (resJson.res == 1) {
                alert("添加成功！");
            } else {
                alert("添加失败！");
            }
        },
        error: function () {
            alert("传输失败！");
        }
    });
});

$("#search_add_btn").click(function () {
    var city = $("#search_val").val();
    var val = $("#sno_val").val();
    if (city == "") {
        alert("城市名为空！");
        return;
    }
    if (val == "") {
        alert("请填写数值!");
        return;
    }
    $.ajax({
        type: "POST",
        url: "/auxiliary/add_search_city/",
        data: {city: city, val: val},
        success: function (resJson) {
            if (resJson.res == 1) {
                alert("添加成功！");
            } else {
                alert("添加失败！");
            }
        },
        error: function () {
            alert("传输必败！");
        }
    });
});

$("#search_btn").click(function () {
    var city = $("#search_val").val();
    if (city == "") {
        return;
    }
    $.ajax({
        type: "POST",
        url: "/auxiliary/search/",
        data: {city: city},
        success: function (resJson) {
            if (resJson.res == 1) {
                var lng = resJson.lng;
                var lat = resJson.lat;
                var map = new BMap.Map("auxiliary");
                map.enableScrollWheelZoom(true);
                map.setMapStyle({
                    style: "midnight"
                });
                var point = new BMap.Point(lng, lat);
                map.centerAndZoom(point, 5);
                var marker = new BMap.Marker(point);
                map.addOverlay(marker);
            } else {
                alert("没找到搜索地区！");
            }
        },
        error: function () {
            alert("传输必败！");
        }
    });
});
function renderItem(params, api) {
    var coords = [
        [116.7,39.53],
        [103.73,36.03],
        [112.91,27.87],
        [120.65,28.01],
        [119.57,39.95]
    ];
    var points = [];
    for (var i = 0; i < coords.length; i++) {
        points.push(api.coord(coords[i]));
    }
    var color = api.visual('color');

    return {
        type: 'polygon',
        shape: {
            points: echarts.graphic.clipPointsByRect(points, {
                x: params.coordSys.x,
                y: params.coordSys.y,
                width: params.coordSys.width,
                height: params.coordSys.height
            })
        },
        style: api.style({
            fill: color,
            stroke: echarts.color.lift(color)
        })
    };
}

function convertData(data, coordMap) {
	var res = [];
    for (var i = 0; i < data.length; i++) {
        var geoCoord = coordMap[data[i].name];
        if (geoCoord) {
            res.push({
                name: data[i].name,
                value: geoCoord.concat([data[i].value, data[i].detail])
            });
        }
    }
    return res;
}

function main(obj) {
    // get map info
    // console.log(obj);
	var data = obj.city;
	var geoCoordMap = obj.loc;
	var sum = 0;
	for (var i = 0; i < data.length; ++i) {
	    sum += data[i].value;
    }

	var dom = document.getElementById("main");
	var myChart = echarts.init(dom);
	var option = {
		// backgroundColor: '#404a59',
    	title: {
    	    text: '堆场集装箱数量情况',
    	    subtext: 'quantity of container in storage yard',
    	    sublink: '#',
    	    left: 'center',
    	    textStyle: {
    	        color: '#fff'
    	    }
    	},
    	tooltip : {
    	    trigger: 'item',
            formatter: function (params) {
    	        var str = params.name + ": " + params.value[2] + "</br>";
    	        str = str + "————————</br>";
    	        for (var i = 0; i < params.value[3].length; ++ i) {
    	            str = str + params.value[3][i].name + ": " + params.value[3][i].value + "</br>";
                }
                return str;
            }
    	},
    	bmap: {
    	    center: [81.389641, 45.289662],
    	    zoom: 4,
    	    roam: true,
			mapStyle: { style: "midnight" }
    	},
    	series : [
    	    {
    	        name: 'container',
    	        type: 'scatter',
    	        coordinateSystem: 'bmap',
    	        data: convertData(data, geoCoordMap),
    	        symbolSize: 10,
    	        label: {
    	            normal: {
    	                formatter: '{b}',
    	                position: 'right',
    	                show: false
    	            },
    	            emphasis: {
    	                show: true
    	            }
    	        },
    	        itemStyle: {
    	            normal: {
    	                color: '#ddb926'
    	            }
    	        }
    	    },
    	    {
    	        // name: 'Top 5',
    	        type: 'effectScatter',
    	        coordinateSystem: 'bmap',
    	        data: convertData(data.sort(function (a, b) {
    	            return b.value - a.value;
    	        }), geoCoordMap),
    	        symbolSize: 10,
    	        showEffectOn: 'emphasis',
    	        rippleEffect: {
    	            brushType: 'stroke'
    	        },
    	        hoverAnimation: true,
    	        label: {
    	            normal: {
    	                formatter: '{b}',
    	                position: 'right',
    	                show: true
    	            }
    	        },
    	        itemStyle: {
    	            normal: {
    	                color: '#f4e925',
    	                shadowBlur: 10,
    	                shadowColor: '#333'
    	            }
    	        },
    	        zlevel: 1
    	    }
    	]
	};

	myChart.setOption(option, true);
}

function fetch_data(s_time, e_time) {
    $.ajax({
        type: "POST",
        url: "/yard_info/",
        data: {start: s_time, end: e_time},
        success: function (resJson) {
            main(resJson);
        },
        error: function () {
            main({city: [], loc: {}});
            alert("获取数据失败！");
        }
    });
}

$(function () {
	// alert("hello, world!");
    $("#start_datetime").datetimepicker({
        format: "YYYY-MM-DD HH:mm",
        defaultDate: "2018-01-01 00:00"
    });
    $("#end_datetime").datetimepicker({
        format: "YYYY-MM-DD HH:mm",
        defaultDate: "2018-08-31 00:00"
    });
    // $("#start_datetime").on("change.datetimepicker", function (e) {
    //     // fetch_data(e.date.format("YYYY-MM-DD HH:mm").toString(), $("#end_datetime input").val());
    //     alert(e.date.format("YYYY-MM-DD HH:mm").toString());
    // });
    // $("#end_datetime").on("change.datetimepicker", function (e) {
    //     // fetch_data($("#start_datetime input").val(), e.date.format("YYYY-MM-DD HH:mm").toString());
    //     alert(e.date.format("YYYY-MM-DD HH:mm").toString());
    // });
    fetch_data($("#start_datetime input").val(), $("#end_datetime input").val());
    // $.getJSON('/static/main/data/map.json', {
    //     format: "json"
    // }).done(function (data) {
    //     main(data);
    // });
    $("#query_yard_btn").click(function () {
        fetch_data($("#start_datetime input").val(), $("#end_datetime input").val());
    });
});
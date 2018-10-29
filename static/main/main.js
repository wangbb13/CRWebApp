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
                value: geoCoord.concat(data[i].value)
            });
        }
    }
    return res;
}

function main(obj) {
    // get map info
	var data = obj.city;
	var geoCoordMap = obj.loc;

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
    	    trigger: 'item'
    	},
    	bmap: {
    	    center: [81.389641, 45.289662],
    	    zoom: 4,
    	    roam: false,
			mapStyle: { style: "midnight" }
    	},
    	series : [
    	    {
    	        name: 'container',
    	        type: 'scatter',
    	        coordinateSystem: 'bmap',
    	        data: convertData(data, geoCoordMap),
    	        symbolSize: function (val) {
    	            return val[2] / 10;
    	        },
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
    	        symbolSize: function (val) {
    	            return val[2] / 10;
    	        },
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

$(function () {
	// alert("hello, world!");
    $.getJSON('/static/main/data/map.json', {
        format: "json"
    }).done(function (data) {
        main(data);
    });
});
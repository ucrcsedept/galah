// Event listeners and use utilities for graphing with flot.
var disabledIndices = {
    'timeline': [],
    'distribution': []
};

var plots = {
    'timeline': null,
    'distribution': null
};

var options = {
    'timeline': null,
    'distribution': null
}

// Plot drawing hook to disable certain series.
function disableSeries(plot, ctx, series) {
    var seriesIndex = plot.getData().indexOf(series);
    var id = $(plot.getPlaceholder()).attr('id');
    if (disabledIndices[id].indexOf(seriesIndex) !== -1) {
	series.data = [];
	series.datapoints.points = [];
    }
}

// Start and end time of series data for spacing.
var start = null;
var end = null;

// Setup graphing options
options.timeline = {
    series: {
	lines: {
	    show: true,
	    lineWidth: 3
	},
	points: {
	    show: true,
	    radius: 5
	}
    },
    crosshair: {
	mode: "x"
    },
    grid: { 
	hoverable: true, 
	clickable: true
    },
    interaction: {
	redrawOverlayInterval: 5
    },
    selection: {
	mode: "x"
    },
    legend: {
	labelFormatter: function(label, series) {
	    labelIndex = seriesLabels.indexOf(label);

	    if (disabledIndices['timeline'].indexOf(labelIndex) !== -1) {
		label = "<span class='disabled'>" + label + "</span>";
	    }

	    return label;
	}
    },
    xaxis: {
	min: start,
	max: end,
	mode: "time",
	timeZone: "America/LosAngeles",
	tickLength: 5,
	twelveHourClock: true
    },
    hooks: {
	drawSeries: [disableSeries]
    }
};

options.distribution = {
    series: {
	lines: {
	    show: true,
	    fill: true,
	    zero: true
	},
	points: {
	    show: true,
	    radius: 4
	}
    },
    crosshair: {
	mode: "x"
    },
    grid: { 
	hoverable: true, 
	clickable: true
    },
    interaction: {
	redrawOverlayInterval: 5
    },
    selection: {
	mode: "x"
    },
    legend: {
	labelFormatter: function(label, series) {
	    labelIndex = distributionLabels.indexOf(label);

	    if (disabledIndices['distribution'].indexOf(labelIndex) !== -1) {
		label = "<span class='disabled'>" + label + "</span>";
	    }

	    return label;
	}
    },
    hooks: {
	drawSeries: [disableSeries]
    }
};

// Logic for disabling certain series on click.
function updateDisabledSeries(chart, plot, disabledIndices, child_index) {
    var index = disabledIndices.indexOf(child_index);

    // Add index if it doesn't exist.
    if (index === -1) {
	disabledIndices.push(child_index);
    } else {
	// Delete it if it does.
	disabledIndices.splice(index, 1);
    }

    // Redraw plot to exclude/include series.
    plot = $.plot($(chart), plot.getData(), plot.getOptions());
}

var plots = {};

// User can zoom in to section by highlighting.
$(".chart").bind("plotselected", function (event, ranges) {
    var id = $(this).attr("id");
    var plot = plots[id];
    plots[id] = $.plot($(this), plot.getData(),
		       $.extend(true, {}, options[id], {
			   xaxis: { 
			       min: ranges.xaxis.from,
			       max: ranges.xaxis.to 
			   }
		       }));
});

// Capture right click and zoom out to original view.
$(".chart").bind("contextmenu", function(e) {
    id = $(this).attr("id");
    var plot = plots[id];
    plots[id] = $.plot($(this), plot.getData(), options[id]);
    return false;
});


// Logic to display score tooltip on point hover
function showTooltip(x, y, contents) {
    $('<div class="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 5,
        border: '1px solid #fdd',
        padding: '2px',
        'background-color': '#fee',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}

var previousPoint = null;
$("#timeline").bind("plothover", function (event, pos, item) {
    $(".y").text(pos.y.toFixed(2));

    if (item) {
        if (previousPoint != item.dataIndex) {
            previousPoint = item.dataIndex;
            
            $(".tooltip").remove();
	    x = new Date(item.datapoint[0]);
	    // Adjust stored datetime from UTC-0800 (LosAngeles) to original
	    x.addHours(8);
            y = item.datapoint[1].toFixed(2);
            
            showTooltip(item.pageX, item.pageY,
                        item.series.label + " : " +  y + "<br>"
			+ "Submitted " + x.toString("M/d/yyyy hh:mm tt"));
        }
    }
    else {
        $(".tooltip").remove();
        previousPoint = null;            
    }
});

var users = [{}];
function distributionToolTip(event, pos, item) {
    $(".y").text(pos.y.toFixed(2));

    if (item) {
        if (previousPoint != item.dataIndex) {
            previousPoint = item.dataIndex;
            
            $(".tooltip").remove();
	    x = item.datapoint[0].toFixed(2);
	    y = item.datapoint[1];
            
	    labelPos = distributionLabels.indexOf(item.series.label);
            showTooltip(item.pageX, item.pageY,
                        item.series.label + " : " + x + "<br>"
			+ "Submission from: " + 
			users[labelPos][item.datapoint[0]]);
        }
    }
    else {
        $(".tooltip").remove();
        previousPoint = null;            
    }
}

$("#distribution").bind("plothover", distributionToolTip);


$("#timeline").bind("plotclick", function (event, pos, item) {
    if (item) {
	time = item.datapoint[0];
	d = new Date(time);
	dateString = d.toISOString();
	element = document.getElementById(dateString);
	if (element !== null) {
	    $("body").scrollTop($(element).offset().top);
	}
    }
});

$(".legend tr").live("click", function() {
    var chart = $(this).closest(".chart");
    var plot = plots[$(chart).attr('id')];
    var disabledIndex = disabledIndices[$(chart).attr('id')];
    updateDisabledSeries(chart, plot, disabledIndex, $(this).index());
});

// Converts default timestamp in db to one recognized by firefox and chrome
function smartTimestamp(default_time) {
    // Replace first space with "T" for firefox timestamp RFC.
    var smartStamp = default_time.replace(/ /, "T");
    // Adjusting to UTC for Flot uses.
    smartStamp += "+00:00";

    var d = new Date(smartStamp);
    return d;
}

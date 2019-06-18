var width = 960,
    height = 600,
    radius = Math.min(width, height) / 2,
    colors = {'Person': '#E14E5F', 'Organization': '#A87621', 'Place': '#43943E', 'CreativeWork': '#AC5CC4', 'Intangible': '#2E99A0',
    'Action': '#2986EC', 'MedicalEntity': '#999900', 'Event': '#ffdd55'  },
    colorOpacity = 0.7;

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2.1 + ") scale(1.05)")
    .call(d3.behavior.zoom().scaleExtent([1, 12]).on("zoom", zoom))
  .append("g");

function zoom() {
  svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

var partition = d3.layout.partition()
    .size([2 * Math.PI, radius * radius])
    .value(function(d) { return d.size; });

var arc = d3.svg.arc()
    .startAngle(function(d) { return d.x; })
    .endAngle(function(d) { return d.x + d.dx; })
    .innerRadius(function(d) { return Math.sqrt(d.y); })
    .outerRadius(function(d) { return Math.sqrt(d.y + d.dy); });

var text = svg.append("text")
            .attr("x", 0)
            .attr("y", 0)
            .attr("dy", "0.35em");

getColor = function(d) {
    var flag;
    if (d.name === "Thing") {
      return '#7E7F7E';
    } else if (d.name in colors) {
      return colors[d.name];
    } else {
      flag = '#7E7F7E';
      while (d.parent.name !== "Thing") {
        if (d.parent.name in colors) {
          flag = colors[d.parent.name];
          break;
        } else {
          d = d.parent;
        }
      }
      return flag;
    }
  };

drawLegend();
thousand_sep_format = d3.format(',');

du = 'http://localhost:8080/docs/tree.jsonld'
// du = 'http://sdo-phobos.appspot.com/docs/tree.jsonld'
// du = 'http://wafi.iit.cnr.it/webvis/tmp/schema.org.json' // http://bl.ocks.org/fabiovalse/63fba792a7922d03243a
d3.json(du, function(error, root) {

  getSize(root);
//  console.log("getsize of " + root["name"]);

root = {"name": root.name, "size": root.size, "children": [root]};

function getSize(d) {
  if (d["children"] &&  d.children.length === 0) {
    d.size = 1;
    return 1;
  } else if (!d["children"]) { // e.g. SomeProducts, no children.
    d.size = 1;           // other code had children=[] in this case
    return 1;
  } else {
    // console.log("Else: "+d["name"] + d["children"])
    var sum = 0;
    if (d.children) {
      d.children.forEach(function(c) { sum += getSize(c); });
    }
    d.size = sum;
    return d.size;
  }
  return d;
}

  var path = svg.datum(root).selectAll("path")
      .data(partition.nodes)
    .enter().append("path")
      .attr("display", function(d) { return d.depth ? null : "none"; }) // hide inner ring
      .attr("d", arc)
      .style("stroke", "#fff")
      .style("fill", function(d) { return getColor(d); })
      .style("opacity", colorOpacity)
      .on("mouseover", mouseover)
      .on("mouseout", mouseout);

  function mouseover(d) {
    var percentage = (100 * d.size / root.size).toPrecision(3);
    text.html("<tspan style='font-size: 30px' x=0 dy='-20'>" + thousand_sep_format(d.size) + "</tspan><tspan style='font-size: 15px' x=0 dy='25'>" + d.name + "</tspan><tspan style='font-size: 30px' x=0 dy='35'>" + percentage + "%</tspan>");

    d3.selectAll("path")
      .filter(function(d1) { return d === d1; })
      .style("opacity", 0.5);
  }

  function mouseout(d) {
    text.html("");

    d3.selectAll("path")
      .filter(function(d1) { return d === d1; })
      .style("opacity", colorOpacity);
  }
});

d3.select(self.frameElement).style("height", height + "px");

function drawLegend() {
  var li = {
    w: 85, h: 30, s: 3, r: 3
  };

  var legend = svg.append("g")
      .attr("transform", function(d, i) {
        return "translate(" + (width/2 - li.w*1.3) + "," + (height/2 - li.h*Object.keys(colors).length*1.2) + ")";
      });

  var g = legend.selectAll("g")
      .data(d3.entries(colors))
      .enter().append("svg:g")
      .attr("transform", function(d, i) {
              return "translate(0," + (i * (li.h + li.s)) + ")";
           });

  g.append("svg:rect")
      .attr("rx", li.r)
      .attr("ry", li.r)
      .attr("width", li.w)
      .attr("height", li.h)
      .style("opacity", colorOpacity)
      .style("fill", function(d) { return d.value; });

  g.append("svg:text")
      .attr("x", li.w / 2)
      .attr("y", li.h / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .classed("legendItem", true)
      .text(function(d) { return d.key; });
}

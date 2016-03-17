color_opacity = 0.7
duration = 2000

svg = d3.select 'svg'

width = svg.node().getBoundingClientRect().width
height = d3.select('body').node().getBoundingClientRect().height/1.1

svg.attr
  width: width
  height: height
  viewBox: "#{-width/2} #{-height/2} #{width} #{height}"

radius = Math.min(width, height) * 2

colors =
  'Person': '#E14E5F'
  'Organization': '#A87621'
  'Place': '#43943E'
  'CreativeWork': '#AC5CC4'
  'MedicalEntity': '#2E99A0'
  'Event': '#2986EC'

# append a group for zoomable content
zoomable_layer = svg.append('g')

# define a zoom behavior
zoom = d3.behavior.zoom()
  .scaleExtent([0.5,64])
  .on 'zoom', () ->
    zoomable_layer
      .attr
        transform: "translate(#{zoom.translate()})scale(#{zoom.scale()})"

    zoomable_layer.selectAll '.semantic_zoom'
      .attr
        transform: "scale(#{1/zoom.scale()})"
        
    lod zoom.scale()
    
svg.call(zoom)

lod = (z) ->
  zoomable_layer.selectAll '.semantic_zoom'
    .attr
      display: (d) -> if 20/z < d.dx*Math.pow(d.dy, 0.4) then 'inline' else 'none'

partition = d3.layout.partition()
  .sort null
  .size [2 * Math.PI, radius * radius]
  .value () -> 1

arc = d3.svg.arc()
  .startAngle (d) -> d.x
  .endAngle (d) -> d.x + d.dx
  .innerRadius (d) -> Math.pow(d.y, 0.4)
  .outerRadius (d) -> Math.pow(d.y + d.dy, 0.4)

get_color = (d) ->
  if d.name is 'Thing'
    '#7E7F7E'
  else if d.name of colors
    colors[d.name]
  else
    get_color d.parent

prune_tree = (node) ->
  if node.children?

    for index, child of node.children
      if child.layer isnt 'core'
        node.children.splice index, 1
      else
        prune_tree child

redraw = (flag) ->
  d3.json 'tree.json', (error, root) ->
    
    if flag
      console.log prune_tree root

    tree_utils.canonical_sort root  
    nodes = partition.nodes root
    
    ### SECTORS
    ###
    sectors = zoomable_layer.selectAll '.class'
      .data nodes, (d) -> d['@id']

    enter_sectors = sectors.enter().append('a')
      .attr
        class: 'class'
        'xlink:href': (d) ->"../#{d.name}"
        target: '_blank'

    enter_sectors.append('path')
      .attr
        class: 'sector',
        fill: (d) -> 
          get_color d
        opacity: 0
        d: arc
      .transition().duration(1500)
        .style
          opacity: 1

    enter_sectors.append 'title'
    
    sectors.select '.sector'
      .transition().delay(1500).duration(1500)
      .attr
        d: arc
      
    sectors.select 'title'
      .text (d) -> "#{d.name}:\n#{d.description}"

    sectors.exit()
      .transition().delay(500).duration(1500)
      .style
        opacity: 0
      .remove()

    ### Sector LABELS
    ###
    labels = zoomable_layer.selectAll '.label'
      .data nodes, (d) -> d['@id']
      
    enter_labels = labels.enter().append 'g'
      .attr
        class: 'label'

    labels.transition().duration(1500)
      .attr
        transform: (d) ->
          if d.name is 'Thing'
            'translate(0,0)'
          else 
            "translate(#{(Math.pow(d.y + d.dy/2, 0.4)) * Math.cos(d.x + d.dx/2 - Math.PI/2)}, #{(Math.pow(d.y + d.dy/2, 0.4)) * Math.sin(d.x + d.dx/2 - Math.PI/2)})"
          
    enter_labels.append 'text'
      .attr
        class: 'halo semantic_zoom'
        dy: '0.35em'
      
    labels.select '.halo'
      .text (d) -> d.name

    enter_labels.append 'text'
      .attr
        class: 'halo_text semantic_zoom'
        dy: '0.35em'
      
    labels.select '.halo_text'
      .text (d) -> d.name

    labels.exit().remove()

    ### Radio buttons on-change transition
    ###
    d3.selectAll('input').on 'change', () ->
      redraw(this.value is 'local')

    # Initialize the visualization with a level of detail equal to 1
    lod 1

redraw d3.select('input[checked]').node().value is 'local'
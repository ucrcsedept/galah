YUI().use('tabview', function(Y) {
    var instances = Y.all(".tabs")
    
    instances.each(function (i) {
        var tab_nodes = i.all(".tab")
        var tabs = []
        tab_nodes.each(function (j) {
            // Get the heading
            var heading_node = j.one("h1")
            if (heading_node == null)
                throw new Error
            
            // Add the tab to the list of tabs
            tabs.push({label: heading_node.getHTML(), content: j})
            
            // Hide the heading, it'll be redundant
            heading_node.hide()
        })
        
        var tabview = new Y.TabView({children: tabs})
        console.log(tabs)
        tabview.render(i)
    })
});


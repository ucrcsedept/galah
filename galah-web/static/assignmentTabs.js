YUI().use('tabview', function(Y) {
    var tabview = new Y.TabView({
        children: [
            {
                label: "Your Submissions",
                content: Y.one("#submissions")
            },
            {
                label: "Tests",
                content: Y.one("#assignment_details")
            }
        ]
    });

    Y.all("h1").hide()

    tabview.render("#container");
});


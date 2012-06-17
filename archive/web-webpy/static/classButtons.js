YUI().use("overlay", "widget-autohide", function(Y) {                
    /* Create the overlay dynamically. Better than markup in this case
     * because we don't want javascript-restricted devices to see it */
    var overlay = new (Y.Base.create("overlay", Y.Overlay, [Y.WidgetAutohide]))
    overlay.set("hideOn", [
        {eventName: "clickoutside"},
        {node: Y.one("document"), eventName: "key", keyCode: "esc"}
    ])
    
    overlay.render()
    overlay.hide()
    
    // Create a function that updates the overlay
    var setOverlayContent = function (title, attributes) {
        /*overlay.set("headerContent",
                    "<span class='overlayTitle'>" + title +
                        "</span>")*/
        
        // Create the content
        var attributeList = Y.Node.create("<div class='attributeList'></div>")
        for (var i = 0; i < attributes.length; i++)
        {
            
            var attributePair = Y.Node.create("<div class='attributePair'></div>")
            attributePair.append("<span class='attribute'>" +
                                     attributes[i][0] + "</span>")
            attributePair.append("<span class='value'>" +
                                     attributes[i][1] + "</span>")
                                     
            attributeList.appendChild(attributePair)
        }
        
        overlay.set("bodyContent", attributeList)
        
        var closeButton = Y.Node.create("<a href='#'>Close</a>")
        closeButton.on("click", function () { overlay.hide() })
        
        //overlay.set("footerContent", closeButton)
    }
    
    // Loop through all of the links to classes
    var classButtons = Y.all(".classButton")
    classButtons.each(function (button) {
        // Grab the class ID
        var classId = button.get("href").split("/").pop()
        //button.removeAttribute("href")
        
        /* The function that will make an overlay appear under the
         * clicked link */
        var overlayAction = function (e, classId) {
            var self = Y.one(this)
            if (self.hasClass("overlaid"))
            {
                self.removeClass("overlaid")
                overlay.hide()
            } else {
                var a = Y.WidgetPositionAlign,
                    classInfo = classMap[classId]
                    
                // Create the attribute list
                var attributes = []
                attributes.push(["Instructor", classInfo["with"]])
                if ("site" in classInfo)
                {
                    attributes.push(["Site", "<a href='" + classInfo["site"] + "'>Click Here</a>"])
                }
                    
                setOverlayContent(classInfo.name, attributes)
                
                overlay.set("align", {node: self, points: [a.TL, a.BL]})
                
                overlay.show()
                
                self.addClass("overlaid")
            }
            
            e.preventDefault()
            
            /* Without this the autohide plugin will think we clicked
             * outside of the overlay and immediately hide it */
            e.stopPropagation()
        }                
        
        button.on("click", overlayAction, button, classId)
    })
})

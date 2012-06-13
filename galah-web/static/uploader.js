YUI().use("uploader", "cookie", "io", function(Y) {
    if (Y.Uploader.TYPE == "none" || Y.UA.ios) {
        Y.one("#uploaderContainer").set("text", "We are sorry, but the uploader technology is not supported" + 
                                               " on this platform.");
        return
    }
    
    var assignment = location.href.split("/").pop(), session = Y.Cookie.get("webpy_session_id")
    
    var uploader = new Y.Uploader({
        width: "250px", 
        height: "35px", 
        multipleFiles: true,
        swfURL: "/static/yui3/uploader/assets/flashuploader.swf?t=" + Math.random(),
        uploadURL: "/submit/" + assignment,
        simLimit: 2
    })

    var uploadDone = false, uploadFailed = false

    if (Y.Uploader.TYPE == "html5") {
        uploader.set("dragAndDropArea", "body")

        Y.one("#ddmessage").setHTML("<strong>Drag and drop files here.</strong>")

        uploader.on(["dragenter", "dragover"], function (event) {
            var ddmessage = Y.one("#ddmessage");
            if (ddmessage) {
                ddmessage.setHTML("<strong>Files detected, drop them here!</strong>");
                ddmessage.addClass("yellowBackground");
            }
        })

        uploader.on(["dragleave", "drop"], function (event) {
            var ddmessage = Y.one("#ddmessage");
            if (ddmessage) {
                ddmessage.setHTML("<strong>Drag and drop files here.</strong>");
                ddmessage.removeClass("yellowBackground");
            }
        })
    }

    uploader.render("#selectFilesButtonContainer")

    uploader.after("fileselect", function (event) {
        var fileList = event.fileList
        var fileTable = Y.one("#filenames tbody")
        if (fileList.length > 0) {
            Y.one("#nofiles").hide()
        } else if (fileList.length == 0) {
            Y.one("#nofiles").show()
        }

        if (uploadDone) {
            uploadDone = false
            fileTable.setHTML("")
        }
      
        var perFileVars = {}

        Y.each(fileList, function (fileInstance) {
            fileTable.append(
                "<tr id='" + fileInstance.get("id") + "_row" + "'>" + 
                "<td class='filename'>" + fileInstance.get("name") + "</td>" + 
                "<td class='percentdone'>Hasn't started yet</td>"
            )

            perFileVars[fileInstance.get("id")] = {
                filename: fileInstance.get("name"),
                session_id: session
            }
        })

        uploader.set("postVarsPerFile", Y.merge(uploader.get("postVarsPerFile"), perFileVars))
    })

    uploader.on("uploadprogress", function (event) {
        var fileRow = Y.one("#" + event.file.get("id") + "_row")
        fileRow.one(".percentdone").set("text", event.percentLoaded + "%")
    })

    uploader.on("uploadstart", function (event) {
        uploader.set("enabled", false)
        Y.one("#uploadFilesButton").addClass("yui3-button-disabled")
        Y.one("#uploadFilesButton").detach("click")
    })

    uploader.on("uploadcomplete", function (event) {
        var fileRow = Y.one("#" + event.file.get("id") + "_row")
        
        if (event.data == "GOOD") {
            fileRow.one(".percentdone").set("text", "Finished!")
        } else {
            fileRow.one(".percentdone").setHTML(event.data)
            
            uploadFailed = true
        }
    })

    uploader.on("totaluploadprogress", function (event) {
        Y.one("#overallProgress").setHTML("Total uploaded: <strong>" + event.percentLoaded + "%" + "</strong>")
    })

    uploader.on("alluploadscomplete", function (event) {
        uploader.set("enabled", true)
        
        ok = Y.io("/submit/" + assignment, {
            method: "POST",
            data: "session_id=" + session + "&done=true",
            sync: true
        })
        
        if (ok.responseText != "GOOD") {
            uploadFailed = true
        }
        
        if (!uploadFailed) {
            Y.one("#overallProgress").set("text", "Uploads complete!")
            location.reload(true)
            alert("Submission has been uploaded.")
        } else {
            Y.one("#uploadFilesButton").set("text", "Try Again")
            Y.one("#overallProgress").set("text", "Errors occured. Try again?")
        }
        
        Y.one("#uploadFilesButton").removeClass("yui3-button-disabled")
        Y.one("#uploadFilesButton").on("click", function () {
            if (!uploadDone && uploader.get("fileList").length > 0) {
                uploader.uploadAll();
            }
        })
        
        uploadDone = true
    })

    Y.one("#uploadFilesButton").on("click", function () {
        if (!uploadDone && uploader.get("fileList").length > 0) {
            uploader.uploadAll()
        }
    })
})

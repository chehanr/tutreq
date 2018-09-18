"use strict";

jQuery(document).ready(function ($) {
    var modalArchiveButton = document.getElementById("requestModalArchiveButton");
    var modalDismissButton = document.getElementById("requestModalDismissButton");
    var modalPDFButton = document.getElementById("requestModalPDFButton");

    // Button to archive/ unarchive requests.
    $(modalArchiveButton).on("click", function (event) {
        event.preventDefault(); // To prevent following the link (optional)
        var requestId = $(this).data("request-id");
        var baseUrl = "/archive_unarchive_request/";
        var dataDict = {
            "request-id": requestId,
        };
        $.ajax({
            type: "GET",
            url: baseUrl,
            data: dataDict,
            success: function (response) {
                if (!jQuery.isEmptyObject(response)) {
                    var requestId = response.id;
                    var archived = response.archived;
                    var archiveUnarchiveDateTime = response["archive_unarchive_date_time"];

                    if (archived) {
                        $(modalArchiveButton).text("Unarchive");
                    } else {
                        $(modalArchiveButton).text("Archive");
                    }
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                var errMsg = textStatus.concat(": ", errorThrown, ".");
            }
        });
        return false;
    });
    // Button to dismiss/ relodge requests.
    $(modalDismissButton).on("click", function (event) {
        event.preventDefault(); // To prevent following the link (optional)
        var requestId = $(this).data("request-id");
        var baseUrl = "/dismiss_relodge_request/";
        var dataDict = {
            "request-id": requestId,
        };
        $.ajax({
            type: "GET",
            url: baseUrl,
            data: dataDict,
            success: function (response) {
                if (!jQuery.isEmptyObject(response)) {
                    var requestId = response.id;
                    var dismissed = response.dismissed;
                    var dismissRelodgeDateTime = response["dismiss_relodge_date_time"];
                    var tableRow = document.querySelector("[data-request-id=\"" + requestId + "\"]");
                    var modalRequestStatus = document.getElementById("requestInfoListItem3");
                    var tableRequestStatusIcon = tableRow.querySelector("#tableRequestStatusIcon");

                    $(modalRequestStatus).removeClass(
                        "list-group-item-success list-group-item-danger");
                    $(tableRequestStatusIcon).removeClass();
                    if (dismissed) {
                        $(modalRequestStatus).addClass("list-group-item-success");
                        $(modalRequestStatus).text("Request status: Dismissed");
                        $(modalDismissButton).text("Relodge");
                        $(tableRequestStatusIcon).addClass("glyphicon glyphicon-ok");
                    } else {
                        $(modalRequestStatus).addClass("list-group-item-danger");
                        $(modalRequestStatus).text("Request status: Waiting");
                        $(modalDismissButton).text("Dismiss");
                        $(tableRequestStatusIcon).addClass("glyphicon glyphicon-time");
                    }
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                var errMsg = textStatus.concat(": ", errorThrown, ".");
            }
        });
        return false;
    });
    // Button to generate pdfs.
    $(modalPDFButton).on("click", function (event) {
        event.preventDefault(); // To prevent following the link (optional)
        var requestId = $(this).data("request-id");
        var baseUrl = "/generate_pdf/";
        var dataDict = {
            "request-id": requestId,
        };
        $.ajax({
            type: "GET",
            url: baseUrl,
            data: dataDict,
            success: function (response, status, xhr) {
                // https://stackoverflow.com/questions/16086162/handle-file-download-from-ajax-post
                // check for a filename
                var filename = "";
                var disposition = xhr.getResponseHeader("Content-Disposition");
                if (disposition && disposition.indexOf("attachment") !== -1) {
                    var filenameRegex = /filename[^;=\n]*=(([""]).*?\2|[^;\n]*)/;
                    var matches = filenameRegex.exec(disposition);
                    if (matches != null && matches[1]) filename = matches[1].replace(/[""]/g, "");
                }

                var type = xhr.getResponseHeader("Content-Type");
                var blob = new Blob([response], {
                    type: type
                });

                if (typeof window.navigator.msSaveBlob !== "undefined") {
                    // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
                    window.navigator.msSaveBlob(blob, filename);
                } else {
                    var URL = window.URL || window.webkitURL;
                    var downloadUrl = URL.createObjectURL(blob);

                    if (filename) {
                        // use HTML5 a[download] attribute to specify filename
                        var a = document.createElement("a");
                        // safari doesn"t support this yet
                        if (typeof a.download === "undefined") {
                            window.location = downloadUrl;
                        } else {
                            a.href = downloadUrl;
                            a.download = filename;
                            document.body.appendChild(a);
                            a.click();
                        }
                    } else {
                        window.location = downloadUrl;
                    }

                    setTimeout(function () {
                        URL.revokeObjectURL(downloadUrl);
                    }, 100); // cleanup
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                // var errMsg = textStatus.concat(": ", errorThrown, ".");
            }
        });
        return false;
    });
    // Populate modal fields.
    $(".clickable-row").click(function () {
        var requestId = $(this).data("request-id");
        var baseUrl = "/request_info_json/";
        var csrftoken = getCookie("csrftoken");
        var dataDict = {
            "request-id": requestId,
        };
        $.ajax({
            type: "GET",
            url: baseUrl,
            data: dataDict,
            success: function (response) {
                var request = response.request;
                var requestDateTimeMoment = moment(request["date_time"]).format(
                    "MMMM Do YYYY, h:mm:ss a");
                var slotNextDateTimeMoment = moment(request.slot["next_date_time"]).format(
                    "MMMM Do, YYYY");

                if (!jQuery.isEmptyObject(request)) {
                    var request = response.request;
                    $("#requestModalLongTitle").text(request.text);

                    $("#requestInfoListItem0").text("Request ID: " + request.id);
                    $("#requestInfoListItem1").text("Requested on: " +
                        requestDateTimeMoment);
                    if (request.description)
                        $("#requestInfoListItem2").text("Notes: " + request.description);
                    else
                        $("#requestInfoListItem2").text("Notes: None");

                    // Setting up the dismiss/ relodge stuff.
                    $("#requestInfoListItem3").removeClass(
                        "list-group-item-success list-group-item-danger");
                    if (request.dismissed) {
                        $("#requestInfoListItem3").addClass("list-group-item-success");
                        $("#requestInfoListItem3").text("Request status: Dismissed");
                        $("#requestModalDismissButton").text("Relodge");
                    } else {
                        $("#requestInfoListItem3").addClass("list-group-item-danger");
                        $("#requestInfoListItem3").text("Request status: Waiting");
                        $("#requestModalDismissButton").text("Dismiss");
                    }

                    // Setting up the archive/ unarchive stuff.
                    if (request.archived) {
                        $("#requestModalArchiveButton").text("Unarchive");
                    } else {
                        $("#requestModalArchiveButton").text("Archive");
                    }

                    $("#feedbackInfoListItem0").text("Reference code: " + request.feedback_ref_code);
                    if (!jQuery.isEmptyObject(request.feedback)) {
                        $("#feedbackInfoListItem2").removeClass("hidden");
                        $("#feedbackInfoListItem3").removeClass("hidden");
                        $("#feedbackInfoListItem1").text("Satisfaction level: " + request.feedback.satisfaction_val);
                        if (request.feedback.description)
                            $("#feedbackInfoListItem2").text("Comment: " + request.feedback.description);
                        else
                            $("#feedbackInfoListItem2").text("Comment: None");
                        $("#feedbackInfoListItem3").text("Made on: " + moment(request.feedback.date_time).format(
                            "MMMM Do YYYY, h:mm:ss a"));
                    } else {
                        $("#feedbackInfoListItem1").text("No feedback");
                        $("#feedbackInfoListItem2").addClass("hidden");
                        $("#feedbackInfoListItem3").addClass("hidden");
                    }

                    $("#studentInfoListItem0").text("Student ID: " + request.student.id);
                    $("#studentInfoListItem1").text("Name: " + request.student.name);
                    $("#studentInfoListItem2").text("Contact number: " + request.student
                        .phone);

                    $("#slotInfoListItem0").text("Day: " + request.slot.day + " (Next available: " +
                        slotNextDateTimeMoment + ")");
                    $("#slotInfoListItem1").text("Time slot: " + request.slot.time);
                    if (request.slot.disabled) {
                        $("#slotInfoListItem2").addClass("list-group-item-danger");
                        $("#slotInfoListItem2").text("Slot status: Unavailable");
                    } else {
                        $("#slotInfoListItem2").removeClass("list-group-item-danger");
                        $("#slotInfoListItem2").text("Slot status: Available");
                    }

                    $("#unitInfoListItem0").text("Unit: " + request.unit.text);
                    $("#unitInfoListItem1").text("Course: " + request.unit.course);
                    $("#unitInfoListItem2").text("Program: " + request.unit.program);

                    // Setting data values for buttons.
                    $("#requestModalDismissButton").data({
                        "request-id": requestId
                    });
                    $("#requestModalPDFButton").data({
                        "request-id": requestId
                    });
                    $("#requestModalArchiveButton").data({
                        "request-id": requestId
                    });

                    $("#requestModal").modal("toggle");
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                var errMsg = textStatus.concat(": ", errorThrown, ".");
            }
        });
    });
});
"use strict";


function setLiveCountElement(count) {
    var liveRequestCountElement = $("#liveRequestCount");

    $(liveRequestCountElement).text(count);
}

function setLiveCount() {
    var baseUrl = '/request_count_json/';
    var count = 0;

    $.ajax({
        type: 'GET',
        url: baseUrl,
        success: function (response) {
            if (!jQuery.isEmptyObject(response)) {
                count = response["request_count"];
            }
            setLiveCountElement(count);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            setLiveCountElement(count);
        }
    });
}

jQuery(document).ready(function ($) {
    setLiveCount();

    setInterval(function () {
        setLiveCount();
    }, 30000);
});
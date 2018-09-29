"use strict";

jQuery(document).ready(function ($) {
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
                if (!$.isEmptyObject(response)) {
                    count = response["request_count"];
                }
                setLiveCountElement(count);
            },
            error: function () {
                setLiveCountElement(count);
            }
        });
    }

    setLiveCount();

    setInterval(function () {
        setLiveCount();
    }, 30000);
});
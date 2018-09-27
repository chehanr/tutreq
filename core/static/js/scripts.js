"use strict";

jQuery(document).ready(function ($) {
    function handleSelectSlot(response) {
        var slots = response.slots;
        var selectSlot = $("#selectSlot");

        // Hide the slot detail list. 
        $("#slotDetailList").addClass("collapse");

        selectSlot.empty();
        document.getElementById("id_slot").value = null;

        // Create the options list.
        $.each(slots, function (index, value) {
            selectSlot.append("<option value=\"" + index + "\" data-subtext=\"\">" + value.day + " (" + value.time + ") </option>");
        });

        selectSlot.selectpicker("refresh");

        selectSlot.on("changed.bs.select", function (e) {
            var val = $(this).val();
            var slot = slots[val];

            if (slot) {
                document.getElementById("id_slot").value = slot.id;
                populateSlotDetailList(slot);
            }
        });
    }

    function populateSlotDetailList(slot) {
        if (!jQuery.isEmptyObject(slot)) {
            var nextDateTimeMoment = moment(slot["next_date_time"]).format("MMMM Do, YYYY");

            // Unhide the slot detail list. 
            $("#slotDetailList").removeClass("d-none");

            $("#listItem0").text("Unit: " + slot.unit.code + " (" + slot.unit.title + ")");
            $("#listItem1").text("Course: " + slot.unit.course);
            $("#listItem2").text("Day: " + slot.day + " (" + nextDateTimeMoment + ")");
            $("#listItem3").text("Time: " + slot.time);
        }
    }
    // TODO set bs select on window change.
    document.getElementById('id_slot').value = null; // Temp.
    jQuery(document).ready(function ($) {
        $('#selectUnit').on('changed.bs.select', function (e) {
            var unitId = $(this).val();
            var baseUrl = '/slots_info_json/';
            var dataDict = {
                'unit-id': unitId,
            };
            $.ajax({
                type: 'GET',
                url: baseUrl,
                data: dataDict,
                success: function (response) {
                    if (!jQuery.isEmptyObject(response))
                        handleSelectSlot(response);
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    // var errMsg = textStatus.concat(': ', errorThrown, '.');
                }
            });
            return false;
        });
    });
});
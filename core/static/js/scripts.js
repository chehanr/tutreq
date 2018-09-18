"use strict";

// TODO set bs select on window change.

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
        $("#slotDetailList").removeClass("collapse");

        $("#listItem0").text("Unit: " + slot.unit.code + " (" + slot.unit.title + ")");
        $("#listItem1").text("Course: " + slot.unit.course);
        $("#listItem2").text("Day: " + slot.day + " (" + nextDateTimeMoment + ")");
        $("#listItem3").text("Time: " + slot.time);
    }
}
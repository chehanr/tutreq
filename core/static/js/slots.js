"use strict";

jQuery(document).ready(function ($) {
    var slotIdInput = $("#id_slot");
    var selectUnitElement = $("#selectUnit");
    var selectSlotElement = $("#selectSlot");
    var slotDetailList = $("#slotDetailList");

    // Clear value.
    slotIdInput.val(null);

    function populateSlotDetailList(slot) {
        if (!$.isEmptyObject(slot)) {
            var nextDateTimeMoment = moment(slot.next_date_time).format("MMMM Do, YYYY");
            var slotDetailData = {
                unitCodeTitle: "Unit: " + slot.unit.code + " (" + slot.unit.title + ")",
                unitCourse: "Course: " + slot.unit.course,
                slotDay: "Day: " + slot.day + " (" + nextDateTimeMoment + ")",
                slotTime: "Time: " + slot.time
            };

            slotDetailList.removeClass("d-none");
            slotDetailList.empty();

            $.each(slotDetailData, function (key, value) {
                $("<li />", {
                    class: "list-group-item",
                    text: value
                }).appendTo(slotDetailList);
            });
        }
    }

    function handleSelectSlot(response) {
        var slotsItems = response.slots;

        slotDetailList.addClass("d-none");
        selectSlotElement.empty();

        slotIdInput.val(null);

        $.each(slotsItems, function (index, value) {
            var slotText = value.day + " (" + value.time + ")";

            $("<option />", {
                value: index,
                text: slotText
            }).appendTo(selectSlotElement);
        });

        selectSlotElement.selectpicker("refresh");
        selectSlotElement.on("changed.bs.select", function () {
            var val = $(this).val();
            var slot = slotsItems[val];

            if (slot) {
                slotIdInput.val(slot.id);
                populateSlotDetailList(slot);
            }
        });
    }

    selectUnitElement.on("changed.bs.select", function () {
        var unitId = $(this).val();
        var baseUrl = "/slots_info_json/";
        var dataDict = {
            "unit-id": unitId
        };
        $.ajax({
            type: "GET",
            url: baseUrl,
            data: dataDict,
            success: function (response) {
                if (!$.isEmptyObject(response)) {
                    handleSelectSlot(response);
                }
            }
        });
        return false;
    });
});
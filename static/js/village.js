window.onload = function () {
    if (document.getElementById('Village_Name')) {
        document.getElementById('Village_Name').focus();
    }
};
 
$(document).ready(function () {

    // ✅ RUN ONLY IF THIS PAGE HAS FORM/TABLE
    if ($('#addForm').length && $('#addTable').length) {

        // ✅ DEFAULT VIEW → SHOW FORM
        $('#addForm').show();
        $('#addTable').hide();


        // 🔥 BUTTON TOGGLE
        $('#addButton').click(function () {
            $('#addForm').show();
            $('#addTable').hide();
        });

        $('#displayButton').click(function () {
            $('#addForm').hide();
            $('#addTable').show();
        });
    }


    // ===============================
    // STATE → DISTRICT
    // ===============================
    if ($('#state_Id').length) {

        $('#state_Id').change(function () {

            var stateId = $(this).val();

            if (stateId) {

                $.ajax({
                    url: '/get_districts/' + stateId,
                    type: 'GET',

                    success: function (data) {

                        var districtDropdown = $('#district_Id');

                        districtDropdown.empty();
                        districtDropdown.append('<option value="" disabled selected>Select District</option>');

                        data.forEach(function (district) {
                            districtDropdown.append(
                                '<option value="' + district.id + '">' + district.name + '</option>'
                            );
                        });

                        districtDropdown.prop('disabled', false);
                    }
                });
            }
        });
    }


    // ===============================
    // DISTRICT → BLOCK
    // ===============================
    if ($('#district_Id').length) {

        $('#district_Id').change(function () {

            var districtId = $(this).val();

            if (districtId) {

                $.ajax({
                    url: '/get_blocks/' + districtId,
                    type: 'GET',

                    success: function (data) {

                        var blockDropdown = $('#block_Id');

                        blockDropdown.empty();
                        blockDropdown.append('<option value="" disabled selected>Select Block</option>');

                        data.forEach(function (block) {
                            blockDropdown.append(
                                '<option value="' + block.id + '">' + block.name + '</option>'
                            );
                        });

                        blockDropdown.prop('disabled', false);
                    }
                });
            }
        });
    }


    // ===============================
    // VILLAGE NAME VALIDATION
    // ===============================
    if ($('#Village_Name').length) {

        $('#Village_Name').on('input', function () {

            var villageName = $(this).val();
            var validPattern = /^[A-Za-z ]*$/;

            if (!validPattern.test(villageName)) {

                $('#villageMessage')
                    .text('Only letters and spaces are allowed!')
                    .css('color', 'red');

                $('#submitVillage').prop('disabled', true);

            } else {

                $('#villageMessage').text('');
                $('#submitVillage').prop('disabled', false);
            }
        });
    }


    // ===============================
    // CHECK DUPLICATE VILLAGE
    // ===============================
    if ($('#Village_Name').length && $('#block_Id').length) {

        $('#Village_Name, #block_Id').on('change keyup', function () {

            var blockId = $('#block_Id').val();
            var villageName = $('#Village_Name').val().trim();

            if (blockId && villageName) {

                $.ajax({
                    url: '/check_village',
                    type: 'POST',

                    data: {
                        block_Id: blockId,
                        Village_Name: villageName
                    },

                    success: function (response) {

                        if (response.status === 'exists') {

                            $('#villageMessage')
                                .text(response.message)
                                .css('color', 'red');

                            $('#submitVillage').prop('disabled', true);

                        } else {

                            $('#villageMessage')
                                .text(response.message)
                                .css('color', 'green');

                            $('#submitVillage').prop('disabled', false);
                        }
                    },

                    error: function () {

                        $('#villageMessage')
                            .text('Error checking village name')
                            .css('color', 'red');

                        $('#submitVillage').prop('disabled', true);
                    }
                });
            }
        });
    }


    // ===============================
    // ADD VILLAGE (SAFE SCOPE FIX)
    // ===============================
    if ($('#villageForm').length) {

        $('#villageForm').submit(function (event) {

            event.preventDefault();

            $.ajax({
                url: '/add_village',
                type: 'POST',
                data: $(this).serialize(),

                success: function (response) {

                    if (response && response.status === 'success') {

                        alert(response.message || 'Village added successfully!');

                        // ✅ clear form
                        $('#villageForm')[0].reset();

                        // ✅ switch to table
                        $('#addForm').hide();
                        $('#addTable').show();

                        // optional refresh
                        location.reload();

                    } else {
                        alert(response.message || 'Error adding village. Please try again.');
                    }
                },

                error: function () {
                    alert('An error occurred. Please try again.');
                }
            });

        });
    }

});




// ===============================
// DELETE FUNCTION (SAFE)
// ===============================
function deleteVillage(villageId, element) {
    if (!confirm("Are you sure you want to delete this village?")) return;

    $.ajax({
        url: '/delete_village/' + villageId,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            alert(response.message); // ✅ now shows "Village deleted successfully!"
            if (element) $(element).closest("tr").remove();
        },
        error: function () {
            alert("Error deleting village. Please try again.");
        }
    });
}
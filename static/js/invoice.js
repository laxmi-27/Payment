// $(document).ready(function () {
//     // ===============================
//     // FORM / TABLE TOGGLE
//     // ===============================
//     if ($('#addForm').length && $('#addTable').length) {
//         $('#addForm').show();
//         $('#addTable').hide();

//         $('#addButton').click(function () {
//             $('#addForm').show();
//             $('#addTable').hide();
//         });

//         $('#displayButton').click(function () {
//             $('#addForm').hide();
//             $('#addTable').show();
//         });
//     }

//     // ===============================
//     // Subcontractor autocomplete
//     // ===============================
//     $("#subcontractor").keyup(function () {
//         let query = $(this).val();
//         if (query !== "") {
//             $.ajax({
//                 url: "/search_subcontractor",
//                 method: "POST",
//                 data: { query: query },
//                 success: function (data) {
//                     $("#subcontractor_list").fadeIn().html(data);
//                 }
//             });
//         } else {
//             $("#subcontractor_list").fadeOut();
//         }
//     });

//     $(document).on("click", "li", function () {
//         $("#subcontractor").val($(this).text());
//         $("#subcontractor_id").val($(this).attr("data-id"));
//         $("#subcontractor_list").fadeOut();
//     });

//     // Focus
//     if (document.getElementById('subcontractor')) {
//         document.getElementById('subcontractor').focus();
//     }

//     // ===============================
//     // ADD INVOICE
//     // ===============================
//     if ($('#invoiceForm').length && window.location.href.includes('add_invoice')) {
//         $("#invoiceForm").on("submit", function (e) {
//             e.preventDefault();
//             let formData = $(this).serialize();

//             $.ajax({
//                 url: '/add_invoice',
//                 method: 'POST',
//                 data: formData,
//                 dataType: 'json',
//                 success: function (response) {
//                     if (response.status === "success") {
//                         alert(response.message || "Invoice added successfully!");
//                         $('#invoiceForm')[0].reset(); // clear form
//                         $('#addForm').hide();
//                         $('#addTable').show(); // switch to table
//                         location.reload(); // optional refresh
//                     } else {
//                         alert(response.message || "Error adding invoice.");
//                     }
//                 },
//                 error: function (xhr) {
//                     alert(xhr.responseJSON?.message || "Submission failed. Please try again.");
//                 }
//             });
//         });
//     }
// // Example AJAX update function
// function updateInvoice(invoiceId, formElement) {
//     const formData = $(formElement).serialize();

//     $.ajax({
//         url: '/update_invoice/' + invoiceId,
//         method: 'POST',
//         data: formData,
//         dataType: 'json',
//         success: function(response) {
//             if(response.status === "success") {
//                 alert(response.message || "Invoice updated successfully!");
                
//                 // ✅ Hide Add Form, Show Table
//                 $('#addForm').hide();
//                 $('#addTable').show();

//                 // Optional: reload table or refresh page
//                 location.reload();
//             } else {
//                 alert(response.message || "Update failed. Please try again.");
//             }
//         },
//         error: function(xhr) {
//             alert(xhr.responseJSON?.message || "Error updating invoice.");
//         }
//     });
// }

// // ===============================
// // DELETE INVOICE
// // ===============================
// function deleteInvoice(invoiceId, element) {
//     if (!confirm("Are you sure you want to delete this invoice?")) return;

//     $.ajax({
//         url: '/delete_invoice/' + invoiceId,
//         method: 'GET',
//         dataType: 'json',
//         success: function (response) {
//             alert(response.message || "Invoice deleted successfully!");
//             if (element) $(element).closest("tr").remove();
//         },
//         error: function (xhr) {
//             alert(xhr.responseJSON?.message || "Error deleting invoice. Please try again.");
//         }
//     });
// }

$(document).ready(function () {
    // ===============================
    // FORM / TABLE TOGGLE
    // ===============================
    if ($('#addForm').length && $('#addTable').length) {
        // Default: show form, hide table
        $('#addForm').show();
        $('#addTable').hide();

        // ✅ Check URL hash to show table instead
        if (window.location.hash === "#addTable") {
            $('#addForm').hide();
            $('#addTable').show();
        }

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
    // Subcontractor autocomplete
    // ===============================
    $("#subcontractor").keyup(function () {
        let query = $(this).val();
        if (query !== "") {
            $.ajax({
                url: "/search_subcontractor",
                method: "POST",
                data: { query: query },
                success: function (data) {
                    $("#subcontractor_list").fadeIn().html(data);
                }
            });
        } else {
            $("#subcontractor_list").fadeOut();
        }
    });

    $(document).on("click", "li", function () {
        $("#subcontractor").val($(this).text());
        $("#subcontractor_id").val($(this).attr("data-id"));
        $("#subcontractor_list").fadeOut();
    });

    // Focus
    if (document.getElementById('subcontractor')) {
        document.getElementById('subcontractor').focus();
    }

    // ===============================
    // ADD INVOICE
    // ===============================
    if ($('#invoiceForm').length && window.location.href.includes('add_invoice')) {
        $("#invoiceForm").on("submit", function (e) {
            e.preventDefault();
            let formData = $(this).serialize();

            $.ajax({
                url: '/add_invoice',
                method: 'POST',
                data: formData,
                dataType: 'json',
                success: function (response) {
                    if (response.status === "success") {
                        alert(response.message || "Invoice added successfully!");
                        $('#invoiceForm')[0].reset(); // clear form
                        $('#addForm').hide();
                        $('#addTable').show(); // switch to table
                        location.reload(); // optional refresh
                    } else {
                        alert(response.message || "Error adding invoice.");
                    }
                },
                error: function (xhr) {
                    let msg = xhr.responseJSON?.message || "Submission failed. Please try again.";
                    alert(msg);
                }
            });
        });
    }

    // ===============================
    // UPDATE INVOICE
    // ===============================
    function updateInvoice(invoiceId, formElement) {
        const formData = $(formElement).serialize();

        $.ajax({
            url: '/update_invoice/' + invoiceId,
            method: 'POST',
            data: formData,
            dataType: 'json',
            success: function(response) {
                if(response.status === "success") {
                    alert(response.message || "Invoice updated successfully!");

                    // Redirect to Add Invoice page's table part
                    window.location.href = "/add_invoice#addTable";
                } else {
                    alert(response.message || "Update failed. Please try again.");
                }
            },
            error: function(xhr) {
                let msg = xhr.responseJSON?.message || "Error updating invoice.";
                alert(msg);
            }
        });
    }
    window.updateInvoice = updateInvoice; // make globally accessible

    // ===============================
    // DELETE INVOICE
    // ===============================
    function deleteInvoice(invoiceId, element) {
        if (!confirm("Are you sure you want to delete this invoice?")) return;

        $.ajax({
            url: '/delete_invoice/' + invoiceId,
            method: 'GET',
            dataType: 'json',
            success: function (response) {
                if (response.status === "success") {
                    alert(response.message || "Invoice deleted successfully!");
                    if (element) $(element).closest("tr").remove();
                } else {
                    alert(response.message || "Error deleting invoice.");
                }
            },
            error: function (xhr) {
                let msg = xhr.responseJSON?.message || "Error deleting invoice. Please try again.";
                alert(msg);
            }
        });
    }
    window.deleteInvoice = deleteInvoice; // make globally accessible
});
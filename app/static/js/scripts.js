// With invaluable input from Roko Buljian
function imagePreviewer(ev) {
    const EL_input = this;
    const EL_form = EL_input.closest("form");
    const EL_filename = EL_form.querySelector(".form-control-filename");
    const EL_thumbnail = EL_form.querySelector(".form-control-thumbnail");
    const files = ev.target.files;

    if (files && files[0]) {
        const file = files[0];
        EL_filename.textContent = EL_filename.dataset.text;
        const FR = new FileReader();
        FR.addEventListener("load", function (ev) {
            EL_thumbnail.style.backgroundImage = `url("${ev.target.result}")`;
        });
        FR.readAsDataURL(file);
    }
}

const ELS_file = document.querySelectorAll(".form-control-file");
ELS_file.forEach((el) => {
    el.addEventListener("change", imagePreviewer);
});

// ? Fades flash messages after a timeout
$(document).ready(() => {
    setTimeout(function () {
        $("#flash").fadeOut("slow");
    }, 3000);
});


// ? Same as above but sliding up
// $(document).ready(() => {
//     $("#flash").delay(3000).slideUp(1000);
// });

// $(document).ready(function () {
//     $(".delete-review").click(function () {
//         $("#cafeId").val($(this).data("id"));
//         $("#deleteReviewModal").modal("show");
//     });
// });

// $(document).on("click", ".open-AddBookDialog", function () {
//     var myDeleteButtonId = $(this).data("id");
//     $(".modal-footer #review_Id").val(myDeleteButtonId);
// });


// With invaluable input from Roko Buljan
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

// Fades flash messages after a timeout
$(document).ready(() => {
    setTimeout(function () {
        $("#flash").fadeOut("slow");
    }, 3000);
});

// Opens the delete review modal passing data to delete review
$(".delete-review").on("click", (evt) => {
    evt.preventDefault();
    const btnData = $(evt.currentTarget).data();
    const formDeleteReview = $("#form-delete-review");
    formDeleteReview.find('[name="review_id"]').val(btnData.review_id);
    formDeleteReview.find('[name="perfume_id"]').val(btnData.perfume_id);
});

// Opens the edit review modal passing data to edit review
// !
$(".edit-review").on("click", (evt) => {
    evt.preventDefault();
    const btnData = $(evt.currentTarget).data();
    const formEditReview = $("#form-edit-review");
    formEditReview.find('[name="review_id"]').val(btnData.review_id);
    formEditReview.find('[name="perfume_id"]').val(btnData.perfume_id);
});

// Triggers the filter query - Deals with a different route
// for the option outside the loop (create new type)
function checkSelected() {
    if (this.value === "/type/new") return (window.location = this.value);
    if (this.value) this.closest("form").submit();
}
const EL_select = document.querySelector("#filter_query");
if (EL_select) EL_select.addEventListener("change", checkSelected);

// Pre-populates the content of the review to edit it, in the modal.
// Worked out together with the help from a gentleman on this question on SO:
//https://stackoverflow.com/questions/61989485/pre-populate-current-value-of-wtforms-field-in-order-to-edit-it/62013979?noredirect=1#comment109698792_62013979
$(document).on("click", "#editFormButton", function (e) {
    const reviewText = $(this)
        .parents("div")
        .siblings("div.review-content")
        .children(".content-review")
        .text();
    CKEDITOR.instances.edit_review.setData(reviewText);
});

// Shows modal with validation error in the event of submitting form in the modal
// with no data on a DataRequired field.
$(".is-invalid").closest(".modal").modal("show");
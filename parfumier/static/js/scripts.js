/**
 * Prieviews avatar and perfume image before upload
 * With invaluable input from Roko Buljan
 * @param {HTMLElement} ev
 */
const imagePreviewer = function (ev) {
    const inputElement = this;
    const formElement = inputElement.closest("form");
    const filenameElement = formElement.querySelector(".form-control-filename");
    const thumbnailElement = formElement.querySelector(".form-control-thumbnail");
    const files = ev.target.files;

    if (files && files[0]) {
        const file = files[0];
        filenameElement.textContent = filenameElement.dataset.text;
        const FR = new FileReader();
        FR.addEventListener("load", function (ev) {
            thumbnailElement.style.backgroundImage = `url("${ev.target.result}")`;
        });
        FR.readAsDataURL(file);
    }
};

const formControlFileRef = document.querySelectorAll(".form-control-file");
formControlFileRef.forEach((el) => {
    el.addEventListener("change", imagePreviewer);
});

/**
 * Fades flash messages after a set timeout
 */
$(document).ready(() => {
    setTimeout(function () {
        $("#flash").fadeOut("slow");
    }, 3000);
});

/**
 * Opens the delete review modal passing data to delete review
 */
$(".delete-review").on("click", (evt) => {
    evt.preventDefault();
    const btnData = $(evt.currentTarget).data();
    const formDeleteReview = $("#form-delete-review");
    formDeleteReview.find('[name="review_id"]').val(btnData.review_id);
    formDeleteReview.find('[name="perfume_id"]').val(btnData.perfume_id);
});

/**
 * Opens the edit review modal passing data to edit review
 */
$(".edit-review").on("click", (evt) => {
    evt.preventDefault();
    const btnData = $(evt.currentTarget).data();
    const formEditReview = $("#form-edit-review");
    formEditReview.find('[name="review_id"]').val(btnData.review_id);
    formEditReview.find('[name="perfume_id"]').val(btnData.perfume_id);
});

/**
 * Triggers the filter query - Deals with a different route
 * for the option outside the loop (create new type)
 */
const checkSelected = function () {
    if (this.value === "/type/new") return (window.location = this.value);
    if (this.value) this.closest("form").submit();
};
const selectElement = document.querySelector("#filter_query");
if (selectElement) selectElement.addEventListener("change", checkSelected);

/**
 * Pre-populates the content of the review to edit it, in the modal.
 * Worked out together with the help from a gentleman on this question on SO:
 * https://www.shorturl.at/ahRX3
 */
$(document).on("click", "#editFormButton", function () {
    const reviewText = $(this)
        .parents("div")
        .siblings("div.review-content")
        .children("div")
        .children("div.content-review")
        .html();
    CKEDITOR.instances.edit_review.setData(reviewText);
});

/**
 * Shows modal with validation error in the event of submitting form in the modal
 * with no data on a DataRequired field.
 * This hack is a temporary workaround. Future version should have
 * JS dealing with forms on the frontend.
 */
$(".is-invalid").closest(".modal").modal("show");

/**
 * This loops through my img elements and on error replaces the
 * eventually missing or broken src attribute, making sure an image
 * is displayed in case the one on cloudinary is not found for some reason.
 * It will still throw a console error if that happens, but the user
 * will at least see a fallback image instead of a broken image icon.
 * This made possible to get rid of my inline 'onerror' JS in the templates
 * My question on SO: shorturl.at/bmJS4
 */
$(document).ready(() => {
    $("img").each(function () {
        this.onerror = () => {
            if ($(this).hasClass("user-picture")) {
                $(this).attr("src", "../static/images/default.png");
            } else if ($(this).hasClass("perfume-picture")) {
                $(this).attr("src", "../static/images/generic.jpg");
            }
        };
    });
});

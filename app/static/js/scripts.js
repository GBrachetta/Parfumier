// // With invaluable input from Roko Buljian
// const EL_avatar = document.querySelector("#avatar");
// const EL_fileName = document.querySelector("#fileName");
// const EL_previewAvatar = document.querySelector("#thumb-avatar");
// const EL_picture = document.querySelector("#picture");
// const EL_pictureFileName = document.querySelector("#pictureFileName");
// const EL_previewPicture = document.querySelector("#thumb-picture");

// if (EL_avatar) {
//     EL_avatar.addEventListener("change", function (ev) {
//         const files = ev.target.files;

//         if (files && files[0]) {
//             const file = files[0];
//             // EL_fileName.textContent = `File ${file.name} loaded, please click Update`;
//             EL_fileName.textContent = `New avatar selected, please click Update`;
//             const FR = new FileReader();
//             FR.addEventListener("load", function (ev) {
//                 EL_previewAvatar.style.backgroundImage = `url("${ev.target.result}")`;
//             });
//             FR.readAsDataURL(file);
//         }
//     });
// }

// if (EL_picture) {
//     EL_picture.addEventListener("change", function (ev) {
//         const files = ev.target.files;

//         if (files && files[0]) {
//             const file = files[0];
//             EL_pictureFileName.textContent = `Picture selected`;
//             const FR = new FileReader();
//             FR.addEventListener("load", function (ev) {
//                 EL_previewPicture.style.backgroundImage = `url("${ev.target.result}")`;
//             });
//             FR.readAsDataURL(file);
//         }
//     });
// }

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

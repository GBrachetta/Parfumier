// With invaluable input from Roko Buljian
const EL_avatar = document.querySelector("#avatar");
const EL_fileName = document.querySelector("#fileName");
const EL_previewAvatar = document.querySelector("#thumb-avatar");

EL_avatar.addEventListener("change", function (ev) {
    const files = ev.target.files;

    if (files && files[0]) {
        const file = files[0];
        // EL_fileName.textContent = `File ${file.name} loaded, please click Update`;
        EL_fileName.textContent = `New avatar selected, please click Update`;
        const FR = new FileReader();
        FR.addEventListener("load", function (ev) {
            EL_previewAvatar.style.backgroundImage = `url("${ev.target.result}")`;
        });
        FR.readAsDataURL(file);
    }
});

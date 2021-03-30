Dropzone.autoDiscover = false;

var imgDz;

function initDz() {
    if (document.getElementById('image-dz')) {
        imgDz = new Dropzone("#image-dz",
            {
                url: "/upload-local-image",
                maxFiles: 4,
                maxFilesize: 5,
                acceptedFiles: '.png, .jpg, .gif, .svg, .webp',
                dictDefaultMessage: "Drop images here to upload"
                // addRemoveLinks: true
            });
    }
}

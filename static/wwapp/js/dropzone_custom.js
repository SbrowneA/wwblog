Dropzone.autoDiscover = false;

var imgDz;

function initDz() {
    if (document.getElementById('image-dz')) {
        imgDz = new Dropzone("#image-dz",
            {
                url: "/upload-to-imgur",
                maxFiles: 4,
                maxFilesize: 20,
                // acceptedFiles: '.png, .jpg, .gif, .svg, .webp',
                acceptedFiles: '.png, .jpg, .jpeg, .gif, .svg, .webp, .apng, .TIFF, .MP4, .MPEG, .AVI, .WEBM, .quicktime, .x-matroska, .x-flv, .x-msvideo, .x-ms-wm',
                dictDefaultMessage: "Drop images or click here to upload",
                // addRemoveLinks: true
                timeout: 50000,
            });
    }
}

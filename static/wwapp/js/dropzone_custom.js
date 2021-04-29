Dropzone.autoDiscover = false;

let imgDz;

function initDz() {
    if (document.getElementById('image-dz')) {
        imgDz = new Dropzone("#image-dz",
            {
                url: "/upload-to-imgur",
                timeout: 50000,
                maxFiles: 4,
                maxFilesize: 20,
                // acceptedFiles: '.png, .jpg, .gif, .svg, .webp',
                acceptedFiles: '.png, .jpg, .jpeg, .gif, .svg, .webp, .apng, .TIFF, .MP4, .MPEG, .AVI, .WEBM, .quicktime, .x-matroska, .x-flv, .x-msvideo, .x-ms-wm',
                dictDefaultMessage: "Drop images or click here to upload<br/><span>Images are automatically be added to your images and embedded in this post</span>",
                // addRemoveLinks: true,
                // dictRemoveFile: "Delete",
                // dictRemoveFileConfirmation: "Are you sure you want to delete this image?",
            });

        imgDz.on("success", function (file, response) {
            response = JSON.parse(response)
            let ratio = response['height'] / response['width'];
            let newWidth = 400;
            let newHeight = Math.floor(newWidth * ratio);
            console.log(`response: ${response} \n new dimensions:${newWidth} x ${newHeight}`);
            tinyMCE.activeEditor.setContent(`${tinyMCE.activeEditor.getContent()}<p><img src="${response['url']}" alt="image upload ${file.name}" width="${newWidth}" height="${newHeight}" /></p>`);
            // let editor = document.getElementById('tiny-mce');
            // editor.innerHTML = editor.innerHTML + `<p><img src="${response['url']}" alt="image upload ${file.name}" width="${newWidth}" height="${newHeight}" /></p>`
            // TODO
            //  add delete link (with hash) to last link of class dz-remove
        });
        /*imgDz.on("removedfile", function (file,) {
            alert("removed file");
            console.log(file.name);
            // console.log("new image url: "+ response)
            // TODO
            //  POST to delete url in the remove link
            //  remove link from tiny editor
        });*/
    }
}


async function openDzPopup() {
    toggleDzPopup();
    initDz();
}

function closeDzPopup() {
    toggleDzPopup();
}

function toggleDzPopup() {
    // let popupSection = document.getElementById("dzPopup");
    let popupSection = document.getElementById("popupContainer");
    popupSection.classList.toggle("hide-popup");
}

Dropzone.autoDiscover = false;

let imgDz;

function initImageDz() {
    // create and append elements to popupContainer programmatically
    //parent div
    // let popup = document.createElement("div" );
    let popup = document.getElementById('genericPopup');
    popup.id = 'imageDzPopup';

    // dz form within parent div
    // let form = document.createElement("form");
    let form = document.getElementById("genericPopupForm");
    form.id = 'image-dz';
    form.method = 'POST';
    // form.action = '';
    form.classList.add('dropzone');
    form.classList.add('dz-custom');
    //fallback div within form
    // let fallback = document.createElement("div");
    // input within fallback

    //close button within parent div
    let closeBtn = document.createElement("button");
    closeBtn.id = 'dzCloseBtn';
    closeBtn.innerHTML = 'close';
    popup.appendChild(closeBtn)

    // initialise dropzone form
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

        imgDz.on("success", (file, response) => {
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
    if (imgDz === undefined) {
        initImageDz();
        console.log("initDz() called");
        let popupContainer = document.getElementById("popupContainer");
        popupContainer.addEventListener("click", (e) => {
            console.log("e: " + e.target.id);
            if ('popupContainer' === e.target.id) {
                closeDzPopup();
            }
        });
        let closeBtn = document.getElementById('dzCloseBtn');
        closeBtn.addEventListener("click", closeDzPopup);
    }
}

function closeDzPopup() {
    toggleDzPopup();
}

function toggleDzPopup() {
    let popupContainer = document.getElementById("popupContainer");
    popupContainer.classList.toggle("hide-popup");
}

Dropzone.autoDiscover = false;

let imgDz;

const imageDZPopupContainerId = "imageDZPopupContainer"

/**
 * creates a hidden input field with the csrf token for forms
 * @returns {HTMLInputElement}
 */
function getCSRFToken() {
    let token = document.createElement("input");
    token.type = 'hidden'
    token.name = 'csrfmiddlewaretoken'
    token.value = getCookie('csrftoken');
    return token;
}

function initImageDz() {
    // create and append elements to popupContainer programmatically
    //container div
    let container = document.createElement("div");
    container.id = imageDZPopupContainerId;
    container.classList.add("popup-container", "hide-popup");

    //parent div
    let popup = document.createElement("div");
    // let popup = document.getElementById('genericPopup');
    popup.id = 'imageDzPopup';
    popup.classList.add('popup');
    // dz form within parent div
    let form = document.createElement("form");
    // let form = document.getElementById("genericPopupForm");
    form.id = 'image-dz';
    form.method = 'POST';
    // form.action = '';
    form.classList.add('dz-custom', 'dropzone');
    form.appendChild(getCSRFToken());
    //fallback div within form
    // let fallback = document.createElement("div");
    // input within fallback

    //close button within parent div
    let closeBtn = document.createElement("button");
    closeBtn.id = 'dzCloseBtn';
    closeBtn.innerText = 'close';
    popup.appendChild(form)
    popup.appendChild(closeBtn)
    container.appendChild(popup);
    document.body.appendChild(container);

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
            tinyMCE.activeEditor.setContent(`${tinyMCE.activeEditor.getContent()}<p><img src="${response['url']}" alt="image upload ${file.name}" width="${newWidth}" height="${newHeight}" /></p>`);
        });
    }
}

/**
 * Keeps track of the container elements that have had an onclick set via the togglePopupContainer() function
 * @type {{}}
 */
let containerOnClickSet = {};

/**
 * Toggles the popup container that masks the whole screen to be hidden or show with the .hide-popup class
 * @param elementID the id of the container to be toggled
 * @param closeFunc the function that should be called when the container is clicked to hide the popup again
 */
function togglePopupContainer(elementID, closeFunc) {
    let popupContainer = document.getElementById(elementID);
    popupContainer.classList.toggle("hide-popup");
    if (!containerOnClickSet[elementID]) {
        popupContainer.addEventListener("click", (e) => {
            if (elementID === e.target.id) {
                closeFunc();
            }
        });
        containerOnClickSet[elementID] = true;
    }
}

// upload image DZ functions
/**
 * Toggles the imageDzPopup and the popupContainer
 */
function toggleImageDzPopup() {
    togglePopupContainer(imageDZPopupContainerId, closeDzPopup);
}

/**
 * called to by the uploadImageBtn in the edit article page
 * @returns {Promise<void>}
 */
async function openImageDzPopup() {
    if (imgDz === undefined) {
        initImageDz();
        let closeBtn = document.getElementById('dzCloseBtn');
        closeBtn.addEventListener("click", closeDzPopup);
    }
    toggleImageDzPopup();
}

function closeDzPopup() {
    toggleImageDzPopup();
}

let uploadImageBtn = document.getElementById('uploadImageBtn');
uploadImageBtn.addEventListener("click", () => {
    openImageDzPopup();
});


//Publish popup code
const publishPopupContainerId = "publishPopupContainer";
const closePublishBtnId = "closePublishBtn";
let publishPopup = undefined;

async function initPublishPopup() {
    //add container
    let container = document.createElement("div");
    container.id = publishPopupContainerId;
    container.classList.add("popup-container");
    container.classList.add("hide-popup");

    //add popup
    let popup = document.createElement("div");
    popup.classList.add("popup");
    let closeBtn = document.createElement("button");
    closeBtn.innerText = "close";
    closeBtn.id = closePublishBtnId;
    closeBtn.addEventListener("click", closePublishPopup);
    let publishBtn = document.createElement("button");
    publishBtn.innerText = "publish";
    publishBtn.disabled = true;
    publishBtn.id = closePublishBtnId;
    publishBtn.addEventListener("click", publishArticle);
    publishPopup = popup;
    //TODO add create buttons
    // ajax to load options getPublishOptions().then()
    // add creatButton for each project loaded
        // set id value of create btn to id of category
        // e.g. id:"btn-create-{id}" value:{id}
        // onclick (e) => create child cat with e.value

    //add form
    let form = document.createElement("form");

    //add csrf token
    getCSRFToken();

    //append elements
    document.body.appendChild(container);
    container.appendChild(popup);
    popup.appendChild(form);
    popup.appendChild(closeBtn);
    popup.appendChild(publishBtn);

}

async function openPublishPopup() {
    if (publishPopup === undefined) {
        initPublishPopup();
    }
    togglePublishPopup();
}

function closePublishPopup() {
    togglePublishPopup();
}

function togglePublishPopup() {
    // let pubPopup = document.getElementById(publishPopupContainerId);
    // pubPopup.classList.toggle("hide-popup");
    togglePopupContainer(publishPopupContainerId, closePublishPopup);
}

let publishBtn = document.getElementById("publishPopupBtn");
publishBtn.addEventListener("click", () => {
    openPublishPopup();
});


// ajax methods
async function publishArticle(articleId){}
async function createCategory(categoryName){}
async function getPublishOptions(){}



//NAVIGATION BUTTONS
function viewArticle(url) {
    console.log(url);
    if (confirm("All unsaved changes will be lost.\nwould yo like to continue?")) {
        window.location.replace(url);
    } else {
        return false;
    }
}

function deleteArticle(url) {
    if (confirm("Are you sure you want to delete this post (" + '{{ article.article_title }}'
        + ")?\nLinked posts will not be deleted, only unliked")) {
        window.location.replace(url);
    } else {
        return false;
    }
}

function setupButtons() {
    /**
     * gets the url from the value of the click event (i.e. the button.value) and forwards it to {@link viewArticle()}
     */
    let viewArticleBtn = document.getElementById("viewArticleBtn");
    if (viewArticleBtn) {
        viewArticleBtn.addEventListener("click", (e) => {
            viewArticle(e.target.value);
        });
    }

    /**
     * gets the url from the value of the click event (i.e. the button.value) and forwards it to {@link deleteArticle()}
     */
    let deleteArticleBtn = document.getElementById("deleteArticleBtn");
    if (deleteArticleBtn) {
        deleteArticleBtn.addEventListener("click", (e) => {
            deleteArticle(e.target.value);
        });
    }
}

setupButtons();
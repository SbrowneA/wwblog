// page hydration
let article = undefined;

updateArticleDetails();

async function updateArticleDetails() {
    console.log("updating article ");
    await getArticleDetailsPromise().then((data) => {
        article = data
        // console.log("updateArticleDetails  ->");
        // console.log(data);
    }).catch((err) => {
            console.error(`Error: ${err.error}`);
        }
    );
    console.log("updated");
}

// hydrateEditor();
// document.getElementById("testBtn").addEventListener("click", publishArticlePromise);
// let testBtn = document.getElementById("testBtn");
// testBtn.addEventListener("click", hydrateEditor);
/*let theEditor;
async function hydrateEditor() {
    console.log(theEditor);
    // await new Promise(resolve => {
    //     setTimeout(() => {
    //         console.log("Timeout -> editor:");
    //         resolve();
    //     }, 500)
    // })

    getArticlePromise().then((data) => {
        article = data;
        console.log("article.content");
        console.log(article.content);
        console.log("tinyMCE.activeEditor");
        console.log(tinyMCE.activeEditor);
        tinyMCE.activeEditor.setContent(article.content);
    }).catch((err) => {
            console.error(`Error: ${err.error}`);
        }
    );
}
tinyMCE.on('addeditor', (e) => {
    theEditor = e.editor;
    hydrateEditor();
});*/

/*function hydrateEditor() {
    getArticlePromise().then(async (data) => {
        article = data;
        //try to update editor content
        // for (let i = 0; i <= 5; i++) {
        // console.log(i)
        // check the editor exists
        console.log("article.content");
        console.log(article.content);
        if (tinyMCE.activeEditor) {
            tinyMCE.activeEditor.setContent(article.content);
            // break;
        } else {
            // timeout if still undefined before trying again
            await new Promise(resolve => {
                setTimeout(() => {
                    console.log("Timeout -> editor:");
                    console.log(tinyMCE.activeEditor);
                    resolve();
                }, 1000)
            })
        }
        // }
    }).catch((err) => {
            console.error(`Error: ${err.error}`);
        }
    );
}*/


/*    function (event) {
    console.log("addeditor event:")
    // console.log(event);
    // console.log("editor:");
    // console.log(event.editor);
    // console.log("editor id");
    // console.log(event.editor.id);
    // event.editor.setContent("SADASDASDASDS");
    console.log(tinyMCE.activeEditor.editor);


    // tinyMCE.activeEditor.setContent(`${article.content}`);


    // setTimeout(() => {
    //     hydrateEditor();
    // }, )
    console.log(tinyMCE.activeEditor.getContent());
    console.log("addEditor Event");
    // var editor = event.editor;
    // var $textarea = $('#' + editor.id);
    // console.log($textarea.val());
}, true);*/

/**
 * gets the article details without the content of the post
 * @returns {Promise<unknown>}
 */
function getArticleDetailsPromise() {
    let fetchUrl = document.getElementById("ajax_get_article_details_url").value;
    return new Promise((resolve, reject) => {
        fetch(fetchUrl)
            .then(response => {
                // console.log("\ngetArticlePromise ->");
                // console.log(response);
                if (response.status === 200) {
                    resolve(response.json());
                } else reject(response);
            });
    });
}

/**
 * gets the article details as well as the content of the post
 * @returns {Promise<unknown>}
 */
function getArticleContentPromise() {
    let fetchUrl = document.getElementById("ajax_get_article_content_url").value;
    return new Promise((resolve, reject) => {
        fetch(fetchUrl)
            .then(response => {
                // console.log("\ngetArticlePromise ->");
                // console.log(response);
                if (response.status === 200) {
                    resolve(response.json());
                } else reject(response);
            });
    });
}


// image DZ code
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


let pubStatusLbl = document.getElementById("txtPublishStatus");
let editControls = document.getElementById("editControlsContainer");
// Publish popup code
const publishPopupContainerId = "publishPopupContainer";
const closePublishBtnId = "closePublishBtn";
let publishPopup = undefined;
let publishBtn;
let selectedCategoryLbl;
let selectedCategory;
let optionsRow;
let categoryOptions = [];
// id naming pattern used for elements ("idPre-" + modelIdValue)
const categoryGroupIdPre = "categoryGroup-";
const categoryGroupBodyIdPre = "categoryGroupBody-";
const createCategoryGroupIdPre = "createCategoryGroup-";
const createCategoryTxtIdPre = "createCategoryTxt-";
const createCategoryBtnPre = "submitCategoryBtn-";
const categoryNameBtnIdPre = "categoryName-";

function initPublishPopupLayout() {
    //add container
    let container = document.createElement("div");
    container.id = publishPopupContainerId;
    container.classList.add("popup-container", "hide-popup");
    //add popup
    let popup = document.createElement("div");
    popup.classList.add("popup", "publish-popup");

    //TOP Heading row
    let headingRow = document.createElement("div");
    headingRow.classList.add("heading-row");
    let headingTxt = document.createElement("h3");
    headingTxt.innerText = "Publish";
    headingRow.append(headingTxt)
    //MIDDLE Options row
    optionsRow = document.createElement("div");
    optionsRow.id = "optionsRow";
    optionsRow.classList.add("options-row", "loading");

    let loadingContainer = document.createElement("div");
    loadingContainer.classList.add("loading-projects-container");
    let loadingText = document.createElement("div");
    loadingText.innerText = "Loading..";
    let loadingAnim = document.createElement("div");
    loadingAnim.classList.add("loading-line");
    loadingContainer.append(loadingText, loadingAnim);
    optionsRow.append(loadingContainer)
    //BOTTOM Button row
    let buttonsRow = document.createElement("div");
    buttonsRow.classList.add("button-row");
    let selectedCatSpan = document.createElement("span");
    selectedCatSpan.id = "selectedCategoryNameTxt";
    selectedCatSpan.innerText = "Selected:";

    let closeBtn = document.createElement("button");
    closeBtn.innerText = "close";
    closeBtn.id = closePublishBtnId;
    closeBtn.addEventListener("click", closePublishPopup);
    publishBtn = document.createElement("button");
    publishBtn.innerText = "publish";
    publishBtn.disabled = true;
    publishBtn.id = "publishBtn";
    publishBtn.addEventListener("click", publishArticle);
    // publishBtn.addEventListener("click", publishArticle);
    buttonsRow.append(selectedCatSpan, publishBtn, closeBtn);

    popup.append(headingRow, optionsRow, buttonsRow);

    //append elements
    document.body.appendChild(container);
    container.appendChild(popup);

    selectedCategoryLbl = document.getElementById("selectedCategoryNameTxt");

    publishPopup = popup;
    // return promise for .then() callback to be called
    return new Promise(resolve => {
        resolve(1)
    });
}

async function initPublishOptions() {
    //load the options from the server
    await getPublishOptionsPromise().then((options) => {
        categoryOptions = options;
        for (let i = 0; i < categoryOptions.length; i++) {
            initOptionElement(categoryOptions[i], null);
        }
        // console.log("initPublishOptions -> options:");
        // console.log(options);
    }).finally(() => {
        // stop loading animation
        // toggleOffElementClass(optionsRow, "loading");
        optionsRow.classList.remove("loading")
        let btns = document.querySelectorAll(`.category-name`);
    })
}


/**
 * Initialises the publish popup when it gets opened in the following order:
 * 1. generate the layout of the popup
 * 2. load the available options from the server
 * 3. generate the html for the options and append them to the popup in the DOM
 * 4. turn off loading animation
 * @return {Promise<void>}
 */
async function initPublishPopup() {
    await initPublishPopupLayout();
    await initPublishOptions();
    if (article === undefined) {
        await updateArticleDetails();
    }
    // if the article is published, the category name button is clicked to be selected in the UI
    if (article.published) {
        let btnId = categoryNameBtnIdPre + article.parent_category.category_id;
        let btn = document.querySelector(`#${btnId}`);
        btn.click();
    }
}

async function openPublishPopup() {
    if (publishPopup === undefined) {
        //initialise all the html elements and data
        await initPublishPopup();
    }
    //make the popup visible
    togglePublishPopup();
}

function closePublishPopup() {
    togglePublishPopup();
}

function togglePublishPopup() {
    togglePopupContainer(publishPopupContainerId, closePublishPopup);
}


let openPublishPopupBtn = document.getElementById("openPublishPopupBtn");
openPublishPopupBtn.addEventListener("click", () => {
    openPublishPopup();
});


// initialisation functions
/**
 * Creates HTML category group element based on the parameters passed
 * @param catId - id of category being created
 * @param catName - name of category being created
 * @param type - category type to be crated, can be PROJECT, TOPIC or SUBTOPIC
 * @return {HTMLDivElement} - Element that contains all the components to select it and create sub-categories
 */
function createCategoryGroupHTMLElement(catId, catName, type) {
    let group = document.createElement("div");
    let tempClsList;
    tempClsList = (type === "PROJECT") ? ["project-group", "category-group"] : ["category-group"];
    group.classList.add(...tempClsList);
    group.id = `categoryGroup-${catId}`;
    // > header
    let catHeader = document.createElement("div");
    tempClsList = (type === "PROJECT") ? ["project-group__header", "category-group__header"] : ["category-group__header"];
    catHeader.classList.add(...tempClsList);
    // > header > drop down arrow
    if (type !== "SUBTOPIC") {
        let arrowBtn = document.createElement("button");
        arrowBtn.classList.add("expand-arrow-btn");
        let arrow = document.createElement("i");
        arrow.classList.add("arrow");
        arrowBtn.value = catId;
        arrowBtn.appendChild(arrow);
        arrowBtn.addEventListener("click", (e) => {
            document.getElementById(categoryGroupIdPre + arrowBtn.value).classList.toggle("expand");
        });
        catHeader.append(arrowBtn);
    }
    // > header > category name title button
    let titleBtn = document.createElement("button");
    titleBtn.innerText = catName;
    titleBtn.id = categoryNameBtnIdPre + catId;
    titleBtn.value = catId;
    titleBtn.classList.add((type === "PROJECT") ? "project-name" : "category-name");
    if (!(type === "PROJECT")) {
        // add onclick
        titleBtn.addEventListener("click", (e) => {
            toggleSelectCategory(e.target);
            //remove focus once buttons is clicked
            titleBtn.blur();
        });
    }
    catHeader.append(titleBtn);
    // > body
    let catBody = document.createElement("div");
    catBody.id = categoryGroupBodyIdPre + catId;
    catBody.classList.add("category-group__body");
    // > body > create-category-group
    let createCatGroup = document.createElement("div");
    createCatGroup.id = `createCategoryGroup-${catId}`;
    createCatGroup.classList.add("create-category-group");

    if (type !== "SUBTOPIC") {
        // > body > create-category-group > create-category-input-group
        let createCatInputGroup = document.createElement("div");
        createCatInputGroup.classList.add("create-category-input-group");
        let txt = document.createElement("input");
        txt.id = createCategoryTxtIdPre + catId
        txt.type = "text";
        // txt.autocomplete = "false";
        let lbl = document.createElement("label");
        lbl.htmlFor = txt.id
        lbl.innerText = "Name";
        let submitBtn = document.createElement("button");
        submitBtn.id = createCategoryBtnPre + catId;
        submitBtn.classList.add("submit-category-btn");
        submitBtn.value = catId;
        submitBtn.innerText = "Create";
        submitBtn.addEventListener("click", (e) => {
            // console.log("onclick - " + submitBtn.classList);
            createCategory(submitBtn.value);
        });
        // > body > create-category-group > create button to toggle input group
        let createBtn = document.createElement("button");
        createBtn.classList.add("create-category-btn");
        createBtn.value = catId;
        createBtn.innerText = "+ create new";
        createBtn.addEventListener("click", () => {
            // console.log("onclick - " + createBtn.classList);
            document.getElementById(createCategoryGroupIdPre + createBtn.value).classList.toggle("expand")
        });
        createCatInputGroup.append(lbl, txt, submitBtn);
        createCatGroup.append(createCatInputGroup, createBtn);
        catBody.append(createCatGroup)
    }
    group.append(catHeader, catBody);
    return group;
}

/**
 * creates a html element for the option and adds it to the parent element in the DOM recursively
 * @param option - object containing 3 properties:
 *      - category - the category object with properties such as id and name.
 *      - children - array of dictionaries(option objects), each contains a category object, an array of its children, and their corresponding html element
 *      - element - the html element returned, added
 * @param parentOptionElem - HtmlDivElement of the parent to append the child element to
 * @returns {HTMLDivElement}
 */
function initOptionElement(option, parentOptionElem) {
    let currentElm = createCategoryGroupHTMLElement(option.category.category_id, option.category.category_name, option.category.category_type);
    for (let i = 0; i < option.children.length; i++) {

        // appendChildCategoryGroup(currentElm, initOptionElement(option.children[i]))
        initOptionElement(option.children[i], currentElm)
    }
    //set element value to update categoryOptions object
    appendChildCategoryGroup(currentElm, parentOptionElem)
    option.element = currentElm;
    return currentElm;
}

/**
 * appends a childGroupElem {HTMLDivElement} to the .category-group__body div in the the parentGroupElem
 * or the optionsRow if the parentGroupElem null
 * @param parentGroupElem - HTML element of the existing category to append the child to
 * @param childGroupElem - HTML element of the new child category created
 */
function appendChildCategoryGroup(childGroupElem, parentGroupElem) {
    if (parentGroupElem) {
        let parentBody = parentGroupElem.querySelector(":scope > .category-group__body");
        let createGroup = parentBody.querySelector(":scope > .create-category-group");
        parentBody.insertBefore(childGroupElem, createGroup);
        createGroup.classList.remove("expand")
        // toggleOffElementClass(createGroup, "expand");
    } else {
        optionsRow.appendChild(childGroupElem);
    }
}


//TOGGLE methods called by click events
function toggleOffElementClass(elem, className) {
    // if (elem.classList.contains(className)) {
    elem.classList.remove(className)
    // }
}

function toggleOnElementClass(elem, className) {
    // if (!elem.classList.contains(className)) {
    elem.classList.add(className)
    // }
}

function toggleSelectCategory(categoryHeaderBtn) {
    if (selectedCategory === categoryHeaderBtn) {
        //deselect the current so none are selected
        // toggleOffElementClass(categoryHeaderBtn, "selected");
        categoryHeaderBtn.classList.remove("selected");
        selectedCategory = null;
        selectedCategoryLbl.innerText = "";
        publishBtn.disabled = true;
    } else {
        if (selectedCategory != null) {
            //deselect the old category
            // toggleOffElementClass(selectedCategory, "selected");
            selectedCategory.classList.remove("selected");
        }
        //select the new category
        selectedCategory = categoryHeaderBtn;
        selectedCategoryLbl.innerText = `Selected: ${categoryHeaderBtn.innerText}`;
        publishBtn.disabled = false;
        categoryHeaderBtn.classList.add("selected")
        // toggleOnElementClass(categoryHeaderBtn, "selected");
    }
}

// fetch methods
function getPublishOptionsPromise() {
    let fetchUrl = document.getElementById("ajax_get_publish_options_url").value;
    return new Promise((resolve, reject) => {
        fetch(fetchUrl)
            .then(response => {
                if (response.status === 200) {
                    resolve(response.json());
                } else reject(response);
            });
    });
}

function publishArticlePromise(articleId, catId) {
    let publishUrl = document.getElementById("ajax_publish_article_url").value;
    let formData = new FormData();
    formData.append('parent_category_id', catId);
    formData.append('article_id', articleId);
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    return new Promise((resolve, reject) => {
        fetch(publishUrl, {
            method: 'POST',
            body: formData,
            credentials: "same-origin"
        }).then(response => {
                // console.log("publishArticlePromise -> in then")
                // console.log(response)
                // console.log(response.status)
                if (response.status === 200) {
                    resolve(response.json())
                } else if (response.status !== 500) {
                    let j = response.json()
                    reject(j.error);
                } else {
                    reject(`Error:${response.status} Internal server error`);
                }
            }
        );
    })
}

async function publishArticle() {
    //start button loading animation
    publishBtn.classList.add("loading");
    publishBtn.innerText = "";
    publishBtn.disabled = true;

    if (!article) {
        await updateArticleDetails();
    }
    // console.log("publishArticle -> " + article);
    publishArticlePromise(article.article_id, selectedCategory.value).then(data => {
            // console.log("publishArticlePromise Then")
            // console.log(data);
            // update variables
            let temp = article.content ? article.content : null;
            article = data;
            article.conent = temp;
            // update publish status lbl and selected label
            if (article.published) {
                pubStatusLbl.innerText = `Currently public in: ${article.parent_category.category_name}`
                editControls.classList.add("published");
            } else {
                editControls.classList.remove("published");
                pubStatusLbl.innerText = `This post is private`
            }
        }
    ).finally(() => {
        // await new Promise(resolve => {
        //     setTimeout(() => {
        //         console.log("Timeout -> editor:");
        //         resolve();
        //     }, 4000)
        // })
        // turn off button loading animation
        publishBtn.classList.remove("loading");
        publishBtn.innerText = "Publish";
        publishBtn.disabled = false;

    })

}

function toggleCreateBtnLoading(btn) {
    if (btn.innerText){
        btn.classList.add("loading");
        btn.innerText = "";
        btn.enabled = true;
    }
    else{
        btn.classList.remove("loading");
        btn.innerText = "Create";
        btn.enabled = false;
    }
}

function createCategory(parentID) {
    let newCatName = document.getElementById(createCategoryTxtIdPre + parentID).value;
    if (newCatName) {
        let btn = document.getElementById(createCategoryBtnPre + parentID);
        toggleCreateBtnLoading(btn);
        createCategoryPromise(newCatName, parentID).then(newOption => {
                // console.log("data:")
                let newCat = newOption.category;
                let newElem = createCategoryGroupHTMLElement(newCat.category_id, newCat.category_name, newCat.category_type);
                document.getElementById(categoryGroupIdPre + parentID);
                let parentElem = document.getElementById(categoryGroupIdPre+parentID)
                appendChildCategoryGroup(newElem, parentElem);
            }
        ).finally(() => {
                toggleCreateBtnLoading(btn);
                document.getElementById(createCategoryGroupIdPre + parentID).classList.remove("expand")
                document.getElementById(createCategoryTxtIdPre + parentID).value = "";
            }
        );
    }
}

function createCategoryPromise(childCatName, parentID) {
    let createUrl = document.getElementById("ajax_create_child_category_url").value;
    let formData = new FormData();
    formData.append('parent_category_id', parentID);
    formData.append('child_category_name', childCatName);
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    return new Promise((resolve, reject) => {
        fetch(createUrl, {
            method: 'POST',
            body: formData,
            credentials: "same-origin"
        }).then(response => {
                console.log("createCategoryPromise -> in then")
                console.log(response.status)
                console.log(response)
                if (response.status === 202) {
                    resolve(response.json())
                } else if (response.status !== 500) {
                    let j = response.json()
                    reject(j.error);
                } else {
                    reject(`Error:${response.status} Internal server error`);
                }
            }
        );
    })
}


//NAVIGATION BUTTONS
function viewArticle(url) {
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
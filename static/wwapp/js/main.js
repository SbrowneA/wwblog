function linked() {
    alert("JS linked");
}

//
// function deleteArticle(the_id) {
//     alert("THe id: " + the_id.toString());
//     if (confirm("Are you sure you want to delete this post (" + '{{ article.article_title }}'
//         + ")?\nLinked posts will not be deleted, only unliked")) {
//         var url = "/post/" + the_id.toString() + "/delete";
//         alert(url);
//         window.location.replace(url)
//     } else {
//         return false;
//     }
// }

// function deleteArticle(article_id) {
//     alert("clickd\n id:" + article_id)
//     if (confirm("Are you sure you want to delete this post?\n linked posts will not be deleted, only unliked")) {
//         window.location.replace("post/" + article_id + "/delete");
//     } else {
//         return false;
//     }
// }


function convert_date_to_user_timezone() {
    const month = {
        0: 'January',
        1: 'February',
        2: 'March',
        3: 'April',
        4: 'May',
        5: 'June',
        6: 'July',
        7: 'August',
        8: 'September',
        9: 'October',
        10: 'November',
        11: 'December'
    }
    let dateTxt = document.getElementById("publish-date");
    let dateStr = dateTxt.innerText
    let date = new Date(dateStr.toString());
    let localDate = new Date(date.getTime() - date.getTimezoneOffset()*60000);
    // alert(`${month[localDate.getMonth()]} ${localDate.getDate()}, ${localDate.getFullYear()}, ${localDate.getHours()}:${localDate.getMinutes()}`)
    let hr = localDate.getHours();
    let min = localDate.getMinutes();
    let ampm = (hr >= 12) ? 'p.m.' : 'a.m.';
    if (hr > 12 && min > 0) {
        hr -= 12;
    }
    hr = (hr === 0) ? 12 : hr;
    min = (min<10) ? "0"+min : min;
    dateTxt.innerText = `${month[localDate.getMonth()]} ${localDate.getDate()}, ${localDate.getFullYear()}, ${hr}:${min} ${ampm}`;
}

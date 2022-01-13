document.addEventListener('DOMContentLoaded', function () {
    const boxes = document.querySelectorAll("input[type='checkbox']");
    for (let i = 0; i < boxes.length; i++) {
        boxes[i].addEventListener("click", (e) => {
            unclick(e);
        });
    }
    function unclick(e) {
        for (let i = 0; i < boxes.length; i++) {
            boxes[i].checked = false;
        }
        e.target.checked = true;
    };
});


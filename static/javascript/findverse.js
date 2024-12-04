const tabsBox = document.querySelector(".tabs-box"),
arrowIcons = document.querySelectorAll(".icon i");

let isDragging = false

// const handleIcons = () => {
//     let scrollVal = tabsBox.scrollLeft;
//     let maxScrollableWidth = tabsBox.scrollWidth - tabsBox.clientWidth;
//     arrowIcons[0].parentElement.style.display = scrollVal > 0 ? "flex" : "none";
//     arrowIcons[1].parentElement.style.display = maxScrollableWidth > scrollVal ? "flex" : "none";
// }

arrowIcons.forEach(icon => {
    icon.addEventListener("click", () => {
        tabsBox.scrollLeft += icon.id === "left" ? -350 : 350;
        setTimeout(() => handleIcons(), 50);
    });
});

const dragging = (e) => {
    if(!isDragging) return;
    tabsBox.classList.add("dragging");
    tabsBox.scrollLeft -= e.movementX;
    // handleIcons();
}

const dragStop = () => {
    isDragging = false;
    tabsBox.classList.remove("dragging");
}

tabsBox.addEventListener("mousedown", () => isDragging = true);
tabsBox.addEventListener("mousemove", dragging);
document.addEventListener("mouseup", dragStop);


let subMenu = document.getElementById("subMenu");

function toggleMenu(){
    subMenu.classList.toggle("open-menu");
}

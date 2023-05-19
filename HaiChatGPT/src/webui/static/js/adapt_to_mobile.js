
const sidebar = document.getElementById("sidebar");
const show_on_mobile_title = document.getElementById("show-on-mobile-title");
const expand_sidebar_btn = document.getElementById("expand-sidebar-btn");


expand_sidebar_btn.addEventListener("click", function () {
    if (sidebar.style.display === "flex") {
        // 切换为隐藏
        sidebar.style.display = "none";
        // 切换按内容为显示
        expand_sidebar_btn.innerText = "展开";
        return;
    } else {
        sidebar.style.display = "flex";
        // 切换按内容为隐藏
        expand_sidebar_btn.innerText = "隐藏";
    }
});








function updateUserInterface(user_data) {
        $("#username").text(user_data.username);
        $("#phone").text(user_data.phone);
        $("#email").text(user_data.email ? user_data.email : "未设置");
        if (!user_data.email) {
            $("#email").after('<button onclick="location.href=\'/verify_email\'">去验证</button>');
        }
        $("#type").text(user_data.type);
        $("#limit").text(user_data.limit + " RMB");
        $("#group").text(user_data.group);
    }
    $(document).ready(function() {
    $.ajax({
        url: "/get_user_data",
        method: "GET",
        success: function(data) {
            updateUserInterface(data);
        },
        error: function(error) {
            console.error("Error fetching user data:", error);
        }
    });
});
    
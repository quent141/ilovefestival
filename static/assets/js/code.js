function updateMarkdown() {
    var $markdown = $("#renderMarkdown");

    $.ajax({
        url: "/api/renderMarkdown",
        method: "POST",
        data : $("#formMarkdown").serialize(),
        success: function(data) {
            console.log("renderMardown", data.markdown);
            $markdown.html(data.markdown);
        },
        error: function() {
            console.log("renderMardown failed");
            $markdown.text("Render failed");
        }
    });
}


$("#formMarkdown").on("keyup",function(){
    updateMarkdown();
});

setTimeout(updateMarkdown,200);

$("#ajaxUpdateMarkdown").on("click",function(){
    updateMarkdown();
});
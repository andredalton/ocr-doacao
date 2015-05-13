function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        $photo = false
        reader.onload = function (e) {
            $('#preview_photo').attr('src', e.target.result);
            $photo = $('#preview_photo');
            if($photo.hasClass("hidden")){
                $photo.toggleClass("hidden");
                $('#enviar').toggleClass("hidden");
            }
        }
        reader.readAsDataURL(input.files[0]);
    }
}
$("#file1").change(function(){
    readURL(this);
});
$("#imgInp").change(function(){
    readURL(this);
});
$("#upfile1").click(function () {
    $("#file1").trigger('click');
});
$("form").submit(function() {
    $(".loading").css("display", "block");
});
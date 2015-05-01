function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

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
$(document).ready(function() {
    var erro = false;
    $("#data").mask("00/00/0000");
    $("#valor").mask("###0.00", { reverse: true });
    $("#coo").mask("000000");
    $("#cnpj").mask("00.000.000/0000-00");
    $("form").submit(function(e) {
        var data = $("#data").val();
        var valor = $("#valor").val();
        var coo = $("#coo").val();
        var cnpj = $("#cnpj").val();
        if (data == null || data == "" ||
            valor == null || valor == "" ||
            coo == null ||  coo == "" ||
            cnpj == null || cnpj == "")
        {
            if (!erro){
                erro = true;
                $("#erro").prepend("<p class='validation_error'>* Todos os campos são obrigatórios</p>");
            }
            e.preventDefault();
        }
    });
});
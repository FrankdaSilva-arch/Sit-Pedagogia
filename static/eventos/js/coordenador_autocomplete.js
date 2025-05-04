document.addEventListener("DOMContentLoaded", function() {
    var input = document.getElementById("id_coordenador");
    console.log("[LOG] Script coordenador_autocomplete.js carregado");
    if (!input) {
        console.log("[LOG] Campo #id_coordenador não encontrado!");
        return;
    }
    console.log("[LOG] Campo #id_coordenador encontrado!");
    var awesomplete = new Awesomplete(input, { minChars: 1, maxItems: 10 });

    input.addEventListener("input", function() {
        var query = input.value;
        console.log("[LOG] Digitado no coordenador:", query);
        if (query.length > 0) {
            fetch("/eventos/autocomplete/coordenadores/?q=" + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => {
                    console.log("[LOG] Sugestões recebidas:", data);
                    awesomplete.list = data;
                });
        }
    });
}); 
document.addEventListener('DOMContentLoaded', function() {
    // Pode adicionar interações JavaScript aqui
    console.log('Catálogo carregado');
    
    // Exemplo: Adicionar evento de clique aos cards de produto
    const productCards = document.querySelectorAll('.product-card');
    if (productCards) {
        productCards.forEach(card => {
            card.addEventListener('click', function() {
                // Aqui você pode adicionar ação quando um produto é clicado
                console.log('Produto clicado');
            });
        });
    }
});
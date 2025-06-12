document.addEventListener('DOMContentLoaded', function() {
    console.log('Catálogo carregado');
    
    const productCards = document.querySelectorAll('.product-card');
    if (productCards) {
        productCards.forEach(card => {
            card.addEventListener('click', function() {
                console.log('Produto clicado');
            });
        });
    }
});
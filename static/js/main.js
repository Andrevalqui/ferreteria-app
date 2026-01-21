document.addEventListener("DOMContentLoaded", function() {
    // 1. Lógica del Splash Screen
    const splash = document.getElementById('splash-screen');
    
    // Esperamos 2 segundos y desvanecemos
    setTimeout(() => {
        splash.style.opacity = '0';
        setTimeout(() => {
            splash.style.display = 'none';
        }, 500); // Espera a que termine la transición CSS
    }, 2000);

    // Aquí agregaremos luego la lógica del Carrito de WhatsApp
});
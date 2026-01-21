let carrito = [];

document.addEventListener("DOMContentLoaded", function() {
    // Splash Screen
    const splash = document.getElementById('splash-screen');
    if(splash){
        setTimeout(() => {
            splash.style.opacity = '0';
            setTimeout(() => { splash.style.display = 'none'; }, 500);
        }, 1500);
    }
});

function agregarAlCarrito(id, nombre, precio) {
    const inputCant = document.getElementById('cant-' + id);
    const cantidad = parseInt(inputCant.value);

    if (cantidad > 0) {
        const existe = carrito.find(p => p.id === id);
        if (existe) {
            existe.cantidad += cantidad;
        } else {
            carrito.push({ id, nombre, precio, cantidad });
        }
        actualizarUI();
        
        // Animación botón
        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check2"></i> AGREGADO';
        btn.classList.remove('btn-warning');
        btn.classList.add('btn-success');
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.add('btn-warning');
            btn.classList.remove('btn-success');
        }, 1000);
    }
}

function actualizarUI() {
    const totalItems = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    const badge = document.getElementById('cart-count');
    if(badge) badge.innerText = totalItems;

    const contenedor = document.getElementById('cart-items-container');
    const totalPrecioEl = document.getElementById('cart-total');
    
    if (carrito.length === 0) {
        contenedor.innerHTML = '<p class="text-center text-muted">Tu carrito está vacío.</p>';
        totalPrecioEl.innerText = 'S/ 0.00';
        return;
    }

    let html = '<ul class="list-group list-group-flush">';
    let totalPrecio = 0;

    carrito.forEach((item, index) => {
        let subtotal = item.precio * item.cantidad;
        totalPrecio += subtotal;
        html += `
            <li class="list-group-item bg-transparent text-white d-flex justify-content-between align-items-center border-secondary ps-0 pe-0">
                <div>
                    <span class="fw-bold text-accent">${item.nombre}</span> <br>
                    <small class="text-muted">Cant: ${item.cantidad} x S/ ${item.precio.toFixed(2)}</small>
                </div>
                <div class="d-flex align-items-center">
                    <span class="me-3">S/ ${subtotal.toFixed(2)}</span>
                    <button class="btn btn-sm btn-outline-danger border-0" onclick="eliminarItem(${index})"><i class="bi bi-trash"></i></button>
                </div>
            </li>
        `;
    });

    html += '</ul>';
    contenedor.innerHTML = html;
    totalPrecioEl.innerText = 'S/ ' + totalPrecio.toFixed(2);
}

function eliminarItem(index) {
    carrito.splice(index, 1);
    actualizarUI();
}

// Lógica de Envío Actualizada
function enviarPedidoWhatsapp() {
    if (carrito.length === 0) {
        alert("El carrito está vacío.");
        return;
    }

    const nombre = document.getElementById('cliente-nombre').value;
    const empresa = document.getElementById('cliente-empresa').value;
    const entrega = document.getElementById('tipo-entrega').value;
    const pago = document.getElementById('tipo-pago').value; // Nuevo campo

    if (!nombre) {
        alert("Por favor ingrese su nombre para el pedido.");
        return;
    }

    // TU NÚMERO ACTUALIZADO
    const telefonoVendedor = "51997317288"; 

    let mensaje = `*HOLA, QUIERO CONFIRMAR ESTE PEDIDO:* 🛒%0A`;
    mensaje += `--------------------------------%0A`;
    mensaje += `👤 *Cliente:* ${nombre}%0A`;
    if(empresa) mensaje += `🏢 *Empresa:* ${empresa}%0A`;
    mensaje += `🚚 *Entrega:* ${entrega}%0A`;
    mensaje += `💳 *Pago:* ${pago}%0A`;
    mensaje += `--------------------------------%0A`;
    
    let totalGeneral = 0;
    carrito.forEach(item => {
        let subtotal = item.precio * item.cantidad;
        totalGeneral += subtotal;
        mensaje += `▪️ ${item.cantidad} un. - ${item.nombre} (S/ ${subtotal.toFixed(2)})%0A`;
    });

    mensaje += `--------------------------------%0A`;
    mensaje += `*TOTAL A PAGAR: S/ ${totalGeneral.toFixed(2)}*%0A`;
    mensaje += `--------------------------------%0A`;
    
    window.open(`https://wa.me/${telefonoVendedor}?text=${mensaje}`, '_blank');
}

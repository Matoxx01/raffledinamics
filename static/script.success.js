document.addEventListener('DOMContentLoaded', function() {
    // Efecto de partículas al cargar
    const container = document.querySelector('.success-container');
    
    function createParticle() {
    const particle = document.createElement('div');
    particle.style.position = 'absolute';
    particle.style.width = '4px';
    particle.style.height = '4px';
    particle.style.background = 'rgba(102, 126, 234, 0.6)';
    particle.style.borderRadius = '50%';
    particle.style.pointerEvents = 'none';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = '100%';
    particle.style.animation = 'floatUp 3s ease-out forwards';
    
    document.body.appendChild(particle);
    
    setTimeout(() => {
        particle.remove();
    }, 3000);
    }
    
    // Crear partículas ocasionalmente
    setInterval(createParticle, 800);
    
    // Efecto hover en números
    const numberItems = document.querySelectorAll('.number-item');
    numberItems.forEach(item => {
    item.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px) scale(1.05)';
    });
    
    item.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
    });
    });
});
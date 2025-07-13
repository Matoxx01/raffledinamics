// Mostrar imagen cuando entra en viewport
const img = document.getElementById('hero-img');
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      img.classList.add('img-visible');
    }
  });
}, { threshold: 0.5 });

observer.observe(img);

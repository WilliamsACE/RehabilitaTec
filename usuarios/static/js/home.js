document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const status = document.getElementById('status');
    const progressBar = document.getElementById('progressBar');
    const presentationControls = document.getElementById('presentationControls');
    const toggleControls = document.getElementById('toggleControls');
    
    
    const sections = document.querySelectorAll('section, footer');
    const sectionTimes = [3000, 3000, 3000, 3000, 3000, 2500];
    let currentSection = 0;
    let isPresenting = false;
    let presentationInterval;
    
    // Función para mostrar/ocultar controles
    function toggleControlsPanel() {
        presentationControls.classList.toggle('hidden');
    }
    
    toggleControls.addEventListener('click', toggleControlsPanel);
    
    // Función para iniciar la presentación
    function startPresentation() {
        if (isPresenting) return;
        
        isPresenting = true;
        status.textContent = 'Presentación en curso...';
        startBtn.disabled = true;
        stopBtn.disabled = false;
        
        // Ocultar controles al iniciar
        presentationControls.classList.add('hidden');
        
        // Ir a la primera sección
        goToSection(0);
        
        // Configurar el intervalo para cambiar de sección automáticamente
        startAutoAdvance();
    }
    
    // Función para iniciar el avance automático
    function startAutoAdvance() {
        if (presentationInterval) {
            clearInterval(presentationInterval);
        }
        
        presentationInterval = setInterval(() => {
            if (currentSection < sections.length - 1) {
                currentSection++;
                goToSection(currentSection);
            } else {
                // Si llegamos al final, reiniciamos
                currentSection = 0;
                goToSection(currentSection);
            }
        }, sectionTimes[currentSection]);
    }
    
    // Función para detener COMPLETAMENTE la presentación
    function stopPresentation() {
        isPresenting = false;
        status.textContent = 'Presentación detenida';
        startBtn.disabled = false;
        stopBtn.disabled = true;
        
        // Limpiar TODOS los intervalos
        if (presentationInterval) {
            clearInterval(presentationInterval);
            presentationInterval = null;
        }
        
        // Quitar el resaltado de la sección actual
        sections.forEach(section => {
            section.classList.remove('section-highlight');
        });
        
        // Reiniciar la barra de progreso
        progressBar.style.width = '0%';
        
        console.log('Presentación detenida completamente');
    }
    
    // Función para ir a una sección específica
    function goToSection(index) {
        if (index < 0 || index >= sections.length) return;
        
        currentSection = index;
        
        // Quitar el resaltado de todas las secciones
        sections.forEach(section => {
            section.classList.remove('section-highlight');
        });
        
        // Aplicar animación y resaltado a la sección actual
        const currentSectionElement = sections[currentSection];
        currentSectionElement.classList.add('section-highlight');
        currentSectionElement.classList.add('section-visible');
        
        // Hacer scroll suave a la sección
        currentSectionElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
        
        // Actualizar la barra de progreso
        const progress = ((currentSection + 1) / sections.length) * 100;
        progressBar.style.width = `${progress}%`;
        
        // Si está en modo presentación, reiniciar el intervalo con el nuevo tiempo
        if (isPresenting && presentationInterval) {
            startAutoAdvance();
        }
        
        // Actualizar el estado
        status.textContent = `Sección ${currentSection + 1} de ${sections.length}`;
    }
    
    // Event listeners para los botones
    startBtn.addEventListener('click', startPresentation);
    stopBtn.addEventListener('click', stopPresentation);
    
    // Controles de teclado
    document.addEventListener('keydown', function(e) {
        // Ctrl+Space para iniciar presentación
        if (e.ctrlKey && e.code === 'Space') {
            e.preventDefault();
            startPresentation();
        }
        
        // ESC para DETENER COMPLETAMENTE la presentación
        if (e.key === 'Escape') {
            e.preventDefault();
            stopPresentation();
        }
        
        // C para mostrar/ocultar controles
        if (e.key === 'c' || e.key === 'C') {
            e.preventDefault();
            toggleControlsPanel();
        }
        
        // Flechas para navegación manual (solo funciona cuando NO está en presentación automática)
        if (!isPresenting) {
            if (e.key === 'ArrowRight' || e.key === 'PageDown') {
                e.preventDefault();
                if (currentSection < sections.length - 1) {
                    goToSection(currentSection + 1);
                }
            }
            
            if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
                e.preventDefault();
                if (currentSection > 0) {
                    goToSection(currentSection - 1);
                }
            }
        }
        
        // Flechas para navegación manual DURANTE la presentación (reinicia el timer)
        if (isPresenting) {
            if (e.key === 'ArrowRight' || e.key === 'PageDown') {
                e.preventDefault();
                if (currentSection < sections.length - 1) {
                    currentSection++;
                    goToSection(currentSection);
                }
            }
            
            if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
                e.preventDefault();
                if (currentSection > 0) {
                    currentSection--;
                    goToSection(currentSection);
                }
            }
        }
    });
    
    // Inicializar animaciones de las secciones
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !isPresenting) {
                entry.target.classList.add('section-visible');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.section-animate').forEach(section => {
        observer.observe(section);
    });
    
    // Menu Hamburguesa (código existente)
    const mobileMenu = document.getElementById('mobile-menu');
    const navLinks = document.getElementById('nav-links');
    
    mobileMenu.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        
        const spans = mobileMenu.querySelectorAll('span');
        if (navLinks.classList.contains('active')) {
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
        } else {
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
        }
    });
    
    const navItems = navLinks.querySelectorAll('a');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                navLinks.classList.remove('active');
                const spans = mobileMenu.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });
    });
});
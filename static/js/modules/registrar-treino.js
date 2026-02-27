/**
 * Módulo para registro de treinos
 */
const RegistrarTreino = (function() {
    
    function init() {
        console.log('Inicializando módulo de registro');
        
        // Configurar listeners para cálculo automático de volume
        document.querySelectorAll('.carga-input, .reps-input, select[name^="num_series"]').forEach(input => {
            input.addEventListener('input', function() {
                const row = this.closest('.exercise-row');
                if (row) {
                    calcularVolume(row);
                }
            });
            
            input.addEventListener('change', function() {
                const row = this.closest('.exercise-row');
                if (row) {
                    calcularVolume(row);
                }
            });
        });
        
        // Calcular volumes iniciais
        document.querySelectorAll('.exercise-row').forEach(row => {
            calcularVolume(row);
        });
    }
    
    function calcularVolume(row) {
        const cargaInput = row.querySelector('.carga-input');
        const repsInput = row.querySelector('.reps-input');
        const seriesSelect = row.querySelector('select[name^="num_series"]');
        const volumeSpan = row.querySelector('.volume-total');
        
        if (!cargaInput || !repsInput || !seriesSelect || !volumeSpan) return;
        
        const carga = parseFloat(cargaInput.value) || 0;
        const reps = parseInt(repsInput.value) || 0;
        const series = parseInt(seriesSelect.value) || 1;
        
        const volume = carga * reps * series;
        
        if (volume > 0) {
            volumeSpan.innerHTML = `<i class="bi bi-bar-chart"></i> ${volume} kg`;
        } else {
            volumeSpan.innerHTML = '<i class="bi bi-bar-chart"></i> 0 kg';
        }
    }
    
    function carregarUltimoRegistro() {
        let carregados = 0;
        
        document.querySelectorAll('.exercise-row').forEach(row => {
            const ultimaCarga = row.dataset.ultimaCarga;
            const ultimasReps = row.dataset.ultimasReps;
            const ultimasSeries = row.dataset.ultimasSeries;
            
            if (ultimaCarga && ultimasReps && ultimaCarga !== 'undefined') {
                const cargaInput = row.querySelector('.carga-input');
                const repsInput = row.querySelector('.reps-input');
                const seriesSelect = row.querySelector('select[name^="num_series"]');
                
                if (cargaInput) cargaInput.value = ultimaCarga;
                if (repsInput) repsInput.value = ultimasReps;
                if (seriesSelect && ultimasSeries && ultimasSeries !== 'undefined') {
                    seriesSelect.value = ultimasSeries;
                }
                
                calcularVolume(row);
                carregados++;
            }
        });
        
        if (carregados > 0) {
            FitLogUtils.showToast(`${carregados} exercícios carregados!`, 'success');
        } else {
            FitLogUtils.showToast('Nenhum dado anterior encontrado', 'warning');
        }
    }
    
    // Validação do formulário
    document.getElementById('registroForm')?.addEventListener('submit', function(e) {
        let valido = true;
        let mensagem = '';
        
        document.querySelectorAll('.exercise-row').forEach(row => {
            const carga = row.querySelector('.carga-input')?.value;
            const reps = row.querySelector('.reps-input')?.value;
            
            if ((carga && !reps) || (!carga && reps)) {
                valido = false;
                mensagem = 'Preencha carga e repetições juntos';
                row.classList.add('border', 'border-danger');
            } else {
                row.classList.remove('border', 'border-danger');
            }
        });
        
        if (!valido) {
            e.preventDefault();
            FitLogUtils.showToast(mensagem, 'danger');
        }
    });
    
    return {
        init: init,
        carregarUltimoRegistro: carregarUltimoRegistro,
        calcularVolume: calcularVolume
    };
})();

// Exportar para uso global
window.RegistrarTreino = RegistrarTreino;
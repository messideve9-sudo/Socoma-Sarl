<script>
// ============================================
// FONCTIONS POUR LA PAGE COMMERCIAUX
// ============================================

/**
 * Affiche ou masque la liste des clients d'un commercial
 * @param {string} clientListId - ID de la liste à afficher/masquer
 * @param {HTMLElement} button - Le bouton cliqué
 */
function toggleClients(clientListId, button) {
    const clientList = document.getElementById(clientListId);
    if (!clientList) return;
    
    const isExpanded = clientList.classList.contains('expanded');
    
    if (isExpanded) {
        // Masquer la liste
        clientList.classList.remove('expanded');
        button.innerHTML = '<i class="fas fa-chevron-down"></i> Voir clients';
        button.classList.remove('active');
    } else {
        // Afficher la liste
        clientList.classList.add('expanded');
        button.innerHTML = '<i class="fas fa-chevron-up"></i> Cacher clients';
        button.classList.add('active');
        
        // Fermer les autres listes dans la même carte (optionnel)
        const card = button.closest('.commercial-card');
        if (card) {
            const otherButtons = card.querySelectorAll('.toggle-clients-btn');
            otherButtons.forEach(btn => {
                if (btn !== button && btn.classList.contains('active')) {
                    // Récupérer l'ID de l'autre liste depuis son attribut onclick
                    const match = btn.getAttribute('onclick')?.match(/'([^']+)'/) || 
                                 btn.getAttribute('onclick')?.match(/"([^"]+)"/);
                    if (match && match[1]) {
                        const otherListId = match[1];
                        const otherList = document.getElementById(otherListId);
                        if (otherList) {
                            otherList.classList.remove('expanded');
                        }
                        btn.innerHTML = '<i class="fas fa-chevron-down"></i> Voir clients';
                        btn.classList.remove('active');
                    }
                }
            });
        }
    }
}

// ============================================
// FONCTIONS DE RECHERCHE
// ============================================

/**
 * Recherche en temps réel dans le tableau des clients
 */
function setupClientSearch() {
    const searchInput = document.getElementById('clientSearchInput');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const table = document.querySelector('table');
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const isVisible = text.includes(searchTerm);
            row.style.display = isVisible ? '' : 'none';
            if (isVisible) visibleCount++;
        });
        
        // Afficher un message si aucun résultat
        const noResults = document.getElementById('noSearchResults');
        if (noResults) {
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    });
}

// ============================================
// FONCTIONS DE TRI
// ============================================

/**
 * Trie le tableau des clients
 * @param {number} columnIndex - Index de la colonne à trier
 */
function sortClientTable(columnIndex) {
    const table = document.querySelector('table');
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    const rows = Array.from(tbody.querySelectorAll('tr'));
    if (rows.length === 0) return;
    
    const isAscending = table.dataset.sortColumn === columnIndex.toString() 
        ? table.dataset.sortOrder === 'desc'
        : true;
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex]?.textContent.trim() || '';
        const bValue = b.cells[columnIndex]?.textContent.trim() || '';
        
        // Essayer de convertir en nombre
        const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // Sinon tri alphabétique
        return isAscending 
            ? aValue.localeCompare(bValue, 'fr')
            : bValue.localeCompare(aValue, 'fr');
    });
    
    // Réorganiser les lignes
    rows.forEach(row => tbody.appendChild(row));
    
    // Mettre à jour les indicateurs de tri
    table.dataset.sortColumn = columnIndex;
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    
    // Mettre à jour les icônes de tri
    updateSortIcons(table, columnIndex, isAscending);
}

/**
 * Met à jour les icônes de tri
 * @param {HTMLElement} table - Le tableau
 * @param {number} activeColumn - Colonne active
 * @param {boolean} isAscending - Ordre de tri
 */
function updateSortIcons(table, activeColumn, isAscending) {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        const icon = header.querySelector('.sort-icon');
        if (icon) {
            if (index === activeColumn) {
                icon.className = `sort-icon fas fa-sort-${isAscending ? 'up' : 'down'}`;
                icon.style.opacity = '1';
            } else {
                icon.className = 'sort-icon fas fa-sort';
                icon.style.opacity = '0.5';
            }
        }
    });
}

// ============================================
// FONCTIONS D'EXPORT
// ============================================

/**
 * Exporte les données au format Excel
 */
function exportToExcel() {
    // Récupérer les données du tableau
    const table = document.querySelector('table');
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(col => {
            rowData.push('"' + col.innerText.replace(/"/g, '""') + '"');
        });
        csv.push(rowData.join(','));
    });
    
    // Créer le fichier CSV
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'commerciaux_socoma.csv');
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Export Excel réussi', 'success');
}

// ============================================
// FONCTIONS DE NOTIFICATION
// ============================================

/**
 * Affiche une notification toast
 * @param {string} message - Message à afficher
 * @param {string} type - Type de notification (success, error, info)
 */
function showNotification(message, type = 'info') {
    const colors = {
        success: '#27ae60',
        error: '#e74c3c',
        info: '#3498db'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;
    
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${colors[type]};
        color: white;
        border-radius: 10px;
        z-index: 9999;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        animation: slideInRight 0.3s ease;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// FONCTIONS D'INTERACTION
// ============================================

/**
 * Appelle un client
 * @param {string} phoneNumber - Numéro de téléphone
 */
function callClient(phoneNumber) {
    if (phoneNumber) {
        window.location.href = `tel:${phoneNumber}`;
    } else {
        showNotification('Numéro non disponible', 'error');
    }
}

/**
 * Affiche les détails d'un client
 * @param {string} clientId - ID du client
 */
function showClientDetails(clientId) {
    // À implémenter selon tes besoins
    console.log('Afficher détails client:', clientId);
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Page commerciaux initialisée');
    
    // Initialiser la recherche
    setupClientSearch();
    
    // Ajouter des événements de tri aux en-têtes de tableau
    const tableHeaders = document.querySelectorAll('table thead th');
    tableHeaders.forEach((header, index) => {
        // Ajouter l'icône de tri si elle n'existe pas
        if (!header.querySelector('.sort-icon')) {
            header.innerHTML += ' <i class="sort-icon fas fa-sort" style="opacity:0.5; margin-left:5px;"></i>';
            header.style.cursor = 'pointer';
        }
        
        header.addEventListener('click', () => sortClientTable(index));
    });
    
    // Ajouter des tooltips aux boutons d'appel
    const callButtons = document.querySelectorAll('.btn-success[href^="tel:"]');
    callButtons.forEach(btn => {
        btn.setAttribute('title', 'Appeler le commercial');
    });
    
    // Compter et afficher le nombre total de clients
    const totalClients = document.querySelectorAll('.client-item').length;
    console.log(`Total clients chargés: ${totalClients}`);
    
    // Animation d'entrée pour les cartes
    const cards = document.querySelectorAll('.commercial-card');
    cards.forEach((card, index) => {
        card.style.animation = `fadeInUp 0.5s ease ${index * 0.1}s both`;
    });
});

// ============================================
// ANIMATIONS CSS (ajoutées dynamiquement)
// ============================================

const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .sort-icon {
        transition: opacity 0.3s ease;
    }
    
    th:hover .sort-icon {
        opacity: 1 !important;
    }
    
    .toast-notification {
        font-family: 'Segoe UI', sans-serif;
    }
`;
document.head.appendChild(style);

// ============================================
// RACCOURCIS CLAVIER
// ============================================

document.addEventListener('keydown', function(e) {
    // Ctrl + F pour focus recherche
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('clientSearchInput');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // Échap pour fermer les listes ouvertes
    if (e.key === 'Escape') {
        const expandedLists = document.querySelectorAll('.clients-list.expanded');
        expandedLists.forEach(list => {
            list.classList.remove('expanded');
        });
        
        const activeButtons = document.querySelectorAll('.toggle-clients-btn.active');
        activeButtons.forEach(btn => {
            btn.innerHTML = '<i class="fas fa-chevron-down"></i> Voir clients';
            btn.classList.remove('active');
        });
    }
});

// ============================================
// GESTION DU REDIMENSIONNEMENT
// ============================================

let resizeTimer;
window.addEventListener('resize', function() {
    document.body.classList.add('resize-animation-stopper');
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        document.body.classList.remove('resize-animation-stopper');
    }, 400);
});
</script>
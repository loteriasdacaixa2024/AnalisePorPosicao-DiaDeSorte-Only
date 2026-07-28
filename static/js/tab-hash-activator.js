/**
 * tab-hash-activator.js
 * -------------------------------------------------------
 * Abre automaticamente uma aba Bootstrap pelo hash da URL.
 *
 * COMO USAR:
 *   1. Coloque este arquivo em /static/js/tab-hash-activator.js
 *   2. Adicione no final do seu HTML (antes de </body>):
 *        <script src="/static/js/tab-hash-activator.js"></script>
 *
 * Se o arquivo usa Jinja2 (Flask) com {% endblock %}. 
 * O </body> real fica no template base. O script deve ser colocado 
 * antes do {% endblock %}, no final do arquivo.
 *
 *   Então o script deve  ficar assim... 
 *   	</script>
 *			<script src="/static/js/tab-hash-activator.js"></script>
 *		{% endblock %}
 *   
 *
 * COMO CHAMAR UMA ABA DIRETO PELA URL:
 *   http://127.0.0.1:5151/analise-visual/#pane-simulador
 *   http://127.0.0.1:5151/outra-rota/#nome-do-id-do-pane
 *
 * REQUISITOS:
 *   - Bootstrap 5 (data-bs-toggle="tab")
 *   - O pane deve ter um id correspondente (ex: id="pane-simulador")
 *   - O botão/link da aba deve ter data-bs-target="#pane-simulador"
 *
 * OPÇÕES DE CONFIGURAÇÃO (window.tabHashConfig):
 *   - updateHashOnClick : true   → atualiza o hash da URL ao clicar em uma aba
 *   - scrollToTabs      : true   → rola a página até as abas ao ativar pelo hash
 *   - defaultTab        : null   → id do pane a ativar se nenhum hash for encontrado
 *                                  ex: 'pane-principal'
 * -------------------------------------------------------
 */

(function () {
    // ── Configurações (podem ser sobrescritas antes de carregar o script) ──
    const config = Object.assign({
        updateHashOnClick: true,
        scrollToTabs: true,
        defaultTab: null
    }, window.tabHashConfig || {});

    // ── Ativa uma aba pelo id do pane ──
    function activateTab(paneId) {
        if (!paneId) return false;

        // Busca o botão/link que aponta para este pane
        const trigger =
            document.querySelector(`[data-bs-target="#${paneId}"]`) ||
            document.querySelector(`[href="#${paneId}"]`);

        if (!trigger) return false;

        // Usa a API do Bootstrap 5 para ativar a aba
        const tabInstance = bootstrap.Tab.getOrCreateInstance(trigger);
        tabInstance.show();

        // Scroll até a área de abas (opcional)
        if (config.scrollToTabs) {
            const tabContainer = trigger.closest('.nav-tabs, .nav-pills, [role="tablist"]');
            if (tabContainer) {
                setTimeout(() => {
                    tabContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        }

        return true;
    }

    // ── Lê o hash da URL e extrai o id do pane ──
    function getPaneIdFromHash() {
        const hash = window.location.hash; // ex: "#pane-simulador"
        if (!hash) return null;
        return hash.replace('#', ''); // ex: "pane-simulador"
    }

    // ── Inicialização: ativa aba ao carregar a página ──
    function init() {
        const paneId = getPaneIdFromHash() || config.defaultTab;
        if (paneId) {
            // Aguarda Bootstrap estar pronto
            const ready = activateTab(paneId);
            if (!ready) {
                // Tenta novamente após renderização completa
                setTimeout(() => activateTab(paneId), 300);
            }
        }

        // ── Atualiza hash na URL ao clicar em abas ──
        if (config.updateHashOnClick) {
            document.addEventListener('shown.bs.tab', function (e) {
                const target = e.target.getAttribute('data-bs-target') ||
                               e.target.getAttribute('href');
                if (target && target.startsWith('#')) {
                    history.replaceState(null, '', target);
                }
            });
        }
    }

    // ── Aguarda o DOM estar pronto ──
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
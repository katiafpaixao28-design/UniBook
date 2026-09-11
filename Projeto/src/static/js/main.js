/**
 * UniBook - Faculdade UniEnsino
 * Scripts mínimos auxiliares
 */

document.addEventListener("DOMContentLoaded", () => {
    // Fechamento suave de mensagens flash de notificação
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = "opacity 0.4s ease, transform 0.4s ease";
                alert.style.opacity = "0";
                alert.style.transform = "translateY(-6px)";
                setTimeout(() => alert.remove(), 400);
            });
        }, 4500);
    }
});

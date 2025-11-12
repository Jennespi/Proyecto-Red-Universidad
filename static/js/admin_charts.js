document.addEventListener("DOMContentLoaded", () => {
    const ctx = document.getElementById("activityChart");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
            datasets: [{
                label: "Actividad de usuarios",
                data: [12, 19, 15, 22, 30, 25, 18],
                borderWidth: 2,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true }
            }
        }
    });
});

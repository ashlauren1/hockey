document.addEventListener("DOMContentLoaded", function () {
    const headers = document.querySelectorAll("thead th[data-tip]");

    headers.forEach(header => {
        const tooltip = document.createElement("span");
        tooltip.className = "tooltip inactive"; // Add both classes initially
        tooltip.textContent = header.getAttribute("data-tip");
        document.body.appendChild(tooltip);

        // Show tooltip on mouseover
        header.addEventListener("mouseover", () => {
            tooltip.classList.add("active");
            tooltip.classList.remove("inactive");

            const rect = header.getBoundingClientRect();
            tooltip.style.left = rect.left + "px"; // Align with header
            tooltip.style.top = (rect.top + window.scrollY - tooltip.offsetHeight + 6) + "px"; // Above header, add a small gap
        });

        // Hide tooltip on mouseout
        header.addEventListener("mouseout", () => {
            tooltip.classList.remove("active");
            tooltip.classList.add("inactive");
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    var glossaryModal = document.getElementById("glossaryModal");
    var glossaryModalButton = document.getElementById("glossaryButton");
    var glossaryModalContent = document.getElementById("glossary-modal-content");
    var closeGlossaryModal = document.getElementsByClassName("closeGlossary")[0];

    glossaryModalButton.onclick = function() {
        glossaryModal.classList.add("open");
        glossaryModal.style.display = "block";
    }

    closeGlossaryModal.onclick = function() {
        glossaryModal.classList.remove("open");
        glossaryModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === glossaryModal) {
            glossaryModal.style.display = "none";
        }
    }
})
        
document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector(".button-container");

    const glossaryButton = document.createElement("button");
    glossaryButton.id = "glossaryButton";
    glossaryButton.innerText = "Glossary";
    container.appendChild(glossaryButton);

    function setupModal(modalId, buttonId, closeClass) {
        const modal = document.getElementById(modalId);
        const button = document.getElementById(buttonId);
        const closeButton = modal.querySelector(`.${closeClass}`);

        // Toggle modal visibility when button is clicked
        button.onclick = function () {
            const isOpen = modal.classList.contains("open");
            modal.style.display = isOpen ? "none" : "block";
            modal.classList.toggle("open", !isOpen);
        };

        // Close modal when the close button is clicked
        closeButton.onclick = function () {
            modal.style.display = "none";
            modal.classList.remove("open");
        };

        // Close modal when clicking outside the modal content
        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
                modal.classList.remove("open");
            }
        };
    }

    setupModal("glossaryModal", "glossaryButton", "closeGlossary");
});
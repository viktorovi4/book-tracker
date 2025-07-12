console.log("Book Tracker is running!");
document.addEventListener("DOMContentLoaded", function () {
    // Валидация форм
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function (event) {
            let isValid = true;
            const inputs = form.querySelectorAll("input[required], select[required], textarea[required]");
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.style.borderColor = "#f72585";
                    isValid = false;
                } else {
                    input.style.borderColor = "#e2e8f0";
                }
            });

            if (!isValid) {
                event.preventDefault();
                alert("Пожалуйста, заполните все обязательные поля!");
            }
        });
    });

    // Анимация кнопок
    const buttons = document.querySelectorAll(".btn");
    buttons.forEach(button => {
        button.addEventListener("mousedown", function() {
            this.style.transform = "translateY(1px)";
        });
        button.addEventListener("mouseup", function() {
            this.style.transform = "translateY(0)";
        });
        button.addEventListener("mouseleave", function() {
            this.style.transform = "translateY(0)";
        });
    });

    // Подсветка активного поля ввода
    const inputs = document.querySelectorAll("input, textarea, select");
    inputs.forEach(input => {
        input.addEventListener("focus", function() {
            this.parentElement.style.borderLeft = "3px solid #4361ee";
            this.parentElement.style.paddingLeft = "10px";
        });
        input.addEventListener("blur", function() {
            this.parentElement.style.borderLeft = "none";
            this.parentElement.style.paddingLeft = "0";
        });
    });
});
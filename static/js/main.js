console.log("Book Tracker is running!");
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (event) {
            const title = form.title.value.trim();
            const author = form.author.value.trim();
            const genre = form.genre.value.trim();
            const dateRead = form.date_read.value;

            if (!title || !author || !genre || !dateRead) {
                alert("Все поля обязательны для заполнения!");
                event.preventDefault();
            }
        });
    }
});
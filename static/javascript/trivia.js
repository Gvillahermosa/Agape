<script>
    const arrowIcons = document.querySelectorAll(".nav-button");
    const triviaQuestions = document.querySelectorAll(".trivia-question");
    let currentIndex = 0;

    // Function to update the visibility of trivia questions
    function updateTriviaVisibility() {
        triviaQuestions.forEach((question, index) => {
            question.style.display = index === currentIndex ? "block" : "none";
        });
        document.querySelector('.question-number').textContent = `${currentIndex + 1}/${triviaQuestions.length}`;
    }

    // Event listeners for the arrow buttons
    arrowIcons.forEach(icon => {
        icon.addEventListener("click", () => {
            if (icon.querySelector('i').classList.contains('fa-angle-left')) { // Previous button
                currentIndex = Math.max(currentIndex - 1, 0);
            } else { // Next button
                currentIndex = Math.min(currentIndex + 1, triviaQuestions.length - 1);
            }
            updateTriviaVisibility();
        });
    });

    // Initialize display for the first trivia question
    updateTriviaVisibility();
</script>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz information</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <link rel="stylesheet" href="/styles.css">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&display=swap"
        rel="stylesheet">

</head>

<body class="modal-overlay">
    <div id="loader">
        <!-- You can add an image, a CSS spinner, or text here -->
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>
    <div class="quiz-modal-fullpage">
        <div class="quiz-modal">
            <div class="quiz-modal-header">
                <h3>📝 Quiz: {{ $lecture->index }}</h3>
                <button class="close-quiz-modal" onclick="history.back()">×</button>
            </div>
            <div class="quiz-modal-content">
                <div class="quiz-info">
                    <p><strong>Subject:</strong> {{ $course->subject }}</p>
                    <p><strong>Lecture:</strong> {{ $lecture->title }}</p>
                    <p><strong>Questions:</strong> {{ $exam->questions->count() }}</p>
                    <p><strong>Time Limit:</strong> {{ $exam->duration }} m</p>
                    <div class="exam-instructions">
                        <h4 style="margin-bottom:0.5rem; color:#d4af37; font-family:'Cinzel Decorative',serif;">Exam
                            Instructions</h4>
                        <ul style="margin-left:1.2em;">
                            <li>Do not close the browser.</li>
                            <li>Read each question carefully before answering.</li>
                            <li>Once submitted, you cannot retake the exam.</li>
                            <li>Keep track of your time; the exam will auto-submit when time runs out.</li>
                        </ul>
                    </div>
                </div>
                <div class="quiz-actions">

                    <form method="POST"
                        action="/courses/{{ $course->id }}/{{ $lecture->id }}/exams/{{ $exam->id }}/submit">
                        @csrf
                        <button class="start-quiz-btn" type="submit">
                            <span class="quiz-icon">🚀</span>
                            Start Quiz
                        </button>
                    </form>
                    <button class="cancel-quiz-btn" onclick="history.back()">
                        <span class="quiz-icon">❌</span>
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    </div>
</body>
<script src="/script.js"></script>

</html>

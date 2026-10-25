<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Th𝕆th Gate - Quiz</title>
    <link rel="stylesheet" href="/styles.css">
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
</head>

<body class="quiz-page">
    <header class="main-header">
        <div class="header-content">
            <div class="logo-container">
                <img src="/imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <div class="switchers-container">
                <button class="theme-switcher" id="themeSwitcher" title="Toggle Dark Mode">
                    <span class="theme-icon">🌙</span>
                </button>
            </div>
        </div>
    </header>
    <main class="quiz-main">
        @if (session('warning'))
            <div class="message error-general" style="margin: 0px 10px;">
                {{ session('warning') }}
            </div>
        @endif
        <div class="container">
            <h2 class="section-title">Quiz</h2>

            <div class="quiz-timer" id="quizTimer">
                ⏳ Time Left: <span id="timer"
                    data-end="{{ $session->started_at->addMinutes($session->duration + 0.03)->toIso8601String() }}"></span>
            </div>

            <form class="quiz-form" method="POST"
                action="/submit/{{ $exam->id }}/{{ $session->id }}/{{ Auth::user()->student->id }}"
                id = "exam-Form">
                <!-- Multiple Choice Question Example -->
                @csrf
                @foreach ($questions as $question)
                    <div class="quiz-question-box">
                        <h3 class="quiz-question"
                            style="border-bottom: 2px solid #ccc; padding-bottom: 35px; margin-bottom: 15px;">
                            <span style="margin-right: 20px">{{ $loop->iteration }}. </span>
                            @if ($question->text)
                                <span style="display: block">{{ $question->text }}</span>
                            @endif

                            @if ($question->image)
                                <img src="{{ asset('storage/' . $question->image) }}" alt="Question Image"
                                    style="max-width: calc(100% - 50px); max-height: 500px; display: block; margin-top: 10px;">
                            @endif
                        </h3>
                        <div class="quiz-choices">
                            @foreach ($question->choices as $choice)
                                <div class="quiz-answer">
                                    <label style="cursor: pointer;">
                                        <div style="margin-bottom: 15px">
                                            <input type="radio" name="answers[{{ $question->id }}]"
                                                value="{{ $choice->id }}" style="cursor: pointer;">
                                            @if ($choice->text)
                                                {{ $choice->text }}
                                            @endif
                                        </div>
                                        @if ($choice->image)
                                            <img src="{{ asset('storage/' . $choice->image) }}" alt="Choice Image"
                                                style="max-width: calc(100% - 50px); max-height: 500px;">
                                        @endif
                                    </label>
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endforeach
                <button type="submit" class="btn quiz-submit-btn" onclick="examSubmitted = true">Submit
                    Answers</button>
            </form>
        </div>
    </main>
    <script>
        const message = document.querySelector(".message");

        if (message) {
            setTimeout(() => {
                message.classList.add("fade-out");
                message.addEventListener("animationend", () => {
                    message.remove();
                });
            }, 3000);
        }
    </script>
    <script src="/script.js"></script>
</body>

</html>

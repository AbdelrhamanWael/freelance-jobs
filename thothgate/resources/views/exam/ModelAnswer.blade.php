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
    <div id="loader">
        <!-- You can add an image, a CSS spinner, or text here -->
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>
    <header class="main-header">
        <div class="header-content">
            <div class="logo-container">
                <img src="/imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <nav class="main-nav">
                <ul>
                    <li><a href="/student/home">Home</a></li>
                    <li><a href="/courses">Courses</a></li>
                    <li><a href="/community">Chat</a></li>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="/profile">Profile</a></li>
                </ul>
            </nav>
            <div class="switchers-container">
                <button class="theme-switcher" id="themeSwitcher" title="Toggle Dark Mode">
                    <span class="theme-icon">🌙</span>
                </button>
            </div>
        </div>
    </header>
    <main class="quiz-main">
        <div class="container">
            <h2 class="section-title">Quiz Model Answer</h2>
            <div class="quiz-timer">
                Your score: <span>{{ $session->score }}/{{ $questions->count() }}</span>
            </div>
            <div class="quiz-form">
                @foreach ($questions as $question)
                    <div class="quiz-question-box">
                        <h3 class="quiz-question">
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
                                <div class="quiz-answer"
                                    @if ($choice->is_correct) style="background-color: #3E7B27; border-radius: 10px; padding: 10px"
                                @elseif($last_choice->firstWhere('question_id', $question->id)->choice_id === $choice->id)
                                    style="background-color: #E62727; border-radius: 10px; padding: 10px" @endif>
                                    <label style="color: white">
                                        <div style="margin-bottom: 15px">
                                            <input type="radio" @if ($choice->is_correct) checked @endif
                                                disabled>
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
            </div>
        </div>
    </main>
    <footer class="main-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Th𝕆th Gate</h3>
                    <p>Gateway to Ancient Wisdom, Modern Learning</p>
                </div>
                <div class="footer-section">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/student/home">Home</a></li>
                        <li><a href="/courses">Courses</a></li>
                        <li><a href="/community">Chat</a></li>
                        <li><a href="/contact">Contact</a></li>
                        <li><a href="/profile">Profile</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>Contact</h4>
                    <a href="mailto:thothgate@gmail.com" 
                    style="color: #FFFFFF; text-decoration: none;">
                    thothgate@gmail.com
                    </a>
                    <p>Phone: +20 111 686 5363</p>
                    <p>WA Business: +20 100 934 1350</p>
                </div>
                <div class="footer-section">
                    <h4>Follow Us</h4>
                    <div class="social-icons">
                        <a href="https://www.facebook.com/share/19ZWmoHhcz/" class="social-icon facebook"
                            target="_blank"> <i class="fab fa-facebook-f"></i></a>
                        <a href="https://www.instagram.com/gate61407?igsh=bWV3ejJlOGpzZmwy" target="_blank"
                            class="social-icon instagram"> <i class="fab fa-instagram"></i></a>
                        <a href="https://youtube.com/@tonyhany8314?si=W4N9yI_GT4gwW_xs" class="social-icon youtube"
                            target="_blank"><i class="fab fa-youtube"></i></a>
                        <a href="https://www.tiktok.com/@thothgate" class="social-icon tiktok" target="_blank"><i
                                class="fab fa-tiktok"></i></a>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 Th𝕆th Gate Learning Center. All rights reserved.</p>
            </div>
        </div>
    </footer>
    <script src="/script.js"></script>
</body>

</html>

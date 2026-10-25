<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Th𝕆th Gate - Home</title>
    <meta name="student-id" content="{{ auth()->user()->student->id }}">
    @vite(['resources/js/app.js'])
    <link rel="stylesheet" href="/styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
</head>

<body class="home-page">
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

            <!-- Hamburger Menu Button -->
            <button class="hamburger-menu" id="hamburgerMenu">
                <span></span>
                <span></span>
                <span></span>
            </button>

            <nav class="main-nav">
                <ul>
                    <li><a href="/student/home" class="active">Home</a></li>
                    <li><a href="/courses">Courses</a></li>
                    <li><a href="/community">Chat</a></li>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="/profile">Profile</a></li>
                    <li>
                        <form method="POST" action="/logout" id = "logoutForm">
                            @csrf
                            @method('DELETE')
                            <a href="#" class="logout-btn"
                                onclick="document.getElementById('logoutForm').submit(); return false;">Logout</a>
                        </form>
                    </li>
                </ul>
            </nav>

            <div class="switchers-container">
                <button class="theme-switcher" id="themeSwitcher" title="Toggle Dark Mode">
                    <span class="theme-icon">🌙</span>
                </button>
                <button class="language-switcher" id="languageSwitcher" title="Switch Language">
                    <span class="language-text">EN</span>
                </button>
            </div>
            <span class="student-points" title="Your Points">
                Points: <span id="studentPointsValue">{{ Auth::user()->student->points }}</span>
            </span>
        </div>
    </header>

    <!-- Mobile Sidebar -->
    <div class="mobile-sidebar" id="mobileSidebar">
        <div class="sidebar-header">
            <div class="logo-container">
                <img src="/imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <button class="close-sidebar" id="closeSidebar">
                <span></span>
                <span></span>
            </button>
        </div>

        <nav class="sidebar-nav">
            <ul>
                <li><a href="/student/home" class="active">Home</a></li>
                <li><a href="/courses">Courses</a></li>
                <li><a href="/community">Chat</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/profile">Profile</a></li>
                <li>
                    <form method="POST" action="/logout" id = "logoutForm">
                        @csrf
                        @method('DELETE')
                        <a href="#" class="logout-btn"
                            onclick="document.getElementById('logoutForm').submit(); return false;">Logout</a>
                    </form>
                </li>
            </ul>
            <span class="student-points-side" title="Your Points"
                style="  justify-self: center;margin: 50px auto;display: block;">
                Points: <span id="studentPointsValueSide">{{ Auth::user()->student->points }}</span>
            </span>
        </nav>

        <div class="sidebar-switchers">
            <button class="theme-switcher" id="sidebarThemeSwitcher" title="Toggle Dark Mode">
                <span class="theme-icon">🌙</span>
            </button>
            <button class="language-switcher" id="sidebarLanguageSwitcher" title="Switch Language">
                <span class="language-text">EN</span>
            </button>
        </div>
    </div>

    <!-- Sidebar Overlay -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>

    <main>
        @if (session('error'))
            <div class="message error-general" style="margin: 0px 10px;">
                {{ session('error') }}
            </div>
        @endif
        <section class="hero-section">
            <div class="hero-content">
                <h2 class="hero-title">Unlock Your Potential</h2>
                <p class="hero-subtitle">Discover the ancient wisdom of learning through modern educational excellence
                </p>
                <div class="hero-buttons">
                    <a href="/courses" class="btn primary">Explore Courses</a>
                    <a href="/community" class="btn secondary">Join Grade Chat</a>
                </div>
            </div>
            <div class="hero-decoration">
                <div class="ancient-symbol"></div>
                <div class="egyptian-patterns">
                    <div class="pattern-1"></div>
                    <div class="pattern-2"></div>
                    <div class="pattern-3"></div>
                </div>
            </div>
        </section>

        <section class="egyptian-wisdom-section">
            <div class="container">
                <h2 class="section-title">Ancient Wisdom</h2>
                <div class="wisdom-content">
                    <div class="wisdom-text">
                        <p>"The beginning of wisdom is to call things by their proper names."</p>
                        <p class="wisdom-author">- Ancient Egyptian Proverb</p>
                    </div>
                    <div class="wisdom-image">
                        <img src="/imgs/1.jpg" alt="Ancient Egyptian Wisdom" class="egyptian-image">
                    </div>
                </div>
            </div>
        </section>

        <section class="plans-section" id="chooseYourPlan">
            <div class="container">
                <h2 class="section-title">Choose Your Plan</h2>
                <div class="plans-grid">
                    <!-- Plan 1: Buy One Lecture -->
                    <div class="plan-card">
                        <h3>Buy One Lecture</h3>
                        <p class="plan-price">EGP 30</p>
                        <ul class="plan-details">
                            <li>Access to a single lecture of your choice</li>
                            <li>General chat unlocked for <strong>1 week</strong></li>
                            <li>Perfect for quick help or trial</li>
                        </ul>
                        <a href="{{ route('courses') }}">
                            <button class="btn plan-btn">Buy Now</button>
                        </a>
                    </div>
                    <!-- Plan 2: Buy 4 Lectures (Specific Course) -->
                    <div class="plan-card">
                        <h3>Buy 4 Lectures<br><span class="plan-sub">(Specific Course)</span></h3>
                        <p class="plan-price">EGP 100</p>
                        <ul class="plan-details">
                            <li>Access to 4 lectures in a single course</li>
                            <li>General chat unlocked for <strong>4 weeks</strong></li>
                            <li>Ideal for focused learning</li>
                        </ul>

                        <a href="https://wa.me/201116865363" target="_blank">
                            <button class="btn plan-btn">Contact Us to Buy</button>
                        </a>
                    </div>
                </div>
            </div>
        </section>
    </main>
    <section class="egyptian-wisdom-section about-section">
        <div class="container">
            <h2 class="section-title">About Us</h2>
            <div class="wisdom-content">
                <div class="wisdom-text">
                    <p class="hero-subtitle">
                        Th𝕆th Gate blends the legacy of ancient Egyptian scholarship with modern pedagogical practice —
                        delivering rigorous courses, expert mentorship, and a nurturing learning environment for the
                        students of today.
                    </p>
                    <p class="wisdom-author">Our mission: preserve wisdom — inspire learning.</p>
                </div>
                <div class="wisdom-image">
                    <img src="/imgs/1.jpg" alt="About Th𝕆th Gate" class="egyptian-image">
                </div>
            </div>
        </div>
    </section>
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
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const studentId = {{ auth()->user()->student->id }};

            window.Echo.private(`student.notification.${studentId}`)
                .listen('.student.notification', (e) => {
                    let toast = document.getElementById("toast");
                    toast.textContent = `📢 ${e.message}`;
                    toast.classList.add("show");

                    setTimeout(() => {
                        toast.classList.remove("show");
                    }, 3000);
                });
        });
    </script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const studentId = {{ auth()->user()->student->id }};
            const pointsValueElement = document.getElementById("studentPointsValue");
            const pointsValueElementSide = document.getElementById("studentPointsValueSide");

            window.Echo.private(`AddPoints.${studentId}`)
                .listen('.points.added', (e) => {
                    if (pointsValueElement) {
                        let currentPoints = parseInt(pointsValueElement.textContent) || 0;
                        pointsValueElement.textContent = currentPoints + parseInt(e.points);
                    }

                    if (pointsValueElementSide) {
                        let currentPointsSide = parseInt(pointsValueElementSide.textContent) || 0;
                        pointsValueElementSide.textContent = currentPointsSide + parseInt(e.points);
                    }
                });
        });
    </script>
    <div id="toast" class="toast"></div>
    <script src="/script.js"></script>
</body>

</html>

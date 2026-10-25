<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home</title>
    <link rel="stylesheet" href="/styles.css">
    <link rel="stylesheet" href="/instructor.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">

    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">

</head>

<body class="instructor-home">
    <div id="loader">
        <!-- You can add an image, a CSS spinner, or text here -->
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>
    <header class="main-header">
        <div class="header-content">
            <div class="logo-container">
                <img src="../imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <button class="hamburger-menu" id="hamburgerMenu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            <nav class="main-nav">
                <ul>
                    <li><a href="/instructor/home" class="active">Home</a></li>
                    <li><a href="/instructor/create/exam">Create Exam</a></li>
                    <li><a href="/instructor/add/lecture">Add Lecture</a></li>
                    <li><a href="/instructor/chats">Chats</a></li>
                    <li><a href="/instructor/students">Students</a></li>
                    <li>
                        <form method="POST" action="/logout" id="logoutForm">
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
        </div>
    </header>
    <!-- Mobile Sidebar for instructor -->
    <div class="mobile-sidebar" id="mobileSidebar">
        <div class="sidebar-header">
            <div class="logo-container">
                <img src="../imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <button class="close-sidebar" id="closeSidebar">
                <span></span>
                <span></span>
            </button>
        </div>
        <nav class="sidebar-nav">
            <ul>
                <li><a href="/instructor/home" class="active">Home</a></li>
                <li><a href="/instructor/create/exam">Create Exam</a></li>
                <li><a href="/instructor/add/lecture">Add Lecture</a></li>
                <li><a href="/instructor/chats">Chats</a></li>
                <li><a href="/instructor/students">Students</a></li>
                <li>
                    <form method="POST" action="/logout" id="logoutForm">
                        @csrf
                        @method('DELETE')
                        <a href="#" class="logout-btn"
                            onclick="document.getElementById('logoutForm').submit(); return false;">Logout</a>
                    </form>
                </li>
            </ul>
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


    <main class="container">
        <h1 class="section-title" style="    margin: revert;">Welcome, Instructor!</h1>
        <p style="text-align:center;">Manage your lectures, exams, and student chats from your dashboard.</p>
        <div class="inst-grid">
            <div class="inst-card" onclick="window.location.href='/instructor/add/lecture'">
                <img src="../imgs/language.jpg" alt="Add Lecture"
                    style="width:60px;height:60px;border-radius:50%;margin-bottom:1rem;object-fit:cover;">
                <h3>Add Lecture</h3>
                <p>Create and share new lectures with your students.</p>
            </div>
            <div class="inst-card" onclick="window.location.href='/instructor/create/exam'">
                <img src="../imgs/history.jpg" alt="Create Exam"
                    style="width:60px;height:60px;border-radius:50%;margin-bottom:1rem;object-fit:cover;">
                <h3>Create Exam</h3>
                <p>Design exams and assign them to grades.</p>
            </div>
            <div class="inst-card" onclick="window.location.href='/instructor/chats'">
                <img src="../imgs/profile.png" alt="Chats"
                    style="width:60px;height:60px;border-radius:50%;margin-bottom:1rem;object-fit:cover;">
                <h3>Chats</h3>
                <p>Access and communicate with students by grade.</p>
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
                        <li><a href="/instructor/home">Home</a></li>
                        <li><a href="/instructor/add/lecture">Add Lecture</a></li>
                        <li><a href="/instructor/create/exam">Create Exam</a></li>
                        <li><a href="/instructor/chats">Chats</a></li>
                        <li><a href="/instructor/students">Students</a></li>
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
    <script src="/instructor.js"></script>
</body>

</html>

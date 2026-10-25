<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chats</title>
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
                    <li><a href="/instructor/home">Home</a></li>
                    <li><a href="/instructor/create/exam">Create Exam</a></li>
                    <li><a href="/instructor/add/lecture">Add Lecture</a></li>
                    <li><a href="/instructor/chats" class="active">Chats</a></li>
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
                <li><a href="/instructor/home">Home</a></li>
                <li><a href="/instructor/create/exam">Create Exam</a></li>
                <li><a href="/instructor/add/lecture">Add Lecture</a></li>
                <li><a href="/instructor/chats" class="active">Chats</a></li>
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
    <main class="container" style="margin: 60px auto;">
        <h2 class="section-title">Chats by Grade</h2>
        <section class="egyptian-wisdom-section-lectures" style="padding: 2rem 0;">
            <div class="container">
                <div class="lectures-grid"
                    style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 340px)); gap: 2rem; justify-content: center;">

                    @foreach ($communities as $com)
                        <div class="course-card lecture-card"
                            onclick="window.location.href='/instructor/chats/{{ $com->id }}'"
                            style="cursor:pointer;">
                            <div class="course-content">
                                <h3 class="lecture-title">{{ $com->grade }}</h3>
                                <p class="lecture-description">Chat with {{ $com->grade }} students</p>
                            </div>
                        </div>
                    @endforeach
                </div>
            </div>
        </section>
    </main>
    <script src="/script.js"></script>
    <script src="/instructor.js"></script>
</body>

</html>

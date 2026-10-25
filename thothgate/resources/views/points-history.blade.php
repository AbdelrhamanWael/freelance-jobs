<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Points History - Th𝕆th Gate</title>
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
    <link rel="stylesheet" href="/styles.css">
    <meta name="student-id" content="{{ auth()->user()->student->id }}">

    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    @vite(['resources/js/app.js'])
</head>

<body class="profile-page-points">
    <div id="loader">
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
                    <li><a href="/student/home">Home</a></li>
                    <li><a href="/courses">Courses</a></li>
                    <li><a href="/community">Chat</a></li>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="/profile" class="active">Profile</a></li>
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
                Points: <span id="studentPointsValue">{{ $student->points }}</span>
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
                <li><a href="/student/home">Home</a></li>
                <li><a href="/courses">Courses</a></li>
                <li><a href="/community">Chat</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/profile" class="active">Profile</a></li>
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
                Points: <span id="studentPointsValueSide">{{ $student->points }}</span>
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

    <main class="profile-main-points">
        <div class="container">
            <div class="profile-header">
                <h2 class="section-title">Points History</h2>
                <div class="profile-btns" style="display: flex; flex-direction:row; gap:1rem; justify-content: center;">
                    <a href="/profile" class="btn primary">Back to Profile</a>
                </div>
            </div>
            <div class="profile-content">
                <div class="academic-stats-section">
                    <div id="pointsHistoryList">
                        @foreach ($pointsHistory as $point)
                            <div class="stat-card" style="margin-bottom:1rem;">
                                <div class="stat-number">+{{ $point->points }} pts</div>
                                <div class="stat-label">{{ $point->reason }}</div>
                                <div style="font-size:0.85rem;color:#aaa;">{{ $point->created_at }}</div>
                            </div>
                        @endforeach
                    </div>
                </div>
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
                <p>&copy; 2024 Th𝕆th Gate Learning Center. All rights reserved.</p>
            </div>
        </div>
    </footer>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const studentId = {{ auth()->user()->student->id }};
            const pointsValueElement = document.getElementById("studentPointsValue");
            const pointsHistoryList = document.getElementById("pointsHistoryList");
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

                    const statCard = document.createElement("div");
                    statCard.classList.add("stat-card");
                    statCard.style.marginBottom = "1rem";

                    const statNumber = document.createElement("div");
                    statNumber.classList.add("stat-number");
                    statNumber.textContent = `+${e.points} pts`;

                    const statLabel = document.createElement("div");
                    statLabel.classList.add("stat-label");
                    statLabel.textContent = e.reason;

                    const statDate = document.createElement("div");
                    statDate.style.fontSize = "0.85rem";
                    statDate.style.color = "#aaa";
                    statDate.textContent = new Date().toLocaleString();

                    statCard.appendChild(statNumber);
                    statCard.appendChild(statLabel);
                    statCard.appendChild(statDate);

                    pointsHistoryList.prepend(statCard);
                });
        });
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
    <div id="toast" class="toast"></div>

    <script src="/script.js"></script>
</body>

</html>

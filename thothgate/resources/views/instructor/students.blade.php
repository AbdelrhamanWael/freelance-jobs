<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Students</title>
    <link rel="stylesheet" href="/styles.css">
    <link rel="stylesheet" href="/instructor.css">
    <link rel="stylesheet" href="/instructor-students-styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
</head>

<body class="instructor-home">
    <header class="main-header">
        <div class="header-content">
            <div class="logo-container">
                <img src="/imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
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
                    <li><a href="/instructor/chats">Chats</a></li>
                    <li><a href="/instructor/students" class="active">Students</a></li>
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
                <li><a href="/instructor/chats">Chats</a></li>
                <li><a href="/instructor/students" class="active">Students</a></li>
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
        <div class="sidebar-switchers">
            <button class="theme-switcher" id="sidebarThemeSwitcher" title="Toggle Dark Mode">
                <span class="theme-icon">🌙</span>
            </button>
            <button class="language-switcher" id="sidebarLanguageSwitcher" title="Switch Language">
                <span class="language-text">EN</span>
            </button>
        </div>
    </div>
    <div class="sidebar-overlay" id="sidebarOverlay"></div>

    <main class="container" style="margin-bottom: 3rem;">
        <h1 class="section-title" style="margin: revert;">Manage Student Points</h1>
        <p style="text-align:center; margin-bottom: 2rem;">Search and manage points for your students</p>

        <!-- Search and Filter Section -->
        <div class="search-section"
            style="border-radius: 15px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);">
            <div class="search-container">
                <div class="search-input-group" style="flex: 1; min-width: 200px;">
                    <input type="text" id="studentSearch" placeholder="Search students by name or ID...">
                </div>
                <div class="filter-group">
                    <select id="gradeFilter"
                        style="padding: 12px 15px; border: 2px solid #d4af37; border-radius: 8px; font-size: 1rem; min-width: 120px;">

                        @foreach ($grades as $grade)
                            <option value="{{ $grade }}">{{ $grade }}</option>
                        @endforeach
                    </select>
                </div>
                <button id="searchBtn" class="exam-btn" style="padding: 12px 24px;">Search</button>
            </div>
        </div>

        <div class="students-grid" id="studentsGrid">
            <!-- Static Student Cards -->

            @foreach ($students as $student)
                <div class="course-card" data-student-id="{{ $student->id }}"
                    data-student-name="{{ $student->user->name }}" data-grade="{{ $student->grade }}">
                    <div class="course-content">
                        <img src="/imgs/profile.png" alt="{{ $student->user->name }}">
                        <h3>{{ $student->user->name }}</h3>
                        <p>ID: {{ $student->id }}</p>
                        <p>{{ $student->grade }}</p>
                        <div>Points: {{ $student->points }}</div>
                        <br>
                        <a href="/instructor/add/points/{{ $student->id }}" class="exam-btn">Add Points</a>
                    </div>
                </div>
            @endforeach
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
    <script>
        window.addEventListener('DOMContentLoaded', () => {
            filterStudents();
        });
    </script>
    <script>
        function filterStudents() {
            const searchTerm = document.getElementById('studentSearch').value.toLowerCase();
            const gradeFilter = document.getElementById('gradeFilter').value;
            const studentCards = document.querySelectorAll('.course-card');

            studentCards.forEach(card => {
                const studentName = card.getAttribute('data-student-name').toLowerCase();
                const studentId = card.getAttribute('data-student-id');
                const studentGrade = card.getAttribute('data-grade');

                const matchesSearch = studentName.includes(searchTerm) || studentId.includes(searchTerm);
                const matchesGrade = !gradeFilter || studentGrade === gradeFilter;

                if (matchesSearch && matchesGrade) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        document.getElementById('searchBtn').addEventListener('click', filterStudents);
        document.getElementById('studentSearch').addEventListener('input', filterStudents);
        document.getElementById('gradeFilter').addEventListener('change', filterStudents);
    </script>
</body>

</html>

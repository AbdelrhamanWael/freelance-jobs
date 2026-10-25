<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="student-id" content="{{ auth()->user()->student->id }}">
    @vite(['resources/js/app.js'])
    <title>Th𝕆th Gate - Course Detail</title>
    <link rel="stylesheet" href="/styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
</head>

<body class="course-detail-page">
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
                    <li><a href="/student/home">Home</a></li>
                    <li><a href="/courses" class="active">Courses</a></li>
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
                <li><a href="/student/home">Home</a></li>
                <li><a href="/courses" class="active">Courses</a></li>
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
    <div class="sidebar-overlay"></div>

    <main class="course-main">
        <div class="course-container">
            <!-- Course Header -->
            <div class="course-header">
                <div class="course-info">
                    <img src="/{{ $course->image }}" alt="Course Image" class="course-banner">
                    <div class="course-details">
                        <h1>{{ $course->subject }}</h1>
                        <div class="course-meta">
                            <span class="course-span" style="display: flex;">
                                <p style="font-weight: 600; font-size: 1rem; margin-bottom: auto;">
                                    Lecture
                                </p>
                                &nbsp;
                                {{ $currentLecture->index }}
                            </span>
                            <span class="course-span" style="display: flex;">
                                <p style="font-weight: 600; font-size: 1rem; margin-bottom: auto; color:#f5deb3">
                                    Teacher
                                </p>
                                &nbsp;
                                <p style="font-weight: 600; font-size: 1rem; margin-bottom: auto;">
                                    {{ $course->teacher }}
                                </p>
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="course-content-wrapper">
                <!-- Lectures Sidebar -->
                <aside class="lectures-sidebar">
                    <div class="sidebar-header">
                        <h3>Course Lectures</h3>
                        <button class="toggle-sidebar">
                            <span></span>
                            <span></span>
                            <span></span>
                        </button>
                    </div>

                    <div class="lectures-list">
                        @foreach ($lectures as $lecture)
                            <a href="/lectures/{{ $course->id }}/{{ $lecture->id }}"
                                style="text-decoration: none;">
                                <div class="lecture-item {{ $lecture->id == $currentLecture->id ? 'active' : '' }}">
                                    <div class="lecture-thumbnail">
                                        <img src="/{{ $course->image }}" alt="{{ $lecture->title }}">
                                    </div>
                                    <div class="lecture-info">
                                        <div style="display: flex;">
                                            <h3 class="lecture-title">Lecture</h3>
                                            <h3 class = "lecture-title">&nbsp;{{ $lecture->index }} :</h3>
                                        </div>
                                        <h4 class="lecture-title">{{ $lecture->title }}</h4>
                                        <p class="lecture-description">{{ $lecture->description }}</p>
                                    </div>
                                </div>
                            </a>
                        @endforeach
                    </div>
                </aside>

                <!-- Main Video Area -->
                <div class="video-main-area">
                    <div class="video-container">
                        @if ($currentLecture->processing_status === 'processing')
                            <div class="processing-alert" style="padding: 60px; background: #1a1a1a; color: #f5deb3; text-align: center; border-radius: 8px; border: 1px solid #d4af37;">
                                <i class="fas fa-cog fa-spin" style="font-size: 3em; margin-bottom: 20px;"></i>
                                <h3>Video is Processing</h3>
                                <p>This lecture is currently being rendered into multiple qualities. It will be available shortly.</p>
                                <button onclick="window.location.reload()" style="margin-top:20px; padding: 10px 20px; background:#d4af37; color:#000; font-weight:bold; border:none; cursor:pointer; border-radius: 4px;">Refresh Page</button>
                            </div>
                        @else
                            <video id="lectureVideo" controls oncontextmenu="return false;" controlsList="nodownload" disablePictureInPicture style="width: 100%; border-radius: 8px;">
                                <source src="{{ asset($currentLecture->video) }}" type="{{ str_ends_with($currentLecture->video, '.m3u8') ? 'application/x-mpegURL' : 'video/mp4' }}">
                            </video>
                        @endif
                        <div class="video-info">
                            <h2>{{ $currentLecture->title }}</h2>
                            <p>{{ $currentLecture->description }}</p>
                            @if ($session)
                                <button class="quiz-btn"
                                    onclick="window.location.href='{{ route('exam.info', $session->id) }}'">
                                    <span class="quiz-icon">📝</span>
                                    Show Score
                                </button>
                            @else
                                <button class="quiz-btn"
                                    onclick="window.location.href='{{ route('exam.prepareExam', [$course->id, $currentLecture->id]) }}'">
                                    <span class="quiz-icon">📝</span>
                                    Take Quiz
                                </button>
                            @endif
                        </div>
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
                <p>&copy; 2025 Th𝕆th Gate Learning Center. All rights reserved.</p>
            </div>
        </div>
    </footer>
    <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@1"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const video = document.getElementById('lectureVideo');
            if (!video) return;

            const source = "{{ asset($currentLecture->video) }}";
            
            // Initialize Plyr with quality options
            const defaultOptions = {
                controls: ['play-large', 'play', 'progress', 'current-time', 'mute', 'volume', 'captions', 'settings', 'pip', 'airplay', 'fullscreen'],
                settings: ['captions', 'quality', 'speed']
            };

            if (Hls.isSupported() && source.endsWith('.m3u8')) {
                const hls = new Hls();
                hls.loadSource(source);

                hls.attachMedia(video);
                window.hls = hls;
                
                hls.on(Hls.Events.MANIFEST_PARSED, function (event, data) {
                    const availableQualities = hls.levels.map((l) => l.height);
                    defaultOptions.quality = {
                        default: availableQualities[0],
                        options: availableQualities,
                        forced: true,
                        onChange: (e) => updateQuality(e),
                    };
                    const player = new Plyr(video, defaultOptions);
                });

                function updateQuality(newQuality) {
                    window.hls.levels.forEach((level, levelIndex) => {
                        if (level.height === newQuality) {
                            window.hls.currentLevel = levelIndex;
                        }
                    });
                }
            } else {
                const player = new Plyr(video, defaultOptions);
            }
        });

        document.addEventListener('keydown', function(event) {
            const video = document.getElementById('lectureVideo');
            if(!video) return;
            if (event.code === 'ArrowRight') {
                video.currentTime += 5;
            } else if (event.code === 'ArrowLeft') {
                video.currentTime -= 5;
            }
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
    <script src="/script.js"></script>
</body>

</html>

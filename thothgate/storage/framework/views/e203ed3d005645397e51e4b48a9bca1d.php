<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="student-id" content="<?php echo e(auth()->user()->student->id); ?>">
    <?php echo app('Illuminate\Foundation\Vite')(['resources/js/app.js']); ?>
    <title>Th𝕆th Gate - Courses</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
</head>

<body class="courses-page">
    <div id="loader">
        <!-- You can add an image, a CSS spinner, or text here -->
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>
    <header class="main-header">
        <div class="header-content">
            <div class="logo-container">
                <img src="imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
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
                            <?php echo csrf_field(); ?>
                            <?php echo method_field('DELETE'); ?>
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
                Points: <span id="studentPointsValue"><?php echo e(Auth::user()->student->points); ?></span>
            </span>
        </div>
    </header>

    <!-- Mobile Sidebar -->
    <div class="mobile-sidebar" id="mobileSidebar">
        <div class="sidebar-header">
            <div class="logo-container">
                <img src="imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
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
                        <?php echo csrf_field(); ?>
                        <?php echo method_field('DELETE'); ?>
                        <a href="#" class="logout-btn"
                            onclick="document.getElementById('logoutForm').submit(); return false;">Logout</a>
                    </form>
                </li>
            </ul>
            <span class="student-points-side" title="Your Points"
                style="  justify-self: center;margin: 50px auto;display: block;">
                Points: <span id="studentPointsValueSide"><?php echo e(Auth::user()->student->points); ?></span>
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
        <?php if(session('error')): ?>
            <div class="message error-general" style="margin: 0px 10px;">
                <?php echo e(session('error')); ?>

            </div>
        <?php endif; ?>
        <section class="courses-section">
            <div class="container">
                <h2 class="section-title">Subjects</h2>
                <div class="courses-grid"
                    style="display: grid;grid-template-columns: repeat(auto-fit, minmax(320px, 340px)); gap: 2rem; justify-content: center;">
                    <?php $__currentLoopData = $courses; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $course): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                        <?php if($course->lectures()->count() > 0): ?>
                            <div class="course-card" data-course-id="mathematics">
                                <div class="course-image">
                                    <img src="<?php echo e($course->image); ?>" alt="<?php echo e($course->subject); ?>">
                                </div>
                                <div class="course-content">
                                    <div class="course-header">
                                        <h3><?php echo e($course->subject); ?></h3>
                                    </div>
                                    <div class="course-meta">
                                        <span class="instructor"><?php echo e($course->teacher); ?></span>
                                    </div>
                                    <a href="/courses/<?php echo e($course->id); ?>" class="course-btn">Enter</a>
                                </div>
                            </div>
                        <?php endif; ?>
                    <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                </div>
            </div>
        </section>
    </main>

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
            const studentId = <?php echo e(auth()->user()->student->id); ?>;

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
            const studentId = <?php echo e(auth()->user()->student->id); ?>;
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
    <script src="script.js"></script>
</body>

</html>
<?php /**PATH /var/www/html/resources/views/Courses/courses.blade.php ENDPATH**/ ?>
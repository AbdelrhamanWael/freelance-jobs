<?php
    use App\Models\Student;
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="student-id" content="<?php echo e(auth()->user()->student->id); ?>">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <?php echo app('Illuminate\Foundation\Vite')(['resources/js/app.js']); ?>
    <title>Th𝕆th Gate - Profile</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
</head>

<body class="profile-page">
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
                    <li><a href="/courses">Courses</a></li>
                    <li><a href="/community">Chat</a></li>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="/profile" class="active">Profile</a></li>
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
                <li><a href="/courses">Courses</a></li>
                <li><a href="/community">Chat</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/profile" class="active">Profile</a></li>
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

    <main class="profile-main">
        <div class="container">
            <div class="profile-header">
                <h2 class="section-title">Student Profile</h2>
                <form action="/profile/delete/<?php echo e(Auth::user()->student->id); ?>" method="POST"
                    onsubmit="return confirm('Are you sure you want to delete your profile?');">
                    <?php echo csrf_field(); ?>
                    <?php echo method_field('DELETE'); ?>
                    <button type = "submit" class="delete-profile-btn">Delete Profile</button>
                </form>
            </div>

            <div class="profile-content">
                <div class="profile-info-section">
                    <div class="profile-card">
                        <div class="profile-image-container">
                            <img src="imgs/profile.png" alt="Student Profile" id="profileImage"
                                class="profile-image">
                            <div class="image-upload" id="imageUpload" style="display: none;">
                                <input type="file" id="imageInput" accept="image/*">
                                <label for="imageInput" class="upload-label">Change Photo</label>
                            </div>
                        </div>

                        <div class="profile-details">
                            <div class="detail-group">
                                <label>Full Name:</label>
                                <span id="studentName"><?php echo e(Auth::user()->name); ?></span>
                                <input type="text" id="nameInput" value="<?php echo e(Auth::user()->name); ?>"
                                    class="edit-input" style="display: none;">
                            </div>

                            <div class="detail-group">
                                <label>Email:</label>
                                <span id="studentEmail"><?php echo e(Auth::user()->email); ?></span>
                                <input type="email" id="emailInput" value="<?php echo e(Auth::user()->email); ?>"
                                    class="edit-input" style="display: none;">
                            </div>

                            <div class="detail-group">
                                <label>Grade Level:</label>
                                <span><?php echo e(Auth::user()->student->grade); ?></span>
                            </div>

                            <div class="detail-group">
                                <label>Student ID:</label>
                                <span><?php echo e(Auth::user()->student->id); ?></span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="enrolled-courses-section">
                    <h3 class="subsection-title">Enrolled Courses</h3>
                    <div class="enrolled-courses-grid">
                        <?php $__currentLoopData = $finished; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $course): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                            <?php if($course['total'] != 0): ?>
                                <div class="enrolled-course-card">
                                    <div class="course-progress">
                                        <div class="progress-bar">
                                            <?php
                                                $percentage =
                                                    $course['total'] > 0
                                                        ? ($course['finished'] / $course['total']) * 100
                                                        : 0;
                                            ?>
                                            <div class="progress-fill" style="width: <?php echo e($percentage); ?>%;"></div>
                                        </div>
                                        <span class="progress-text"><?php echo e(round($percentage)); ?>% Complete</span>
                                    </div>

                                    <h4><?php echo e($course['subject']); ?></h4>
                                    <span style="display: flex;">
                                        <p>Teacher</p>
                                        :&nbsp;
                                        <p><?php echo e($course['teacher']); ?></p>
                                    </span>

                                    <?php if($course['finished'] == $course['total']): ?>
                                        <p class="course-status completed">Completed</p>
                                    <?php else: ?>
                                        <p class="course-status">In Progress</p>
                                    <?php endif; ?>
                                </div>
                            <?php endif; ?>
                        <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                    </div>
                </div>

                <div class="academic-stats-section">
                    <h3 class="subsection-title">Academic Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number"><?php echo e(Student::getLevel(Auth::user()->student->points)); ?>

                            </div>
                            <div class="stat-label">Level</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="studentPointsValue1"><?php echo e(Auth::user()->student->points); ?>

                            </div>
                            <div class="stat-label">Points</div>
                        </div>
                    </div>
                    <div class="profile-btns">
                        <a href="<?php echo e(route('student.levels')); ?>" class="btn primary"
                            style="margin-top: 2rem; text-align: center;display: flex;justify-content: center;align-self: center;justify-self: center;">
                            View all Levels
                        </a>
                        <a href="<?php echo e(route('student.pointsHistory')); ?>" class="btn primary"
                            style="margin-top: 2rem; text-align: center;display: flex;justify-content: center;align-self: center;justify-self: center;">View Points History</a>
                    </div>
                </div>
            </div>
            <div class="lectures-left" style="padding-top: 30px;">
                <h3 class="subsection-title">Lectures Left in Your Plan</h3>
                <div class="contain">
                    <?php $__currentLoopData = $packages; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $package): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                        <?php
                            $circumference = 2 * pi() * 56;
                            $progress = ($package->remaining / $package->total) * $circumference;
                        ?>
                        <div class="lectures-left-section profile-section">
                            <h4 class="title"><?php echo e($package->course->subject); ?></h4>
                            <div class="circle-progress-container">
                                <svg class="circle-progress" width="140" height="140">
                                    <circle class="circle-bg" cx="70" cy="70" r="56"></circle>
                                    <circle class="circle-bar" cx="70" cy="70" r="56"
                                        style="stroke-dasharray: <?php echo e($circumference); ?>;stroke-dashoffset: <?php echo e($circumference - $progress); ?>;">
                                    </circle>
                                </svg>
                                <div class="circle-progress-text">
                                    <?php echo e($package->remaining); ?>/<?php echo e($package->total); ?>

                                </div>
                            </div>
                            <span class="lectures-left-label"><?php echo e($package->remaining); ?> lectures left to be
                                uploaded</span>
                        </div>
                    <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
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
    <div id="toast" class="toast"></div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const studentId = <?php echo e(auth()->user()->student->id); ?>;
            const pointsValueElement = document.getElementById("studentPointsValue");
            const pointsValueElement1 = document.getElementById("studentPointsValue1");
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

                    if (pointsValueElement1) {
                        let points = parseInt(pointsValueElement1.textContent) || 0;
                        pointsValueElement1.textContent = points + parseInt(e.points);
                    }
                });
        });
    </script>
    <script src="script.js"></script>
</body>

</html>
<?php /**PATH /var/www/html/resources/views/profile.blade.php ENDPATH**/ ?>
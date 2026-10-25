<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Admin Dashboard - Home</title>
    <link rel="icon" href="../imgs/logo.png" type="image/x-icon" />
    <link rel="stylesheet" href="../styles.css" />
    <link rel="stylesheet" href="../admin-styles.css" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet" />
    @vite(['resources/js/app.js'])
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>

<body>
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
                    <li><a href="/admin/home" class="active">Dashboard</a></li>
                    <li><a href="/admin/instructors">Instructors</a></li>
                    <li><a href="/admin/students">Students</a></li>
                    <li><a href="/admin/messages">Messages</a></li>
                    <li><a href="/admin/notifications" id="notifLink">
                            @if (App\Models\AdminNotification::where('is_read', false)->count() > 0)
                                <span class="notif-dot" id = "notif-dot">🔴</span>
                            @endif
                            Notifications
                        </a></li>
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
                <li><a href="/admin/home" class="active">Home</a></li>
                <li><a href="/admin/instructors">Instructors</a></li>
                <li><a href="/admin/students">Students</a></li>
                <li><a href="/admin/messages">Messages</a></li>
                <li>
                    <a href="/admin/notifications" id="notifLink">
                        @if (App\Models\AdminNotification::where('is_read', false)->count() > 0)
                            <span class="notif-dot" id = "notif-dot">🔴</span>
                        @endif
                        Notifications
                    </a>
                </li>
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

    <div class="admin-layout">
        @if (session('error'))
            <div class="message error-general">
                {{ session('error') }}
            </div>
        @endif

        @if (session('success'))
            <div class="message success-general">
                {{ session('success') }}
            </div>
        @endif

        <main class="admin-main-content">
            <!-- Section Title -->
            <h2 class="section-title">Dashboard</h2>
            <div style="display: flex;justify-content: flex-end; margin-bottom: 12px;">
                <a href="{{ route('editAdminPassword') }}">
                    <button class="btn">Edit Admin Password</button>
                </a>
            </div>

            <!-- Top Stats Cards -->
            <div class="dashboard-stats-cards">
                <div class="stats-card">
                    <h3 class="stats-title">Total Courses</h3>
                    <p class="stats-value">{{ $totalCourses }}</p>
                    <button class = "btn" onclick="location.href = '/admin/courses';">Edit Courses</button>
                </div>
                <div class="stats-card">
                    <h3 class="stats-title">Total Instructors</h3>
                    <p class="stats-value">{{ $totalInstructors }}</p>
                </div>
                <div class="stats-card">
                    <h3 class="stats-title">Total Students</h3>
                    <p class="stats-value">{{ $totalStudents }}</p>
                </div>
                <div class="stats-card">
                    <h3 class="stats-title">Total Purchased Lectures</h3>
                    <p class="stats-value">{{ $totalPurchased }}</p>
                </div>
            </div>


            <!-- Bottom Section: Lists -->
            <section class="dashboard-stats-cards">

                <div class="widget stats-card">
                    <h3 class="stats-title">Notifications</h3>
                    <ul id = "notificationsList">
                        @if ($notifications->isEmpty())
                            <li>
                                <strong>there is no notifications at this moment</strong>
                            </li>
                        @endif
                        @foreach ($notifications as $notification)
                            <li class="{{ $notification->is_read ? '' : 'unread-notification' }}"
                                style="padding: 10px;">
                                <strong>📢&ensp;{{ $notification->title }}</strong><br>
                            </li>
                        @endforeach
                    </ul>
                </div>
                <div class="widget stats-card">
                    <h3 class="stats-title">Top Courses</h3>
                    <ol>
                        @foreach ($topCourses as $course)
                            <li>{{ $course }}</li>
                        @endforeach
                    </ol>
                </div>

                <div class="stats-card export-data">
                    <h3 class="stats-title">Export Data</h3>
                    <div class="export-grid">
                        <a href="{{ route('students.export') }} ">
                            <button class="export-btn">⬇ Students</button>
                        </a>
                        <a href="{{ route('instructors.export') }}">
                            <button class="export-btn">⬇ Instructors</button>
                        </a>
                    </div>
                </div>
            </section>


            <section class="dashboard-widgets-quick">
                <!-- Quick Actions -->
                <div class="stats-card quick-actions" style="
    width: fit-content;
">
                    <h3 class="stats-title">Quick Actions</h3>
                    <div class="actions-grid">
                        <a href="/admin/instructors/create" style="text-decoration: none;">
                            <div class="action-tile">
                                <span class="icon">👨‍🏫</span>
                                <p>Add Instructor</p>
                            </div>
                        </a>
                        <a href="/admin/students" style="text-decoration: none;">
                            <div class="action-tile">
                                <span class="icon">🎓</span>
                                <p>View Students</p>
                            </div>
                        </a>
                        <a href="/admin/messages" style="text-decoration: none;">
                            <div class="action-tile">
                                <span class="icon">✉️</span>
                                <p>View Messages</p>
                            </div>
                        </a>
                    </div>
                </div>

                <!-- Export Data -->

            </section>

        </main>
    </div>

    <footer class="main-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Th𝕆th Gate Admin</h3>
                    <p>Gateway to Ancient Wisdom, Modern Learning</p>
                </div>
                <div class="footer-section">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/admin/home">Dashboard</a></li>
                        <li><a href="/admin/instructors">Instructors</a></li>
                        <li><a href="/admin/students">Students</a></li>
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
                <p>© 2025 Th𝕆th Gate Admin. All rights reserved.</p>
            </div>
        </div>
    </footer>
    <script>
        const message = document.querySelector(".error-general");


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
            window.Echo.channel('admin.notifications')
                .listen('AdminNotificationEvent', (e) => {
                    console.log("📢 New Notification:", e.notification);

                    const ul = document.getElementById("notificationsList");
                    const placeholder = ul.querySelector("li strong");

                    if (placeholder && placeholder.textContent.includes("there is no notifications")) {
                        ul.innerHTML = "";
                    }

                    const li = document.createElement("li");
                    li.innerHTML = `
              <strong>📢 ${e.notification.title}</strong><br>
          `;
                    li.classList.add("unread-notification");
                    ul.prepend(li);
                    if (ul.children.length > 3) {
                        ul.removeChild(ul.lastElementChild);
                    }

                    let toast = document.getElementById("toast");
                    toast.textContent = "📢 New Notification Received!";
                    toast.classList.add("show");

                    let notifLink = document.getElementById("notifLink");
                    if (!document.getElementById("notif-dot")) {
                        let dot = document.createElement("span");
                        dot.id = "notif-dot";
                        dot.className = "notif-dot";
                        dot.textContent = "🔴";
                        notifLink.insertBefore(dot, notifLink.childNodes[0]);
                    }

                    setTimeout(() => {
                        toast.classList.remove("show");
                    }, 2000);
                });
        });
    </script>


    <script src="../admin.js"></script>
    <script src="../script.js"></script>
    <div id="toast" class="toast"></div>

</body>

</html>

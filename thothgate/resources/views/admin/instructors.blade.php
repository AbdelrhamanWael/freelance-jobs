@php
    use App\Models\AdminNotification;
@endphp
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Instructors</title>
    <link rel="icon" href="../imgs/logo.png" type="image/x-icon">
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="../admin-styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
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
                    <!-- <li><a href="../home.html">Main Site</a></li> -->
                    <li><a href="/admin/home">Dashboard</a></li>
                    <li><a href="/admin/instructors" class="active">Instructors</a></li>
                    <li><a href="/admin/students">Students</a></li>
                    <li><a href="/admin/messages">Messages</a></li>
                    <li><a href="/admin/notifications" id="notifLink">
                            @if (AdminNotification::where('is_read', false)->count() > 0)
                                <span class="notif-dot" id = "notif-dot">🔴</span>
                            @endif
                            Notifications
                        </a></li>

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
                <li><a href="/admin/home">Home</a></li>
                <li><a href="/admin/instructors" class="active">Instructors</a></li>
                <li><a href="/admin/students">Students</a></li>
                <li><a href="/admin/messages">Messages</a></li>
                <li><a href="/admin/notifications" id="notifLink">
                        @if (AdminNotification::where('is_read', false)->count() > 0)
                            <span class="notif-dot" id = "notif-dot">🔴</span>
                        @endif
                        Notifications
                    </a></li>

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
    <div class="admin-layout ">
        @if (session('success'))
            <div class="message success-general">
                {{ session('success') }}
            </div>
        @endif
        <main class="admin-main-content">
            <section class="admin-section">
                <div class="admin-section-header">
                    <h2 class="section-title">Instructors</h2>
                    <button class="btn" onclick="  window.location.href = '/admin/instructors/create';">Add
                        Instructor</button>
                </div>
                <div class="admin-table-responsive">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Subject</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach ($instructors as $ins)
                                <tr>
                                    <td>{{ $ins->user->name }}</td>
                                    <td>{{ $ins->user->email }}</td>
                                    <td>
                                        @foreach ($ins->courses as $subjects)
                                            {{ $subjects->course->subject }}@if (!$loop->last)
                                                ,
                                            @endif
                                        @endforeach
                                    </td>

                                    <td>
                                        <form action="/admin/instructors/{{ $ins->id }}" method="POST"
                                            onsubmit="return confirm('Are you sure you want to delete this instructor?');">
                                            @csrf
                                            @method('DELETE')
                                            <button type="submit" class="btn btn-delete">Delete</button>
                                        </form>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>

                <div>
                    {{ $instructors->links('vendor.pagination.custom') }}
                </div>

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
                <p>&copy; 2025 Th𝕆th Gate Admin. All rights reserved.</p>
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
            window.Echo.channel('admin.notifications')
                .listen('AdminNotificationEvent', (e) => {
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

    <div id="toast" class="toast"></div>


    <script src="../admin.js"></script>
    <script src="../script.js"></script>

</body>

</html>

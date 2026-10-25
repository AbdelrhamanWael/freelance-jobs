<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us - Th𝕆th Gate Academy</title>
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <meta name="student-id" content="{{ auth()->user()->student->id }}">
    <link rel="stylesheet" href="styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Add Google Fonts for Cinzel Decorative and Cinzel -->
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>

<body class="contact-page">
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
                    <li><a href="/courses">Courses</a></li>
                    <li><a href="/community">Chat</a></li>
                    <li><a href="/contact" class="active">Contact</a></li>
                    <li><a href="/profile">Profile</a></li>
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
            <span class="student-points" title="Your Points">
                Points: <span id="studentPointsValue">{{ Auth::user()->student->points }}</span>
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
                <li><a href="/contact" class="active">Contact</a></li>
                <li><a href="/profile">Profile</a></li>
                <li>
                    <form method="POST" action="/logout" id="logoutForm">
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

    <!-- Contact Section -->
    <section class="contact-section">
        <div class="container">
            @if (session('success'))
                <div class="message success-general">
                    {{ session('success') }}
                </div>
            @endif
            <div class="contact-header">
                <h1>Get in Touch</h1>
                <p>Have questions? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
                </p>
            </div>

            <div class="contact-content">
                <!-- Contact Form -->
                <div class="contact-form-container">
                    <div class="form-header">
                        <h2>Send us a Message</h2>
                        <p>Fill out the form below and we'll get back to you within 24 hours.</p>
                    </div>
                    <form class="contact-form" id="contactForm" method="post" action="/contact">
                        @csrf
                        <div class="form-group">
                            <label for="subject">Subject</label>
                            <select id="subject" name="subject" required>
                                <option value="">Select a subject</option>
                                <option value="general">General Inquiry</option>
                                <option value="courses">Course Information</option>
                                <option value="technical">Technical Support</option>
                                <option value="billing">Billing & Payment</option>
                                <option value="feedback">Feedback & Suggestions</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="message">Message</label>
                            <textarea id="message" name="message" rows="6" required placeholder="Tell us how we can help you..."></textarea>
                        </div>

                        @if ($errors->any())
                            <div class="alert alert-danger">
                                <ul>
                                    @foreach ($errors->all() as $error)
                                        <div class="message error-general">
                                            {{ $error }}
                                        </div>
                                    @endforeach
                                </ul>
                            </div>
                        @endif

                        <button type="submit" class="submit-btn" id = "contactSubmitBtn">
                            <span class="btn-icon">📧</span>
                            Send Message
                        </button>

                    </form>
                </div>

                <!-- Contact Information -->
                <div class="contact-info-container">
                    <div class="info-header">
                        <h2>Contact Information</h2>
                        <p>Reach out to us through any of these channels</p>
                    </div>
                    <div class="contact-info">
                        <div class="info-item">
                            <div class="info-icon">
                                <i class="fas fa-phone"></i>
                            </div>
                            <div class="info-content">
                                <h3>Phone</h3>
                                <p>+20 111 686 5363</p>
                            </div>
                        </div>
                        <div class="info-item">
                            <div class="info-icon">
                                <i class="fas fa-envelope"></i>
                            </div>
                            <div class="info-content">
                                <h3>Email</h3>
                                <p>thothgate@gmail.com</p>
                            </div>
                        </div>
                        <div class="info-item">
                            <div class="info-icon">
                                <i class="fas fa-clock"></i>
                            </div>
                            <div class="info-content">
                                <h3>Working Hours</h3>
                                <p>Sunday - Thursday: 9:00 AM - 6:00 PM<br>Friday - Saturday: 10:00 AM - 4:00 PM</p>
                            </div>
                        </div>
                    </div>
                    <div class="social-links">
                        <h3>Follow Us</h3>
                        <div class="social-icons">
                            <a href="https://www.facebook.com/share/19ZWmoHhcz/" class="social-icon facebook"
                                target="_blank"> <i class="fab fa-facebook-f"></i></a>
                            <a href="https://www.instagram.com/gate61407?igsh=bWV3ejJlOGpzZmwy" target="_blank"
                                class="social-icon instagram"> <i class="fab fa-instagram"></i></a>
                            <a href="https://youtube.com/@tonyhany8314?si=W4N9yI_GT4gwW_xs"
                                class="social-icon youtube" target="_blank"><i class="fab fa-youtube"></i></a>
                            <a href="https://www.tiktok.com/@thothgate" class="social-icon tiktok" target="_blank"><i
                                    class="fab fa-tiktok"></i></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
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
        const ContactForm = document.getElementById("contactForm");
        const messageIn = document.getElementById("message");
        const subjectIn = document.getElementById("subject");
        const submitBtn = document.getElementById("contactSubmitBtn");
        ContactForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!messageIn.value.trim() || !subjectIn.value.trim()) return;

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="btn-icon">⏳</span>Sending...';

            const formData = new FormData(ContactForm);
            try {
                const response = await fetch("/contact", {
                    method: "POST",
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
                    },
                    body: formData,
                });
                const data = await response.json();

                if (data.status === "success") {
                    let toast = document.getElementById("toast");
                    toast.textContent = "Message sent successfully!";
                    toast.classList.add("show");
                    ContactForm.reset();
                    messageIn.value = '';
                }

            } catch (error) {
                console.error("Error:", error);
            }
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span class="btn-icon">📧</span> Send Message';

            setTimeout(() => {
                let toast = document.getElementById("toast");
                toast.classList.remove("show");
            }, 3000);
        });
    </script>
    <script src="/script.js"></script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const studentId = {{ auth()->user()->student->id }};

            window.Echo.private(`student.notification.${studentId}`)
                .listen('.student.notification', (e) => {
                    let toast = document.getElementById("toast2");
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
    <div id="toast2" class="toast"></div>

    <div id="toast" class="toast-success"></div>

</body>

</html>

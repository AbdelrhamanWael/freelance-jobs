<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Lecture</title>
    <link rel="stylesheet" href="/styles.css">
    <link rel="stylesheet" href="/instructor.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">

    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
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
                    <li><a href="/instructor/add/lecture" class="active">Add Lecture</a></li>
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
                <li><a href="/instructor/home">Home</a></li>
                <li><a href="/instructor/create/exam">Create Exam</a></li>
                <li><a href="/instructor/add/lecture" class="active">Add Lecture</a></li>
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
    <section class="contact-section">
        @if (session('success'))
            <div class="message success-general" style="margin: 10px;">
                {{ session('success') }}
            </div>
        @endif
        @if ($errors->any())
            <div class="message error-general">
                <ul style="margin:0; padding-left:1.2rem;">
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif
        <div class="container">
            <div class="contact-header">
                <h1>Add Lecture</h1>
                <p>Fill out the form below to add a new lecture for your students.</p>
            </div>
            <div class="contact-content" style="display: flex; justify-content: center;">
                <div class="contact-form-container" style="width: 900px;">
                    <div class="form-header">
                        <h2>Lecture Details</h2>
                        <p>Provide the lecture title, grade, and content.</p>
                    </div>
                    <form class="contact-form" id="addLectureForm" method="POST" action="/instructor/add/lecture">
                        @csrf

                        <input type="hidden" name="video_path" id="video_path">

                        <div class="form-group-group">
                            <div class="form-group">
                                <label for="lecture-video">Upload Lecture Video</label>
                                <input type="file" id="lecture-video" accept="video/*" required>
                            </div>
                            <div class="form-group">
                                <label for="lecture-title">Lecture Title</label>
                                <input type="text" id="lecture-title" name="lecture-title" required>
                            </div>


                        </div>

                        <div class="form-group">
                            <label for="lecture-description">Lecture Description</label>
                            <textarea id="lecture-description" name="lecture-description" rows="3" required></textarea>
                        </div>

                        <div class="form-group">
                            <label for="quiz-name">Quiz Name</label>
                            <select id="quiz-name" name="quiz-name" required>
                                <option value="">Select a quiz</option>
                                @foreach ($exams as $exam)
                                    <option value="{{ $exam->id }}">{{ $exam->title }}</option>
                                @endforeach
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="grade">Grade & Subject</label>
                            <select id="grade" name="grade" required>
                                <option value="">Select grade and subject</option>
                                @foreach ($courses as $course)
                                    <option value="{{ $course->course_id }}">{{ $course->subject }},
                                        {{ $course->grade }}</option>
                                @endforeach
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="lecture-price">Lecture Price</label>
                            <input type="text" id="lecture-price" name="lecture-price" required>
                        </div>

                        <button type="submit" class="submit-btn" id="submit-btn" disabled>Add Lecture</button>
                    </form>

                    <!-- Overlay -->
                    <div id="overlay"
                        style="display:none;
    position:fixed; top:0; left:0; width:100%; height:100%;
    background:rgba(0,0,0,0.8); color:white;
    display:none; flex-direction:column;
    align-items:center; justify-content:center;
    z-index:9999;">
                        <h2>Uploading video...</h2>
                        <progress id="upload-progress" value="0" max="100" style="width:60%;"></progress>
                        <span id="progress-text">0%</span>
                        <button type="button" id="cancel-upload"
                            style="margin-top:20px; padding:10px 20px;">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    </section>
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
        let xhr;

        document.getElementById("lecture-video").addEventListener("change", function() {
            let file = this.files[0];
            if (!file) return;

            let formData = new FormData();
            formData.append("lecture-video", file);
            formData.append("_token", document.querySelector('input[name="_token"]').value);

            xhr = new XMLHttpRequest();
            xhr.open("POST", "/instructor/upload-video", true);

            document.getElementById("overlay").style.display = "flex";

            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    let percent = Math.round((e.loaded / e.total) * 100);
                    document.getElementById("upload-progress").value = percent;
                    document.getElementById("progress-text").textContent = percent + "%";
                }
            };

            xhr.onload = function() {
                if (xhr.status === 200) {
                    let response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        document.getElementById("video_path").value = response.video_path;
                        document.getElementById("submit-btn").disabled = false;
                    } else {
                        alert("Upload failed!");
                        document.getElementById("lecture-video").value = "";
                    }
                } else {
                    alert("Error while uploading!");
                    document.getElementById("lecture-video").value = "";
                }

                document.getElementById("overlay").style.display = "none";
            };

            xhr.onerror = function() {
                alert("Network error during upload!");
                document.getElementById("overlay").style.display = "none";
                document.getElementById("lecture-video").value = "";
            };

            xhr.send(formData);
        });

        document.getElementById("cancel-upload").addEventListener("click", function() {
            if (xhr) {
                xhr.abort();
                alert("Upload canceled!");
                document.getElementById("overlay").style.display = "none";
                document.getElementById("lecture-video").value = "";
            }
        });
    </script>
    <script src="/script.js"></script>
    <script src="/instructor.js"></script>
</body>

</html>

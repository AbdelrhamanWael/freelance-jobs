<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Th𝕆th Gate - Register</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
</head>

<body class="login-page register-page">
    <div id="loader">
        <!-- You can add an image, a CSS spinner, or text here -->
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>
    <div class="login-container">
        <div class="login-header">
            <div class="logo-container">
                <img src="imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <p class="tagline">Student Registration - Begin Your Journey to Ancient Wisdom</p>

            <div class="switchers-container">
                <button class="theme-switcher" id="themeSwitcher" title="Toggle Dark Mode">
                    <span class="theme-icon">🌙</span>
                </button>
                <button class="language-switcher" id="languageSwitcher" title="Switch Language">
                    <span class="language-text">EN</span>
                </button>
            </div>
        </div>

        <div class="login-form-container">
            <form class="login-form register-form" action="/register" method="POST">
                @csrf
                <div class="form-group">
                    <label for="fullName">Full Name</label>
                    <input type="text" id="fullName" name="name" required value="{{ old('name') }}">
                    @error('name')
                        <span class="message error">{{ $message }}</span>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required value="{{ old('email') }}">
                    @error('email')
                        <span class="message error">{{ $message }}</span>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="phone">Phone Number</label>
                    <input type="text" id="phone_number" name="phone_number" required
                        value="{{ old('phone_number') }}">
                    @error('phone')
                        <span class="message error">{{ $message }}</span>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="dateOfBirth">Date of Birth</label>
                    <input type="date" id="dateOfBirth" name="dateOfBirth" required value="{{ old('dateOfBirth') }}">
                    @error('dateOfBirth')
                        <span class="message error">{{ $message }}</span>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                    @error('password')
                        <span class="message error">{{ $message }}</span>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="confirmPassword">Confirm Password</label>
                    <input type="password" id="confirmPassword" name="password_confirmation" required>
                    @error('password_confirmation')
                        <span class="error-message">{{ $message }}</span>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="grade">Grade Level:</label>
                    <select id="grade" name="grade" required>
                        <option value="" disabled selected>Select your grade</option>
                      <option value="Third Preparatory">الصف الثالث الإعدادي - Third Preparatory</option>
                      <option value="First Secondary">الصف الأول الثانوي - First Secondary</option>

                    </select>
                    @error('grade')
                        <span class="error message">{{ $message }}</span>
                    @enderror
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="terms" name="terms" required>
                        <span class="checkmark"></span>
                        I agree to the <a href="/privacy" class="terms-link">Terms of Service and Privacy Policy</a>
                    </label>
                </div>

                <button type="submit" class="login-btn">Create Account</button>
            </form>

            <div class="login-footer">
                <p>Already have an account? <a href="/login" class="register-link">Login Here</a></p>
            </div>
        </div>
    </div>

    <div class="hieroglyph-bg"></div>

    <script src="script.js"></script>
</body>

</html>

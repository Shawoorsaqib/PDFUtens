/**
 * PDFUtens - Theme Switcher Engine (Light <-> Dark)
 * Manages theme state, persistent localStorage preferences, system color scheme detection,
 * and dynamic UI button updates.
 */

(function () {
    const THEME_KEY = "pdfutens-theme";

    // Detect initial theme preference
    function getStoredTheme() {
        return localStorage.getItem(THEME_KEY);
    }

    function getPreferredTheme() {
        const storedTheme = getStoredTheme();
        if (storedTheme) {
            return storedTheme;
        }
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        updateButtonsUI(theme);
    }

    function updateButtonsUI(theme) {
        const isDark = theme === "dark";
        
        // Desktop Toggle Button Elements
        const themeBtn = document.getElementById("themeToggleBtn");
        const themeIcon = document.getElementById("themeIcon");
        const themeLabel = document.getElementById("themeLabel");

        if (themeIcon) {
            themeIcon.className = isDark ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
        }
        if (themeLabel) {
            themeLabel.textContent = isDark ? "Light" : "Dark";
        }
        if (themeBtn) {
            themeBtn.setAttribute("aria-label", isDark ? "Switch to Light Theme" : "Switch to Dark Theme");
            themeBtn.setAttribute("title", isDark ? "Switch to Light Theme" : "Switch to Dark Theme");
        }

        // Mobile Toggle Button Elements
        const mobileThemeIcon = document.getElementById("mobileThemeIcon");
        const mobileThemeLabel = document.getElementById("mobileThemeLabel");

        if (mobileThemeIcon) {
            mobileThemeIcon.className = isDark ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
        }
        if (mobileThemeLabel) {
            mobileThemeLabel.textContent = isDark ? "Light Mode" : "Dark Mode";
        }
    }

    // Apply initial theme immediately to prevent screen flashing
    const initialTheme = getPreferredTheme();
    document.documentElement.setAttribute("data-theme", initialTheme);

    // Attach listeners on DOM ready
    function initThemeToggle() {
        applyTheme(getPreferredTheme());

        const themeBtn = document.getElementById("themeToggleBtn");
        const mobileThemeBtn = document.getElementById("mobileThemeToggleBtn");

        function handleToggle() {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            localStorage.setItem(THEME_KEY, newTheme);
            applyTheme(newTheme);
        }

        if (themeBtn) {
            themeBtn.addEventListener("click", handleToggle);
        }
        if (mobileThemeBtn) {
            mobileThemeBtn.addEventListener("click", handleToggle);
        }

        // Listen for OS system theme preference changes
        window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
            if (!getStoredTheme()) {
                applyTheme(e.matches ? "dark" : "light");
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initThemeToggle);
    } else {
        initThemeToggle();
    }
})();

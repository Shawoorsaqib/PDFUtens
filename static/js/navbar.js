const menuToggle = document.querySelector(".menu-toggle");

const mobileMenu = document.querySelector(".mobile-menu");

const menuIcon = menuToggle.querySelector("i");

menuToggle.addEventListener("click", () => {

    mobileMenu.classList.toggle("active");

    if(mobileMenu.classList.contains("active")){

        menuIcon.classList.remove("bi-list");

        menuIcon.classList.add("bi-x");

    }else{

        menuIcon.classList.remove("bi-x");

        menuIcon.classList.add("bi-list");

    }

});
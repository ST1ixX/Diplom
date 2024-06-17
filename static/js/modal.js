// Авторизация

const authElement = document.getElementById("auth");

if (authElement) {
    authElement.addEventListener("click", function(e) {
        e.preventDefault();
        document.getElementById("my-modal").classList.add("open");
        document.body.parentNode.classList.add("no-scroll");
    });
}

document.getElementById("close-btn").addEventListener("click", function() {
    document.getElementById("my-modal").classList.remove("open");
    document.body.parentNode.classList.remove("no-scroll");
});

window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.getElementById("my-modal").classList.remove("open");
        document.body.parentNode.classList.remove("no-scroll");
    }
});


// Регистрация

document.getElementById("register__btn").addEventListener("click", function(e) {
    e.preventDefault();
    document.getElementById("my-modal").classList.remove("open")
    document.getElementById("reg__modal").classList.add("open")
    document.body.parentNode.classList.add("no-scroll")
  });
  
  document.getElementById("close-reg-btn").addEventListener("click", function() {
    document.getElementById("reg__modal").classList.remove("open")
    document.body.parentNode.classList.remove("no-scroll")
  });
  
  document.getElementById("reg_btn").addEventListener("click", function() {
    document.getElementById("reg__modal").classList.remove("open")
    document.body.parentNode.classList.remove("no-scroll")
  });
  
  window.addEventListener('keydown', (e) => {
    if(e.key === 'Escape') {
      document.getElementById("reg__modal").classList.remove("open")
      document.body.parentNode.classList.remove("no-scroll")
    }
  })


// Бургер

document.addEventListener("DOMContentLoaded", function() {
  const burgerMenu = document.querySelector('.burger-menu');
  const headerMenu = document.querySelector('.header__menu');
  const links = document.querySelectorAll('.header__menu a'); 

  burgerMenu.addEventListener('click', function() {
      headerMenu.classList.toggle('open');
  });

  links.forEach(link => {
      link.addEventListener('click', function() {
          headerMenu.classList.remove('open'); 
      });
  });
});


// ЧАВО

document.addEventListener("DOMContentLoaded", function() {
  var accordions = document.getElementsByClassName("accordion");

  for (var i = 0; i < accordions.length; i++) {
      accordions[i].addEventListener("click", function() {
          this.classList.toggle("active");
          var panel = this.nextElementSibling;
          if (panel.style.maxHeight) {
              panel.style.maxHeight = null;
          } else {
              // Убедитесь, что scrollHeight доступен и правильно вычисляется
              panel.style.maxHeight = panel.scrollHeight + "px";
          }
      });
  }
});




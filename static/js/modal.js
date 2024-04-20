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
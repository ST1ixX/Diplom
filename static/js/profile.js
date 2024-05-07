document.addEventListener('DOMContentLoaded', function () {
    var settingsButton = document.querySelector('.settings-btn');
    var settingsList = document.querySelector('.settings-list');
    var changePasswordButton = document.querySelector('#change-password');
    var changePinButton = document.querySelector('#change-pin');
    var settings = document.querySelector('.settings');

    settingsButton.addEventListener('click', function(event) {
        var isVisible = settingsList.style.display === 'block';
        settingsList.style.display = isVisible ? 'none' : 'block';
        event.stopPropagation(); 
    });

    document.addEventListener('click', function(event) {
        if (!settingsList.contains(event.target)) {
            settingsList.style.display = 'none';
        }
    });

    changePinButton.addEventListener('click', function() {
        settings.style.display = 'block';
    });

    changePasswordButton.addEventListener('click', function() {
        settings.style.display = 'block';
    });

});

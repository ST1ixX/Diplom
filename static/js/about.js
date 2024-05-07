// Карта

ymaps.ready(init);
    function init(){
        var myMap = new ymaps.Map("map", {
            center: [47.237332, 39.712270],
            zoom: 16
        });

        var myPlacemark = new ymaps.Placemark([55.76, 37.64], {
            hintContent: 'Москва!',
            balloonContent: 'Столица России'
        });
    
        myMap.geoObjects.add(myPlacemark);
    }
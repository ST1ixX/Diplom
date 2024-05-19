// Карта

ymaps.ready(init);

function init(){
    var myMap = new ymaps.Map("map", {
        center: [47.237332, 39.712270],
        zoom: 17
    });

    var placemarks = [
        {
            coords: [47.237864, 39.713021],
            hint: 'Лаборатория ДГТУ',
            balloon: '3 этаж 324 аудитория'
        },
        {
            coords: [47.237260, 39.711821],
            hint: 'Столовая 5',
            balloon: '3 этаж 124 аудитория'
        },
        {
            coords: [47.237674, 39.710400],
            hint: 'Столовая ДГТУ',
            balloon: 'Столовая ДГТУ'
        },
        {
            coords: [47.237341, 39.712195],
            hint: 'Печать ДГТУ',
            balloon: '3 этаж'
        },
    ];

    placemarks.forEach(function(placemark) {
        var myPlacemark = new ymaps.Placemark(placemark.coords, {
            hintContent: placemark.hint,
            balloonContent: placemark.balloon
        });
        myMap.geoObjects.add(myPlacemark);
    });
}



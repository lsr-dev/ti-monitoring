function toggleAccordion(clickedAccordion) {
    var currentContentHeight = window.getComputedStyle(clickedAccordion.parentElement.getElementsByClassName('accordion-element-content')[0]).height;
    // close clicked accordion element
    if (currentContentHeight != '0px') {
        clickedAccordion.parentElement.getElementsByClassName('accordion-element-content')[0].style.height = '0px';
        clickedAccordion.classList.remove('is-open');
        clickedAccordion.getElementsByClassName('expand-collapse-icon')[0].textContent = '+';
    }
    // open clicked accordion element and close all other accordion elements
    else {
        var accordionElements = document.getElementsByClassName('accordion-element');
        Array.from(accordionElements).forEach(function(element) {
            title = element.getElementsByClassName('accordion-element-title')[0];
            content = element.getElementsByClassName('accordion-element-content')[0];
            if (title == clickedAccordion) {
                clickedAccordion.classList.add('is-open');
                content.style.height =  content.scrollHeight + 'px';
                title.getElementsByClassName('expand-collapse-icon')[0].textContent = '–';
            }
            else {
                title.classList.remove('is-open');
                content.style.height = '0px';
                title.getElementsByClassName('expand-collapse-icon')[0].textContent = '+';
            }
        });
    }
}

window.addEventListener('click', function(event) {
    const clickedElement = event.target;
    if (clickedElement.classList.contains('accordion-element-title')) {
        toggleAccordion(clickedElement);
    }
});

// add favicon to head
var favicon_png = document.createElement('link')
favicon_png.rel = 'apple-touch-icon'
favicon_png.type = 'image/png'
favicon_png.href = 'assets/favicon.png'
document.getElementsByTagName('head')[0].appendChild(favicon_png)
var favicon_svg = document.createElement('icon')
favicon_svg.rel = 'icon'
favicon_svg.type = 'image/svg+xml'
favicon_svg.href = 'assets/logo.svg'
document.getElementsByTagName('head')[0].appendChild(favicon_svg)var favicon_png = document.createElement('link')
favicon_png.rel = 'apple-touch-icon'
favicon_png.type = 'image/png'
favicon_png.href = 'assets/favicon.png'
document.getElementsByTagName('head')[0].appendChild(favicon_png)
var favicon_svg = document.createElement('icon')
favicon_svg.rel = 'icon'
favicon_svg.type = 'image/svg+xml'
favicon_svg.href = 'assets/logo.svg'
document.getElementsByTagName('head')[0].appendChild(favicon_svg)

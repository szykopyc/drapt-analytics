function toggleRGBBorder() {
    const element = document.getElementById('element-container');
    element.classList.toggle('moving-rgb-border');

    const button = document.getElementById('rgb-button-toggle');
    if (button.innerHTML==="RGB"){
        button.innerHTML="OFF"
    }else{
        button.innerHTML="RGB"
    }
    button.classList.toggle('rgb-button-toggle')
}
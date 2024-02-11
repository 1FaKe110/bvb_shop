const buttonBuy = document.querySelectorAll('.buy-button');
const buttonBuyInc = document.querySelectorAll('.buy-button-inc');
const dec = document.querySelectorAll('.dec')
const count = document.querySelectorAll('.count')
const inc = document.querySelectorAll('.inc')
buttonBuy.forEach((item, i) => {
    item.addEventListener('click', () => {
        item.style.display = 'none';
        buttonBuyInc[i].style.display = "flex";
    })
})

inc.forEach((item, i) => {
    item.addEventListener('click', () => {
        count[i].innerHTML = Number(count[i].innerText) + 1
    })
})

dec.forEach((item, i) => {
    item.addEventListener('click', () => {
        if (Number(count[i].innerText) <= 1) {
            buttonBuy[i].style.display = '';
            buttonBuyInc[i].style.display = "";
            count[i].innerHTML = 1;
        } else {
            count[i].innerHTML = Number(count[i].innerText) - 1
        }
    })
})
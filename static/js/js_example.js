document.addEventListener('DOMContentLoaded', function(){

    const btn = document.querySelector('#btn')
    btn.addEventListener('click', function() {
        console.log('button clicked')

    })
    const textInput = document.querySelector('.text-input')

    textInput.addEventListener('change', function() {
        console.log('asdasdasd')
    })
    textInput.addEventListener('keyup', function() {
        console.log('keyup')
    })
})

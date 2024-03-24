function confirmSubmit() {
    if (confirm("All progress will be lost. Are you sure?") == true) {
        return true
    } else {
        return false
    }
}

function setTime(timer) {
    minutes = parseInt(timer / 60, 10);
    seconds = parseInt(timer % 60, 10);

    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;

    display.textContent = minutes + ":" + seconds;
}


function startTimer(duration, display) {
    var timer = duration, minutes, seconds;
    setTime(timer);
    var intervalId = setInterval(function () {
        setTime(timer);

        if (--timer < 0) {
            clearInterval(intervalId); // Stop the timer
            display.textContent = "Times up !";
        }
    }, 1000);
}

let ans_selected = null;

function setAnswer(no) {
    if (event) {
        event.preventDefault();
    }
    document.getElementById("user_ans").value = no;

    document.getElementById("ans_" + no).classList.add("selected-item");
    if (ans_selected !== null) {
        document.getElementById("ans_" + ans_selected).classList.remove("selected-item");
        document.getElementById("ans_" + ans_selected).classList.remove("wrong-item");
        document.getElementById("ans_" + ans_selected).classList.remove("correct-item");
    }
    ans_selected = no;
}

let next_question = false;

function checkBeforeSubmit() {
    if (!next_question) {
        event.preventDefault();
    }
    fetch("/exam/get_answer", {
        method: "POST",
    })
        .then(response => {
            if (response.ok) {
                response.json().then(payload => {

                    console.log(payload)
                    console.log(payload["ans_id"])
                    const ans_id = payload["ans_id"]

                    document.getElementById("ans_" + ans_id).classList.add("correct-item");
                    document.getElementById("next").innerText = "Next"
                    if (ans_selected && ans_id != ans_selected){
                        document.getElementById("ans_" + ans_selected).classList.add("wrong-item");
                    }
                    const btnSecondaryElements = document.getElementsByClassName("btn-secondary");
                    for (const btn of btnSecondaryElements) {
                        btn.setAttribute("disabled", "");
                    }
                    next_question = true;
                })

            } else {
                // Handle error response
                console.error("Error submitting form:", response.statusText);
                // Optionally, you can display an error message or perform other actions
            }
        })
        .catch(error => {
            console.error("Error submitting form:", error);
            // Optionally, you can display an error message or perform other actions
        });


}


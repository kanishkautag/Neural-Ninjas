document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const firstname = document.getElementById("firstname").value;
    const lastname = document.getElementById("lastname").value;

    signUp(email, password, firstname, lastname);
});

function signUp(email, password, firstname, lastname) {
    clearErrorMessage();

    firebase.auth().createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            const userId = user.uid; 
            user.sendEmailVerification()
                .then(() => {
                    console.log("Verification email sent");
                    saveEntryToFirebase(userId, firstname, lastname, () => {
                        alert("Verification Email Sent")
                        location.replace("login.html");
                    });
                })
                .catch((error) => {
                    console.error("Error sending verification email:", error);
                    displayErrorMessage(error.message);
                });
        })
        .catch((error) => {
            console.error("Error creating user:", error);
            displayErrorMessage(error.message);
        });
}

function saveEntryToFirebase(userId, firstname, lastname, callback) {
    const database = firebase.database();
    database.ref('users/' + userId).set({
        firstname: firstname,
        lastname: lastname
    }).then(() => {
        if (callback && typeof callback === 'function') {
            callback();
        }
    }).catch((error) => {
        console.error("Error saving entry: ", error);
    });
}

function clearErrorMessage() {
    const errorMessage = document.getElementById("error");
    errorMessage.innerHTML = ""; 
}

function displayErrorMessage(message) {
    const errorMessage = document.getElementById("error");
    errorMessage.innerHTML = message;

    setTimeout(clearErrorMessage, 5000);
}

firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        sessionStorage.setItem("user", JSON.stringify(user));
    }
});



function login() {
    clearErrorMessage();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    firebase.auth().signInWithEmailAndPassword(email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            if (user.emailVerified) {

                location.replace("home.html");
            } else {
                document.getElementById("error").innerHTML = "Please verify your email address first.";

            }

        })

    .catch((error) => {
        document.getElementById("error").innerHTML = error.message;
    });
}

function logout() {
    sessionStorage.removeItem("user");
    location.replace("/login.html");
}

function sendVerificationEmail(email, password) {
    firebase.auth().createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            user.sendEmailVerification()
                .then(() => {
                    console.log("Verification email sent");
                })
                .catch((error) => {
                    console.error("Error sending verification email:", error);
                    document.getElementById("error").innerHTML = error.message;
                });
        })
        .catch((error) => {
            console.error("Error creating user:", error);
            document.getElementById("error").innerHTML = error.message;
        });
}

function forgotPass() {
    const email = document.getElementById("email").value;
    firebase.auth().sendPasswordResetEmail(email)
        .then(() => {
            alert("Reset link sent to your email id");
        })
        .catch((error) => {
            document.getElementById("error").innerHTML = error.message;
        });
}

document.addEventListener("DOMContentLoaded", function() {
    clearErrorMessage();
});

function getUserSession() {
    const userSession = sessionStorage.getItem("user");
    if (userSession) {
        return JSON.parse(userSession);
    } else {
        return null;
    }
}

function getFormValues() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    return { email, password };
}
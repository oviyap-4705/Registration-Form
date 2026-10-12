
const form = document.getElementById("registrationForm");
const experience = document.getElementById("experience");
const experienceValue = document.getElementById("experienceValue");

experience.addEventListener("input", function () {
    experienceValue.textContent = experience.value;
});

form.addEventListener("submit", async function (event) {

    event.preventDefault();


    const name =
        document.getElementById("name").value.trim();

    const email =
        document.getElementById("email").value.trim();

    const password =
        document.getElementById("password").value;

    const phone =
        document.getElementById("phone").value.trim();

    const address =
        document.getElementById("address").value.trim();

    const dob =
        document.getElementById("dob").value;

    const websiteInput =
        document.getElementById("website");

    let website =
        websiteInput.value.trim();

    const state =
        document.getElementById("state").value;

    const languages =
        document.getElementById("languages");

    const gender =
        document.querySelector(
            'input[name="gender"]:checked'
        );

    const skills =
        document.querySelectorAll(
            'input[name="skills"]:checked'
        );

    const photo =
        document.getElementById("photo").files[0];

    const resume =
        document.getElementById("resume").files[0];

    const audio =
        document.getElementById("audio").files[0];

    const video =
        document.getElementById("video").files[0];

    if (name === "") {
        alert("Please enter your full name.");
        return;
    }

    if (email === "") {
        alert("Please enter your email address.");
        return;
    }

    if (password === "") {
        alert("Please enter a password.");
        return;
    }

    if (phone === "") {
        alert("Please enter your phone number.");
        return;
    }

    if (address === "") {
        alert("Please enter your address.");
        return;
    }

    if (dob === "") {
        alert("Please select your date of birth.");
        return;
    }

    if (website === "") {
        alert("Please enter your website URL.");
        return;
    }

    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
        alert("Please enter a valid email address.");
        return;
    }

    if (password.length < 8) {
        alert("Password must contain at least 8 characters.");
        return;
    }


    const phonePattern = /^\d{10}$/;

    if (!phonePattern.test(phone)) {
        alert("Phone number must contain exactly 10 digits.");
        return;
    }

    if (
        !website.startsWith("http://") &&
        !website.startsWith("https://")
    ) {
        website = "https://" + website;
    }

    if (state === "") {
        alert("Please select your state.");
        return;
    }

    const selectedLanguages =
        Array.from(languages.selectedOptions);

    if (selectedLanguages.length === 0) {
        alert("Please select at least one language.");
        return;
    }

    if (!gender) {
        alert("Please select your gender.");
        return;
    }

    if (skills.length === 0) {
        alert("Please select at least one skill.");
        return;
    }

    if (!photo) {
        alert("Please upload your profile photo.");
        return;
    }

    const allowedImageTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (!allowedImageTypes.includes(photo.type)) {
        alert("Profile photo must be JPG, PNG or WEBP.");
        return;
    }

    if (!resume) {
        alert("Please upload your resume.");
        return;
    }

    if (resume.type !== "application/pdf") {
        alert("Resume must be a PDF file.");
        return;
    }


    if (audio) {

        if (!audio.type.startsWith("audio/")) {
            alert("Please upload a valid audio file.");
            return;
        }
    }


    if (video) {

        if (!video.type.startsWith("video/")) {
            alert("Please upload a valid video file.");
            return;
        }
    }


    const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
    const MAX_PDF_SIZE = 10 * 1024 * 1024;
    const MAX_AUDIO_SIZE = 20 * 1024 * 1024;
    const MAX_VIDEO_SIZE = 100 * 1024 * 1024;


    if (photo.size > MAX_IMAGE_SIZE) {
        alert("Profile photo must be less than 5 MB.");
        return;
    }

    if (resume.size > MAX_PDF_SIZE) {
        alert("Resume must be less than 10 MB.");
        return;
    }

    if (audio && audio.size > MAX_AUDIO_SIZE) {
        alert("Audio file must be less than 20 MB.");
        return;
    }

    if (video && video.size > MAX_VIDEO_SIZE) {
        alert("Video file must be less than 100 MB.");
        return;
    }

    const formData = new FormData(form);

    formData.set(
        "password",
        password
    );
    
    console.log(
    "PASSWORD BEING SENT:",
    formData.get("password")
    );

    formData.set(
        "website",
        website
    );

    const languageValues =
        selectedLanguages.map(
            option => option.value
        );

    formData.set(
        "languages",
        languageValues.join(", ")
    );


    const skillValues =
        Array.from(skills).map(
            skill => skill.value
        );

    formData.set(
        "skills",
        skillValues.join(", ")
    );

    try {

        const csrfToken =
            document.querySelector(
                '[name=csrfmiddlewaretoken]'
            ).value;


        const response =
            await fetch(
                "/api/registrations/",
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken": csrfToken
                    },

                    body: formData
                }
            );


        const data =
            await response.json();


        console.log(
            "API Response:",
            data
        );


        if (response.ok) {

            alert(
                "Registration successful! Please login."
            );

            form.reset();

            experienceValue.textContent = "0";

            window.location.href = "/login/";

        }

        else {

            console.error(
                "API Error:",
                data
            );

            alert(
                "Registration failed:\n\n" +
                JSON.stringify(
                    data,
                    null,
                    2
                )
            );
        }

    }

    catch (error) {

        console.error(
            "Connection Error:",
            error
        );

        alert(
            "Unable to connect to the server."
        );
    }

});
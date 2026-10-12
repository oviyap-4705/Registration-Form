const form = document.getElementById("registrationForm");
const experience = document.getElementById("experience");
const experienceValue = document.getElementById("experienceValue");

const ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp"
];

const MB = 1024 * 1024;
const MAX_IMAGE_SIZE = 5 * MB;
const MAX_PDF_SIZE = 10 * MB;
const MAX_AUDIO_SIZE = 20 * MB;
const MAX_VIDEO_SIZE = 100 * MB;

// Each part of the domain is separated by a dot and cannot contain one,
// so the pattern has no ambiguity and runs in linear time.
const EMAIL_PATTERN = /^[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+$/;
const PHONE_PATTERN = /^\d{10}$/;

const REQUIRED_TEXT_FIELDS = [
    ["name", "Please enter your full name."],
    ["email", "Please enter your email address."],
    ["password", "Please enter a password."],
    ["phone", "Please enter your phone number."],
    ["address", "Please enter your address."],
    ["dob", "Please select your date of birth."],
    ["website", "Please enter your website URL."]
];

experience.addEventListener("input", function () {
    experienceValue.textContent = experience.value;
});


function textValue(id) {
    return document.getElementById(id).value.trim();
}

function readFormValues() {
    return {
        name: textValue("name"),
        email: textValue("email"),
        password: document.getElementById("password").value,
        phone: textValue("phone"),
        address: textValue("address"),
        dob: document.getElementById("dob").value,
        website: textValue("website"),
        state: document.getElementById("state").value,
        languages: Array.from(
            document.getElementById("languages").selectedOptions
        ),
        gender: document.querySelector('input[name="gender"]:checked'),
        skills: Array.from(
            document.querySelectorAll('input[name="skills"]:checked')
        ),
        photo: document.getElementById("photo").files[0],
        resume: document.getElementById("resume").files[0],
        audio: document.getElementById("audio").files[0],
        video: document.getElementById("video").files[0]
    };
}


/* ---------- Validation (each function returns a message or null) ---------- */

function validateRequiredText(values) {
    const missing = REQUIRED_TEXT_FIELDS.find(
        ([field]) => values[field] === ""
    );

    return missing ? missing[1] : null;
}

function validateFormats(values) {
    if (!EMAIL_PATTERN.test(values.email)) {
        return "Please enter a valid email address.";
    }

    if (values.password.length < 8) {
        return "Password must contain at least 8 characters.";
    }

    if (!PHONE_PATTERN.test(values.phone)) {
        return "Phone number must contain exactly 10 digits.";
    }

    return null;
}

function validateSelections(values) {
    if (values.state === "") {
        return "Please select your state.";
    }

    if (values.languages.length === 0) {
        return "Please select at least one language.";
    }

    if (!values.gender) {
        return "Please select your gender.";
    }

    if (values.skills.length === 0) {
        return "Please select at least one skill.";
    }

    return null;
}

function validateFileTypes(values) {
    const { photo, resume, audio, video } = values;

    if (!photo) {
        return "Please upload your profile photo.";
    }

    if (!ALLOWED_IMAGE_TYPES.includes(photo.type)) {
        return "Profile photo must be JPG, PNG or WEBP.";
    }

    if (!resume) {
        return "Please upload your resume.";
    }

    if (resume.type !== "application/pdf") {
        return "Resume must be a PDF file.";
    }

    if (audio && !audio.type.startsWith("audio/")) {
        return "Please upload a valid audio file.";
    }

    if (video && !video.type.startsWith("video/")) {
        return "Please upload a valid video file.";
    }

    return null;
}

function validateFileSizes(values) {
    const { photo, resume, audio, video } = values;

    if (photo.size > MAX_IMAGE_SIZE) {
        return "Profile photo must be less than 5 MB.";
    }

    if (resume.size > MAX_PDF_SIZE) {
        return "Resume must be less than 10 MB.";
    }

    if (audio && audio.size > MAX_AUDIO_SIZE) {
        return "Audio file must be less than 20 MB.";
    }

    if (video && video.size > MAX_VIDEO_SIZE) {
        return "Video file must be less than 100 MB.";
    }

    return null;
}

const VALIDATORS = [
    validateRequiredText,
    validateFormats,
    validateSelections,
    validateFileTypes,
    validateFileSizes
];

function findValidationError(values) {
    for (const validate of VALIDATORS) {
        const message = validate(values);

        if (message) {
            return message;
        }
    }

    return null;
}


/* ---------- Building and sending the request ---------- */

function normalizeWebsite(website) {
    const hasProtocol =
        website.startsWith("http://") ||
        website.startsWith("https://");

    return hasProtocol ? website : "https://" + website;
}

function buildFormData(values) {
    const formData = new FormData(form);

    formData.set("password", values.password);
    formData.set("website", normalizeWebsite(values.website));

    formData.set(
        "languages",
        values.languages.map(option => option.value).join(", ")
    );

    formData.set(
        "skills",
        values.skills.map(skill => skill.value).join(", ")
    );

    return formData;
}

async function submitRegistration(formData) {
    const csrfToken =
        document.querySelector(
            '[name=csrfmiddlewaretoken]'
        ).value;

    const response = await fetch(
        "/api/registrations/",
        {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            body: formData
        }
    );

    const data = await response.json();

    console.log("API Response:", data);

    return { ok: response.ok, data };
}

function handleSuccess() {
    alert("Registration successful! Please login.");

    form.reset();

    experienceValue.textContent = "0";

    window.location.href = "/login/";
}

function handleFailure(data) {
    console.error("API Error:", data);

    alert(
        "Registration failed:\n\n" +
        JSON.stringify(data, null, 2)
    );
}


form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const values = readFormValues();
    const errorMessage = findValidationError(values);

    if (errorMessage) {
        alert(errorMessage);
        return;
    }

    try {
        const { ok, data } = await submitRegistration(
            buildFormData(values)
        );

        if (ok) {
            handleSuccess();
        } else {
            handleFailure(data);
        }

    } catch (error) {
        console.error("Connection Error:", error);

        alert("Unable to connect to the server.");
    }
});
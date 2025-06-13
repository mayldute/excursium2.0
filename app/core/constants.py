# Allowed MIME types for user photo uploads
ALLOWED_IMAGE_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

# Allowed MIME types for document uploads
ALLOWED_DOC_TYPES: set[str] = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png"
}

# Define a mapping for email fields based on the OAuth provider
EMAIL_FIELDS = {
    "google": "email",
    "yandex": "default_email"
}

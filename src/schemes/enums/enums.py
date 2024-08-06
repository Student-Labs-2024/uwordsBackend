from enum import Enum


class Providers(Enum):
    email = "email"
    vk = "vk"
    google = "google"
    admin = "admin"


class ImageAnnotations(Enum):
    adult = "adult"
    medical = "medical"
    violence = "violence"
    racy = "racy"

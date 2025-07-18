import cloudinary
import cloudinary.uploader
import cloudinary.api
cloudinary.config(
    cloud_name = "djdmzvxrq",
    api_key = "263564482372149",
    api_secret = "NRZUwu0TOC1jDXogmYZIyaZI16c",
    secure = True

)
def upload_file(file_path):
    result = cloudinary.uploader.upload(file_path)
    return result["secure_url"]
"""
Cloudinary helper functions for image upload and deletion.
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app


def init_cloudinary(app):
    """Initialize Cloudinary with credentials from environment."""
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def upload_image(file, folder="kotd", public_id=None):
    """
    Upload a file object to Cloudinary.
    Returns dict with url, public_id, format, bytes.
    Raises cloudinary exceptions on failure.
    """
    options = {
        "folder": folder,
        "resource_type": "image",
        "overwrite": False,
    }
    if public_id:
        options["public_id"] = public_id

    result = cloudinary.uploader.upload(file, **options)
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "format": result["format"],
        "bytes": result["bytes"],
    }


def delete_image(public_id):
    """Delete an image from Cloudinary by its public_id."""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        print(f"[cloudinary] Delete error: {e}")
        return False
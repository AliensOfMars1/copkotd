"""
Test Cloudinary upload + delete.

Place any image (JPG/PNG) at project root named test_upload.jpg
Then run: python test_cloudinary.py
"""
import os
from app import create_app
from app.utils.cloudinary import upload_image, delete_image


def main():
    app = create_app()
    with app.app_context():
        # Check env vars are set
        missing = [
            k for k in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET")
            if not os.getenv(k)
        ]
        if missing:
            print(f"[ERROR] Missing env vars: {missing}")
            print("Add them to .env and try again.")
            return

        print("Env vars present ✅")

        # Check test image exists
        if not os.path.exists("test_upload.jpg"):
            print("[ERROR] No test image found. Create one named test_upload.jpg")
            return

        print("Uploading test_upload.jpg to Cloudinary...")
        try:
            result = upload_image(open("test_upload.jpg", "rb"), folder="kotd/test")
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
            return

        print("\nUpload successful ✅")
        print(f"  URL:        {result['url']}")
        print(f"  Public ID:  {result['public_id']}")
        print(f"  Format:     {result['format']}")
        print(f"  Size:       {result['bytes']} bytes")

        # Verify URL looks right
        if result["url"].startswith("https://res.cloudinary.com/"):
            print("\nURL format correct ✅")
        else:
            print("\nURL format looks wrong ⚠️")

        # Delete the test image to keep account clean
        print("\nDeleting test image from Cloudinary...")
        if delete_image(result["public_id"]):
            print("Deletion successful ✅")
        else:
            print("Deletion failed ⚠️")

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED")
        print("=" * 50)


if __name__ == "__main__":
    main()
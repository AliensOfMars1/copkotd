// app/static/js/image_compressor.js
//
// Client-side image compressor.
// Compresses only if the file exceeds the size limit for its type.
// Converts everything to JPEG 
const COMPRESSOR_SIZES = {
    member: { maxSizeMB: 2, maxWidth: 800, maxHeight: 800, quality: 0.85 },
    event:  { maxSizeMB: 3, maxWidth: 1200, maxHeight: 1200, quality: 0.8 },
};

async function compressImage(file, maxWidth, maxHeight, quality, maxSizeBytes) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);

        reader.onload = function (event) {
            const img = new Image();
            img.src = event.target.result;

            img.onload = function () {
                const canvas = document.createElement("canvas");
                let width = img.width;
                let height = img.height;

                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width = Math.floor(width * ratio);
                    height = Math.floor(height * ratio);
                }

                canvas.width = width;
                canvas.height = height;

                const ctx = canvas.getContext("2d");
                // Fill white so transparent areas become white (not black)
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(0, 0, width, height);
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob(
                    function (blob) {
                        if (blob.size > maxSizeBytes) {
                            reduceQuality(canvas, quality - 0.1, maxSizeBytes)
                                .then(resolve)
                                .catch(reject);
                        } else {
                            resolve(blob);
                        }
                    },
                    "image/jpeg",
                    quality
                );
            };

            img.onerror = function () {
                reject(new Error("Failed to load image"));
            };
        };

        reader.onerror = function () {
            reject(new Error("Failed to read file"));
        };
    });
}

async function reduceQuality(canvas, quality, maxSizeBytes) {
    return new Promise((resolve, reject) => {
        canvas.toBlob(
            function (blob) {
                if (blob.size <= maxSizeBytes || quality <= 0.1) {
                    resolve(blob);
                } else {
                    reduceQuality(canvas, quality - 0.1, maxSizeBytes)
                        .then(resolve)
                        .catch(reject);
                }
            },
            "image/jpeg",
            quality
        );
    });
}

function setupImageCompression(inputId, type = "member", callback = null) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const config = COMPRESSOR_SIZES[type] || COMPRESSOR_SIZES.member;
    const maxSizeBytes = config.maxSizeMB * 1024 * 1024;

    input.addEventListener("change", async function (event) {
        const file = event.target.files[0];
        if (!file) return;

        // Only compress images
        if (!file.type.startsWith("image/")) return;

        const originalSizeMB = file.size / (1024 * 1024);

        // Show "will compress" message only if needed
        if (originalSizeMB > config.maxSizeMB) {
            const parent = input.parentNode;
            const existingMsg = parent.querySelector(".compression-msg");
            if (existingMsg) existingMsg.remove();

            const loadingDiv = document.createElement("div");
            loadingDiv.className = "compression-msg form-text text-primary";
            loadingDiv.innerHTML =
                '<i class="bi bi-arrow-repeat"></i> Compressing image (' +
                originalSizeMB.toFixed(1) +
                "MB → " +
                config.maxSizeMB +
                "MB max)...";
            parent.appendChild(loadingDiv);

            try {
                const compressedBlob = await compressImage(
                    file,
                    config.maxWidth,
                    config.maxHeight,
                    config.quality,
                    maxSizeBytes
                );

                loadingDiv.remove();

                const compressedFile = new File([compressedBlob], file.name.replace(/\.[^.]+$/, ".jpg"), {
                    type: "image/jpeg",
                    lastModified: Date.now(),
                });

                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(compressedFile);
                input.files = dataTransfer.files;

                const successDiv = document.createElement("div");
                successDiv.className = "compression-msg form-text text-success";
                successDiv.innerHTML =
                    '<i class="bi bi-check-circle"></i> Compressed to ' +
                    (compressedBlob.size / (1024 * 1024)).toFixed(2) +
                    " MB";
                parent.appendChild(successDiv);
                setTimeout(() => successDiv.remove(), 3000);

                if (callback && typeof callback === "function") {
                    callback(compressedFile);
                }
            } catch (error) {
                console.error("Compression failed:", error);
                loadingDiv.remove();

                const errDiv = document.createElement("div");
                errDiv.className = "compression-msg form-text text-warning";
                errDiv.innerHTML =
                    '<i class="bi bi-exclamation-triangle"></i> Compression failed — original will be uploaded';
                parent.appendChild(errDiv);
                setTimeout(() => errDiv.remove(), 4000);

                if (callback && typeof callback === "function") {
                    callback(file);
                }
            }
        } else {
            if (callback && typeof callback === "function") {
                callback(file);
            }
        }
    });
}

window.setupImageCompression = setupImageCompression;
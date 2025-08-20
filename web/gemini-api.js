/**
 * @file Handles interaction with the Gemini API through the backend.
 *
 * Calls the given Gemini model with the given image and/or text
 * parts, streaming output (as a generator function).
 */
export async function* streamGemini({
  model = 'gemini-1.5-flash', // or gemini-1.5-pro
  contents = [],
} = {}) {
  // Send the prompt to the Python backend
  // Call API defined in main.py
  let response = await fetch("/api/generate", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ model, contents })
  });

  yield* streamResponseChunks(response);
}

/**
 * A helper that streams text output chunks from a fetch() response.
 */
async function* streamResponseChunks(response) {
  let buffer = '';

  const CHUNK_SEPARATOR = '\n\n';

  let processBuffer = async function* (streamDone = false) {
    while (true) {
      let flush = false;
      let chunkSeparatorIndex = buffer.indexOf(CHUNK_SEPARATOR);
      if (streamDone && chunkSeparatorIndex < 0) {
        flush = true;
        chunkSeparatorIndex = buffer.length;
      }
      if (chunkSeparatorIndex < 0) {
        break;
      }

      let chunk = buffer.substring(0, chunkSeparatorIndex);
      buffer = buffer.substring(chunkSeparatorIndex + CHUNK_SEPARATOR.length);
      chunk = chunk.replace(/^data:\s*/, '').trim();
      if (!chunk) {
        if (flush) break;
        continue;
      }
      let { error, text } = JSON.parse(chunk);
      if (error) {
        console.error(error);
        throw new Error(error?.message || JSON.stringify(error));
      }
      yield text;
      if (flush) break;
    }
  };

  const reader = response.body.getReader();
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break;
      buffer += new TextDecoder().decode(value);
      console.log(new TextDecoder().decode(value));
      yield* processBuffer();
    }
  } finally {
    reader.releaseLock();
  }

  yield* processBuffer(true);
}

// --- Google Sign-In for Drive Integration ---

// Assuming Firebase is initialized elsewhere in the application
// import { getAuth, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';

// Get a reference to the Google Sign-In button
const googleSigninButton = document.getElementById('google-signin-button');

if (googleSigninButton) {
  googleSigninButton.addEventListener('click', () => {
    const auth = getAuth();
    const provider = new GoogleAuthProvider();

    // Request the necessary scope for Google Drive access
    provider.addScope('https://www.googleapis.com/auth/drive');

    signInWithPopup(auth, provider)
      .then((result) => {
        // This gives you a Google Access Token. You can use it to access the Google API.
        const credential = GoogleAuthProvider.credentialFromResult(result);
        const accessToken = credential.accessToken;

        // The signed-in user info.
        const user = result.user;

        console.log("User signed in:", user);
        console.log("Google Access Token:", accessToken);

        // TODO: Store or use the accessToken for Google Drive API calls

      })
      .catch((error) => {
        console.error("Google Sign-In Error:", error.code, error.message);
      });
  });
}

// --- File Upload Handling ---

// Get references to the file upload area and input
const fileUploadArea = document.querySelector('.file-upload-area');
const fileInput = document.getElementById('file-input');

// Add click listener to the upload area to trigger file input click
if (fileUploadArea && fileInput) {
  fileUploadArea.addEventListener('click', () => {
    fileInput.click();
  });

  // Add drag and drop listeners
  fileUploadArea.addEventListener('dragover', (event) => {
    event.preventDefault(); // Prevent default to allow drop
    fileUploadArea.classList.add('drag-over');
  });

  fileUploadArea.addEventListener('dragleave', (event) => {
    event.preventDefault(); // Prevent default
    fileUploadArea.classList.remove('drag-over');
  });

  fileUploadArea.addEventListener('drop', (event) => {
    event.preventDefault(); // Prevent default
    fileUploadArea.classList.remove('drag-over');
    console.log('Dropped files:', event.dataTransfer.files);
  });

  fileUploadArea.addEventListener('drop', (event) => {
    event.preventDefault(); // Prevent default
    fileUploadArea.classList.remove('drag-over');
    const files = event.dataTransfer.files;
    uploadFiles(files); // Call the new upload function
  });

  // Add change listener to the file input to log selected files
  fileInput.addEventListener('change', (event) => {
    console.log('Selected files:', event.target.files);
    const files = event.target.files;
    uploadFiles(files); // Call the new upload function
  });
}

// Function to upload files to the backend
async function uploadFiles(files) {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]); // 'files' is the field name the backend will expect
  }

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    const result = await response.json();
    console.log('Upload response:', result);
  } catch (error) {
    console.error('Upload error:', error);
  }
}
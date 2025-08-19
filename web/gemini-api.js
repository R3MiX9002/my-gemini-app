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

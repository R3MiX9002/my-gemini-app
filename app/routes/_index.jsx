import { Links, Meta, Scripts, LiveReload, Form } from "@remix-run/react";
import { useEffect } from "react";

// You might want to move your CSS to a separate file and link it
// import styles from "~/styles/index.css";

export const meta = () => [
  { title: "Remix App" },
  { name: "description", content: "Welcome to Remix!" },
];

/*
export const links = () => [
  { rel: "stylesheet", href: styles },
];
*/

export const action = async ({ request }) => {
  const formData = await request.formData();
  const imageFile = formData.get("image");

  // Here you would send the imageFile to your Python backend
  // For now, let's just log the file details
  console.log("Received image file:", imageFile);

  return null; // Or return a response from your backend
};
*/

export default function Index() {
  useEffect(() => {
    // Your original web/main.js content goes here.
    // Make sure to adapt it to work within a React/Remix component.
    // You might need to use refs or state for DOM manipulation.
    console.log("Main JS logic running...");

    // Example of original main.js content (replace with your actual code)
    const myButton = document.getElementById('myButton');
    if (myButton) {
      myButton.addEventListener('click', () => {
        alert('Button clicked!');
      });
    }

  }, []); // Empty dependency array means this runs once after initial render

  return (
    <html>
      <head>
        <Meta />
        <Links />
        {/* You can include inline styles here for simplicity,
            but linking to a separate CSS file is generally better practice */}
        <style>{`
          /* Your original web/style.css content goes here */
          body {
            font-family: sans-serif;
            line-height: 1.4;
          }

          h1 {
            color: navy;
          }
        `}</style>
      </head>
      <body>
        {/* Your original web/index.html content goes here, adapted to JSX */}
        <div style={{ fontFamily: "system-ui, sans-serif", lineHeight: "1.8" }}>
          <h1>Welcome to Remix</h1>
          <p>This is content from your old index.html</p>
          <button id="myButton">Click Me</button>

          {/* Image upload form */}
          <Form method="post" encType="multipart/form-data">
            <input type="file" name="image" accept="image/*" />
            <button type="submit">Upload Image</button>
          </Form>
        </div>

        <Scripts />
        <LiveReload />
      </body>
    </html>
  );
}
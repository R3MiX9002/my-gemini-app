/**
 * By default, @remix-run/node builds a server-side only bundle.
 *
 * If you want to hydrate your app on the client, add this file.
 */
import { RemixBrowser } from "@remix-run/react";
import { hydrateRoot } from "react-dom/client";

hydrateRoot(document, <RemixBrowser />);
/** @type {import('@remix-run/dev').AppConfig} */
export default {
  ignoredRouteFiles: ["**/.*"],
  routes(defineRoutes) {
    return defineRoutes(async (route) => {
      // Example:
      // route("/", "app/routes/_index.tsx");
      // route("/posts", "app/routes/posts._index.tsx");
      // route("/posts/:id", "app/routes/posts.$id.tsx");
    });
  },
  appDirectory: "app",
  assetsBuildDirectory: "public/build",
  publicPath: "/build/",
  serverBuildPath: "build/index.js",
};
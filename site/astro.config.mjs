import { defineConfig } from "astro/config";

const repository = process.env.GITHUB_REPOSITORY?.split("/")[1];
const isGitHubPages = process.env.GITHUB_ACTIONS === "true" && repository;

export default defineConfig({
  site: "https://carlosurteaga.github.io",
  base: isGitHubPages ? `/${repository}/` : "/",
  output: "static",
  server: {
    host: true,
  },
});

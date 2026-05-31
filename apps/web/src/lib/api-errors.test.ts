import { describe, expect, it } from "vitest";
import { artifactUrl, parseErrorMessage } from "./api-errors";

describe("api-errors", () => {
  it("maps known error codes", () => {
    expect(parseErrorMessage({ detail: "400_PDF_INVALID" }, 400)).toContain("Invalid");
  });

  it("builds artifact urls", () => {
    expect(artifactUrl("/v1/jobs/x/artifacts/chunks.jsonl", "/api/v1")).toBe(
      "/api/v1/jobs/x/artifacts/chunks.jsonl"
    );
  });
});

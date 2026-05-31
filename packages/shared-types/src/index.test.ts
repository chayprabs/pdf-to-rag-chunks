import { describe, expect, it } from "vitest";
import type { Chunk } from "./index.js";

describe("shared-types", () => {
  it("exports Chunk shape", () => {
    const chunk: Chunk = {
      id: "c1",
      text: "hello",
      kind: "text",
      page: 1,
      bbox: [0, 0, 100, 100],
      sectionPath: ["Intro"],
      tokenCount: 1,
      confidence: 0.9,
    };
    expect(chunk.kind).toBe("text");
  });
});

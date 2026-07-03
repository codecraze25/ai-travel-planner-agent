import { afterEach, describe, expect, it } from "vitest";
import { getApiBaseUrl } from "./api";

describe("getApiBaseUrl", () => {
  const previous = process.env.NEXT_PUBLIC_API_URL;

  afterEach(() => {
    if (previous === undefined) {
      delete process.env.NEXT_PUBLIC_API_URL;
    } else {
      process.env.NEXT_PUBLIC_API_URL = previous;
    }
  });

  it("defaults to localhost when env is unset", () => {
    delete process.env.NEXT_PUBLIC_API_URL;
    expect(getApiBaseUrl()).toBe("http://localhost:8000");
  });

  it("uses NEXT_PUBLIC_API_URL when set", () => {
    process.env.NEXT_PUBLIC_API_URL = "http://api:8000";
    expect(getApiBaseUrl()).toBe("http://api:8000");
  });
});
